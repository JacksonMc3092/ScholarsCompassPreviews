#!/usr/bin/env python3
"""Static and browser smoke tests for the ENG 1010 release candidate."""

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
OUTPUT = ROOT / "release-candidate"
OUTPUT_1010 = OUTPUT / "1010"
EXPECTED_TITLES = [
    "Annotating Your Way to Greatness",
    "Active Reading Strategies",
    "Summarizing Your Way to Synthesis",
    "Quoting, Paraphrasing, and Signal Phrases",
    "Understanding Rhetoric: The Art of Persuasion",
    "Values, Assumptions, and Ideology",
    "Strategies for Getting Started",
    "Crafting Powerful Thesis Statements",
    "Designing Effective Paragraphs",
    "Analysis and Synthesis",
    "Argumentation: Joining the Academic Conversation",
    "Finding and Evaluating Sources",
    "Using Sources in Your Argument",
    "Revision: From Draft to Final",
]


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def static_tests() -> list[str]:
    failures: list[str] = []
    require(OUTPUT.exists(), "release-candidate directory is missing", failures)
    require((OUTPUT / "BUILD-MANIFEST.json").exists(), "build manifest is missing", failures)
    require((OUTPUT_1010 / "index.html").exists(), "ENG 1010 release-candidate index is missing", failures)

    pages = [OUTPUT_1010 / f"chapter-{number}.html" for number in range(1, 15)]
    for page in pages:
        require(page.exists(), f"missing {page.name}", failures)

    if failures:
        return failures

    soup = BeautifulSoup((OUTPUT_1010 / "index.html").read_text(encoding="utf-8"), "html.parser")
    links = soup.select("a.chapter-link[href]")
    hrefs = [link.get("href") for link in links]
    require(hrefs == [f"chapter-{n}.html" for n in range(1, 15)], "homepage chapter links are not in final static order", failures)
    numbers = [link.select_one(".card-number").get_text(strip=True) for link in links]
    require(numbers == [str(n) for n in range(1, 15)], "homepage card numbers are not sequential", failures)
    data_numbers = [link.get("data-chapter") for link in links]
    require(data_numbers == [str(n) for n in range(1, 15)], "homepage data-chapter values are not sequential", failures)

    visible_titles = [link.select_one(".chapter-title").get_text(" ", strip=True) for link in links]
    require(visible_titles == EXPECTED_TITLES, "homepage chapter titles do not match the approved sequence", failures)

    existing = {page.name for page in pages}
    for number, page in enumerate(pages, start=1):
        text = page.read_text(encoding="utf-8")
        page_soup = BeautifulSoup(text, "html.parser")
        body = page_soup.body
        require(body is not None, f"{page.name} has no body", failures)
        if body is not None:
            require(body.get("data-page") == f"chapter-{number}", f"{page.name} has incorrect data-page", failures)
            require(body.get("data-course") == "1010", f"{page.name} lacks explicit ENG 1010 course identity", failures)
        require(page_soup.select_one(".header h1") is not None or page_soup.find("h1") is not None, f"{page.name} has no chapter heading", failures)
        require(page_soup.select_one("#chaptersList") is not None, f"{page.name} lacks shared chapter navigation target", failures)
        require(page_soup.select_one("#hamburgerMenu") is not None, f"{page.name} lacks hamburger control", failures)
        require(page_soup.select_one("#darkModeToggle") is not None, f"{page.name} lacks theme control", failures)
        require(page_soup.select_one("#backToTop") is not None, f"{page.name} lacks back-to-top control", failures)
        require(page_soup.select_one(".section") is not None, f"{page.name} has no instructional sections", failures)
        require("../app.js?v=21-rc1" in text, f"{page.name} does not load the release-candidate shared script", failures)

        for match in re.finditer(r"chapter-(\d+)\.html", text, re.IGNORECASE):
            target = f"chapter-{int(match.group(1))}.html"
            require(target in existing, f"{page.name} links to missing {target}", failures)

    active_reading = (OUTPUT_1010 / "chapter-2.html").read_text(encoding="utf-8")
    require("IV. Adapting Strategies for Digital vs. Print Reading" in active_reading, "Active Reading section IV was not normalized", failures)
    require("V. Practice Exercises" in active_reading, "Active Reading final visible section was not normalized", failures)
    require("VI. Practice Exercises" not in active_reading, "Active Reading still contains the old visible Section VI label", failures)

    chapter12 = (OUTPUT_1010 / "chapter-12.html").read_text(encoding="utf-8")
    for marker in [
        "The Three-Lane Search Method",
        "Peer-Reviewed Sources",
        "Popular Sources",
        "Trade or Professional Sources",
        "How the Rhetorical Appeals Appear Across Source Types",
        "Keyword Builder",
        "Source Log",
    ]:
        require(marker in chapter12, f"Chapter 12 is missing approved content marker: {marker}", failures)
    require("chapter-12-tools.js?v=2-rc1" in chapter12, "Chapter 12 tool script is not loaded", failures)
    require((OUTPUT_1010 / "chapter-12-tools.js").exists(), "Chapter 12 tool script is missing", failures)
    require((OUTPUT_1010 / "chapter-12.css").exists(), "Chapter 12 scoped stylesheet is missing", failures)

    app = (OUTPUT / "app.js").read_text(encoding="utf-8")
    app_hrefs = re.findall(r"href: 'chapter-(\d+)\.html'", app.split("var CHAPTERS_1020", 1)[0])
    require(app_hrefs == [str(n) for n in range(1, 15)], "shared navigation array does not use final sequential filenames", failures)
    require("stabilization-0.2.css?v=7" in app, "shared stabilization cache version was not updated", failures)
    require("interactive-tools.js?v=2" in app, "shared interactive-tools cache version was not updated", failures)

    manifest = json.loads((OUTPUT / "BUILD-MANIFEST.json").read_text(encoding="utf-8"))
    require(manifest.get("internal_destination_problems") == [], "build manifest reports internal destination problems", failures)
    require(len(manifest.get("source_sha256", {})) == 14, "build manifest does not record all protected source chapter hashes", failures)

    return failures


