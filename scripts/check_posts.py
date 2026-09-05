"""Check post frontmatter against the site's conventions.

An error means the post ships broken. A missing description empties the
OpenGraph card, and a bare unquoted date can shift a day in the feed. A warning
means it ships worse, so only errors set the exit code.
"""

import re
import sys
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

# section -> keys every published document in it must carry
REQUIRED = {
    "posts": ("title", "description", "date", "categories"),
    "til": ("title", "date", "categories"),
}
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def vocabulary():
    """Every category term _categories.yml allows, with its headings dropped."""
    groups = yaml.safe_load((ROOT / "_categories.yml").read_text())
    return {term for terms in groups.values() for term in terms}


def line_of(key, text):
    for n, line in enumerate(text.splitlines(), 1):
        if line.startswith(f"{key}:"):
            return n
    return 1


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, path, line, message):
        self.errors.append(f"{path}:{line} {message}")

    def warn(self, path, line, message):
        self.warnings.append(f"{path}:{line} {message}")


def check(qmd, section, terms, report):
    path = qmd.relative_to(ROOT)
    raw = qmd.read_text()
    match = FRONTMATTER.match(raw)
    if not match:
        report.error(path, 1, "no YAML frontmatter")
        return None

    text = match.group(1)
    try:
        meta = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        report.error(path, 1, f"unparseable frontmatter: {exc}")
        return None

    # A sequence, scalar, or number parses fine but has no keys to read, and
    # without this the whole scan dies before any finding is printed.
    if not isinstance(meta, dict):
        report.error(
            path, 1, f"frontmatter is {type(meta).__name__}, expected a mapping"
        )
        return None

    def at(key):
        return line_of(key, text) + 1  # +1 for the opening ---

    draft = meta.get("draft", False)
    if not isinstance(draft, bool):
        report.error(path, at("draft"), "draft must be a boolean")
        return None
    if draft:
        return meta

    for key in ("title", "description", "image-alt"):
        if key in meta and not isinstance(meta[key], str):
            report.error(path, at(key), f"{key} must be a string")

    for key in REQUIRED[section]:
        value = meta.get(key)
        if value is None or value == "" or value == []:
            report.error(path, at(key), f"missing {key}")

    # yaml.safe_load returns a date object for a bare 2026-08-22 and a str for a
    # quoted one. The bare form is what shifts a day in feeds across timezones.
    published = meta.get("date")
    if isinstance(published, date):
        report.error(path, at("date"), "quote the date to keep it timezone-stable")
    elif isinstance(published, str):
        try:
            # Local calendar date on purpose. Comparing against UTC would call
            # a post written this evening in Amsterdam a future post.
            if date.fromisoformat(published) > date.today():  # noqa: DTZ011
                report.error(path, at("date"), f"date {published} is in the future")
        except ValueError:
            report.error(path, at("date"), f"date {published!r} is not ISO YYYY-MM-DD")
    elif published is not None:
        report.error(path, at("date"), "date must be a quoted ISO YYYY-MM-DD string")

    categories = meta.get("categories")
    if categories is not None:
        if not isinstance(categories, list) or any(
            not isinstance(term, str) for term in categories
        ):
            report.error(path, at("categories"), "categories must be a list of strings")
        else:
            for term in categories:
                if term not in terms:
                    report.error(
                        path,
                        at("categories"),
                        f"category {term!r} not in _categories.yml",
                    )

    image = meta.get("image")
    if image is None or image is False or image == "":
        if section == "posts":
            report.warn(path, at("image"), "no preview image")
    elif not isinstance(image, str):
        report.error(path, at("image"), "image must be a path string or false")
    else:
        if not (qmd.parent / image).exists():
            report.error(path, at("image"), f"image {image} not found")
        if "image-alt" not in meta:
            report.warn(path, at("image"), 'no image-alt (use "" if decorative)')
    return meta


def main():
    terms = vocabulary()
    report = Report()
    drafts = 0
    published = 0

    for section in REQUIRED:
        for qmd in sorted((ROOT / section).glob("*/index.qmd")):
            meta = check(qmd, section, terms, report)
            if meta is None:
                continue
            drafts += bool(meta.get("draft"))
            published += not meta.get("draft")

    for warning in report.warnings:
        print(f"warn  {warning}")
    for error in report.errors:
        print(f"error {error}")

    counts = f"{published} published, {drafts} draft"
    print(f"\n{counts}: {len(report.errors)} errors, {len(report.warnings)} warnings")
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
