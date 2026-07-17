#!/usr/bin/env python3
"""Build an isolated ENG 1010 direct-renaming release candidate.

The source preview remains untouched. The generated site is written to
release-candidate/ so it can be reviewed and tested before canonical deployment.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SOURCE_1010 = ROOT / "1010"
OUTPUT = ROOT / "release-candidate"
OUTPUT_1010 = OUTPUT / "1010"

# Protected source file -> approved final chapter number.
SOURCE_TO_FINAL = {
    1: 1,
    2: 2,
    4: 3,
    7: 4,
    13: 5,
    14: 6,
    3: 7,
    9: 8,
    11: 9,
    10: 10,
    5: 11,
    6: 12,
    8: 13,
    12: 14,
}

FINAL_CHAPTERS = [
    (1, "Annotating Your Way to Greatness", "fas fa-highlighter", "15 min"),
    (2, "Active Reading Strategies", "fas fa-book-reader", "12 min"),
    (3, "Summarizing Your Way to Synthesis", "fas fa-clipboard-list", "10 min"),
    (4, "Quoting, Paraphrasing, and Signal Phrases", "fas fa-quote-left", "12 min"),
    (5, "Understanding Rhetoric: The Art of Persuasion", "fas fa-bullhorn", "18 min"),
    (6, "Values, Assumptions, and Ideology", "fas fa-layer-group", "14 min"),
    (7, "Strategies for Getting Started", "fas fa-pen-fancy", "9 min"),
    (8, "Crafting Powerful Thesis Statements", "fas fa-bullseye", "11 min"),
    (9, "Designing Effective Paragraphs", "fas fa-align-left", "13 min"),
    (10, "Analysis and Synthesis", "fas fa-project-diagram", "16 min"),
    (11, "Argumentation: Joining the Academic Conversation", "fas fa-comments", "18 min"),
    (12, "Finding and Evaluating Sources", "fas fa-search", "12 min"),
    (13, "Using Sources in Your Argument", "fas fa-link", "14 min"),
    (14, "Revision: From Draft to Final", "fas fa-pen-to-square", "12 min"),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def chapter_placeholder(final_number: int) -> str:
    return f"__SC_FINAL_CHAPTER_{final_number}__.html"


def rewrite_internal_chapter_links(html: str) -> str:
    """Rewrite numbered chapter destinations without cascade errors.

    Anchor text such as "Chapter 9" is normalized when its destination is a
    numbered Scholar's Compass chapter. Raw internal URLs are then rewritten in
    one placeholder pass.
    """

    anchor_pattern = re.compile(r"<a\b(?P<attrs>[^>]*?)>(?P<body>.*?)</a>", re.IGNORECASE | re.DOTALL)

    def rewrite_anchor(match: re.Match[str]) -> str:
        attrs = match.group("attrs")
        body = match.group("body")
        destination = re.search(r"chapter-(\d+)\.html", attrs, re.IGNORECASE)
        if destination:
            source_number = int(destination.group(1))
            final_number = SOURCE_TO_FINAL.get(source_number)
            if final_number:
                attrs = re.sub(
                    rf"chapter-{source_number}\.html",
                    chapter_placeholder(final_number),
                    attrs,
                    flags=re.IGNORECASE,
                )
                body = re.sub(
                    rf"\bChapter\s+{source_number}\b",
                    f"Chapter {final_number}",
                    body,
                    flags=re.IGNORECASE,
                )
        return f"<a{attrs}>{body}</a>"

    html = anchor_pattern.sub(rewrite_anchor, html)

    def rewrite_remaining(match: re.Match[str]) -> str:
        source_number = int(match.group(1))
        final_number = SOURCE_TO_FINAL.get(source_number)
        return chapter_placeholder(final_number) if final_number else match.group(0)

    html = re.sub(r"chapter-(\d+)\.html", rewrite_remaining, html, flags=re.IGNORECASE)
    html = re.sub(
        r"__SC_FINAL_CHAPTER_(\d+)__\.html",
        lambda match: f"chapter-{match.group(1)}.html",
        html,
    )
    return html


def replace_first_tag_text_number(html: str, tag: str, final_number: int) -> str:
    pattern = re.compile(rf"(<{tag}\b[^>]*>)(.*?)(</{tag}>)", re.IGNORECASE | re.DOTALL)

    def update(match: re.Match[str]) -> str:
        middle = re.sub(
            r"\bChapter\s+\d+\b",
            f"Chapter {final_number}",
            match.group(2),
            count=1,
            flags=re.IGNORECASE,
        )
        return match.group(1) + middle + match.group(3)

    return pattern.sub(update, html, count=1)


def transform_chapter(source_number: int, final_number: int, html: str) -> str:
    html = rewrite_internal_chapter_links(html)
    html = re.sub(
        r'data-page=["\']chapter-\d+["\']',
        f'data-page="chapter-{final_number}"',
        html,
        count=1,
        flags=re.IGNORECASE,
    )

    # Ensure the shared course palette and course detection remain explicit.
    if re.search(r"<body\b", html, re.IGNORECASE):
        if re.search(r"<body\b[^>]*\bdata-course=", html, re.IGNORECASE):
            html = re.sub(
                r'(<body\b[^>]*\bdata-course=)["\'][^"\']*["\']',
                r'\1"1010"',
                html,
                count=1,
                flags=re.IGNORECASE,
            )
        else:
            html = re.sub(r"<body\b", '<body data-course="1010"', html, count=1, flags=re.IGNORECASE)

    html = replace_first_tag_text_number(html, "title", final_number)
    html = replace_first_tag_text_number(html, "h1", final_number)

    # Deployment cache versions. Paths stay relative to the isolated package.
    html = re.sub(r"\.\./styles\.css\?v=[^\"']+", "../styles.css?v=18-rc1", html)
    html = re.sub(r"\.\./app\.js\?v=[^\"']+", "../app.js?v=21-rc1", html)
    html = re.sub(r"chapter-12\.css\?v=[^\"']+", "chapter-12.css?v=2-rc1", html)
    html = re.sub(r"chapter-12-tools\.js\?v=[^\"']+", "chapter-12-tools.js?v=2-rc1", html)

    # Active Reading retained all prose but had a visible Roman-numeral gap.
    if final_number == 2:
        html = html.replace(
            "V. Adapting Strategies for Digital vs. Print Reading",
            "IV. Adapting Strategies for Digital vs. Print Reading",
        )
        html = html.replace(
            "VI. Practice Exercises &amp; Application",
            "V. Practice Exercises &amp; Application",
        )
        html = html.replace(
            "VI. Practice Exercises & Application",
            "V. Practice Exercises & Application",
        )

    return html


def build_index() -> str:
    source = (SOURCE_1010 / "index.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(source, "html.parser")
    body = soup.body
    if body is None:
        raise RuntimeError("ENG 1010 index has no body element")
    body["data-course"] = "1010"

    cards: dict[int, object] = {}
    for link in soup.select("a.chapter-link[href]"):
        match = re.search(r"chapter-(\d+)\.html", str(link.get("href", "")))
        if not match:
            continue
        source_number = int(match.group(1))
        final_number = SOURCE_TO_FINAL[source_number]
        link["href"] = f"chapter-{final_number}.html"
        link["data-chapter"] = str(final_number)
        number = link.select_one(".card-number")
        if number:
            number.string = str(final_number)
        column = link.find_parent("div", class_="col")
        if column is not None:
            cards[final_number] = column

    if set(cards) != set(range(1, 15)):
        missing = sorted(set(range(1, 15)) - set(cards))
        raise RuntimeError(f"Could not identify all homepage cards; missing {missing}")

    first_link = soup.select_one("a.chapter-link[href]")
    row = first_link.find_parent("div", class_="row") if first_link else None
    if row is None:
        raise RuntimeError("Could not locate homepage chapter-card row")
    for final_number in range(1, 15):
        row.append(cards[final_number])

    for stylesheet in soup.select('link[href*="../styles.css"]'):
        stylesheet["href"] = "../styles.css?v=18-rc1"
    for script in soup.select('script[src*="../app.js"]'):
        script["src"] = "../app.js?v=21-rc1"

    return soup.decode(formatter="minimal")


def build_app_js() -> str:
    app = (ROOT / "app.js").read_text(encoding="utf-8")
    rows = []
    for number, title, icon, reading_time in FINAL_CHAPTERS:
        rows.append(
            "    { href: 'chapter-{0}.html', icon: '{1}', title: '{0}. {2}', readingTime: '{3}' }".format(
                number, icon, title.replace("'", "\\'"), reading_time
            )
        )
    array = "  // Approved ENG 1010 final deployment sequence and filenames.\n  var CHAPTERS_1010 = [\n" + ",\n".join(rows) + "\n  ];"
    app, count = re.subn(
        r"  // Approved ENG 1010 student-facing sequence\..*?\n  var CHAPTERS_1010 = \[.*?\n  \];",
        array,
        app,
        count=1,
        flags=re.DOTALL,
    )
    if count != 1:
        raise RuntimeError("Could not replace CHAPTERS_1010 array")

    app = app.replace("stabilization-0.2.css?v=6", "stabilization-0.2.css?v=7")
    app = app.replace('data-sc-stabilization="0.6"', 'data-sc-stabilization="0.7"')
    app = app.replace("interactive-tools.js?v=1", "interactive-tools.js?v=2")
    return app


def copy_shared_assets() -> None:
    for filename in [
        "styles.css",
        "interactive-tools.js",
        "stabilization-0.2.css",
        "favicon.svg",
    ]:
        source = ROOT / filename
        if source.exists():
            shutil.copy2(source, OUTPUT / filename)

    (OUTPUT / "app.js").write_text(build_app_js(), encoding="utf-8")

    for directory in ["assets", "images", "media"]:
        source = ROOT / directory
        if source.exists() and source.is_dir():
            shutil.copytree(source, OUTPUT / directory)


def write_release_hub() -> None:
    hub = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>ENG 1010 Release Candidate - Scholar's Compass</title>
  <link rel="icon" type="image/svg+xml" href="favicon.svg" />
  <link rel="stylesheet" href="styles.css?v=18-rc1" />
</head>
<body data-course="1010" data-page="release-candidate">
  <main class="container" id="main-content" style="margin-top: 2rem;">
    <header class="header">
      <h1>ENG 1010 Direct-Renaming Release Candidate</h1>
      <p class="subtitle">An isolated deployment package for final review</p>
    </header>
    <section class="section active">
      <div class="section-content" style="display:block;">
        <p>This package uses the approved fourteen-chapter sequence and final numbered filenames. It does not replace the current preview or the canonical Scholar's Compass site.</p>
        <p><a class="btn" href="1010/index.html">Open the ENG 1010 release candidate</a></p>
        <p><a href="../1010/index.html">Return to the currently approved preview</a></p>
      </div>
    </section>
  </main>
</body>
</html>
"""
    (OUTPUT / "index.html").write_text(hub, encoding="utf-8")


