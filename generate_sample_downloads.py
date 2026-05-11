"""
generate_sample_downloads.py
----------------------------
Creates a realistic, messy sample_downloads folder for the demo.

Generates 40+ files spanning all categories, with some edge cases:
  - Files with no extension
  - Duplicate filenames (to test collision handling)
  - Hidden files (should be skipped)
  - Mixed case extensions (.JPG, .Pdf, etc.)
"""

import os

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "data", "sample_downloads")

FILES = [
    # Images
    "holiday_photo_mallorca.jpg",
    "profile_picture.PNG",           # uppercase extension
    "logo_design_v2.svg",
    "screenshot_2024_01_15.webp",
    "family_reunion.jpeg",
    "product_mockup.gif",

    # Documents
    "Q4_Sales_Report_2024.pdf",
    "invoice_client_abc.pdf",
    "project_proposal.docx",
    "meeting_notes_march.txt",
    "budget_forecast.xlsx",
    "data_export_raw.csv",
    "presentation_final.pptx",
    "README.md",

    # Audio
    "podcast_episode_42.mp3",
    "background_music.wav",
    "voicenote_memo.m4a",
    "lo_fi_beats.flac",

    # Video
    "screen_recording_demo.mp4",
    "tutorial_python_basics.mkv",
    "holiday_clip_ibiza.mov",

    # Code
    "data_cleaner.py",
    "index.html",
    "styles.css",
    "api_config.json",
    "deploy.sh",
    "requirements.txt.backup",       # goes to Misc

    # Archives
    "project_backup_2024.zip",
    "old_photos_archive.tar.gz",
    "fonts_collection.rar",

    # Edge cases
    "mysterious_file_no_extension",  # no extension → Misc
    "another.unknown.extension.xyz", # unknown ext → Misc
    ".hidden_system_file",           # hidden → should be SKIPPED
    "Q4_Sales_Report_2024.pdf",      # DUPLICATE of above → collision test
    "holiday_photo_mallorca.jpg",    # DUPLICATE → collision test
]


def main():
    os.makedirs(SAMPLE_DIR, exist_ok=True)

    created = 0
    for filename in FILES:
        path = os.path.join(SAMPLE_DIR, filename)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"Sample content for: {filename}\n")
            created += 1

    total = len([f for f in os.listdir(SAMPLE_DIR)])
    print(f"Sample downloads folder ready.")
    print(f"  Created : {created} new files")
    print(f"  Total   : {total} files in {SAMPLE_DIR}")


if __name__ == "__main__":
    main()
