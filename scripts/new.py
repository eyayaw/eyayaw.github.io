"""Scaffold a new post or TIL entry from _templates/."""

import argparse
import re
from datetime import date
from pathlib import Path
from string import Template

import yaml

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "_templates"

# kind -> (section directory, template file)
KINDS = {
    "post": ("posts", "post.qmd"),
    "package": ("posts", "package.qmd"),
    "til": ("til", "til.qmd"),
}


def slugify(title):
    slug = re.sub(r"[^\w-]", "-", title.lower().strip())
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def scaffold(kind, title, slug=None, when=None, project=None):
    section, template = KINDS[kind]
    slug = slug or slugify(title)
    # The directory name is the post's URL and its giscus comment key, so it is
    # frozen once published even if the title later changes.
    target = (ROOT / section / slug).resolve()
    # A --slug of "../elsewhere", "/tmp/x", or "a/b/c" would otherwise write
    # outside the section, and the listings only glob one level deep.
    if target.parent != (ROOT / section) or not slug:
        raise SystemExit(f"error: {slug!r} must be a single directory name")
    if target.exists():
        raise SystemExit(f"error: {target.relative_to(ROOT)} already exists")

    # Local calendar date on purpose. UTC would date a post written late in the
    # evening to the following day.
    when = when or date.today()  # noqa: DTZ011
    # A package post carries its project name as a category, which is what
    # groups the project's posts. The first slug word is usually that name.
    project = project or slug.split("-")[0]

    # A literal $ in a template must be written $$.
    source = Template((TEMPLATES / template).read_text())
    try:
        body = source.substitute(
            TITLE=yaml.safe_dump(title, default_style='"', allow_unicode=True).strip(),
            DATE=when.isoformat(),
            PROJECT=yaml.safe_dump(
                project, default_style='"', allow_unicode=True
            ).strip(),
        )
    except KeyError as unknown:
        # Raised before mkdir below, so a broken template leaves nothing behind.
        raise SystemExit(
            f"error: _templates/{template} asks for unknown placeholder {unknown}"
        ) from None

    target.mkdir(parents=True)
    qmd = target / "index.qmd"
    qmd.write_text(body)
    return qmd


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=sorted(KINDS))
    parser.add_argument("title")
    parser.add_argument("--slug", help="override the slug derived from the title")
    parser.add_argument(
        "--date", type=date.fromisoformat, help="ISO date (default: today)"
    )
    parser.add_argument("--project", help="project category for a package post")
    args = parser.parse_args()

    if args.project and args.kind != "package":
        parser.error("--project applies to package posts only")

    qmd = scaffold(args.kind, args.title, args.slug, args.date, args.project)
    print(qmd.relative_to(ROOT))


if __name__ == "__main__":
    main()
