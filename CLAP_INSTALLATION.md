# CLAP Model Installation Guide

This project integrates the **LAION-CLAP (Contrastive Language-Audio Pretraining)** model for advanced audio analysis. Due to specific dependency constraints, setting up the `laion-clap` package within this environment requires a manual workaround.

## Requirements Added
The following packages have been added to the project's ecosystem to support CLAP:
- `laion-clap`
- `torch` & `torchaudio` (Already present)
- `torchvision` (For model architectures used under the hood)
- `transformers` & `huggingface_hub` (For loading model configurations and weights)
- Miscellaneous utility dependencies: `pandas`, `progressbar`, `torchlibrosa`, `wandb`, `webdataset`, `wget`, `braceexpand`, `ftfy`, `h5py`

## Installation Steps (Windows / PowerShell)

Due to LAION-CLAP attempting to strictly downgrade `numpy` to an incompatible `<2.0.0` version, which breaks on Python 3.14 without a C Compiler, we installed it explicitly without dependencies, and provided the dependencies manually.

1. **Activate your virtual environment:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

2. **Install all underlying dependencies manually:**
   ```powershell
   pip install pandas progressbar torchlibrosa wandb webdataset wget braceexpand ftfy h5py 
   ```

3. **Install supporting deep-learning libraries:**
   ```powershell
   pip install transformers huggingface_hub torchvision
   ```

4. **Install `laion-clap` without fetching dependencies:**
   ```powershell
   pip install laion-clap --no-deps
   ```

## Verification

A verification script `backend/verify_clap.py` is provided to ensure everything was installed successfully and that the pretrained weights can be downloaded and instantiated securely.

Run the script:
```powershell
python backend/verify_clap.py
```

Expected Output:
```text
CLAP model correctly loaded.
```