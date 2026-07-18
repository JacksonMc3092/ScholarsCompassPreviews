#!/usr/bin/env python3
"""Apply the first instructor HTML-review batch to release-candidate-v2.

The base release-candidate and canonical Scholar's Compass repository remain
untouched. This script operates only on the generated preview package.
"""

from __future__ import annotations

import re
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "release-candidate-v2"
COURSE = OUTPUT / "1010"
SOURCE = ROOT / "release-candidate" / "1010"


def load(path: Path) -> BeautifulSoup:
    return BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")


def save(path: Path, soup: BeautifulSoup) -> None:
    path.write_text(soup.decode(formatter="minimal"), encoding="utf-8")


def replace_text(soup: BeautifulSoup, old: str, new: str) -> None:
    for node in list(soup.find_all(string=lambda value: value and old in value)):
        node.replace_with(str(node).replace(old, new))


def patch_shared_assets() -> None:
    css_path = OUTPUT / "revision-round-2.css"
    css = css_path.read_text(encoding="utf-8")
    marker = "/* HTML review batch 1 */"
    css = css.split(marker, 1)[0].rstrip() + "\n\n"
    css += """/* HTML review batch 1 */
body[data-page="introduction"] .header h1 { color: #fff !important; }
.sc-reading-progress-bar {
  width: 100% !important;
  transform: scaleX(0);
  transform-origin: left center;
  transition: transform .12s linear, background-color .2s linear;
}
.sc-resource-button {
  display: inline-flex;
  align-items: center;
  gap: .45rem;
  margin: .35rem 0 .8rem;
}
@media (max-width: 768px) {
  .sc-sticky-chapter {
    top: 50px;
    width: auto;
    max-width: calc(100vw - 5rem);
    padding: .18rem .55rem;
    border-radius: 0 0 .45rem .45rem;
    font-size: .72rem;
    line-height: 1.15;
    font-weight: 650;
    box-shadow: 0 2px 8px rgba(0,0,0,.12);
    opacity: 0;
  }
  .sc-sticky-chapter.is-visible { opacity: .9; }
}
"""
    css_path.write_text(css, encoding="utf-8")

    js_path = OUTPUT / "revision-round-2.js"
    js = js_path.read_text(encoding="utf-8")
    replacement = """function updateReadingUI() {
    var scrollRoot = document.scrollingElement || document.documentElement;
    var top = scrollRoot.scrollTop || window.pageYOffset || 0;
    var height = Math.max(1, scrollRoot.scrollHeight - scrollRoot.clientHeight);
    var percent = Math.max(0, Math.min(100, top / height * 100));
    var progress = qs('.sc-reading-progress');
    var bar = qs('.sc-reading-progress-bar');
    if (bar) {
      bar.style.width = '100%';
      bar.style.transform = 'scaleX(' + (percent / 100) + ')';
    }
    if (progress) progress.setAttribute('aria-valuenow', String(Math.round(percent)));
    document.documentElement.style.setProperty('--sc-progress-hue', String(Math.round(210 - percent * .9)));
    var header = qs('.header');
    var sticky = qs('.sc-sticky-chapter');
    if (header && sticky) {
      sticky.classList.toggle('is-visible', header.getBoundingClientRect().bottom < 58 && top < height - 40);
    }
  }"""
    js, count = re.subn(
        r"function updateReadingUI\(\) \{.*?\n  \}",
        replacement,
        js,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise RuntimeError("Could not replace updateReadingUI")
    old_resize = "window.addEventListener('resize',updateReadingUI,{passive:true});"
    new_resize = (
        old_resize
        + "\n    window.addEventListener('load',updateReadingUI,{once:true});"
        + "\n    window.addEventListener('pageshow',updateReadingUI);"
        + "\n    setTimeout(updateReadingUI, 100);"
    )
    if "window.addEventListener('pageshow',updateReadingUI);" not in js:
        js = js.replace(old_resize, new_resize)
    js_path.write_text(js, encoding="utf-8")


def patch_progress_markup() -> None:
    destinations = [
        COURSE / "index.html",
        COURSE / "introduction.html",
        *[COURSE / f"chapter-{number}.html" for number in range(1, 15)],
    ]
    for path in destinations:
        soup = load(path)
        for old in soup.select(".progress-container-top, .progress-container"):
            old.decompose()
        progress = soup.select_one(".sc-reading-progress")
        if progress is None:
            progress = soup.new_tag(
                "div",
                attrs={
                    "class": "sc-reading-progress",
                    "role": "progressbar",
                    "aria-label": "Reading progress",
                    "aria-valuemin": "0",
                    "aria-valuemax": "100",
                    "aria-valuenow": "0",
                },
            )
            bar = soup.new_tag(
                "div",
                attrs={"class": "sc-reading-progress-bar", "id": "scReadingProgressBar"},
            )
            progress.append(bar)
            soup.body.insert(0, progress)
        else:
            bar = progress.select_one(".sc-reading-progress-bar")
            if bar is not None:
                bar["id"] = "scReadingProgressBar"
        save(path, soup)


def patch_chapter_2() -> None:
    path = COURSE / "chapter-2.html"
    soup = load(path)

    # Markdown treated the bare URL as text, so replace the complete resource line.
    resource_paragraph = soup.find(
        "p", string=lambda value: value and "human.libretexts.org" in value
    )
    if resource_paragraph is None:
        resource_paragraph = soup.find(
            "p", string=lambda value: value and value.strip().startswith("Resource:")
        )
    if resource_paragraph is None:
        raise RuntimeError("Chapter 2 LibreTexts resource line not found")
    resource_paragraph.clear()
    link = soup.new_tag(
        "a",
        href=(
            "https://human.libretexts.org/Courses/Chabot_College/"
            "College_Success_and_Advanced_ESL_Writing/"
            "02%3A_The_Role_of_Active_Reading/"
            "2.05%3A_Annotating_a_Text_-_a_detailed_example"
        ),
        target="_blank",
        rel="noopener",
    )
    link["class"] = ["btn", "sc-resource-button"]
    link.string = "View the Detailed Annotation Example on LibreTexts"
    resource_paragraph.append(link)

    for paragraph in list(soup.find_all("p")):
        text = paragraph.get_text(" ", strip=True)
        if (
            "The current chapter includes the video" in text
            or "The video will be included only after it is verified" in text
        ):
            paragraph.decompose()

    embed = soup.find("iframe", src=lambda src: src and "gXRwTI7Dv3s" in src)
    if embed is None:
        raise RuntimeError("Chapter 2 annotation video not found")
    wrapper = embed.find_parent(class_="sc-video-embed")
    introduction = soup.new_tag("p")
    introduction.string = (
        "This video presents twelve practical approaches to annotating academic "
        "texts and books."
    )
    wrapper.insert_before(introduction)
    save(path, soup)


def patch_chapter_3() -> None:
    path = COURSE / "chapter-3.html"
    soup = load(path)
    replace_text(soup, "Mollie Chambers and her coauthors", "Jordan Lee")
    replace_text(soup, "Chambers and her coauthors", "Lee")
    replace_text(soup, "Chambers et al.", "Lee")
    replace_text(soup, "Lee explain", "Lee explains")
    replace_text(soup, "Lee emphasize", "Lee emphasizes")

    heading = soup.find(
        "h3", string=lambda value: value and "Write a source sentence" in value
    )
    if heading is not None:
        note = soup.new_tag("p")
        note.string = "The MLA examples below use a fictional practice article by Jordan Lee."
        heading.insert_after(note)
    save(path, soup)


def patch_chapter_4() -> None:
    path = COURSE / "chapter-4.html"
    soup = load(path)
    replacements = {
        "The following is an original Scholar’s Compass practice passage:": "Practice Passage:",
        "Original Scholar’s Compass practice source:": "Practice Passage:",
        "Original Scholar’s Compass practice passage": "Practice Passage",
        "The video previously located in Chapter 13 now belongs in this chapter:": (
            "This video reviews MLA in-text citations, quotations, and paraphrases:"
        ),
        "From the following original Scholar’s Compass practice sentence, select only the words needed to support a claim about stopping points:": (
            "Here is a practice sentence. Select only the words needed to support a claim about stopping points:"
        ),
    }
    for old, new in replacements.items():
        replace_text(soup, old, new)
    for paragraph in list(soup.find_all("p")):
        if "The revised HTML chapter will use a responsive embed" in paragraph.get_text(
            " ", strip=True
        ):
            paragraph.decompose()
    save(path, soup)


def patch_open_oregon_links() -> None:
    destinations = {
        7: (
            "openoregon.pressbooks.pub/aboutwriting/chapter/strategies-for-getting-started",
            "https://openoregon.pressbooks.pub/wrd/chapter/strategies-for-getting-started/",
        ),
        9: (
            "openoregon.pressbooks.pub/aboutwriting/chapter/writing-paragraphs",
            "https://openoregon.pressbooks.pub/wrd/chapter/writing-paragraphs/",
        ),
    }
    for number, (old_fragment, new_url) in destinations.items():
        path = COURSE / f"chapter-{number}.html"
        soup = load(path)
        found = False
        for anchor in soup.find_all("a", href=True):
            if old_fragment in anchor["href"]:
                anchor["href"] = new_url
                anchor.string = new_url
                found = True
        if not found:
            raise RuntimeError(f"Chapter {number} legacy Open Oregon link not found")
        save(path, soup)


def patch_chapter_10() -> None:
    path = COURSE / "chapter-10.html"
    soup = load(path)
    source = load(SOURCE / "chapter-10.html")
    visual = source.select_one(".blooms-container")
    if visual is None:
        raise RuntimeError("Protected Bloom visualizer not found")
    interactive = visual.find_parent(class_="interactive-element")
    target = soup.select_one("#section-what-analysis-does .section-content")
    if target is None:
        raise RuntimeError("Chapter 10 analysis section not found")
    imported = BeautifulSoup(str(interactive), "html.parser").select_one(
        ".interactive-element"
    )
    heading = target.find(
        "h3", string=lambda value: value and "part-to-whole" in value.lower()
    )
    if heading is not None:
        heading.insert_before(imported)
    else:
        target.append(imported)
    replace_text(
        soup,
        "The current Scholar’s Compass chapter uses a building-block analogy.",
        "Imagine taking apart a model castle as a way to understand the part-to-whole relationship in analysis.",
    )
    save(path, soup)


def patch_chapter_11() -> None:
    path = COURSE / "chapter-11.html"
    soup = load(path)
    for box in list(soup.select(".citation-adapted")):
        paragraphs = box.find_all("p", recursive=False)
        if len(paragraphs) > 1:
            paragraphs[0].decompose()
            box.unwrap()
        else:
            box.decompose()

    nav = soup.select_one(".chapter-sequence-nav")
    if nav is None:
        raise RuntimeError("Chapter 11 sequence navigation not found")
    attribution = soup.new_tag(
        "div", attrs={"class": "citation-box sc-consolidated-attribution"}
    )
    label = soup.new_tag("p")
    strong = soup.new_tag("strong")
    strong.string = "Adaptation and Attribution"
    label.append(strong)
    attribution.append(label)

    detail = soup.new_tag("p")
    detail.append("Portions of this chapter are adapted from Wanda M. Waller’s “Argument” in ")
    title = soup.new_tag("em")
    title.string = "English Composition I"
    detail.append(title)
    detail.append(", LOUIS: The Louisiana Library Network, 2022, licensed under CC BY 4.0. ")
    link = soup.new_tag(
        "a",
        href="https://louis.pressbooks.pub/englishcomp1/",
        target="_blank",
        rel="noopener",
    )
    link.string = "View the original open textbook."
    detail.append(link)
    attribution.append(detail)
    nav.insert_before(attribution)
    save(path, soup)


def main() -> None:
    patch_shared_assets()
    patch_progress_markup()
    patch_chapter_2()
    patch_chapter_3()
    patch_chapter_4()
    patch_open_oregon_links()
    patch_chapter_10()
    patch_chapter_11()
    print("Applied ENG 1010 HTML review batch 1")


if __name__ == "__main__":
    main()
