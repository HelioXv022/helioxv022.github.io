#!/usr/bin/env python3
"""Build the site into _site/.

    python build.py            # published pages and posts
    python build.py --drafts   # also posts marked `draft: true`
    python -m http.server -d _site 8000

Pages live in content/, posts in posts/ (Markdown with YAML front matter),
templates in templates/, static files in static/. If cv/cv.pdf exists (CI
builds it from cv/cv.tex) it is copied to /cv.pdf.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import re
import shutil
from pathlib import Path
from string import Template

import markdown
import yaml

ROOT = Path(__file__).parent
OUT = ROOT / "_site"
FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.S)


def read_markdown(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    match = FRONT_MATTER.match(text)
    if not match:
        return {}, text
    return yaml.safe_load(match.group(1)) or {}, match.group(2)


def to_html(source: str) -> str:
    return markdown.markdown(
        source,
        extensions=["extra", "sane_lists", "smarty", "pymdownx.arithmatex"],
        extension_configs={"pymdownx.arithmatex": {"generic": True}},
    )


def render(template: str, **fields: str) -> str:
    return Template((ROOT / "templates" / template).read_text(encoding="utf-8")).substitute(fields)


def page(config: dict, title: str, body: str, path: str, description: str = "",
         math: bool = False) -> str:
    nav = '<a href="/#projects">Projects</a>'
    if config.get("has_posts"):
        nav += '<a href="/#writing">Writing</a>'
    nav += '<a href="/cv.pdf">CV</a>'
    links = " · ".join(
        f'<a href="{html.escape(link["url"])}">{html.escape(link["label"])}</a>'
        for link in config["links"]
    )
    katex = (ROOT / "templates" / "katex.html").read_text(encoding="utf-8") if math else ""
    full_title = config["title"] if title == config["title"] else f"{title} · {config['title']}"
    return render(
        "base.html",
        title=html.escape(full_title),
        description=html.escape(description or config["description"]),
        canonical=config["url"].rstrip("/") + path,
        site_title=html.escape(config["title"]),
        body=body,
        links=links,
        nav=nav,
        katex=katex,
        year=str(dt.date.today().year),
    )


def write(path: str, content: str) -> None:
    target = OUT / path.lstrip("/")
    if path.endswith("/"):
        target = target / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def load_posts(include_drafts: bool) -> list[dict]:
    posts = []
    for path in sorted((ROOT / "posts").glob("*.md")):
        meta, source = read_markdown(path)
        if meta.get("draft") and not include_drafts:
            continue
        slug = path.stem
        posts.append({
            "slug": slug,
            "title": meta["title"],
            "date": meta["date"],
            "summary": meta.get("summary", ""),
            "draft": bool(meta.get("draft")),
            "html": to_html(source),
            "math": "$" in source or "\\(" in source,
        })
    return sorted(posts, key=lambda p: p["date"], reverse=True)


def post_list(posts: list[dict]) -> str:
    if not posts:
        return ""
    items = "\n".join(
        f'<li><a href="/posts/{p["slug"]}/">{html.escape(p["title"])}</a>'
        f'{" <em>(draft)</em>" if p["draft"] else ""}'
        f'<span class="date">{p["date"]:%b %Y}</span>'
        f'<p>{html.escape(p["summary"])}</p></li>'
        for p in posts
    )
    return f'<h2 id="writing">Writing</h2>\n<ul class="posts">\n{items}\n</ul>'


def atom_feed(config: dict, posts: list[dict]) -> str:
    base = config["url"].rstrip("/")
    updated = max((p["date"] for p in posts), default=dt.date.today())
    entries = "".join(
        f"""  <entry>
    <title>{html.escape(p["title"])}</title>
    <link href="{base}/posts/{p["slug"]}/"/>
    <id>{base}/posts/{p["slug"]}/</id>
    <updated>{p["date"]:%Y-%m-%d}T00:00:00Z</updated>
    <summary>{html.escape(p["summary"])}</summary>
  </entry>
"""
        for p in posts
    )
    return f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>{html.escape(config["title"])}</title>
  <link href="{base}/feed.xml" rel="self"/>
  <link href="{base}/"/>
  <id>{base}/</id>
  <updated>{updated:%Y-%m-%d}T00:00:00Z</updated>
  <author><name>{html.escape(config["title"])}</name></author>
{entries}</feed>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--drafts", action="store_true", help="include draft posts")
    args = parser.parse_args()

    config = yaml.safe_load((ROOT / "site.yml").read_text(encoding="utf-8"))
    config["links"] = [link for link in config.get("links") or [] if link.get("url")]
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "static", OUT)

    posts = load_posts(args.drafts)
    config["has_posts"] = bool(posts)
    for post in posts:
        body = render(
            "post.html",
            title=html.escape(post["title"]),
            date=f'{post["date"]:%-d %B %Y}',
            content=post["html"],
        )
        write(f'/posts/{post["slug"]}/',
              page(config, post["title"], body, f'/posts/{post["slug"]}/',
                   post["summary"], post["math"]))
        images = ROOT / "posts" / post["slug"]
        if images.is_dir():
            shutil.copytree(images, OUT / "posts" / post["slug"], dirs_exist_ok=True)

    for path in sorted((ROOT / "content").glob("*.md")):
        meta, source = read_markdown(path)
        source = source.replace("{{ posts }}", post_list(posts))
        url = "/" if path.stem == "index" else f"/{path.stem}/"
        write(url, page(config, meta.get("title", config["title"]), to_html(source), url,
                        meta.get("description", "")))

    cv = ROOT / "cv" / "cv.pdf"
    if cv.exists():
        shutil.copy(cv, OUT / "cv.pdf")
    write("/feed.xml", atom_feed(config, [p for p in posts if not p["draft"]]))
    write("/404.html", page(config, "Not found",
                            '<h1>Not found</h1><p><a href="/">Back to the home page</a></p>', "/404"))
    print(f"Built {OUT} ({len(posts)} post{'s' if len(posts) != 1 else ''}"
          f"{', cv.pdf included' if cv.exists() else ', no cv.pdf'})")


if __name__ == "__main__":
    main()