def verify_internal_destinations() -> list[str]:
    problems: list[str] = []
    existing = {path.name for path in OUTPUT_1010.glob("chapter-*.html")}
    for page in [OUTPUT_1010 / "index.html", *sorted(OUTPUT_1010.glob("chapter-*.html"))]:
        text = page.read_text(encoding="utf-8")
        for match in re.finditer(r"chapter-(\d+)\.html", text, re.IGNORECASE):
            target = f"chapter-{int(match.group(1))}.html"
            if target not in existing:
                problems.append(f"{page.relative_to(OUTPUT)} -> missing {target}")
    return problems


def main() -> None:
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT_1010.mkdir(parents=True)

    source_hashes: dict[str, str] = {}
    output_hashes: dict[str, str] = {}

    # Read every protected source before writing any final destination.
    source_text: dict[int, str] = {}
    for source_number in range(1, 15):
        path = SOURCE_1010 / f"chapter-{source_number}.html"
        if not path.exists():
            raise FileNotFoundError(path)
        source_text[source_number] = path.read_text(encoding="utf-8")
        source_hashes[str(path.relative_to(ROOT))] = sha256(path)

    for source_number, final_number in SOURCE_TO_FINAL.items():
        destination = OUTPUT_1010 / f"chapter-{final_number}.html"
        transformed = transform_chapter(source_number, final_number, source_text[source_number])
        destination.write_text(transformed, encoding="utf-8")

    (OUTPUT_1010 / "index.html").write_text(build_index(), encoding="utf-8")

    # Chapter 12's approved scoped assets keep their semantic names.
    for filename in ["chapter-12.css", "chapter-12-tools.js"]:
        source = SOURCE_1010 / filename
        if source.exists():
            shutil.copy2(source, OUTPUT_1010 / filename)

    copy_shared_assets()
    write_release_hub()

    problems = verify_internal_destinations()
    if problems:
        raise RuntimeError("Internal destination verification failed:\n" + "\n".join(problems))

    for path in sorted(OUTPUT.rglob("*")):
        if path.is_file():
            output_hashes[str(path.relative_to(ROOT))] = sha256(path)

    manifest = {
        "built_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_repository_area": "1010/",
        "output_area": "release-candidate/",
        "source_to_final": {str(key): value for key, value in SOURCE_TO_FINAL.items()},
        "approved_sequence": [title for _, title, _, _ in FINAL_CHAPTERS],
        "storage_policy": "Legacy content-tied localStorage keys are intentionally retained so existing saved work is not discarded during renaming.",
        "source_sha256": source_hashes,
        "output_sha256": output_hashes,
        "internal_destination_problems": problems,
    }
    (OUTPUT / "BUILD-MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    readme = """# ENG 1010 Direct-Renaming Release Candidate

This directory is generated from the approved Scholar's Compass preview. It is isolated from the existing `1010/` preview and from the canonical repository.

Review entry point: `release-candidate/1010/index.html`

The package includes:

- the approved static homepage order;
- direct final filenames `chapter-1.html` through `chapter-14.html`;
- rewritten internal chapter destinations and linked chapter-number labels;
- final `data-page` identities;
- the Active Reading Roman-numeral correction;
- the approved full Chapter 12;
- shared accessibility, mobile, dark-mode, print, and interactive behavior;
- preserved legacy local-storage keys so saved tool work remains associated with its original content.

`BUILD-MANIFEST.json` records source and output hashes. `TEST-RESULTS.md` is produced by the release-candidate test suite.
"""
    (OUTPUT / "README.md").write_text(readme, encoding="utf-8")

    print(f"Built {len(list(OUTPUT_1010.glob('chapter-*.html')))} final chapter pages in {OUTPUT}")


if __name__ == "__main__":
    main()
