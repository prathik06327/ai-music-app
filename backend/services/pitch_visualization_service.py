"""
Pitch visualization data preparation service.

This service reuses the existing audio loading and TorchCREPE pitch extraction
pipeline to produce a clean, timestamped contour that can be consumed by a
frontend graph library later.
"""

from __future__ import annotations
import logging
from pathlib import Path
from typing import Literal, TypedDict

import numpy as np

from services.audio_service import load_audio
from services.pitch_service import HOP_LENGTH, extract_pitch_from_audio

logger = logging.getLogger(__name__)

MAX_INTERPOLATION_GAP_FRAMES = 5
SMOOTHING_WINDOW = 5
SPIKE_NEIGHBOR_SEMITONE_THRESHOLD = 2.0
SPIKE_CURRENT_SEMITONE_THRESHOLD = 7.0
SMOOTHING_BREAK_SEMITONE_THRESHOLD = 3.0

SUSTAINED_PITCH_TOLERANCE_SEMITONES = 0.5
MIN_SUSTAINED_DURATION_SECONDS = 0.30

STABILITY_WINDOW_SECONDS = 0.30
STABILITY_MAX_STD_SEMITONES = 0.20
MIN_STABLE_REGION_SECONDS = 0.30

MIN_TRANSITION_SEMITONES = 2.0
MIN_TRANSITION_SEPARATION_SECONDS = 0.10
TRANSITION_CONTEXT_SECONDS = 0.10

NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")


class PitchPoint(TypedDict):
    """Single timestamped pitch sample ready for JSON serialization."""

    time: float
    pitch: float


class PitchVisualizationResult(TypedDict):
    """Structured payload returned to the frontend."""

    duration: float
    sample_rate: int
    frame_count: int
    pitch_points: list[PitchPoint]
    summary: "PitchSummary"
    highest_pitch_point: "PitchExtremePoint"
    lowest_pitch_point: "PitchExtremePoint"
    sustained_regions: list["SustainedRegion"]
    stable_regions: list["StableRegion"]
    pitch_transitions: list["PitchTransition"]


class PitchSummary(TypedDict):
    minimum_pitch: float
    maximum_pitch: float
    average_pitch: float
    median_pitch: float
    pitch_range: float
    minimum_note: str
    maximum_note: str
    average_note: str


class PitchExtremePoint(TypedDict):
    time: float
    pitch: float
    note: str


class SustainedRegion(TypedDict):
    start_time: float
    end_time: float
    duration: float
    average_pitch: float
    note: str


class StableRegion(TypedDict):
    start_time: float
    end_time: float
    duration: float
    average_pitch: float
    note: str
    stability: float


class PitchTransition(TypedDict):
    time: float
    from_pitch: float
    to_pitch: float
    from_note: str
    to_note: str
    semitone_change: float
    direction: Literal["up", "down"]


def _merge_adjacent_transitions(transitions: list[PitchTransition]) -> list[PitchTransition]:
    """
    Merges nearby transitions with the same direction into one event.

    This prevents abrupt note changes from being split into multiple markers
    due to context windows around a single transition boundary.
    """
    if len(transitions) <= 1:
        return transitions

    merged: list[PitchTransition] = [dict(transitions[0])]
    for transition in transitions[1:]:
        last = merged[-1]
        if (
            transition["direction"] == last["direction"]
            and (transition["time"] - last["time"]) <= (2.0 * MIN_TRANSITION_SEPARATION_SECONDS)
        ):
            updated_to_pitch = float(transition["to_pitch"])
            updated_from_pitch = float(last["from_pitch"])
            semitone_change = _semitone_change(updated_from_pitch, updated_to_pitch)
            last["time"] = float(transition["time"])
            last["to_pitch"] = _round2(updated_to_pitch)
            last["to_note"] = transition["to_note"]
            last["semitone_change"] = _round2(semitone_change)
            last["direction"] = "up" if semitone_change > 0 else "down"
            continue

        merged.append(dict(transition))

    return merged


def _validate_audio_path(audio_path: Path) -> Path:
    """Ensures the requested audio file exists and is a file."""
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    if not audio_path.is_file():
        raise FileNotFoundError(f"Path is not a file: {audio_path}")
    return audio_path


