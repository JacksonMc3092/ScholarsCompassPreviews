#!/usr/bin/env python3
"""Build the isolated Scholar's Compass ENG 1010 revision-round-2 package.

The existing release-candidate/ package remains untouched. This builder uses it as
an approved shell/content rollback point, incorporates the approved Markdown
revision drafts, and writes a new package to release-candidate-v2/.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import markdown
from bs4 import BeautifulSoup, NavigableString, Tag

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "release-candidate"
SOURCE_1010 = SOURCE / "1010"
OUTPUT = ROOT / "release-candidate-v2"
OUTPUT_1010 = OUTPUT / "1010"

DRAFTS: dict[str | int, str] = {
    "intro": "ENG1010-INTRODUCTION-WRITING-AS-CONVERSATION-DRAFT.md",
    1: "ENG1010-CHAPTER-1-ACTIVE-READING-REVISION-DRAFT.md",
    2: "ENG1010-CHAPTER-2-ANNOTATION-REVISION-DRAFT.md",
    3: "ENG1010-CHAPTER-3-SUMMARIZING-REVISION-DRAFT.md",
    4: "ENG1010-CHAPTER-4-QUOTING-PARAPHRASING-REVISION-DRAFT.md",
    5: "ENG1010-CHAPTER-5-RHETORIC-REVISION-DRAFT.md",
    10: "ENG1010-CHAPTER-10-ANALYSIS-REVISION-DRAFT.md",
    13: "ENG1010-CHAPTER-13-SYNTHESIS-REVISION-DRAFT.md",
}

CHAPTERS = [
    (1, "Active Reading Strategies", "fas fa-book-reader", "15 min", "Read with purpose, questions, and a plan for understanding."),
    (2, "Annotating Your Way to Greatness", "fas fa-highlighter", "15 min", "Turn reading into visible thinking through focused notes and marks."),
    (3, "Summarizing Your Way to Synthesis", "fas fa-clipboard-list", "14 min", "Represent a source accurately before responding or connecting it."),
    (4, "Quoting, Paraphrasing, and Signal Phrases", "fas fa-quote-left", "18 min", "Choose, integrate, and cite source material in MLA style."),
    (5, "Understanding Rhetoric: The Art of Persuasion", "fas fa-bullhorn", "20 min", "Examine how strategic choices work for audiences in context."),
    (6, "Values, Assumptions, and Ideology", "fas fa-layer-group", "14 min", "Read the worldview behind arguments, images, and everyday choices."),
    (7, "Strategies for Getting Started", "fas fa-pen-fancy", "9 min", "Generate ideas and create a workable path into a draft."),
    (8, "Crafting Powerful Thesis Statements", "fas fa-bullseye", "11 min", "Build a focused, arguable claim that guides the essay."),
    (9, "Designing Effective Paragraphs", "fas fa-align-left", "13 min", "Shape paragraphs around clear purposes and visible reasoning."),
    (10, "Analysis", "fas fa-magnifying-glass-chart", "22 min", "Move from observation to interpretation and significance."),
    (11, "Argumentation: Joining the Academic Conversation", "fas fa-comments", "18 min", "Develop claims, reasons, evidence, and responsible responses."),
    (12, "Finding and Evaluating Sources", "fas fa-search", "22 min", "Search strategically and judge sources for credibility and usefulness."),
    (13, "Synthesis: Putting Sources into Conversation", "fas fa-diagram-project", "24 min", "Connect sources to develop a larger understanding or claim."),
    (14, "Revision: From Draft to Final", "fas fa-pen-to-square", "12 min", "Revise globally before polishing the sentence-level details."),
]

TITLES = {number: title for number, title, _, _, _ in CHAPTERS}
TEMPLATE_SOURCE = {1: 2, 2: 1, 3: 3, 4: 4, 5: 5, 10: 10, 13: 13}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clean_draft(text: str) -> str:
    """Remove implementation-only notes while preserving substantive chapter text."""
    text = re.split(r"^## Revision and Implementation Notes\s*$", text, maxsplit=1, flags=re.MULTILINE)[0]
    text = re.sub(
        r'(?m)^(\*\*Video link:\*\*\s*)(https://(?:www\.)?youtube\.com/watch\?v=[A-Za-z0-9_-]+)\s*$',
        r'\1<\2>',
        text,
    )
    text = re.sub(
        r'(?m)^(https://(?:www\.)?youtube\.com/watch\?v=[A-Za-z0-9_-]+)\s*$',
        r'<\1>',
        text,
    )
    return text.rstrip() + "\n"


def markdown_fragment(text: str) -> BeautifulSoup:
    html = markdown.markdown(
        clean_draft(text),
        extensions=["tables", "fenced_code", "sane_lists"],
        output_format="html5",
    )
    return BeautifulSoup(html, "html.parser")


def strip_numbering(text: str) -> str:
    return re.sub(r"^(?:[IVXLCDM]+\.|\d+\.)\s*", "", text.strip(), flags=re.IGNORECASE)


def slug(text: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return value or "section"


def icon_for_heading(text: str) -> str:
    lower = text.lower()
    choices = [
        ("works cited", "fas fa-scroll"),
        ("works consulted", "fas fa-scroll"),
        ("practice", "fas fa-pencil-alt"),
        ("checkpoint", "fas fa-check-circle"),
        ("source", "fas fa-book"),
        ("evidence", "fas fa-file-lines"),
        ("analysis", "fas fa-magnifying-glass-chart"),
        ("synthesis", "fas fa-diagram-project"),
        ("rhetor", "fas fa-bullhorn"),
        ("quote", "fas fa-quote-left"),
        ("paraphras", "fas fa-rotate"),
        ("summary", "fas fa-clipboard-list"),
        ("reading", "fas fa-book-reader"),
        ("annotat", "fas fa-highlighter"),
        ("process", "fas fa-list-check"),
        ("problem", "fas fa-triangle-exclamation"),
        ("revision", "fas fa-pen-to-square"),
    ]
    for needle, icon in choices:
        if needle in lower:
            return icon
    return "fas fa-compass"


def make_tag(soup: BeautifulSoup, name: str, text: str | None = None, **attrs: str) -> Tag:
    tag = soup.new_tag(name)
    for key, value in attrs.items():
        if key == "class_":
            attr_name = "class"
        elif key == "for_":
            attr_name = "for"
        else:
            attr_name = key.replace("_", "-")
        tag.attrs[attr_name] = value
    if text is not None:
        tag.string = text
    return tag


def split_draft(draft_path: Path) -> tuple[str, str, list[tuple[str, list[Tag | NavigableString]]]]:
    fragment = markdown_fragment(draft_path.read_text(encoding="utf-8"))
    h1 = fragment.find("h1")
    if h1 is None:
        raise RuntimeError(f"Draft has no H1: {draft_path}")
    title = h1.get_text(" ", strip=True)
    h1.extract()

    subtitle_tag = fragment.find("h2")
    subtitle = subtitle_tag.get_text(" ", strip=True) if subtitle_tag else ""
    if subtitle_tag:
        subtitle_tag.extract()

    groups: list[tuple[str, list[Tag | NavigableString]]] = []
    current_title = "Introduction"
    current_nodes: list[Tag | NavigableString] = []
    for child in list(fragment.contents):
        if isinstance(child, NavigableString) and not child.strip():
            continue
        if isinstance(child, Tag) and child.name == "h2":
            if current_nodes:
                groups.append((current_title, current_nodes))
            current_title = child.get_text(" ", strip=True)
            current_nodes = []
            child.extract()
            continue
        if isinstance(child, Tag) and child.name == "hr":
            continue
        current_nodes.append(child.extract() if isinstance(child, Tag) else child)
    if current_nodes:
        groups.append((current_title, current_nodes))

    return title, subtitle, groups


def make_section(soup: BeautifulSoup, section_id: str, heading: str, nodes: list[Tag | NavigableString], active: bool) -> Tag:
    section = make_tag(soup, "section", id=section_id, class_="section" + (" active" if active else ""))
    button = make_tag(soup, "button", type="button", class_="section-header")
    label = make_tag(soup, "span")
    icon = make_tag(soup, "i", class_=icon_for_heading(heading))
    icon.attrs["aria-hidden"] = "true"
    label.append(icon)
    label.append(NavigableString(" " + heading))
    button.append(label)
    marker = make_tag(soup, "span", class_="section-icon")
    chevron = make_tag(soup, "i", class_="fas fa-chevron-right")
    chevron.attrs["aria-hidden"] = "true"
    marker.append(chevron)
    button.append(marker)
    content = make_tag(soup, "div", class_="section-content")
    for node in nodes:
        content.append(node)
    section.append(button)
    section.append(content)
    return section


def wrap_tables(soup: BeautifulSoup) -> None:
    for table in soup.find_all("table"):
        if table.find_parent(class_="table-responsive"):
            continue
        wrapper = make_tag(soup, "div", class_="table-responsive")
        table.replace_with(wrapper)
        wrapper.append(table)
        table.attrs["class"] = list(dict.fromkeys([*(table.get("class") or []), "table", "table-striped"]))


def youtube_id(url: str) -> str | None:
    try:
        parsed = urlparse(url)
    except ValueError:
        return None
    host = parsed.netloc.lower().replace("www.", "")
    if host == "youtu.be":
        return parsed.path.strip("/").split("/")[0] or None
    if host in {"youtube.com", "m.youtube.com", "youtube-nocookie.com"}:
        if parsed.path == "/watch":
            return parse_qs(parsed.query).get("v", [None])[0]
        match = re.search(r"/(?:embed|shorts)/([A-Za-z0-9_-]{6,})", parsed.path)
        if match:
            return match.group(1)
    return None


def embed_youtube_links(soup: BeautifulSoup) -> list[str]:
    embedded: list[str] = []
    for anchor in list(soup.find_all("a", href=True)):
        video_id = youtube_id(str(anchor.get("href")))
        if not video_id or anchor.find_parent(class_="sc-video-embed"):
            continue
        title = anchor.get_text(" ", strip=True) or "YouTube video"
        wrapper = make_tag(soup, "div", class_="sc-video-embed")
        iframe = make_tag(
            soup,
            "iframe",
            title=title,
            src=f"https://www.youtube-nocookie.com/embed/{video_id}?rel=0&cc_load_policy=1",
            loading="lazy",
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share",
            referrerpolicy="strict-origin-when-cross-origin",
        )
        iframe.attrs["allowfullscreen"] = ""
        wrapper.append(iframe)
        fallback = make_tag(soup, "p", class_="sc-video-fallback")
        link = make_tag(soup, "a", title + " (open on YouTube)", href=str(anchor.get("href")), target="_blank", rel="noopener")
        fallback.append(link)
        wrapper.append(fallback)
        parent = anchor.parent
        if isinstance(parent, Tag) and parent.name == "p" and len([x for x in parent.contents if not (isinstance(x, NavigableString) and not x.strip())]) == 1:
            parent.replace_with(wrapper)
        else:
            anchor.replace_with(wrapper)
        embedded.append(video_id)
    return embedded


def rewrite_cross_references(soup: BeautifulSoup) -> None:
    for anchor in soup.find_all("a", href=True):
        href = str(anchor.get("href"))
        file_part = href.split("#", 1)[0]
        suffix = "#" + href.split("#", 1)[1] if "#" in href else ""
        if file_part.endswith("chapter-1.html"):
            anchor["href"] = file_part[:-len("chapter-1.html")] + "chapter-2.html" + suffix
            text = anchor.get_text(" ", strip=True)
            if "Chapter 1" in text or "Annotat" in text:
                for node in anchor.find_all(string=True):
                    node.replace_with(str(node).replace("Chapter 1", "Chapter 2"))
        elif file_part.endswith("chapter-2.html"):
            anchor["href"] = file_part[:-len("chapter-2.html")] + "chapter-1.html" + suffix
            text = anchor.get_text(" ", strip=True)
            if "Chapter 2" in text or "Active Reading" in text:
                for node in anchor.find_all(string=True):
                    node.replace_with(str(node).replace("Chapter 2", "Chapter 1"))

    replacements = {
        "Chapter 1: Annotating Your Way to Greatness": "Chapter 2: Annotating Your Way to Greatness",
        "Chapter 2: Active Reading Strategies": "Chapter 1: Active Reading Strategies",
        "Chapter 10: Analysis and Synthesis": "Chapter 10: Analysis",
        "Chapter 13: Using Sources in Your Argument": "Chapter 13: Synthesis: Putting Sources into Conversation",
    }
    for node in list(soup.find_all(string=True)):
        if node.parent and node.parent.name in {"script", "style"}:
            continue
        value = str(node)
        updated = value
        for old, new in replacements.items():
            updated = updated.replace(old, new)
        if updated != value:
            node.replace_with(updated)


def add_css_and_js(soup: BeautifulSoup) -> None:
    head = soup.head
    if head is None:
        raise RuntimeError("Page has no head")
    for old in soup.select('link[data-sc-revision-round="2"]'):
        old.decompose()
    css = make_tag(soup, "link", rel="stylesheet", href="../revision-round-2.css?v=1")
    css.attrs["data-sc-revision-round"] = "2"
    head.append(css)

    for script in soup.select('script[data-sc-revision-round="2"]'):
        script.decompose()
    body = soup.body
    if body is None:
        raise RuntimeError("Page has no body")
    script = make_tag(soup, "script", src="../revision-round-2.js?v=1")
    script.attrs["data-sc-revision-round"] = "2"
    body.append(script)

    for app in soup.select('script[src*="../app.js"]'):
        app["src"] = "../app.js?v=22-rc2"
    for styles in soup.select('link[href*="../styles.css"]'):
        styles["href"] = "../styles.css?v=19-rc2"


def standardize_progress_and_sticky(soup: BeautifulSoup, identity: str) -> None:
    body = soup.body
    if body is None:
        raise RuntimeError("Page has no body")
    for node in soup.select(".progress-container, .progress-container-top, .sc-reading-progress, .sc-sticky-chapter"):
        node.decompose()
    progress = make_tag(soup, "div", class_="sc-reading-progress")
    progress.attrs.update({"role": "progressbar", "aria-label": "Reading progress", "aria-valuemin": "0", "aria-valuemax": "100", "aria-valuenow": "0"})
    bar = make_tag(soup, "div", id="scrollProgress", class_="sc-reading-progress-bar")
    progress.append(bar)
    body.insert(0, progress)

    sticky = make_tag(soup, "div", identity, class_="sc-sticky-chapter")
    sticky.attrs["aria-hidden"] = "true"
    navbar = soup.select_one(".navbar")
    if navbar:
        navbar.insert_after(sticky)
    else:
        progress.insert_after(sticky)


def sequence_nav(soup: BeautifulSoup, key: str | int) -> Tag:
    order: list[str | int] = ["intro", *range(1, 15)]
    index = order.index(key)
    previous = order[index - 1] if index > 0 else None
    following = order[index + 1] if index + 1 < len(order) else None

    nav = make_tag(soup, "nav", class_="chapter-sequence-nav")
    nav.attrs["aria-label"] = "Chapter sequence"

    def destination(item: str | int | None, direction: str) -> Tag:
        if item is None:
            href = "index.html"
            label = "ENG 1010 Home"
        elif item == "intro":
            href = "introduction.html"
            label = "Introduction: Writing as Conversation"
        else:
            href = f"chapter-{item}.html"
            label = f"Chapter {item}: {TITLES[int(item)]}"
        link = make_tag(soup, "a", href=href, class_=f"chapter-sequence-{direction}")
        small = make_tag(soup, "span", "Previous" if direction == "previous" else "Next", class_="chapter-sequence-label")
        strong = make_tag(soup, "strong", label)
        link.append(small)
        link.append(strong)
        return link

    nav.append(destination(previous, "previous"))
    nav.append(destination(following, "next"))
    return nav


def choose_quick_sections(sections: list[Tag]) -> list[Tag]:
    if len(sections) <= 8:
        return sections
    chosen = sections[:5]
    for needle in ["practice", "checkpoint", "works"]:
        match = next((s for s in sections if needle in s.get_text(" ", strip=True).lower()), None)
        if match and match not in chosen:
            chosen.append(match)
    return chosen[:8]


def build_quick_nav(soup: BeautifulSoup, sections: list[Tag]) -> Tag:
    quick = make_tag(soup, "nav", id="quickNav", class_="quick-nav")
    quick.attrs["aria-label"] = "On this page"
    for section in choose_quick_sections(sections):
        header = section.select_one(".section-header span")
        heading = header.get_text(" ", strip=True) if header else "Section"
        clean = strip_numbering(heading)
        label = clean if len(clean) <= 22 else clean[:20].rstrip() + "…"
        link = make_tag(soup, "a", href=f"#{section.get('id')}", title=clean)
        link.attrs["data-section"] = section.get("id")
        label_span = make_tag(soup, "span", label)
        icon = make_tag(soup, "i", class_=icon_for_heading(clean))
        icon.attrs["aria-hidden"] = "true"
        link.append(label_span)
        link.append(icon)
        quick.append(link)
    return quick


def insert_learning_tool(soup: BeautifulSoup, chapter: int, sections: list[Tag]) -> None:
    target = next((section.select_one(".section-content") for section in reversed(sections) if "works" not in section.get_text(" ", strip=True).lower()), None)
    if target is None:
        return

    tool = make_tag(soup, "div", class_="interactive-element sc-revision-tool")

    if chapter == 1:
        tool.attrs["data-progress-tracker"] = "chapter-1-sq3r"
        tool.append(BeautifulSoup("""