def browser_tests() -> list[str]:
    failures: list[str] = []
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return ["Playwright is not installed"]

    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", "8765", "--bind", "127.0.0.1"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        time.sleep(1.5)
        base = "http://127.0.0.1:8765/release-candidate/1010"
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)

            desktop = browser.new_context(viewport={"width": 1280, "height": 900})
            page = desktop.new_page()
            page.goto(f"{base}/index.html", wait_until="domcontentloaded")
            page.wait_for_timeout(700)
            hrefs = page.locator("a.chapter-link").evaluate_all("els => els.map(e => e.getAttribute('href'))")
            require(hrefs == [f"chapter-{n}.html" for n in range(1, 15)], "browser homepage order does not match final sequence", failures)
            sidebar_text = page.locator("#chaptersList .sidebar-link").all_inner_texts()
            require(len(sidebar_text) == 14, "browser sidebar does not contain fourteen chapters", failures)

            # Keyboard navigation and disclosure behavior.
            chapter1 = desktop.new_page()
            chapter1.goto(f"{base}/chapter-1.html", wait_until="domcontentloaded")
            chapter1.wait_for_timeout(500)
            chapter1.keyboard.press("Tab")
            active_text = chapter1.evaluate("document.activeElement && document.activeElement.textContent") or ""
            require("Skip to main content" in active_text, "first Tab does not reveal the skip link", failures)
            chapter1.keyboard.press("Enter")
            focused_id = chapter1.evaluate("document.activeElement && document.activeElement.id")
            require(focused_id == "main-content", "skip link did not move focus to main content", failures)

            chapter2 = desktop.new_page()
            chapter2.goto(f"{base}/chapter-2.html", wait_until="domcontentloaded")
            chapter2.wait_for_timeout(500)
            second_header = chapter2.locator(".section-header").nth(1)
            second_header.focus()
            before = second_header.get_attribute("aria-expanded")
            chapter2.keyboard.press("Enter")
            after = second_header.get_attribute("aria-expanded")
            require(before != after, "section disclosure did not respond to Enter", failures)

            hamburger = chapter2.locator("#hamburgerMenu")
            hamburger.click()
            require(chapter2.locator("#sidebar").evaluate("el => el.classList.contains('active')"), "sidebar did not open", failures)
            chapter2.keyboard.press("Escape")
            require(not chapter2.locator("#sidebar").evaluate("el => el.classList.contains('active')"), "sidebar did not close with Escape", failures)

            # Chapter 12 tools.
            ch12 = desktop.new_page()
            ch12.goto(f"{base}/chapter-12.html", wait_until="domcontentloaded")
            ch12.wait_for_timeout(700)
            ch12.evaluate("document.querySelectorAll(\'.section\').forEach(section => section.classList.add(\'active\'))")
            ch12.fill("#concept1", "short-form video")
            ch12.fill("#concept2", "sleep quality")
            ch12.click("#buildKeywords")
            require("AND" in ch12.locator("#keywordOutput").inner_text(), "Keyword Builder did not produce a search string", failures)
            ch12.evaluate("document.querySelector(\'#routeNeed\').closest(\'.section\').classList.add(\'active\')")
            ch12.select_option("#routeNeed", "scholarship")
            ch12.click("#chooseRoute")
            require("library database" in ch12.locator("#routeOutput").inner_text().lower(), "Route Chooser did not produce guidance", failures)
            ch12.fill("#logTitle", "Regression Test Source")
            ch12.fill("#logUse", "Test local save behavior")
            ch12.click("#saveSourceLog")
            require("saved" in ch12.locator("#sourceLogStatus").inner_text().lower(), "Source Log did not save", failures)
            ch12.click("#clearSourceLog")
            ch12.click("#loadSourceLog")
            # Clear intentionally removes the stored entry, so load should report none.
            require("no saved" in ch12.locator("#sourceLogStatus").inner_text().lower(), "Source Log clear/load behavior is inconsistent", failures)

            # Mobile overflow across the entire chapter set.
            mobile = browser.new_context(viewport={"width": 375, "height": 812})
            for number in range(1, 15):
                mobile_page = mobile.new_page()
                mobile_page.goto(f"{base}/chapter-{number}.html", wait_until="domcontentloaded")
                mobile_page.wait_for_timeout(250)
                overflow = mobile_page.evaluate("document.documentElement.scrollWidth > window.innerWidth + 1")
                require(not overflow, f"chapter-{number}.html has horizontal body overflow at 375px", failures)
                mobile_page.close()

            # No-JavaScript access and static order.
            nojs = browser.new_context(viewport={"width": 1024, "height": 768}, java_script_enabled=False)
            nojs_index = nojs.new_page()
            nojs_index.goto(f"{base}/index.html", wait_until="domcontentloaded")
            nojs_hrefs = nojs_index.locator("a.chapter-link").evaluate_all("els => els.map(e => e.getAttribute('href'))")
            require(nojs_hrefs == [f"chapter-{n}.html" for n in range(1, 15)], "no-JavaScript homepage order is incorrect", failures)
            nojs_ch12 = nojs.new_page()
            nojs_ch12.goto(f"{base}/chapter-12.html", wait_until="domcontentloaded")
            visible_content = nojs_ch12.locator(".section-content").count()
            require(visible_content >= 12, "no-JavaScript Chapter 12 does not retain all substantive sections", failures)

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
        "# ENG 1010 Release-Candidate Test Results",
        "",
        f"- Static tests: {'Pass' if not static_failures else 'Fail'}",
        f"- Browser tests: {browser_status}",
        "",
    ]
    if static_failures:
        lines.extend(["## Static failures", ""] + [f"- {item}" for item in static_failures] + [""])
    if browser_failures:
        lines.extend(["## Browser failures", ""] + [f"- {item}" for item in browser_failures] + [""])
    if not static_failures and browser_failures == []:
        lines.extend(
            [
                "## Verified behavior",
                "",
                "- final static homepage order and sequential filenames;",
                "- fourteen-page sidebar generation;",
                "- keyboard skip link, section disclosure, and sidebar Escape behavior;",
                "- Chapter 12 keyword, route, and source-log behavior;",
                "- mobile body-overflow checks at 375 pixels for all fourteen chapters;",
                "- no-JavaScript homepage order and Chapter 12 content access;",
                "- internal destination, asset, content-marker, and manifest checks.",
                "",
            ]
        )
    (OUTPUT / "TEST-RESULTS.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--static", action="store_true")
    parser.add_argument("--browser", action="store_true")
    args = parser.parse_args()

    run_static = args.static or not args.browser
    static_failures = static_tests() if run_static else []
    browser_failures = browser_tests() if args.browser else None
    write_results(static_failures, browser_failures)

    failures = list(static_failures)
    if browser_failures:
        failures.extend(browser_failures)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print("ENG 1010 release-candidate tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