def _generate_timestamps(frame_count: int, sample_rate: int, hop_length: int) -> np.ndarray:
    """Creates the time axis for each TorchCREPE frame."""
    if frame_count <= 0:
        return np.array([], dtype=np.float64)

    frame_indices = np.arange(frame_count, dtype=np.float64)
    return frame_indices * (hop_length / float(sample_rate))


def _prepare_raw_pitch_contour(pitch_values: np.ndarray) -> np.ndarray:
    """
    Preserves the original frame count while converting invalid frames to NaN.

    The visualization pipeline keeps missing frames internally so it can decide
    whether a gap is short enough to interpolate later.
    """
    contour = np.asarray(pitch_values, dtype=np.float64).reshape(-1)
    invalid_mask = ~np.isfinite(contour) | (contour <= 0)
    contour = contour.copy()
    contour[invalid_mask] = np.nan
    return contour


def _semitone_distance(left_pitch: float, right_pitch: float) -> float:
    """Returns the absolute semitone distance between two positive pitch values."""
    if left_pitch <= 0 or right_pitch <= 0:
        return float("inf")
    return float(abs(12.0 * np.log2(right_pitch / left_pitch)))


def _semitone_change(from_pitch: float, to_pitch: float) -> float:
    """Returns signed semitone change from one positive pitch to another."""
    if from_pitch <= 0 or to_pitch <= 0:
        return 0.0
    return float(12.0 * np.log2(to_pitch / from_pitch))


def _round2(value: float) -> float:
    return float(np.round(value, 2))


