# /// script
# requires-python = ">=3.13"
# ///
import argparse
import re
from datetime import date
from pathlib import Path

POSTS_DIR = Path("posts/")


def slugify(title):
    slug = title.lower().strip()

    # Replace special characters with hyphens
    slug = re.sub(r"[^\w-]", "-", slug)

    # Condense hyphens
    slug = re.sub(r"-+", "-", slug)

    # Remove leading/trailing hyphens
    slug = slug.strip("-")

    return slug


def create_blogpost_boilerplate(title):
    slug = slugify(title)
    blog_dir = POSTS_DIR / slug
    if blog_dir.exists():
        raise ValueError(f"Blog dir taken for {title=}")
    blog_dir.mkdir()
    # The dir name (slug) is the post's URL and giscus comment key --
    # treat it as frozen once published, even if the title changes.
    header = f"""\
---
title: {title}
date: {date.today().isoformat()}
categories: [code, tutorial, programming]
engine: knitr # [jupyter]
code-fold: true
execute:
    echo: false
    warning: false
    message: false
---
"""

    qmd_file = blog_dir / "index.qmd"
    qmd_file.write_text(header)
    return qmd_file


def main():
    parser = argparse.ArgumentParser(description="Create a new blog post boilerplate")
    parser.add_argument("title", type=str, help="The title of the blog post")
    args = parser.parse_args()
    qmd_file = create_blogpost_boilerplate(args.title)
    print(f"Created {qmd_file}")


if __name__ == "__main__":
    main()