<h3><i class="fas fa-list-check" aria-hidden="true"></i> SQ3R Practice Tracker</h3>
<p>Use the checklist with a current reading. Your progress is saved in this browser.</p>
<label><input class="progress-checkbox" type="checkbox"> I surveyed the title, headings, visuals, and opening material.</label>
<label><input class="progress-checkbox" type="checkbox"> I turned headings or goals into questions.</label>
<label><input class="progress-checkbox" type="checkbox"> I read to answer those questions.</label>
<label><input class="progress-checkbox" type="checkbox"> I recited or paraphrased without looking.</label>
<label><input class="progress-checkbox" type="checkbox"> I reviewed my questions and difficult sections.</label>
<div class="progress sc-tool-progress"><div id="progressIndicator" class="progress-bar" role="progressbar"></div></div>
<p><strong>Progress:</strong> <span id="progressPercent">0%</span></p>
""", "html.parser"))
    elif chapter == 2:
        tool.append(BeautifulSoup("""
<h3><i class="fas fa-highlighter" aria-hidden="true"></i> Annotation Purpose Check</h3>
<p>Select each annotation move to see how several purposes can work together. These are examples, not a required personal color key.</p>
<div class="annotation-grid">
<button type="button" class="annotation-item" aria-pressed="false"><span class="annotation-color" aria-hidden="true"></span>Mark a central claim</button>
<button type="button" class="annotation-item" aria-pressed="false"><span class="annotation-color" aria-hidden="true"></span>Ask a genuine question</button>
<button type="button" class="annotation-item" aria-pressed="false"><span class="annotation-color" aria-hidden="true"></span>Connect ideas across the text</button>
<button type="button" class="annotation-item" aria-pressed="false"><span class="annotation-color" aria-hidden="true"></span>Note evidence you may use later</button>
</div>
""", "html.parser"))
    elif chapter == 3:
        tool.attrs["data-progress-tracker"] = "chapter-3-summary-audit"
        tool.append(BeautifulSoup("""
