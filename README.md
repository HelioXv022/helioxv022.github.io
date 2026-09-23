# helioxv022.github.io

Source of my personal site, [helioxv022.github.io](https://helioxv022.github.io): a short profile, projects, writing, and my CV.

The site is built by a small Python script (`build.py`, about 150 lines) from Markdown, and the CV is compiled from LaTeX. On every push to `main`, GitHub Actions builds both and deploys to GitHub Pages.

## Layout

```text
content/index.md       home page ({{ posts }} is replaced by the list of posts)
posts/*.md             articles, Markdown with YAML front matter; images in posts/<slug>/
cv/cv.tex              CV source (ATS-friendly: one column, plain text, standard headings)
templates/, static/    HTML templates, CSS, favicon
site.yml               title, URL and footer links
build.py               Markdown -> _site/, plus an Atom feed and 404 page
.github/workflows/pages.yml   builds the CV and the site, deploys to Pages
```

## Local preview

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python build.py --drafts          # --drafts includes posts marked draft: true
python -m http.server -d _site 8000
```

To build the CV locally: `cd cv && latexmk -pdf cv.tex`, then rerun `build.py` to copy it to `/cv.pdf`.

## Writing a post

Create `posts/YYYY-MM-short-title.md`:

```markdown
---
title: A clear, specific title
date: 2026-10-01
summary: One or two sentences for the post list and the feed.
draft: true
---

Text, with $inline$ and $$display$$ math.
```

Posts with `draft: true` are skipped by the published build. Remove that line to publish.

## Deployment

In the repository settings, **Pages > Build and deployment > Source** must be set to **GitHub Actions**. The workflow fails on purpose while `cv/cv.tex` still contains `\TODO{...}` markers, so an unfinished CV is never published.
