"""Metadata validation for published posts."""

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import yaml

from scripts import check_posts


class CheckPostsTests(unittest.TestCase):
    def test_invalid_fields_report_errors_and_scan_continues(self):
        cases = {
            "draft": ["false", 0, None, []],
            "title": [False, 123, []],
            "description": [False, {}],
            "date": [123, False, [], {}],
            "categories": [123, "r", [{"r": True}], [False]],
            "image": [123, True, [], {}],
            "image-alt": [False, None, []],
        }
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "_categories.yml").write_text("tech: [r]\n")
            broken = root / "posts/a-broken/index.qmd"
            valid = root / "posts/z-valid/index.qmd"
            broken.parent.mkdir(parents=True)
            valid.parent.mkdir(parents=True)
            self.write_post(valid)
            with patch.object(check_posts, "ROOT", root):
                for key, values in cases.items():
                    for value in values:
                        with self.subTest(key=key, value=value):
                            self.write_post(broken, **{key: value})
                            output = io.StringIO()
                            with redirect_stdout(output):
                                status = check_posts.main()
                            self.assertEqual(status, 1)
                            self.assertIn(f"{key} must be", output.getvalue())
                            self.assertIn(
                                "posts/z-valid/index.qmd:2 no preview image",
                                output.getvalue(),
                            )

    def test_image_warnings_and_missing_files(self):
        cases = [
            ({}, "posts", 0, 1),
            ({"image": None}, "posts", 0, 1),
            ({"image": ""}, "posts", 0, 1),
            ({"image": False}, "posts", 0, 1),
            ({"draft": True}, "posts", 0, 0),
            ({}, "til", 0, 0),
            ({"image": "thumbnail.png", "image-alt": ""}, "posts", 0, 0),
            ({"image": "absent.png", "image-alt": ""}, "posts", 1, 0),
        ]
        with TemporaryDirectory() as directory:
            root = Path(directory)
            qmd = root / "index.qmd"
            (root / "thumbnail.png").touch()
            with patch.object(check_posts, "ROOT", root):
                for meta, section, errors, warnings in cases:
                    with self.subTest(meta=meta, section=section):
                        self.write_post(qmd, **meta)
                        report = check_posts.Report()
                        check_posts.check(qmd, section, {"r"}, report)
                        self.assertEqual(len(report.errors), errors)
                        self.assertEqual(len(report.warnings), warnings)

    @staticmethod
    def write_post(path, **overrides):
        meta = {
            "title": "Example",
            "description": "Example",
            "date": "2025-01-01",
            "categories": ["r"],
        }
        meta.update(overrides)
        path.write_text("---\n" + yaml.safe_dump(meta) + "---\n")
