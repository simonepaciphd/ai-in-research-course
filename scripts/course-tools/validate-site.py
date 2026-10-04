"""Validate rendered course pages, local links, deck counts, and publication boundaries."""
from __future__ import annotations
import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()
        self.sections = 0
    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if data.get("id"):
            self.ids.add(data["id"])
        if tag == "section":
            self.sections += 1
        if "notes" in data.get("class", "").split():
            raise ValueError("Presenter notes survived the public render")
        for key in ("href", "src"):
            if data.get(key):
                self.links.append(data[key])

def validate(output: Path, source: Path) -> dict:
    output = output.resolve()
    if not (output / "index.html").is_file():
        raise ValueError("Missing rendered homepage")
    if not (output / ".nojekyll").is_file():
        raise ValueError("Missing GitHub Pages .nojekyll marker")
    pages = {}
    errors = []
    for path in output.rglob("*.html"):
        body = path.read_text(encoding="utf-8")
        if re.search(r"C:[/\\]Users[/\\]|ai-os-private|native-bookkeeping|20261004-codex-v2", body, re.I):
            errors.append(f"Private coordination reference in {path.relative_to(output)}")
        page = Page()
        try:
            page.feed(body)
        except ValueError as error:
            errors.append(f"{path.relative_to(output)}: {error}")
        pages[path] = page
    local_links = 0
    for path, page in pages.items():
        for ref in page.links:
            parts = urlsplit(ref)
            if parts.scheme or parts.netloc or ref.startswith(("mailto:", "data:", "javascript:")):
                continue
            target = (output / unquote(parts.path).lstrip("/")) if parts.path.startswith("/") else (path.parent / unquote(parts.path))
            target = target.resolve() if parts.path else path
            if target.is_dir():
                target = target / "index.html"
            if not target.is_relative_to(output):
                errors.append(f"Link escapes public output: {path.name}: {ref}")
                continue
            local_links += 1
            if not target.exists():
                errors.append(f"Missing local link: {path.relative_to(output)}: {ref}")
            elif parts.fragment and target in pages and parts.fragment not in pages[target].ids:
                if not (target.parent.name == "slides" and parts.fragment.startswith("/")):
                    errors.append(f"Missing fragment: {path.relative_to(output)}: {ref}")
    decks = {}
    for qmd in sorted((source / "slides").glob("*.qmd")):
        expected = 1 + len(re.findall(r"^## ", qmd.read_text(encoding="utf-8"), re.M))
        html = output / "slides" / (qmd.stem + ".html")
        actual = pages[html].sections if html in pages else 0
        decks[qmd.stem] = {"slides": actual, "expected": expected}
        if actual != expected:
            errors.append(f"Slide count mismatch in {qmd.name}: {actual} != {expected}")
    if len(decks) != 7:
        errors.append(f"Expected seven authored decks, found {len(decks)}")
    for path in output.rglob("*"):
        if path.is_file() and (path.suffix.lower() in {".pptx", ".snap", ".py", ".ps1"} or "internal" in path.parts):
            errors.append(f"Private/build source copied to public output: {path.relative_to(output)}")
    result = {"status": "pass" if not errors else "fail", "html_pages": len(pages), "local_links_checked": local_links, "decks": decks, "errors": errors}
    if errors:
        raise ValueError(json.dumps(result, indent=2))
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = validate(args.output, args.source.resolve())
    text = json.dumps(report, indent=2)
    print(text)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text + "\n", encoding="utf-8")
