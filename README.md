# helioxv022.github.io

Source for my website, <https://helioxv022.github.io>.

Pages and posts are Markdown, turned into HTML by `build.py`. The CV is LaTeX. Pushing to `main` runs a GitHub Actions workflow that builds both and deploys to Pages.

## Files

```text
content/index.md     home page; {{ posts }} becomes the post list
posts/*.md           posts (YAML front matter); images go in posts/<slug>/
cv/cv.tex            CV
templates/           HTML templates
static/              CSS, favicon
site.yml             site title, URL, footer links
build.py             writes _site/, including feed.xml and 404.html
.github/workflows/pages.yml
```

## Building locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python build.py --drafts        # --drafts also builds draft posts
python -m http.server -d _site 8000
```

For the CV: `cd cv && latexmk -pdf cv.tex`. If `cv/cv.pdf` exists, `build.py` copies it to `_site/cv.pdf`.

## Posts

New post: `posts/YYYY-MM-slug.md`, starting with

```markdown
---
title: ...
date: 2026-10-01
summary: ...
draft: true
---
```

Math works with `$...$` and `$$...$$`. Drafts don't get published; delete the `draft` line when it's ready.

## Deploying

Set **Settings > Pages > Source** to **GitHub Actions**. The workflow stops if `cv/cv.tex` still has any `\TODO{...}` in it.
