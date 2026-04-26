# Spotifyanalysis

Small data-cleaning project for Spotify chart trends. The main script loads the raw dataset, normalizes column names, removes duplicates, cleans text and numeric fields, filters invalid rows, adds a few helper columns for analysis, and writes the cleaned output back to disk.

## What it does

- Reads `spotify_global_trends.csv`
- Cleans and standardizes the dataset with pandas
- Writes `cleaned_spotify_global_trends.csv`
- Includes unit tests for the cleaning pipeline

## Requirements

- Python 3.10 or newer
- `pandas`

## Setup

Create and activate a virtual environment, then install the dependency:

```bash
python -m venv .venv
source .venv/bin/activate
pip install pandas
```

## Run the cleaner

```bash
python run.py
```

The script prints a short summary and saves the cleaned file as `cleaned_spotify_global_trends.csv` in the project root.

## Run tests

```bash
python -m unittest test_run.py
```

## Project files

- `run.py` contains the cleaning pipeline
- `test_run.py` covers the helper functions and end-to-end cleaning flow
- `spotify_global_trends.csv` is the raw input dataset
- `cleaned_spotify_global_trends.csv` is the generated output
