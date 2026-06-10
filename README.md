# 🎵 AI Music Performance Analyzer

An AI-powered music evaluation platform that analyzes a user's singing performance against a reference track and generates detailed accuracy scores based on pitch, rhythm, tempo, and timbre.

The system uses modern audio processing and machine learning techniques to isolate vocals, extract musical features, compare performances, and generate an overall performance rating.

---

# Features

## Vocal Isolation

Uses Demucs source separation to isolate vocals from uploaded audio tracks.

Extracted stems:

* Vocals
* Drums
* Bass
* Other

Current analysis is performed using the isolated vocal track.

---

## Pitch Analysis

Evaluates how accurately the user matches the notes of the reference performance.

Technologies:

* TorchCrepe
* librosa
* Dynamic Time Warping (DTW)

Outputs:

* Pitch Accuracy Score
* Pitch Comparison Graph
* Pitch Difference Metrics

---

## Rhythm Analysis

Measures timing accuracy by comparing note and syllable onsets between performances.

Technology:

* librosa Onset Detection

Outputs:

* Rhythm Score

---

## Tempo Analysis

Compares the overall speed and pacing of both performances.

Technology:

* librosa Beat Tracking

Outputs:

* Tempo Score

---

## Timbre Analysis

Measures vocal similarity using audio embeddings.

Technology:

* CLAP (Contrastive Language-Audio Pretraining)

Outputs:

* Timbre Score
* Similarity Score

---

## Weighted Scoring Engine

Generates a final performance score using weighted metrics.

Weights:

| Metric | Weight |
| ------ | ------ |
| Pitch  | 50%    |
| Rhythm | 25%    |
| Tempo  | 10%    |
| Timbre | 15%    |

Outputs:

* Overall Score
* Individual Component Scores

---

## AI Feedback (Planned)

Future versions will integrate Gemma 2 9B to provide:

* Performance Summaries
* Strength Analysis
* Improvement Suggestions
* Vocal Coaching Feedback

---

# System Architecture

```text
User
↓
Next.js Frontend
↓
FastAPI Backend
↓
Audio Upload
↓
Demucs Source Separation
↓
Isolated Vocals
↓
Pitch Analysis
↓
Rhythm Analysis
↓
Tempo Analysis
↓
Timbre Analysis
↓
Weighted Score Engine
↓
Results Dashboard
```

---

# Technology Stack

## Frontend

* Next.js
* TypeScript
* TailwindCSS

## Backend

* FastAPI
* Python

## Audio Processing

* Demucs
* librosa

## Machine Learning

* TorchCrepe
* CLAP

## Visualization

* Matplotlib

---

# Project Structure

```text
frontend/
│
├── app/
├── components/
├── public/
└── styles/

backend/
│
├── services/
│   ├── audio_service.py
│   ├── pitch_service.py
│   ├── rhythm_service.py
│   ├── timbre_service.py
│   └── alignment_service.py
│
├── uploads/
├── outputs/
│
├── main.py
├── requirements.txt
└── test_*.py
```

---

# API Endpoints

## Health Check

```http
GET /
```

Response:

```json
{
  "message": "AI Music App Running"
}
```

---

## Upload Audio

```http
POST /upload
```

Uploads audio and performs vocal separation.

Response:

```json
{
  "success": true,
  "vocals_path": "outputs/htdemucs/song/vocals.wav"
}
```

---

## Pitch Analysis

```http
POST /analyze-pitch
```

Returns:

```json
{
  "pitch_score": 98.7,
  "average_difference": 1.2,
  "graph_path": "..."
}
```

---

## Timbre Analysis

```http
POST /analyze-timbre
```

Returns:

```json
{
  "timbre_score": 94,
  "similarity": 0.94
}
```

---

## Full Performance Analysis

```http
POST /analyze-performance
```

Returns:

```json
{
  "pitch_score": 98.7,
  "rhythm_score": 87.2,
  "tempo_score": 92.1,
  "timbre_score": 94.0,
  "overall_score": 93.4
}
```

---

# Installation

## Clone Repository

```bash
git clone <repository-url>
cd ai-music-app
```

---

## Backend Setup

Create virtual environment:

```bash
python -m venv .venv
```

Activate:

Windows

```bash
.venv\Scripts\activate
```

Mac/Linux

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run backend:

```bash
uvicorn main:app --reload
```

Backend:

```text
http://localhost:8000
```

---

## Frontend Setup

Navigate:

```bash
cd frontend
```

Install packages:

```bash
npm install
```

Run:

```bash
npm run dev
```

Frontend:

```text
http://localhost:3000
```

---

# Example Workflow

1. Upload Reference Audio
2. Upload User Performance
3. Demucs isolates vocals
4. Backend extracts musical features
5. Scores are calculated
6. Results are displayed
7. Optional AI feedback (future release)

---

# Current Status

## Completed

* Audio Upload
* Demucs Integration
* Pitch Analysis
* Rhythm Analysis
* Tempo Analysis
* Timbre Analysis
* Overall Scoring Engine
* FastAPI Backend
* Next.js Frontend
* Results Dashboard

## In Progress

* Frontend Refinements
* UI Enhancements
* Deterministic Model Improvements

## Planned

* Gemma 2 AI Feedback
* Instrument-Level Scoring
* Enhanced Visual Analytics
* Improved Scoring Accuracy
* Production Deployment

---


# License

This project was developed for educational and research purposes.

---

# Author

AI Music Performance Analyzer

Built using FastAPI, Demucs, TorchCrepe, CLAP, and Next.js.