<h3><i class="fas fa-clipboard-check" aria-hidden="true"></i> Summary Audit</h3>
<p>Check a summary before using it in an essay.</p>
<label><input class="progress-checkbox" type="checkbox"> I identify the source and its central idea.</label>
<label><input class="progress-checkbox" type="checkbox"> I represent the source accurately and proportionally.</label>
<label><input class="progress-checkbox" type="checkbox"> I use my own sentence structure and wording.</label>
<label><input class="progress-checkbox" type="checkbox"> I distinguish the source’s ideas from my response.</label>
<label><input class="progress-checkbox" type="checkbox"> I use MLA attribution and citation when required.</label>
<div class="progress sc-tool-progress"><div id="progressIndicator" class="progress-bar" role="progressbar"></div></div>
<p><strong>Progress:</strong> <span id="progressPercent">0%</span></p>
""", "html.parser"))
    elif chapter == 4:
        tool.append(BeautifulSoup("""
<h3><i class="fas fa-quote-left" aria-hidden="true"></i> Prepare, Present, Explain Builder</h3>
<p>Use the scaffold to plan evidence integration. Revise the result so it fits your paragraph rather than treating it as a fixed formula.</p>
<label for="scQuotePoint">Paragraph point</label><textarea id="scQuotePoint"></textarea>
<label for="scQuoteContext">Source context and signal phrase</label><textarea id="scQuoteContext"></textarea>
<label for="scQuoteEvidence">Quotation or paraphrase with MLA citation</label><textarea id="scQuoteEvidence"></textarea>
<label for="scQuoteExplanation">Explanation and connection</label><textarea id="scQuoteExplanation"></textarea>
<div class="sc-tool-actions"><button type="button" class="btn" id="scBuildQuote">Preview</button><button type="button" class="btn btn-secondary" id="scSaveQuote">Save</button><button type="button" class="btn btn-secondary" id="scClearQuote">Clear</button></div>
<div id="scQuoteOutput" class="sc-tool-output" role="status" aria-live="polite"></div>
""", "html.parser"))
    elif chapter == 5:
        tool.append(BeautifulSoup("""
