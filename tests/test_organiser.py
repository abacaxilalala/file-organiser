"""
tests/test_organiser.py
-----------------------
Unit tests for the config, organiser, and reporter modules.

All tests use temporary directories — nothing is written to the
actual project folder, and tests clean up after themselves.

Run with:
    python -m pytest tests/ -v
    python tests/test_organiser.py
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from organiser.config import load_config, build_extension_map, get_catchall_folder
from organiser.organiser import FileOrganiser
from organiser.reporter import generate_report
from organiser.exceptions import SourceNotFoundError, ConfigError


def make_temp_dir_with_files(files: list[str]) -> str:
    """Create a temporary directory containing the given (empty) files."""
    tmp = tempfile.mkdtemp()
    for filename in files:
        open(os.path.join(tmp, filename), "w").close()
    return tmp


class TestConfig(unittest.TestCase):

    def test_default_config_returned_when_no_path(self):
        """load_config(None) should return the built-in defaults."""
        config = load_config(None)
        self.assertIn("Images", config)
        self.assertIn("Documents", config)
        self.assertIn("Misc", config)

    def test_default_config_returned_when_file_missing(self):
        """load_config with a nonexistent path returns defaults, not error."""
        config = load_config("/nonexistent/path/config.json")
        self.assertIsInstance(config, dict)
        self.assertTrue(len(config) > 0)

    def test_valid_custom_config_loaded(self):
        """A valid JSON config file is loaded correctly."""
        data = {"Photos": [".jpg", ".png"], "Docs": [".pdf"], "Other": []}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(data, f)
            path = f.name

        config = load_config(path)
        self.assertIn("Photos", config)
        self.assertIn(".jpg", config["Photos"])
        os.unlink(path)

    def test_extensions_normalised_to_lowercase(self):
        """Extensions without dots or in uppercase are normalised."""
        data = {"Images": ["JPG", ".PNG", "gif"]}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(data, f)
            path = f.name

        config = load_config(path)
        for ext in config["Images"]:
            self.assertTrue(ext.startswith("."), ext)
            self.assertEqual(ext, ext.lower(), ext)
        os.unlink(path)

    def test_invalid_json_raises_config_error(self):
        """A malformed JSON file raises ConfigError."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            f.write("this is not json {{{")
            path = f.name

        with self.assertRaises(ConfigError):
            load_config(path)
        os.unlink(path)

    def test_build_extension_map(self):
        """build_extension_map inverts the categories correctly."""
        categories = {"Images": [".jpg", ".png"], "Docs": [".pdf"], "Misc": []}
        ext_map = build_extension_map(categories)
        self.assertEqual(ext_map[".jpg"], "Images")
        self.assertEqual(ext_map[".png"], "Images")
        self.assertEqual(ext_map[".pdf"], "Docs")
        self.assertNotIn("Misc", ext_map)  # Catch-all has no entries

    def test_get_catchall_folder(self):
        """Folder with empty extension list is identified as catch-all."""
        categories = {"Images": [".jpg"], "Misc": []}
        self.assertEqual(get_catchall_folder(categories), "Misc")


class TestOrganiser(unittest.TestCase):

    def setUp(self):
        self.categories = load_config(None)

    def test_raises_if_source_not_found(self):
        """SourceNotFoundError raised for nonexistent source dir."""
        with self.assertRaises(SourceNotFoundError):
            FileOrganiser("/nonexistent/path", None, self.categories)

    def test_plan_returns_one_move_per_file(self):
        """Plan has exactly one Move per file in the source dir."""
        src = make_temp_dir_with_files(["photo.jpg", "report.pdf", "song.mp3"])
        organiser = FileOrganiser(src, None, self.categories)
        plan = organiser.plan()
        self.assertEqual(len(plan), 3)

    def test_plan_assigns_correct_category(self):
        """JPG → Images, PDF → Documents, MP3 → Audio."""
        src = make_temp_dir_with_files(["photo.jpg", "report.pdf", "song.mp3"])
        organiser = FileOrganiser(src, None, self.categories)
        plan = organiser.plan()
        by_file = {m.filename: m.category for m in plan}
        self.assertEqual(by_file["photo.jpg"], "Images")
        self.assertEqual(by_file["report.pdf"], "Documents")
        self.assertEqual(by_file["song.mp3"], "Audio")

    def test_unknown_extension_goes_to_misc(self):
        """Files with unknown extensions are categorised as Misc."""
        src = make_temp_dir_with_files(["mystery.xyz"])
        organiser = FileOrganiser(src, None, self.categories)
        plan = organiser.plan()
        self.assertEqual(plan[0].category, "Misc")

    def test_hidden_files_skipped(self):
        """Files starting with '.' are excluded from the plan."""
        src = make_temp_dir_with_files([".hidden", "visible.txt"])
        organiser = FileOrganiser(src, None, self.categories)
        plan = organiser.plan()
        filenames = [m.filename for m in plan]
        self.assertNotIn(".hidden", filenames)
        self.assertIn("visible.txt", filenames)

    def test_execute_moves_files(self):
        """After execute(), files exist in dest and not in source."""
        src = make_temp_dir_with_files(["photo.jpg"])
        dest = tempfile.mkdtemp()
        organiser = FileOrganiser(src, dest, self.categories)
        plan = organiser.plan()
        results = organiser.execute(plan)

        self.assertTrue(results[0].success)
        self.assertFalse(os.path.exists(os.path.join(src, "photo.jpg")))
        self.assertTrue(os.path.exists(results[0].move.destination))

    def test_execute_creates_category_folders(self):
        """Destination category subdirectories are created automatically."""
        src = make_temp_dir_with_files(["photo.jpg", "report.pdf"])
        dest = tempfile.mkdtemp()
        organiser = FileOrganiser(src, dest, self.categories)
        results = organiser.execute(organiser.plan())

        self.assertTrue(os.path.isdir(os.path.join(dest, "Images")))
        self.assertTrue(os.path.isdir(os.path.join(dest, "Documents")))

    def test_collision_resolved_with_suffix(self):
        """Duplicate filenames get a numeric suffix rather than overwriting."""
        src = make_temp_dir_with_files(["photo.jpg"])
        dest = tempfile.mkdtemp()

        # Pre-create a file at the destination to simulate a collision.
        os.makedirs(os.path.join(dest, "Images"))
        with open(os.path.join(dest, "Images", "photo.jpg"), "w") as f:
            f.write("existing file")

        organiser = FileOrganiser(src, dest, self.categories)
        plan = organiser.plan()

        # The plan should resolve to "photo_1.jpg", not "photo.jpg".
        self.assertIn("photo_1.jpg", plan[0].destination)

    def test_plan_empty_for_empty_directory(self):
        """An empty source directory produces an empty plan."""
        src = tempfile.mkdtemp()
        organiser = FileOrganiser(src, None, self.categories)
        self.assertEqual(organiser.plan(), [])


class TestReporter(unittest.TestCase):

    def test_report_file_created(self):
        """generate_report should write a file to the given path."""
        from organiser.organiser import Move, MoveResult
        move = Move("/src/photo.jpg", "/dst/Images/photo.jpg", "photo.jpg", "Images", ".jpg")
        results = [MoveResult(move=move, success=True)]

        with tempfile.TemporaryDirectory() as tmp:
            report_path = os.path.join(tmp, "report.txt")
            generate_report(results, "/src", "/dst", report_path)
            self.assertTrue(os.path.exists(report_path))

    def test_report_contains_key_sections(self):
        """Report file should contain Overview, Category, and Move Log sections."""
        from organiser.organiser import Move, MoveResult
        move = Move("/src/doc.pdf", "/dst/Documents/doc.pdf", "doc.pdf", "Documents", ".pdf")
        results = [MoveResult(move=move, success=True)]

        with tempfile.TemporaryDirectory() as tmp:
            report_path = os.path.join(tmp, "report.txt")
            generate_report(results, "/src", "/dst", report_path)
            with open(report_path, encoding="utf-8") as f:
                content = f.read()

        self.assertIn("OVERVIEW", content)
        self.assertIn("FILES BY CATEGORY", content)
        self.assertIn("MOVE LOG", content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
