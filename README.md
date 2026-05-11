# File Organiser

A configurable Python tool that sorts a messy directory into clean category subfolders — images, documents, audio, video, code, archives, and more. Includes a **dry-run mode** to preview changes before anything is moved, and writes a full move log after each run.

---

## Features

- **Fully configurable** — category rules live in `config.json`, not in the code. Add, rename, or remove categories without touching a line of Python
- **Dry-run mode** — preview exactly what would be moved before committing (`--dry-run`)
- **Collision-safe** — if a file with the same name already exists in the destination, a numeric suffix is added (`photo.jpg` → `photo_1.jpg`) rather than overwriting
- **Edge cases handled** — hidden files skipped, files with no extension go to Misc, mixed-case extensions (`.JPG`, `.Pdf`) normalised automatically
- **Two-phase design** — plan first, execute second. The plan can be inspected, logged, or cancelled before a single file is touched
- **Full run report** — per-category breakdown + complete file-by-file move log saved to `data/organiser_report.txt`
- **18 unit tests** — covering config loading, categorisation, collision resolution, and reporting

---

## Project structure

```
project-03-file-organiser/
├── main.py                       # Entry point — run this
├── config.json                   # Customisable category rules
├── generate_sample_downloads.py  # Creates a demo messy folder
├── requirements.txt              # No third-party dependencies!
├── organiser/
│   ├── __init__.py
│   ├── config.py                 # Loads + validates JSON config
│   ├── organiser.py              # FileOrganiser — plan & execute
│   ├── reporter.py               # Console output + report file
│   └── exceptions.py             # SourceNotFoundError, ConfigError, MoveError
├── tests/
│   └── test_organiser.py         # 18 unit tests
└── data/
    ├── sample_downloads/         # Drop files here for the demo
    └── organiser_report.txt      # Generated after each run
```

---

## Quickstart

**1. Clone the repo**

```bash
git clone https://github.com/danieldobos/file-organiser.git
cd file-organiser
```

No third-party dependencies — this project uses only the Python standard library (`os`, `shutil`, `pathlib`, `json`, `argparse`).

**2. Generate a demo messy folder**

```bash
python generate_sample_downloads.py
```

This creates 33 files across all categories in `data/sample_downloads/`.

**3. Preview the plan without moving anything**

```bash
python main.py --dry-run
```

**4. Run it for real**

```bash
python main.py
```

**5. Use it on your own folder**

```bash
python main.py --source ~/Downloads
python main.py --source ~/Downloads --dest ~/Sorted
```

---

## Sample output

```
============================================================
  FILE ORGANISER
============================================================
  Source  : /home/user/Downloads
  Mode    : DRY RUN — no files will be moved

  Loaded 7 categories: Images, Documents, Audio, Video, Code, Archives, Misc

Planning...

  FILE                                     CATEGORY        EXTENSION
  ---------------------------------------- --------------- ----------
  Q4_Sales_Report_2024.pdf                 Documents       .pdf
  holiday_photo_mallorca.jpg               Images          .jpg
  podcast_episode_42.mp3                   Audio           .mp3
  mysterious_file_no_extension             Misc            (no extension)
  ...

  Total: 32 file(s) would be moved.

  DRY RUN complete — no files were moved.
```

---

## Customising the categories

Edit `config.json` to define your own rules:

```json
{
    "Design":       [".ai", ".psd", ".fig", ".sketch"],
    "Spreadsheets": [".xlsx", ".csv", ".ods"],
    "Writing":      [".docx", ".pdf", ".txt", ".md"],
    "Everything Else": []
}
```

The folder with an **empty list** (`[]`) is the catch-all — files that don't match any other rule go there. Rename it to whatever you like.

---

## All command-line options

```
python main.py --source PATH   Directory to organise
               --dest   PATH   Destination root (default: same as --source)
               --config FILE   Custom JSON config (default: built-in rules)
               --dry-run       Preview only — no files moved
```

---

## Run the tests

```bash
python tests/test_organiser.py
# or
pytest tests/ -v
```

All 18 tests use temporary directories and clean up after themselves.

---

## Tech stack

- **Pure Python standard library** — `os`, `shutil`, `pathlib`, `json`, `argparse`, `dataclasses`
- Zero pip dependencies

---

## Skills demonstrated

- **Two-phase architecture** — plan → execute, making dry-run trivial to implement
- **Configurable via JSON** — behaviour changed through data, not code edits
- **`dataclasses`** — `Move` and `MoveResult` as clean data containers
- **`pathlib`** — modern file path handling
- **`argparse`** — full CLI with `--source`, `--dest`, `--config`, `--dry-run`
- **Edge case handling** — hidden files, no-extension files, filename collisions, uppercase extensions
- **18 unit tests** — covering every module with temporary directories, zero side effects

---

## Author

**Daniel Dobos** — Python student based in Seville, Spain.  
Open to entry-level freelance projects in data cleaning, web scraping, and automation.