<h3><i class="fas fa-bullhorn" aria-hidden="true"></i> Rhetorical Choice Planner</h3>
<p>Move beyond naming an appeal by tracing one choice through its likely effect.</p>
<label for="scRhetChoice">Choice: What did the creator do?</label><textarea id="scRhetChoice"></textarea>
<label for="scRhetEffect">Effect: What does the choice emphasize, suggest, or invite?</label><textarea id="scRhetEffect"></textarea>
<label for="scRhetAudience">Audience: Why might the effect matter to this audience?</label><textarea id="scRhetAudience"></textarea>
<label for="scRhetPurpose">Purpose: How might the choice help or hinder the purpose?</label><textarea id="scRhetPurpose"></textarea>
<div class="sc-tool-actions"><button type="button" class="btn" id="scBuildRhetoric">Build analysis notes</button><button type="button" class="btn btn-secondary" id="scClearRhetoric">Clear</button></div>
<div id="scRhetoricOutput" class="sc-tool-output" role="status" aria-live="polite"></div>
""", "html.parser"))
    elif chapter == 10:
        tool.append(BeautifulSoup("""
<h3><i class="fas fa-magnifying-glass-chart" aria-hidden="true"></i> Observation to Significance Planner</h3>
<label for="scAnalysisObservation">Observation: What specific detail or pattern do you notice?</label><textarea id="scAnalysisObservation"></textarea>
<label for="scAnalysisInterpretation">Interpretation: What might the detail mean or do?</label><textarea id="scAnalysisInterpretation"></textarea>
<label for="scAnalysisSignificance">Significance: Why does the interpretation matter?</label><textarea id="scAnalysisSignificance"></textarea>
<div class="sc-tool-actions"><button type="button" class="btn" id="scBuildAnalysis">Preview analytical movement</button><button type="button" class="btn btn-secondary" id="scSaveAnalysis">Save</button><button type="button" class="btn btn-secondary" id="scClearAnalysis">Clear</button></div>
<div id="scAnalysisOutput" class="sc-tool-output" role="status" aria-live="polite"></div>
""", "html.parser"))
    elif chapter == 13:
        tool.append(BeautifulSoup("""
