
# MangaDexExport GUI

Simple `tkinter`-based interface for browsing a MangaDex library export.

1. Place your exported library JSON as `library.json` in this directory.
2. Run `python gui.py` to launch the viewer.

Selecting a title shows its description.

## Windows executable

Releases include a pre-built `MangaDexLibrary.exe` created with
[PyInstaller](https://pyinstaller.org/). To build the executable locally
you can run:

```
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name MangaDexLibrary gui.py
```

The resulting file will be available at `dist/MangaDexLibrary.exe`.

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

