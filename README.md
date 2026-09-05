# My website

[eyayaw.github.io](https://eyayaw.github.io), built with [Quarto](https://quarto.org/).

```sh
uv run scripts/new.py post "<TITLE>" # kinds: post,package,til; --help for flags
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