<h3><i class="fas fa-diagram-project" aria-hidden="true"></i> Synthesis Planner</h3>
<p>Plan the relationship and your conclusion before drafting. The tool saves notes but does not manufacture a paragraph for you.</p>
<label for="scSynthClaim">My paragraph’s claim or question</label><textarea id="scSynthClaim"></textarea>
<label for="scSynthA">Source A’s contribution and role</label><textarea id="scSynthA"></textarea>
<label for="scSynthB">Source B’s contribution and role</label><textarea id="scSynthB"></textarea>
<label for="scSynthRelationship">Relationship between the sources</label><textarea id="scSynthRelationship"></textarea>
<label for="scSynthConclusion">My conclusion or inference</label><textarea id="scSynthConclusion"></textarea>
<label for="scSynthMissing">Evidence or source still missing</label><textarea id="scSynthMissing"></textarea>
<div class="sc-tool-actions"><button type="button" class="btn" id="scSaveSynthesis">Save notes</button><button type="button" class="btn btn-secondary" id="scLoadSynthesis">Load saved notes</button><button type="button" class="btn btn-secondary" id="scClearSynthesis">Clear</button></div>
<div id="scSynthesisStatus" class="sc-tool-output" role="status" aria-live="polite"></div>
""", "html.parser"))
    else:
        return

    target.append(tool)


def build_revised_page(key: str | int, draft_path: Path) -> tuple[str, list[str]]:
    if key == "intro":
        template_path = SOURCE_1010 / "chapter-5.html"
        identity = "Introduction: Writing as Conversation"
        page_data = "introduction"
    else:
        number = int(key)
        template_path = SOURCE_1010 / f"chapter-{TEMPLATE_SOURCE.get(number, number)}.html"
        identity = f"Chapter {number}: {TITLES[number]}"
        page_data = f"chapter-{number}"

    soup = BeautifulSoup(template_path.read_text(encoding="utf-8"), "html.parser")
    title, subtitle, groups = split_draft(draft_path)

    body = soup.body
    if body is None:
        raise RuntimeError(f"Template has no body: {template_path}")
    body["data-course"] = "1010"
    body["data-page"] = page_data

    for old in soup.select(".quick-nav"):
        old.decompose()
    for old in soup.find_all("script"):
        src = str(old.get("src") or "")
        if "app.js" not in src:
            old.decompose()

    container = soup.select_one(".container")
    if container is None:
        raise RuntimeError(f"Template has no container: {template_path}")
    container.name = "main"
    container["id"] = "main-content"
    container["tabindex"] = "-1"
    container.clear()

    header = make_tag(soup, "header", class_="header")
    h1 = make_tag(soup, "h1")
    icon = make_tag(soup, "i", class_="fas fa-compass")
    icon.attrs["aria-hidden"] = "true"
    h1.append(icon)
    h1.append(NavigableString(" " + title))
    header.append(h1)
    if subtitle:
        header.append(make_tag(soup, "p", subtitle, class_="subtitle"))
    actions = make_tag(soup, "div", class_="sc-header-actions")
    print_button = make_tag(soup, "button", type="button", class_="btn")
    print_button["onclick"] = "window.print()"
    print_button.append(BeautifulSoup('<i class="fas fa-file-pdf" aria-hidden="true"></i> Save as PDF', "html.parser"))
    hub_link = make_tag(soup, "a", href="../index.html", class_="btn")
    hub_link.append(BeautifulSoup('<i class="fas fa-home" aria-hidden="true"></i> Course Hub', "html.parser"))
    actions.append(print_button)
    actions.append(hub_link)
    header.append(actions)
    container.append(header)

    sections: list[Tag] = []
    used_ids: set[str] = set()
    for index, (heading, nodes) in enumerate(groups, start=1):
        base_id = "section-" + slug(strip_numbering(heading))
        section_id = base_id
        counter = 2
        while section_id in used_ids:
            section_id = f"{base_id}-{counter}"
            counter += 1
        used_ids.add(section_id)
        section = make_section(soup, section_id, heading, nodes, active=index == 1)
        sections.append(section)
        container.append(section)

    if isinstance(key, int):
        insert_learning_tool(soup, key, sections)
    container.append(sequence_nav(soup, key))

    quick = build_quick_nav(soup, sections)
    sidebar = soup.select_one(".sidebar")
    if sidebar:
        sidebar.insert_after(quick)
    else:
        body.insert(1, quick)

    standardize_progress_and_sticky(soup, identity)
    wrap_tables(soup)
    videos = embed_youtube_links(soup)
    add_css_and_js(soup)

    if soup.title:
        soup.title.string = f"{identity} - Scholar's Compass"
    meta = soup.find("meta", attrs={"name": "description"})
    if meta:
        meta["content"] = subtitle or identity

    return soup.decode(formatter="minimal"), videos


def transform_unchanged_page(number: int) -> tuple[str, list[str]]:
    source = SOURCE_1010 / f"chapter-{number}.html"
    soup = BeautifulSoup(source.read_text(encoding="utf-8"), "html.parser")
    body = soup.body
    if body is None:
        raise RuntimeError(f"Page has no body: {source}")
    body["data-course"] = "1010"
    body["data-page"] = f"chapter-{number}"
    identity = f"Chapter {number}: {TITLES[number]}"
    standardize_progress_and_sticky(soup, identity)
    rewrite_cross_references(soup)
    wrap_tables(soup)
    videos = embed_youtube_links(soup)
    add_css_and_js(soup)

    container = soup.select_one(".container")
    if container:
        container.name = "main"
        container["id"] = "main-content"
        container["tabindex"] = "-1"
        for old in container.select(".chapter-sequence-nav"):
            old.decompose()
        container.append(sequence_nav(soup, number))

    if soup.title:
        soup.title.string = f"{identity} - Scholar's Compass"
    return soup.decode(formatter="minimal"), videos


def build_index() -> str:
    soup = BeautifulSoup((SOURCE_1010 / "index.html").read_text(encoding="utf-8"), "html.parser")
    body = soup.body
    if body is None:
        raise RuntimeError("Homepage has no body")
    body["data-course"] = "1010"
    body["data-page"] = "index"

    cards: dict[int, Tag] = {}
    for link in soup.select("a.chapter-link[href]"):
        match = re.search(r"chapter-(\d+)\.html", str(link.get("href")))
        if not match:
            continue
        cards[int(match.group(1))] = link

    if set(cards) != set(range(1, 15)):
        raise RuntimeError("Could not locate all fourteen homepage cards")

    row = cards[1].find_parent("div", class_="row")
    if row is None:
        raise RuntimeError("Could not locate chapter-card row")

    for number, title, icon, _, description in CHAPTERS:
        link = cards[number]
        link["href"] = f"chapter-{number}.html"
        link["data-chapter"] = str(number)
        card_number = link.select_one(".card-number")
        card_title = link.select_one(".chapter-title")
        card_text = link.select_one(".card-text")
        card_icon = link.select_one(".card-icon i")
        if card_number:
            card_number.string = str(number)
        if card_title:
            card_title.string = title
        if card_text:
            card_text.string = description
        if card_icon:
            card_icon["class"] = icon.split()
        column = link.find_parent("div", class_="col")
        if column:
            row.append(column)

    intro = soup.select_one(".sc-intro-card")
    if intro:
        intro.decompose()
    chapter_heading = soup.find(id="chapters")
    if chapter_heading:
        card = BeautifulSoup("""
<section class="sc-intro-card" aria-labelledby="sc-intro-title">
  <div>
    <p class="sc-eyebrow">Begin here</p>
    <h2 id="sc-intro-title">Introduction: Writing as Conversation</h2>
    <p>See how reading, inquiry, evidence, analysis, and revision fit together in a composition course.</p>
  </div>
  <a class="btn" href="introduction.html">Open the Introduction</a>
</section>
""", "html.parser").find("section")
        chapter_heading.insert_before(card)

    progress_text = soup.find(id="progressText")
    if progress_text:
        progress_text.string = "0 of 14 chapters completed"

    add_css_and_js(soup)
    if soup.title:
        soup.title.string = "ENG 1010 Scholar's Compass"
    return soup.decode(formatter="minimal")


def build_app_js() -> str:
    app = (SOURCE / "app.js").read_text(encoding="utf-8")
    rows = [
        "    { href: 'chapter-%d.html', icon: '%s', title: '%d. %s', readingTime: '%s' }"
        % (number, icon, number, title.replace("'", "\\'"), reading_time)
        for number, title, icon, reading_time, _ in CHAPTERS
    ]
    replacement = "  // Approved ENG 1010 revision-round-2 sequence.\n  var CHAPTERS_1010 = [\n" + ",\n".join(rows) + "\n  ];"
    app, count = re.subn(
        r"  // Approved ENG 1010.*?\n  var CHAPTERS_1010 = \[.*?\n  \];",
        replacement,
        app,
        count=1,
        flags=re.DOTALL,
    )
    if count != 1:
        raise RuntimeError("Could not replace CHAPTERS_1010")

    intro_code = """
    if (getCourse() === '1010') {
      var intro = document.createElement('a');
      intro.href = 'introduction.html';
      intro.className = 'sidebar-link sidebar-introduction';
      if (here === 'introduction.html') {
        intro.className += ' current';
        intro.setAttribute('aria-current', 'page');
      }
      var introIcon = document.createElement('i');
      introIcon.className = 'fas fa-compass';
      intro.appendChild(introIcon);
      intro.appendChild(document.createTextNode('Introduction: Writing as Conversation'));
      var introTime = document.createElement('span');
      introTime.className = 'reading-time';
      introTime.textContent = '8 min';
      intro.appendChild(introTime);
      container.appendChild(intro);
    }
