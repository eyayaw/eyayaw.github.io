# My website

[eyayaw.github.io](https://eyayaw.github.io), built with [Quarto](https://quarto.org/).

```sh
uv run scripts/new.py post "<TITLE>" # kinds: post,package,til; --help for flags
uv run scripts/check_posts.py # frontmatter + categories
```

`new.py` drops a `draft: true` skeleton at `<section>/<slug>/index.qmd`, flip it for publish.

## Stuff I may forget

Don't rename a post directory once it's live. The slug is the URL *and* the
giscus comment key, so renaming orphans the thread. Same reason slugs are named
after the post rather than its subject.

New top-level directory only if it needs its own listing, `_metadata.yml`, or
render settings. `til/` does. "All my package posts" doesn't, that's a category
and a listing that filters on it:

```yaml
listing:
  contents: posts
  include:
    categories: "package"
```

`_categories.yml` is read only by `check_posts.py`, to catch a category typo before it becomes a real category.

`check_posts.py` ignores drafts. Errors set the exit code, warnings don't.

Published posts without a preview image get a warning. A specified image must exist.