def _frequency_to_note(frequency_hz: float) -> str | None:
    """
    Converts a frequency in Hz to the nearest equal-temperament note name.

    Uses A4 = 440 Hz and standard MIDI mapping.
    """
    if not np.isfinite(frequency_hz) or frequency_hz <= 0:
        return None

    midi_note = int(np.round(69 + 12 * np.log2(frequency_hz / 440.0)))
    note_name = NOTE_NAMES[midi_note % 12]
    octave = (midi_note // 12) - 1
    return f"{note_name}{octave}"


def _empty_pitch_summary() -> PitchSummary:
    return {
        "minimum_pitch": 0.0,
        "maximum_pitch": 0.0,
        "average_pitch": 0.0,
        "median_pitch": 0.0,
        "pitch_range": 0.0,
        "minimum_note": "N/A",
        "maximum_note": "N/A",
        "average_note": "N/A",
    }


def _calculate_pitch_summary(pitch_values: np.ndarray) -> PitchSummary:
    """Calculates basic pitch statistics and note labels from valid pitch values."""
    values = np.asarray(pitch_values, dtype=np.float64)
    if values.size == 0:
        return _empty_pitch_summary()

    minimum_pitch = float(np.min(values))
    maximum_pitch = float(np.max(values))
    average_pitch = float(np.mean(values))
    median_pitch = float(np.median(values))
    pitch_range = maximum_pitch - minimum_pitch

    return {
        "minimum_pitch": _round2(minimum_pitch),
        "maximum_pitch": _round2(maximum_pitch),
        "average_pitch": _round2(average_pitch),
        "median_pitch": _round2(median_pitch),
        "pitch_range": _round2(pitch_range),
        "minimum_note": _frequency_to_note(minimum_pitch) or "N/A",
        "maximum_note": _frequency_to_note(maximum_pitch) or "N/A",
        "average_note": _frequency_to_note(average_pitch) or "N/A",
    }


def _empty_extreme_point() -> PitchExtremePoint:
    return {"time": 0.0, "pitch": 0.0, "note": "N/A"}


def _find_highest_pitch_point(timestamps: np.ndarray, pitch_values: np.ndarray) -> PitchExtremePoint:
    """Returns the first highest valid pitch point with note label."""
    if pitch_values.size == 0:
        return _empty_extreme_point()

    index = int(np.argmax(pitch_values))
    pitch = float(pitch_values[index])
    return {
        "time": _round2(float(timestamps[index])),
        "pitch": _round2(pitch),
        "note": _frequency_to_note(pitch) or "N/A",
    }


def _find_lowest_pitch_point(timestamps: np.ndarray, pitch_values: np.ndarray) -> PitchExtremePoint:
    """Returns the first lowest valid pitch point with note label."""
    if pitch_values.size == 0:
        return _empty_extreme_point()

    index = int(np.argmin(pitch_values))
    pitch = float(pitch_values[index])
    return {
        "time": _round2(float(timestamps[index])),
        "pitch": _round2(pitch),
        "note": _frequency_to_note(pitch) or "N/A",
    }


def _iter_voiced_segments(pitch_values: np.ndarray) -> list[tuple[int, int]]:
    """Returns (start, end) index pairs for contiguous finite voiced segments."""
    segments: list[tuple[int, int]] = []
    if pitch_values.size == 0:
        return segments

    start = None
    for index, value in enumerate(pitch_values):
        if np.isfinite(value) and value > 0:
            if start is None:
                start = index
            continue

        if start is not None:
            segments.append((start, index))
            start = None

    if start is not None:
        segments.append((start, pitch_values.size))
    return segments


def _region_duration_seconds(start_time: float, end_time: float, frame_step_seconds: float) -> float:
    return max(0.0, (end_time - start_time) + frame_step_seconds)


def _detect_sustained_regions(
    timestamps: np.ndarray,
    pitch_values: np.ndarray,
    frame_step_seconds: float,
) -> list[SustainedRegion]:
    """
    Detects conservative sustained-note regions within each voiced segment.
    """
    regions: list[SustainedRegion] = []

    for start, end in _iter_voiced_segments(pitch_values):
        segment_pitches = pitch_values[start:end]
        segment_times = timestamps[start:end]
        if segment_pitches.size == 0:
            continue

        candidate_start = 0
        for index in range(1, segment_pitches.size):
            representative_pitch = float(np.median(segment_pitches[candidate_start:index]))
            distance = _semitone_distance(representative_pitch, float(segment_pitches[index]))

            if distance <= SUSTAINED_PITCH_TOLERANCE_SEMITONES:
                continue

            candidate_end = index - 1
            start_time = float(segment_times[candidate_start])
            end_time = float(segment_times[candidate_end])
            duration = _region_duration_seconds(start_time, end_time, frame_step_seconds)
            if duration >= MIN_SUSTAINED_DURATION_SECONDS:
                region_values = segment_pitches[candidate_start : candidate_end + 1]
                avg_pitch = float(np.mean(region_values))
                regions.append(
                    {
                        "start_time": _round2(start_time),
                        "end_time": _round2(end_time),
                        "duration": _round2(duration),
                        "average_pitch": _round2(avg_pitch),
                        "note": _frequency_to_note(avg_pitch) or "N/A",
                    }
                )
            candidate_start = index

        start_time = float(segment_times[candidate_start])
        end_time = float(segment_times[-1])
        duration = _region_duration_seconds(start_time, end_time, frame_step_seconds)
        if duration >= MIN_SUSTAINED_DURATION_SECONDS:
            region_values = segment_pitches[candidate_start:]
            avg_pitch = float(np.mean(region_values))
            regions.append(
                {
                    "start_time": _round2(start_time),
                    "end_time": _round2(end_time),
                    "duration": _round2(duration),
                    "average_pitch": _round2(avg_pitch),
                    "note": _frequency_to_note(avg_pitch) or "N/A",
                }
            )

    return regions


def _stable_std_semitones(region_pitches: np.ndarray) -> float:
    """Computes std in semitone space around the region median."""
    if region_pitches.size == 0:
        return 0.0
    median_pitch = float(np.median(region_pitches))
    semitone_offsets = 12.0 * np.log2(region_pitches / median_pitch)
    return float(np.std(semitone_offsets))


def _detect_stable_regions(
    timestamps: np.ndarray,
    pitch_values: np.ndarray,
    frame_step_seconds: float,
) -> list[StableRegion]:
    """
    Detects low-variation pitch regions using semitone-space standard deviation.
    """
    regions: list[StableRegion] = []
    if frame_step_seconds <= 0:
        return regions

    window_frames = max(1, int(np.ceil(STABILITY_WINDOW_SECONDS / frame_step_seconds)))

    for start, end in _iter_voiced_segments(pitch_values):
        segment_pitches = pitch_values[start:end]
        segment_times = timestamps[start:end]
        if segment_pitches.size < window_frames:
            continue

        stable_mask = np.zeros(segment_pitches.size, dtype=bool)
        for index in range(0, segment_pitches.size - window_frames + 1):
            window = segment_pitches[index : index + window_frames]
            if _stable_std_semitones(window) <= STABILITY_MAX_STD_SEMITONES:
                stable_mask[index : index + window_frames] = True

        region_start = None
        for index, is_stable in enumerate(stable_mask):
            if is_stable and region_start is None:
                region_start = index
                continue

            if (not is_stable) and region_start is not None:
                region_end = index - 1
                start_time = float(segment_times[region_start])
                end_time = float(segment_times[region_end])
                duration = _region_duration_seconds(start_time, end_time, frame_step_seconds)
                if duration >= MIN_STABLE_REGION_SECONDS:
                    region_values = segment_pitches[region_start : region_end + 1]
                    avg_pitch = float(np.mean(region_values))
                    stability = _stable_std_semitones(region_values)
                    regions.append(
                        {
                            "start_time": _round2(start_time),
                            "end_time": _round2(end_time),
                            "duration": _round2(duration),
                            "average_pitch": _round2(avg_pitch),
                            "note": _frequency_to_note(avg_pitch) or "N/A",
                            "stability": _round2(stability),
                        }
                    )
                region_start = None

        if region_start is not None:
            start_time = float(segment_times[region_start])
            end_time = float(segment_times[-1])
            duration = _region_duration_seconds(start_time, end_time, frame_step_seconds)
            if duration >= MIN_STABLE_REGION_SECONDS:
                region_values = segment_pitches[region_start:]
                avg_pitch = float(np.mean(region_values))
                stability = _stable_std_semitones(region_values)
                regions.append(
                    {
                        "start_time": _round2(start_time),
                        "end_time": _round2(end_time),
                        "duration": _round2(duration),
                        "average_pitch": _round2(avg_pitch),
                        "note": _frequency_to_note(avg_pitch) or "N/A",
                        "stability": _round2(stability),
                    }
                )

    return regions


def _detect_pitch_transitions(
    timestamps: np.ndarray,
    pitch_values: np.ndarray,
    frame_step_seconds: float,
) -> list[PitchTransition]:
    """
    Detects significant local pitch transitions within voiced segments.

    Uses median context windows to avoid tagging frame-level jitter.
    """
    transitions: list[PitchTransition] = []
    if frame_step_seconds <= 0:
        return transitions

    context_frames = max(1, int(np.ceil(TRANSITION_CONTEXT_SECONDS / frame_step_seconds)))
    min_separation_frames = max(1, int(np.ceil(MIN_TRANSITION_SEPARATION_SECONDS / frame_step_seconds)))

    for start, end in _iter_voiced_segments(pitch_values):
        segment_pitches = pitch_values[start:end]
        segment_times = timestamps[start:end]
        if segment_pitches.size < (2 * context_frames + 1):
            continue

        last_transition_index = -10**9
        for boundary in range(context_frames - 1, segment_pitches.size - context_frames - 1):
            if boundary - last_transition_index < min_separation_frames:
                continue

            left_window = segment_pitches[boundary - context_frames + 1 : boundary + 1]
            right_window = segment_pitches[boundary + 1 : boundary + 1 + context_frames]

            from_pitch = float(np.median(left_window))
            to_pitch = float(np.median(right_window))
            semitone_change = _semitone_change(from_pitch, to_pitch)

            if abs(semitone_change) < MIN_TRANSITION_SEMITONES:
                continue

            transition_time = float(segment_times[boundary + 1])
            transitions.append(
                {
                    "time": _round2(transition_time),
                    "from_pitch": _round2(from_pitch),
                    "to_pitch": _round2(to_pitch),
                    "from_note": _frequency_to_note(from_pitch) or "N/A",
                    "to_note": _frequency_to_note(to_pitch) or "N/A",
                    "semitone_change": _round2(semitone_change),
                    "direction": "up" if semitone_change > 0 else "down",
                }
            )
            last_transition_index = boundary

    return _merge_adjacent_transitions(transitions)


def _interpolate_short_gaps(pitch_values: np.ndarray) -> tuple[np.ndarray, int]:
    """
    Interpolates only short NaN gaps that are surrounded by valid pitch values.
    """
    processed = np.asarray(pitch_values, dtype=np.float64).copy()
    interpolated_frames = 0

    if processed.size == 0 or not np.any(np.isnan(processed)):
        return processed, interpolated_frames

    valid_indices = np.flatnonzero(np.isfinite(processed))
    if valid_indices.size < 2:
        return processed, interpolated_frames

    nan_mask = np.isnan(processed)
    gap_start = None

    for index, is_nan in enumerate(nan_mask):
        if is_nan and gap_start is None:
            gap_start = index
            continue

        if not is_nan and gap_start is not None:
            gap_end = index - 1
            gap_length = gap_end - gap_start + 1
            left_index = gap_start - 1
            right_index = index

            if (
                gap_length <= MAX_INTERPOLATION_GAP_FRAMES
                and left_index >= 0
                and right_index < processed.size
                and np.isfinite(processed[left_index])
                and np.isfinite(processed[right_index])
            ):
                interpolated_values = np.linspace(
                    processed[left_index],
                    processed[right_index],
                    gap_length + 2,
                    dtype=np.float64,
                )[1:-1]
                processed[gap_start : gap_end + 1] = interpolated_values
                interpolated_frames += gap_length
            gap_start = None

    return processed, interpolated_frames


def _remove_pitch_spikes(pitch_values: np.ndarray) -> tuple[np.ndarray, int]:
    """
    Replaces clearly isolated outliers with a local linear estimate.

    The thresholds are intentionally conservative: the surrounding frames must
    be close to each other while the current frame is far from both of them in
    semitone space. This avoids deleting legitimate note jumps and fast runs.
    """
    processed = np.asarray(pitch_values, dtype=np.float64).copy()
    detected_spikes = 0

    if processed.size < 3:
        return processed, detected_spikes

    for index in range(1, processed.size - 1):
        current = processed[index]
        left = processed[index - 1]
        right = processed[index + 1]

        if not (np.isfinite(current) and np.isfinite(left) and np.isfinite(right)):
            continue

        surrounding_distance = _semitone_distance(left, right)
        left_distance = _semitone_distance(left, current)
        right_distance = _semitone_distance(current, right)

        if (
            surrounding_distance <= SPIKE_NEIGHBOR_SEMITONE_THRESHOLD
            and left_distance >= SPIKE_CURRENT_SEMITONE_THRESHOLD
            and right_distance >= SPIKE_CURRENT_SEMITONE_THRESHOLD
        ):
            processed[index] = (left + right) / 2.0
            detected_spikes += 1

    return processed, detected_spikes


def _smooth_pitch_contour(pitch_values: np.ndarray) -> np.ndarray:
    """
    Smooths only continuous voiced regions with a small moving-average window.
    """
    processed = np.asarray(pitch_values, dtype=np.float64).copy()
    if processed.size == 0 or SMOOTHING_WINDOW <= 1:
        return processed

    half_window = SMOOTHING_WINDOW // 2
    region_start = None

    def _smooth_region(start: int, end: int) -> None:
        region = processed[start:end]
        region_length = region.size
        if region_length < SMOOTHING_WINDOW:
            return

        pad_width = half_window
        padded = np.pad(region, (pad_width, pad_width), mode="edge")
        kernel = np.ones(SMOOTHING_WINDOW, dtype=np.float64) / float(SMOOTHING_WINDOW)
        smoothed = np.convolve(padded, kernel, mode="valid")
        processed[start:end] = smoothed

    def _smooth_stable_subregions(start: int, end: int) -> None:
        region = processed[start:end]
        if region.size < SMOOTHING_WINDOW:
            return

        subregion_start = 0
        for offset in range(1, region.size):
            previous_value = region[offset - 1]
            current_value = region[offset]
            if _semitone_distance(previous_value, current_value) > SMOOTHING_BREAK_SEMITONE_THRESHOLD:
                _smooth_region(start + subregion_start, start + offset)
                subregion_start = offset

        _smooth_region(start + subregion_start, end)

    for index, value in enumerate(processed):
        if np.isfinite(value) and value > 0:
            if region_start is None:
                region_start = index
            continue

        if region_start is not None:
            _smooth_stable_subregions(region_start, index)
            region_start = None

    if region_start is not None:
        _smooth_stable_subregions(region_start, processed.size)

    return processed


def _clean_pitch_points(timestamps: np.ndarray, pitch_values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Removes invalid pitch frames only at the final JSON construction step."""
    valid_mask = np.isfinite(timestamps) & np.isfinite(pitch_values) & (pitch_values > 0)
    return timestamps[valid_mask], pitch_values[valid_mask]


def _validate_visualization_series(timestamps: np.ndarray, pitch_values: np.ndarray) -> None:
    """Validates the cleaned contour before it is converted to JSON-ready data."""
    if timestamps.size != pitch_values.size:
        raise ValueError("Timestamp and pitch arrays must have the same length.")

    if timestamps.size == 0:
        logger.warning("No valid pitch frames were available after cleaning.")
        return

    if not np.all(np.isfinite(timestamps)):
        raise ValueError("Pitch timestamps must be finite.")
    if not np.all(np.isfinite(pitch_values)):
        raise ValueError("Pitch values must be finite.")
    if np.any(pitch_values <= 0):
        raise ValueError("Pitch values must be strictly positive after cleaning.")
    if np.any(np.diff(timestamps) <= 0):
        raise ValueError("Pitch timestamps must be strictly increasing.")


def _build_pitch_points(timestamps: np.ndarray, pitch_values: np.ndarray) -> list[PitchPoint]:
    """Converts aligned arrays into JSON-ready dictionaries."""
    return [
        {"time": float(time_value), "pitch": float(pitch_value)}
        for time_value, pitch_value in zip(timestamps, pitch_values, strict=False)
    ]


def generate_pitch_visualization(audio_path: str | Path) -> PitchVisualizationResult:
    """
    Generates timestamped pitch contour data for visualization.

    The function intentionally reuses the existing audio loader and TorchCREPE
    inference helper so the scoring pipeline remains untouched.
    """
    path = _validate_audio_path(Path(audio_path))
    logger.info("Generating pitch visualization for %s", path)

    try:
        audio_array, sample_rate = load_audio(path.as_posix())
        raw_pitch_values = extract_pitch_from_audio(audio_array, sample_rate)
    except Exception as exc:
        logger.exception("Failed to generate pitch visualization for %s", path)
        raise RuntimeError(f"Failed to generate pitch visualization: {exc}") from exc

    duration = float(len(audio_array) / float(sample_rate))
    timestamps = _generate_timestamps(len(raw_pitch_values), sample_rate, HOP_LENGTH)
    frame_step_seconds = float(HOP_LENGTH / float(sample_rate))

    raw_pitch_contour = _prepare_raw_pitch_contour(raw_pitch_values)
    invalid_raw_frames = int(np.count_nonzero(np.isnan(raw_pitch_contour)))

    interpolated_pitch, interpolated_frames = _interpolate_short_gaps(raw_pitch_contour)
    spike_free_pitch, detected_spikes = _remove_pitch_spikes(interpolated_pitch)
    smoothed_pitch = _smooth_pitch_contour(spike_free_pitch)

    summary = _calculate_pitch_summary(smoothed_pitch[np.isfinite(smoothed_pitch) & (smoothed_pitch > 0)])
    sustained_regions = _detect_sustained_regions(timestamps, smoothed_pitch, frame_step_seconds)
    stable_regions = _detect_stable_regions(timestamps, smoothed_pitch, frame_step_seconds)
    pitch_transitions = _detect_pitch_transitions(timestamps, smoothed_pitch, frame_step_seconds)

    clean_timestamps, clean_pitch_values = _clean_pitch_points(timestamps, smoothed_pitch)
    _validate_visualization_series(clean_timestamps, clean_pitch_values)

    highest_pitch_point = _find_highest_pitch_point(clean_timestamps, clean_pitch_values)
    lowest_pitch_point = _find_lowest_pitch_point(clean_timestamps, clean_pitch_values)

    pitch_points = _build_pitch_points(clean_timestamps, clean_pitch_values)

    result: PitchVisualizationResult = {
        "duration": duration,
        "sample_rate": int(sample_rate),
        "frame_count": len(pitch_points),
        "pitch_points": pitch_points,
        "summary": summary,
        "highest_pitch_point": highest_pitch_point,
        "lowest_pitch_point": lowest_pitch_point,
        "sustained_regions": sustained_regions,
        "stable_regions": stable_regions,
        "pitch_transitions": pitch_transitions,
    }

    logger.info(
        "Pitch visualization generated: duration=%.2f, sample_rate=%d, raw_frames=%d, invalid_raw_frames=%d, interpolated_frames=%d, detected_spikes=%d, final_valid_pitch_points=%d",
        result["duration"],
        result["sample_rate"],
        len(raw_pitch_values),
        invalid_raw_frames,
        interpolated_frames,
        detected_spikes,
        result["frame_count"],
    )
    logger.info(
        "Pitch metadata generated: minimum_pitch=%.2fHz, maximum_pitch=%.2fHz, sustained_regions=%d, stable_regions=%d, pitch_transitions=%d",
        summary["minimum_pitch"],
        summary["maximum_pitch"],
        len(sustained_regions),
        len(stable_regions),
        len(pitch_transitions),
    )
    return result