"""
    marker = "    var here = currentFile().toLowerCase();\n"
    if intro_code.strip() not in app:
        if marker not in app:
            raise RuntimeError("Could not locate sidebar insertion point")
        app = app.replace(marker, marker + intro_code, 1)

    app = app.replace("qsa('.sidebar-link[href*=\"chapter\"]')", "qsa('.sidebar-link[href]')")
    app = app.replace('data-sc-stabilization="0.6"', 'data-sc-stabilization="0.7"')
    app = app.replace("interactive-tools.js?v=2", "interactive-tools.js?v=3")
    return app


def write_revision_css() -> None:
    css = r"""
:root { --sc-progress-hue: 210; }
.sc-reading-progress { position: fixed; inset: 0 0 auto 0; height: 5px; z-index: 2100; background: rgba(127,127,127,.22); }
.sc-reading-progress-bar { width: 0; height: 100%; background: hsl(var(--sc-progress-hue) 78% 44%); transition: width .12s linear, background-color .2s linear; }
.sc-sticky-chapter { position: fixed; top: 64px; left: 50%; transform: translate(-50%, -130%); z-index: 1090; max-width: min(92vw, 850px); padding: .48rem 1rem; border-radius: 0 0 .7rem .7rem; background: var(--card-bg, #fff); color: var(--text-primary, #1f2937); box-shadow: 0 4px 18px rgba(0,0,0,.15); font-weight: 700; text-align: center; opacity: 0; pointer-events: none; transition: transform .2s ease, opacity .2s ease; }
.sc-sticky-chapter.is-visible { transform: translate(-50%, 0); opacity: 1; }
.sc-header-actions { margin-top: 1.2rem; display: flex; gap: .65rem; justify-content: center; flex-wrap: wrap; }
.chapter-sequence-nav { display: grid; grid-template-columns: minmax(0,1fr) minmax(0,1fr); gap: 1rem; margin: 2.5rem 0 1rem; }
.chapter-sequence-nav a { display: flex; flex-direction: column; min-height: 6rem; padding: 1rem 1.15rem; border: 1px solid var(--border-color, #d9dee7); border-radius: .8rem; background: var(--card-bg, #fff); color: inherit; text-decoration: none; box-shadow: 0 3px 12px rgba(0,0,0,.07); }
.chapter-sequence-nav a:hover, .chapter-sequence-nav a:focus-visible { transform: translateY(-2px); box-shadow: 0 7px 20px rgba(0,0,0,.12); }
.chapter-sequence-next { text-align: right; align-items: flex-end; }
.chapter-sequence-label { display: block; margin-bottom: .35rem; font-size: .8rem; text-transform: uppercase; letter-spacing: .08em; opacity: .72; }
.sc-intro-card { display: flex; align-items: center; justify-content: space-between; gap: 1.5rem; margin: 0 auto 2.2rem; padding: 1.4rem 1.6rem; border-radius: 1rem; background: linear-gradient(135deg, rgba(25,76,135,.12), rgba(46,139,87,.12)); border: 1px solid rgba(25,76,135,.22); }
.sc-intro-card h2 { margin: .15rem 0 .4rem; }
.sc-intro-card p { margin-bottom: 0; }
.sc-eyebrow { text-transform: uppercase; letter-spacing: .1em; font-size: .78rem; font-weight: 800; }
.table-responsive { width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; margin: 1rem 0; }
.sc-video-embed { max-width: 900px; margin: 1.5rem auto; }
.sc-video-embed iframe { width: 100%; aspect-ratio: 16 / 9; height: auto; border: 0; border-radius: .7rem; background: #111; }
.sc-video-fallback { margin: .5rem 0 0; font-size: .92rem; }
.sc-revision-tool label { display: block; margin: .8rem 0 .35rem; font-weight: 700; }
.sc-revision-tool textarea { width: 100%; min-height: 5.4rem; padding: .75rem; border: 1px solid var(--border-color, #cbd5e1); border-radius: .45rem; background: var(--card-bg, #fff); color: inherit; }
.sc-revision-tool > label:has(input) { display: flex; gap: .55rem; align-items: flex-start; font-weight: 500; }
.sc-tool-actions { display: flex; flex-wrap: wrap; gap: .6rem; margin-top: 1rem; }
.sc-tool-output { margin-top: 1rem; min-height: 2.8rem; padding: .85rem; border-left: 4px solid var(--primary, #194c87); background: rgba(25,76,135,.08); white-space: pre-wrap; }
.sc-tool-progress { margin-top: 1rem; }
.annotation-grid { display: grid; grid-template-columns: repeat(2,minmax(0,1fr)); gap: .75rem; }
.annotation-grid .annotation-item { width: 100%; text-align: left; }
html:not(.js) .section-content { display: block !important; }
html:not(.js) .section { opacity: 1 !important; }
.dark-mode .sc-sticky-chapter, .dark-mode .chapter-sequence-nav a { background: #1f2937; color: #f8fafc; border-color: #475569; }
.dark-mode .sc-revision-tool textarea { background: #111827; color: #f8fafc; border-color: #64748b; }
@media (max-width: 768px) {
  .sc-sticky-chapter { top: 56px; width: calc(100vw - 1rem); font-size: .9rem; }
  .chapter-sequence-nav { grid-template-columns: 1fr; }
  .chapter-sequence-next { text-align: left; align-items: flex-start; }
  .sc-intro-card { flex-direction: column; align-items: flex-start; }
  .annotation-grid { grid-template-columns: 1fr; }
}
@media (prefers-reduced-motion: reduce) {
  .sc-reading-progress-bar, .sc-sticky-chapter, .chapter-sequence-nav a { transition: none !important; }
}
@media print {
  .sc-reading-progress, .sc-sticky-chapter, .chapter-sequence-nav, .quick-nav, .sc-tool-actions, .sc-video-embed iframe { display: none !important; }
  .sc-video-fallback { display: block !important; }
}
""".lstrip()
    (OUTPUT / "revision-round-2.css").write_text(css, encoding="utf-8")


def write_revision_js() -> None:
    js = r"""
(function () {
  'use strict';
  function qs(selector) { return document.querySelector(selector); }
  function value(id) { var node = qs('#' + id); return node ? node.value.trim() : ''; }
  function setValue(id, text) { var node = qs('#' + id); if (node) node.value = text || ''; }
  function status(id, text) { var node = qs('#' + id); if (node) node.textContent = text; }
  function save(key, object) { try { localStorage.setItem(key, JSON.stringify(object)); return true; } catch (err) { return false; } }
  function load(key) { try { return JSON.parse(localStorage.getItem(key) || 'null'); } catch (err) { return null; } }
  function remove(key) { try { localStorage.removeItem(key); } catch (err) {} }

  function updateReadingUI() {
    var top = window.scrollY || document.documentElement.scrollTop || 0;
    var height = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
    var percent = Math.max(0, Math.min(100, top / height * 100));
    var progress = qs('.sc-reading-progress');
    var bar = qs('.sc-reading-progress-bar');
    if (bar) bar.style.width = percent + '%';
    if (progress) progress.setAttribute('aria-valuenow', String(Math.round(percent)));
    document.documentElement.style.setProperty('--sc-progress-hue', String(Math.round(210 - percent * .9)));
    var header = qs('.header');
    var sticky = qs('.sc-sticky-chapter');
    if (header && sticky) sticky.classList.toggle('is-visible', header.getBoundingClientRect().bottom < 72 && top < height - 40);
  }

  function initQuoteTool() {
    var button = qs('#scBuildQuote');
    if (!button) return;
    var key = 'scholarsCompass:chapter-4:prepare-present-explain';
    function data() { return { point:value('scQuotePoint'), context:value('scQuoteContext'), evidence:value('scQuoteEvidence'), explanation:value('scQuoteExplanation') }; }
    function render() { var d=data(); status('scQuoteOutput', [d.point,d.context,d.evidence,d.explanation].filter(Boolean).join(' ')); }
    button.addEventListener('click', render);
    qs('#scSaveQuote').addEventListener('click', function(){ save(key,data()); status('scQuoteOutput','Saved in this browser.'); });
    qs('#scClearQuote').addEventListener('click', function(){ ['scQuotePoint','scQuoteContext','scQuoteEvidence','scQuoteExplanation'].forEach(function(id){setValue(id,'');}); remove(key); status('scQuoteOutput','Cleared.'); });
    var stored=load(key); if(stored){ Object.keys(stored).forEach(function(name){ var ids={point:'scQuotePoint',context:'scQuoteContext',evidence:'scQuoteEvidence',explanation:'scQuoteExplanation'}; setValue(ids[name],stored[name]); }); }
  }

  function initRhetoricTool() {
    var button=qs('#scBuildRhetoric'); if(!button) return;
    button.addEventListener('click', function(){
      var parts=[['Choice',value('scRhetChoice')],['Effect',value('scRhetEffect')],['Audience',value('scRhetAudience')],['Purpose',value('scRhetPurpose')]];
      status('scRhetoricOutput',parts.filter(function(p){return p[1];}).map(function(p){return p[0]+': '+p[1];}).join('\n'));
    });
    qs('#scClearRhetoric').addEventListener('click',function(){['scRhetChoice','scRhetEffect','scRhetAudience','scRhetPurpose'].forEach(function(id){setValue(id,'');}); status('scRhetoricOutput','Cleared.');});
  }

  function initAnalysisTool() {
    var button=qs('#scBuildAnalysis'); if(!button) return;
    var key='scholarsCompass:chapter-10:observation-interpretation-significance';
    function data(){return {observation:value('scAnalysisObservation'),interpretation:value('scAnalysisInterpretation'),significance:value('scAnalysisSignificance')};}
    function render(){var d=data();status('scAnalysisOutput',['Observation: '+d.observation,'Interpretation: '+d.interpretation,'Significance: '+d.significance].join('\n'));}
    button.addEventListener('click',render);
    qs('#scSaveAnalysis').addEventListener('click',function(){save(key,data());status('scAnalysisOutput','Saved in this browser.');});
    qs('#scClearAnalysis').addEventListener('click',function(){['scAnalysisObservation','scAnalysisInterpretation','scAnalysisSignificance'].forEach(function(id){setValue(id,'');});remove(key);status('scAnalysisOutput','Cleared.');});
    var d=load(key); if(d){setValue('scAnalysisObservation',d.observation);setValue('scAnalysisInterpretation',d.interpretation);setValue('scAnalysisSignificance',d.significance);}
  }

  function initSynthesisTool() {
    var saveButton=qs('#scSaveSynthesis'); if(!saveButton) return;
    var key='scholarsCompass:chapter-13:synthesis-planner';
    var fields=['scSynthClaim','scSynthA','scSynthB','scSynthRelationship','scSynthConclusion','scSynthMissing'];
    function data(){var d={};fields.forEach(function(id){d[id]=value(id);});return d;}
    function restore(d){if(!d)return;fields.forEach(function(id){setValue(id,d[id]);});}
    saveButton.addEventListener('click',function(){status('scSynthesisStatus',save(key,data())?'Synthesis notes saved in this browser.':'The notes could not be saved in this browser.');});
    qs('#scLoadSynthesis').addEventListener('click',function(){var d=load(key);restore(d);status('scSynthesisStatus',d?'Saved notes loaded.':'No saved synthesis notes were found.');});
    qs('#scClearSynthesis').addEventListener('click',function(){fields.forEach(function(id){setValue(id,'');});remove(key);status('scSynthesisStatus','Synthesis notes cleared.');});
    restore(load(key));
  }

  function ready() {
    updateReadingUI();
    var ticking=false;
    window.addEventListener('scroll',function(){if(ticking)return;ticking=true;requestAnimationFrame(function(){updateReadingUI();ticking=false;});},{passive:true});
    window.addEventListener('resize',updateReadingUI,{passive:true});
    initQuoteTool(); initRhetoricTool(); initAnalysisTool(); initSynthesisTool();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',ready);else ready();
})();
""".lstrip()
    (OUTPUT / "revision-round-2.js").write_text(js, encoding="utf-8")


def write_hub() -> None:
    hub = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ENG 1010 Revision Round 2</title><link rel="icon" href="favicon.svg"><link rel="stylesheet" href="styles.css?v=19-rc2"><link rel="stylesheet" href="revision-round-2.css?v=1"></head>
<body data-course="1010" data-page="release-candidate-v2"><main class="container" id="main-content" tabindex="-1" style="margin-top:2rem">
<header class="header"><h1>ENG 1010 Revision Round 2</h1><p class="subtitle">Isolated HTML package for content, visual, and functional review</p></header>
<section class="section active"><div class="section-content" style="display:block"><p>The previous release candidate remains available as a rollback point. This package includes the approved introduction, revised chapters, final sequence, sticky identity, enhanced reading progress, embedded videos, and chapter-to-chapter navigation.</p><p><a class="btn" href="1010/index.html">Open the revised ENG 1010 guide</a></p><p><a href="../release-candidate/1010/index.html">Open the previous release candidate</a></p></div></section>
</main></body></html>"""
    (OUTPUT / "index.html").write_text(hub, encoding="utf-8")


def audit_output(video_map: dict[str, list[str]]) -> dict[str, object]:
    pages = [OUTPUT_1010 / "introduction.html", *[OUTPUT_1010 / f"chapter-{n}.html" for n in range(1, 15)]]
    missing_destinations: list[str] = []
    obvious_apa_patterns: list[str] = []
    raw_youtube_links: list[str] = []
    duplicate_videos: dict[str, list[str]] = {}
    all_videos: dict[str, list[str]] = {}

    existing = {page.name for page in pages} | {"index.html"}
    for page in [OUTPUT_1010 / "index.html", *pages]:
        text = page.read_text(encoding="utf-8")
        for match in re.finditer(r'href=["\']([^"\']+)["\']', text, flags=re.IGNORECASE):
            href = match.group(1).split("#", 1)[0]
            if href.startswith(("http:", "https:", "mailto:", "tel:", "javascript:")) or not href:
                continue
            name = Path(href).name
            if name.endswith(".html") and name not in existing and name != "../index.html":
                missing_destinations.append(f"{page.name} -> {href}")
        for match in re.finditer(r"\b[A-Z][A-Za-z-]+\s*\((?:19|20)\d{2}\)", text):
            obvious_apa_patterns.append(f"{page.name}: {match.group(0)}")
        soup = BeautifulSoup(text, "html.parser")
        for anchor in soup.find_all("a", href=True):
            if youtube_id(str(anchor.get("href"))) and not anchor.find_parent(class_="sc-video-embed"):
                raw_youtube_links.append(f"{page.name}: {anchor.get('href')}")
        for iframe in soup.select(".sc-video-embed iframe[src]"):
            vid = youtube_id(str(iframe.get("src")))
            if vid:
                all_videos.setdefault(vid, []).append(page.name)

    for vid, locations in all_videos.items():
        if len(locations) > 1:
            duplicate_videos[vid] = locations

    return {
        "missing_internal_destinations": sorted(set(missing_destinations)),
        "obvious_apa_patterns": sorted(set(obvious_apa_patterns)),
        "unembedded_youtube_links": sorted(set(raw_youtube_links)),
        "duplicate_video_ids": duplicate_videos,
        "video_ids_by_page": video_map,
    }


def main() -> None:
    if not SOURCE_1010.exists():
        raise FileNotFoundError("The approved release-candidate package is missing")
    for draft in DRAFTS.values():
        if not (ROOT / draft).exists():
            raise FileNotFoundError(ROOT / draft)

    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT_1010.mkdir(parents=True)

    source_hashes: dict[str, str] = {}
    for path in sorted(SOURCE.rglob("*")):
        if path.is_file():
            source_hashes[str(path.relative_to(ROOT))] = sha256(path)

    # Carry the approved shell and chapter-specific assets forward first.
    for path in SOURCE.iterdir():
        if path.name in {"index.html", "README.md", "BUILD-MANIFEST.json", "TEST-RESULTS.md"}:
            continue
        destination = OUTPUT / path.name
        if path.is_dir():
            shutil.copytree(path, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(path, destination)

    video_map: dict[str, list[str]] = {}
    intro_html, intro_videos = build_revised_page("intro", ROOT / DRAFTS["intro"])
    (OUTPUT_1010 / "introduction.html").write_text(intro_html, encoding="utf-8")
    video_map["introduction.html"] = intro_videos

    revised_numbers = {int(key) for key in DRAFTS if isinstance(key, int)}
    for number in range(1, 15):
        if number in revised_numbers:
            html, videos = build_revised_page(number, ROOT / DRAFTS[number])
        else:
            html, videos = transform_unchanged_page(number)
        (OUTPUT_1010 / f"chapter-{number}.html").write_text(html, encoding="utf-8")
        video_map[f"chapter-{number}.html"] = videos

    (OUTPUT_1010 / "index.html").write_text(build_index(), encoding="utf-8")
    (OUTPUT / "app.js").write_text(build_app_js(), encoding="utf-8")
    write_revision_css()
    write_revision_js()
    write_hub()

    audit = audit_output(video_map)
    manifest = {
        "built_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_area": "release-candidate/",
        "output_area": "release-candidate-v2/",
        "introduction": "Introduction: Writing as Conversation",
        "approved_sequence": [title for _, title, _, _, _ in CHAPTERS],
        "revised_chapters": sorted(revised_numbers),
        "unchanged_substantive_chapters": [6, 7, 8, 9, 11, 12, 14],
        "storage_policy": "Existing content-tied keys remain; new revision tools use chapter-specific keys.",
        "source_sha256": source_hashes,
        "audit": audit,
    }
    (OUTPUT / "BUILD-MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    audit_lines = [
        "# ENG 1010 Revision-Round-2 Audit",
        "",
        f"- Missing internal destinations: {len(audit['missing_internal_destinations'])}",
        f"- Obvious APA-style author-year patterns: {len(audit['obvious_apa_patterns'])}",
        f"- YouTube links not converted to responsive embeds: {len(audit['unembedded_youtube_links'])}",
        f"- Duplicate embedded video IDs: {len(audit['duplicate_video_ids'])}",
        "",
        "The video audit verifies local embed construction and duplication. External caption availability and owner-controlled embeddability still require final visual review because those settings can change outside the repository.",
    ]
    for heading, key in [
        ("Missing internal destinations", "missing_internal_destinations"),
        ("Obvious APA-style patterns", "obvious_apa_patterns"),
        ("Unembedded YouTube links", "unembedded_youtube_links"),
    ]:
        values = audit[key]
        if values:
            audit_lines.extend(["", f"## {heading}", "", *[f"- {item}" for item in values]])
    if audit["duplicate_video_ids"]:
        audit_lines.extend(["", "## Duplicate embedded videos", ""])
        for vid, pages in audit["duplicate_video_ids"].items():
            audit_lines.append(f"- `{vid}`: {', '.join(pages)}")
    (OUTPUT / "AUDIT-REPORT.md").write_text("\n".join(audit_lines) + "\n", encoding="utf-8")

    readme = """# ENG 1010 Revision Round 2

This generated directory is an isolated review package. It does not replace `release-candidate/`, the current preview, or the canonical Scholar's Compass repository.

Review entry point: `release-candidate-v2/1010/index.html`

The package includes:

- the approved unnumbered introduction;
- the final fourteen-chapter sequence, with Active Reading before Annotation;
- approved substantive revisions to Chapters 1–5, 10, and 13;
- the approved Chapter 12 and substantively unchanged Chapters 6–9, 11, and 14;
- responsive YouTube embeds with direct fallback links;
- a color-changing reading progress bar;
- sticky chapter identity after the large heading scrolls away;
- static previous/next navigation on every destination;
- accessible disclosures, keyboard navigation, no-JavaScript reading, dark mode, mobile, and print support;
- an audit report and automated regression results.
"""
    (OUTPUT / "README.md").write_text(readme, encoding="utf-8")
    print("Built introduction plus fourteen chapters in release-candidate-v2/")


if __name__ == "__main__":
    main()
