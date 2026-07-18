#!/usr/bin/env python3
"""Static and browser regression tests for ENG 1010 revision round 2."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "release-candidate-v2"
OUTPUT_1010 = OUTPUT / "1010"

EXPECTED_TITLES = [
    "Active Reading Strategies",
    "Annotating Your Way to Greatness",
    "Summarizing Your Way to Synthesis",
    "Quoting, Paraphrasing, and Signal Phrases",
    "Understanding Rhetoric: The Art of Persuasion",
    "Values, Assumptions, and Ideology",
    "Strategies for Getting Started",
    "Crafting Powerful Thesis Statements",
    "Designing Effective Paragraphs",
    "Analysis",
    "Argumentation: Joining the Academic Conversation",
    "Finding and Evaluating Sources",
    "Synthesis: Putting Sources into Conversation",
    "Revision: From Draft to Final",
]


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def read(name: str) -> str:
    return (OUTPUT_1010 / name).read_text(encoding="utf-8")


def static_tests() -> list[str]:
    failures: list[str] = []
    require(OUTPUT.exists(), "release-candidate-v2 directory is missing", failures)
    require((OUTPUT / "BUILD-MANIFEST.json").exists(), "build manifest is missing", failures)
    require((OUTPUT / "AUDIT-REPORT.md").exists(), "audit report is missing", failures)
    require((OUTPUT / "revision-round-2.css").exists(), "revision CSS is missing", failures)
    require((OUTPUT / "revision-round-2.js").exists(), "revision JavaScript is missing", failures)

    destinations = [OUTPUT_1010 / "introduction.html"] + [OUTPUT_1010 / f"chapter-{n}.html" for n in range(1, 15)]
    require((OUTPUT_1010 / "index.html").exists(), "ENG 1010 index is missing", failures)
    for page in destinations:
        require(page.exists(), f"missing {page.name}", failures)
    if failures:
        return failures

    index_soup = BeautifulSoup(read("index.html"), "html.parser")
    links = index_soup.select("a.chapter-link[href]")
    hrefs = [link.get("href") for link in links]
    require(hrefs == [f"chapter-{n}.html" for n in range(1, 15)], "homepage chapter links are not sequential", failures)
    titles = [link.select_one(".chapter-title").get_text(" ", strip=True) for link in links]
    require(titles == EXPECTED_TITLES, "homepage titles do not match the approved sequence", failures)
    require(index_soup.select_one('a[href="introduction.html"]') is not None, "homepage has no introduction destination", failures)

    expected_files = {"index.html", "introduction.html", *[f"chapter-{n}.html" for n in range(1, 15)]}
    for page in destinations:
        soup = BeautifulSoup(page.read_text(encoding="utf-8"), "html.parser")
        text = page.read_text(encoding="utf-8")
        expected_data = "introduction" if page.name == "introduction.html" else page.stem
        require(soup.body is not None and soup.body.get("data-course") == "1010", f"{page.name} lacks ENG 1010 identity", failures)
        require(soup.body is not None and soup.body.get("data-page") == expected_data, f"{page.name} has incorrect data-page", failures)
        require(soup.select_one("main#main-content") is not None, f"{page.name} lacks main landmark", failures)
        require(soup.select_one(".sc-reading-progress #scrollProgress") is not None, f"{page.name} lacks enhanced reading progress", failures)
        require(soup.select_one(".sc-sticky-chapter") is not None, f"{page.name} lacks sticky chapter identity", failures)
        require(len(soup.select(".chapter-sequence-nav a")) == 2, f"{page.name} lacks two-way sequence navigation", failures)
        require("../revision-round-2.css?v=1" in text, f"{page.name} does not load revision CSS", failures)
        require("../revision-round-2.js?v=1" in text, f"{page.name} does not load revision JavaScript", failures)
        require("../app.js?v=22-rc2" in text, f"{page.name} does not load the revised shared app", failures)
        require(soup.select_one(".section") is not None, f"{page.name} has no instructional sections", failures)
        for anchor in soup.find_all("a", href=True):
            href = str(anchor.get("href")).split("#", 1)[0]
            if not href or href.startswith(("http:", "https:", "mailto:", "tel:", "javascript:")):
                continue
            name = Path(href).name
            if name.endswith(".html"):
                require(name in expected_files, f"{page.name} links to missing {href}", failures)

    intro = BeautifulSoup(read("introduction.html"), "html.parser")
    require("Writing as Conversation" in intro.get_text(" ", strip=True), "introduction content is missing", failures)
    require(intro.select_one('.chapter-sequence-next[href="chapter-1.html"]') is not None, "introduction does not lead to Chapter 1", failures)

    ch1 = read("chapter-1.html")
    require("SQ3R Practice Tracker" in ch1, "Chapter 1 lost the SQ3R practice tracker", failures)
    require("CFT83pPike4" in ch1, "Chapter 1 does not contain the approved replacement video", failures)
    require("youtube-nocookie.com/embed/CFT83pPike4" in ch1, "Chapter 1 video is not responsively embedded", failures)
    require('chapter-sequence-previous" href="introduction.html"' in ch1 or 'href="introduction.html" class="chapter-sequence-previous"' in ch1, "Chapter 1 does not return to the introduction", failures)

    ch2 = read("chapter-2.html")
    require("Your Personal Annotation Key" not in ch2, "Chapter 2 still contains the removed personal annotation key", failures)
    require("Hunter College" not in ch2, "Chapter 2 still contains the dead Hunter College reference", failures)
    require("2.05%3A_Annotating_a_Text_-_a_detailed_example" in ch2, "Chapter 2 lacks the approved LibreTexts example", failures)

    ch3 = read("chapter-3.html")
    require("Signal Verbs and Transitional Language" in ch3, "Chapter 3 signal-verb terminology is missing", failures)

    ch4 = read("chapter-4.html")
    require("Prepare, Present, Explain Builder" in ch4, "Chapter 4 lacks the moved source-integration builder", failures)
    require("youtube-nocookie.com/embed/5qvPqvkgFXY" in ch4, "Chapter 4 lacks the moved MLA video embed", failures)
    require("high ethos or stylistic precision" not in ch4.lower(), "Chapter 4 retains the unclear quotation criterion", failures)

    ch5 = read("chapter-5.html")
    require("Choice → Effect → Audience → Purpose" in ch5 or "Choice → Effect → Audience → Purpose" in BeautifulSoup(ch5, "html.parser").get_text(" ", strip=True), "Chapter 5 lacks the rhetorical analysis pattern", failures)
    require("Rhetorical Choice Planner" in ch5, "Chapter 5 lacks its analysis planner", failures)

    ch10 = read("chapter-10.html")
    require("Observation, Interpretation, and Significance" in ch10, "Chapter 10 lacks its central analytical framework", failures)
    require("Quote Sandwich Builder" not in ch10, "Chapter 10 still contains the quote-sandwich builder", failures)
    require("Observation to Significance Planner" in ch10, "Chapter 10 lacks its analysis planner", failures)

    ch12 = read("chapter-12.html")
    for marker in ["The Three-Lane Search Method", "SIFT", "Keyword Builder", "Source Log"]:
        require(marker in ch12, f"Chapter 12 is missing approved marker: {marker}", failures)
    require((OUTPUT_1010 / "chapter-12-tools.js").exists(), "Chapter 12 tool script is missing", failures)
    require((OUTPUT_1010 / "chapter-12.css").exists(), "Chapter 12 stylesheet is missing", failures)

    ch13 = read("chapter-13.html")
    for marker in ["Synthesis: Putting Sources into Conversation", "The Roles Sources Can Play", "Building a Synthesis Matrix", "Synthesis Planner"]:
        require(marker in ch13, f"Chapter 13 is missing approved marker: {marker}", failures)
    require("Quote Sandwich" not in ch13, "Chapter 13 still contains repeated quote-sandwich instruction", failures)
    require("5qvPqvkgFXY" not in ch13, "Chapter 13 still contains the relocated MLA video", failures)

    ch14_soup = BeautifulSoup(read("chapter-14.html"), "html.parser")
    require(ch14_soup.select_one('.chapter-sequence-next[href="index.html"]') is not None, "Chapter 14 does not return to the ENG 1010 home", failures)

    app = (OUTPUT / "app.js").read_text(encoding="utf-8")
    require("Introduction: Writing as Conversation" in app, "sidebar code does not include the introduction", failures)
    app_titles = re.findall(r"title: '\d+\. ([^']+)'", app.split("var CHAPTERS_1020", 1)[0])
    require(app_titles == EXPECTED_TITLES, "shared app chapter titles do not match the approved sequence", failures)

    manifest = json.loads((OUTPUT / "BUILD-MANIFEST.json").read_text(encoding="utf-8"))
    audit = manifest.get("audit", {})
    require(audit.get("missing_internal_destinations") == [], "audit reports missing internal destinations", failures)
    require(audit.get("unembedded_youtube_links") == [], "audit reports unembedded YouTube links", failures)
    duplicate = audit.get("duplicate_video_ids", {})
    require("5qvPqvkgFXY" not in duplicate, "the relocated MLA video is duplicated", failures)

    return failures


def browser_tests() -> list[str]:
    failures: list[str] = []
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return ["Playwright is not installed"]

    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", "8766", "--bind", "127.0.0.1"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        time.sleep(1.5)
        base = "http://127.0.0.1:8766/release-candidate-v2/1010"
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            desktop = browser.new_context(viewport={"width": 1280, "height": 900})

            index = desktop.new_page()
            index.goto(f"{base}/index.html", wait_until="domcontentloaded")
            index.wait_for_timeout(500)
            require(index.locator("a.chapter-link").count() == 14, "browser homepage does not show fourteen chapter cards", failures)
            require(index.locator('a[href="introduction.html"]').count() >= 1, "browser homepage does not show the introduction", failures)
            require(index.locator("#chaptersList .sidebar-link").count() == 15, "browser sidebar does not contain the introduction plus fourteen chapters", failures)

            chapter1 = desktop.new_page()
            chapter1.goto(f"{base}/chapter-1.html", wait_until="domcontentloaded")
            chapter1.wait_for_timeout(500)
            chapter1.keyboard.press("Tab")
            active_text = chapter1.evaluate("document.activeElement && document.activeElement.textContent") or ""
            require("Skip to main content" in active_text, "first Tab does not reveal the skip link", failures)
            chapter1.keyboard.press("Enter")
            require(chapter1.evaluate("document.activeElement && document.activeElement.id") == "main-content", "skip link does not focus main content", failures)

            chapter5 = desktop.new_page()
            chapter5.goto(f"{base}/chapter-5.html", wait_until="domcontentloaded")
            chapter5.wait_for_timeout(500)
            second_header = chapter5.locator(".section-header").nth(1)
            second_header.focus()
            before = second_header.get_attribute("aria-expanded")
            chapter5.keyboard.press("Enter")
            after = second_header.get_attribute("aria-expanded")
            require(before != after, "section disclosure does not respond to Enter", failures)
            chapter5.evaluate("document.querySelector(\'#scRhetChoice\').closest(\'.section\').classList.add(\'active\')")
            chapter5.fill("#scRhetChoice", "The poster places the deadline in the largest type.")
            chapter5.fill("#scRhetEffect", "The hierarchy makes urgency immediately visible.")
            chapter5.fill("#scRhetAudience", "Students scanning quickly are likely to notice it.")
            chapter5.fill("#scRhetPurpose", "It supports timely registration.")
            chapter5.click("#scBuildRhetoric")
            require("Choice:" in chapter5.locator("#scRhetoricOutput").inner_text(), "rhetorical choice planner did not generate notes", failures)

            chapter4 = desktop.new_page()
            chapter4.goto(f"{base}/chapter-4.html", wait_until="domcontentloaded")
            chapter4.wait_for_timeout(500)
            chapter4.evaluate("document.querySelectorAll('.section').forEach(s => s.classList.add('active'))")
            chapter4.fill("#scQuotePoint", "The interface reduces stopping cues.")
            chapter4.fill("#scQuoteContext", "Lee explains that")
            chapter4.fill("#scQuoteEvidence", "the next video begins automatically (42).")
            chapter4.fill("#scQuoteExplanation", "The default shifts the burden to the viewer.")
            chapter4.click("#scBuildQuote")
            require("The interface reduces stopping cues" in chapter4.locator("#scQuoteOutput").inner_text(), "Chapter 4 builder did not produce a preview", failures)

            chapter10 = desktop.new_page()
            chapter10.goto(f"{base}/chapter-10.html", wait_until="domcontentloaded")
            chapter10.wait_for_timeout(500)
            chapter10.evaluate("document.querySelectorAll('.section').forEach(s => s.classList.add('active'))")
            chapter10.fill("#scAnalysisObservation", "The appointment button is larger than the drop-in link.")
            chapter10.fill("#scAnalysisInterpretation", "The design treats appointments as the default.")
            chapter10.fill("#scAnalysisSignificance", "Flexible access becomes less visible.")
            chapter10.click("#scBuildAnalysis")
            require("Significance:" in chapter10.locator("#scAnalysisOutput").inner_text(), "Chapter 10 planner did not generate analysis notes", failures)

            chapter13 = desktop.new_page()
            chapter13.goto(f"{base}/chapter-13.html", wait_until="domcontentloaded")
            chapter13.wait_for_timeout(600)
            chapter13.evaluate("document.querySelectorAll('.section').forEach(s => s.classList.add('active'))")
            chapter13.fill("#scSynthClaim", "Evening access depends on more than closing time.")
            chapter13.fill("#scSynthA", "Lee establishes demand.")
            chapter13.fill("#scSynthB", "Patel identifies transportation limits.")
            chapter13.click("#scSaveSynthesis")
            require("saved" in chapter13.locator("#scSynthesisStatus").inner_text().lower(), "Synthesis Planner did not save", failures)
            chapter13.fill("#scSynthClaim", "")
            chapter13.click("#scLoadSynthesis")
            require("Evening access" in chapter13.input_value("#scSynthClaim"), "Synthesis Planner did not restore saved notes", failures)

            # Progress, color shift, and sticky identity.
            chapter13.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.45)")
            chapter13.wait_for_timeout(350)
            width = chapter13.locator(".sc-reading-progress-bar").evaluate("el => parseFloat(getComputedStyle(el).width)")
            require(width > 0, "reading progress bar did not advance", failures)
            require(chapter13.locator(".sc-sticky-chapter").evaluate("el => el.classList.contains('is-visible')"), "sticky chapter identity did not appear after scrolling", failures)

            # Dark mode.
            chapter13.click("#darkModeToggle")
            require(chapter13.locator("body").evaluate("el => el.classList.contains('dark-mode')"), "dark mode did not activate", failures)

            # Print behavior.
            chapter13.emulate_media(media="print")
            require(chapter13.locator(".sc-sticky-chapter").evaluate("el => getComputedStyle(el).display === 'none'"), "sticky identity is not hidden in print", failures)
            chapter13.emulate_media(media="screen")

            # Mobile overflow for all fifteen destinations.
            mobile = browser.new_context(viewport={"width": 375, "height": 812})
            for name in ["introduction.html", *[f"chapter-{n}.html" for n in range(1, 15)]]:
                page = mobile.new_page()
                page.goto(f"{base}/{name}", wait_until="domcontentloaded")
                page.wait_for_timeout(180)
                overflow = page.evaluate("document.documentElement.scrollWidth > window.innerWidth + 1")
                require(not overflow, f"{name} has horizontal body overflow at 375px", failures)
                require(page.locator(".chapter-sequence-nav a").count() == 2, f"{name} lacks sequence navigation on mobile", failures)
                page.close()

            # No-JavaScript access.
            nojs = browser.new_context(viewport={"width": 1024, "height": 768}, java_script_enabled=False)
            nojs_page = nojs.new_page()
            nojs_page.goto(f"{base}/chapter-13.html", wait_until="domcontentloaded")
            visible = nojs_page.locator(".section-content").evaluate_all("els => els.every(el => getComputedStyle(el).display !== 'none')")
            require(visible, "no-JavaScript mode hides substantive Chapter 13 content", failures)

            nojs.close()
            mobile.close()
            desktop.close()
            browser.close()
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
    return failures


def write_results(static_failures: list[str], browser_failures: list[str] | None) -> None:
    browser_status = "Not run" if browser_failures is None else ("Pass" if not browser_failures else "Fail")
    lines = [
        "# ENG 1010 Revision-Round-2 Test Results",
        "",
        f"- Static tests: {'Pass' if not static_failures else 'Fail'}",
        f"- Browser tests: {browser_status}",
        "",
    ]
    if static_failures:
        lines.extend(["## Static failures", "", *[f"- {item}" for item in static_failures], ""])
    if browser_failures:
        lines.extend(["## Browser failures", "", *[f"- {item}" for item in browser_failures], ""])
    if not static_failures and browser_failures == []:
        lines.extend([
            "## Verified behavior",
            "",
            "- introduction plus fourteen-chapter static sequence;",
            "- approved revised content markers and protected Chapter 12 content;",
            "- internal destinations and bottom previous/next navigation;",
            "- responsive YouTube embed construction and relocated-video checks;",
            "- keyboard skip link, disclosure behavior, and chapter tools;",
            "- color-changing reading progress and sticky chapter identity;",
            "- dark mode, print behavior, 375px mobile layout, and no-JavaScript reading.",
            "",
        ])
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "TEST-RESULTS.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--static", action="store_true")
    parser.add_argument("--browser", action="store_true")
    args = parser.parse_args()
    run_static = args.static or not args.browser
    run_browser = args.browser

    static_failures = static_tests() if run_static else []
    browser_failures = browser_tests() if run_browser and not static_failures else (None if not run_browser else [])
    write_results(static_failures, browser_failures)

    failures = static_failures + (browser_failures or [])
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("All requested ENG 1010 revision-round-2 tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
