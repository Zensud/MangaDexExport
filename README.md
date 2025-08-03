# MangaDex to ComicK Exporter

This repository provides a small utility for synchronising your MangaDex
followed manga with your ComicK library.

## Installation

```
pip install -r requirements.txt
```

## Usage

```
python exporter.py --md-username YOUR_USER --md-password YOUR_PASS \
    --comick-token YOUR_COMICK_TOKEN
```

Run with `--dry-run` to preview what would be added without modifying the
ComicK library.
