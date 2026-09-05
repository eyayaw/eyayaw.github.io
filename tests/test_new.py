"""YAML serialization in post scaffolding."""

import unittest
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import yaml

from scripts import new


class ScaffoldTests(unittest.TestCase):
    def test_scaffold_preserves_yaml_strings(self):
        titles = [
            r"Working in C:\temp",
            r"R regex: \d+",
            'A "quoted" title: [true, false] # $HOME',
            "First line\nSecond line\twith a tab",
            "Unicode: እያያው 🦆\u0085next line",
        ]
        project = "true, other] # category"
        with (
            TemporaryDirectory() as directory,
            patch.object(new, "ROOT", Path(directory)),
        ):
            for kind in new.KINDS:
                for index, title in enumerate(titles):
                    with self.subTest(kind=kind, title=title):
                        qmd = new.scaffold(
                            kind,
                            title,
                            slug=f"{kind}-{index}",
                            when=date(2025, 1, 1),
                            project=project,
                        )
                        frontmatter = qmd.read_text().split("---\n", 2)[1]
                        meta = yaml.safe_load(frontmatter)
                        self.assertEqual(meta["title"], title)
                        self.assertEqual(meta["date"], "2025-01-01")
                        self.assertIs(meta["draft"], True)
                        if kind == "package":
                            self.assertEqual(meta["categories"], ["package", project])
