#!/usr/bin/env python3
"""Regression tests for ENG 1010 HTML review batch 1."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "release-candidate-v2"
COURSE = OUTPUT / "1010"


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def chapter_text(number: int) -> str:
    return (COURSE / f"chapter-{number}.html").read_text(encoding="utf-8")


def static_tests() -> list[str]:
    failures: list[str] = []

    chapter2 = chapter_text(2)
    require(
        "View the Detailed Annotation Example on LibreTexts" in chapter2,
        "Chapter 2 lacks the LibreTexts resource button",
        failures,
    )
    require(
        "The current chapter includes the video" not in chapter2,
        "Chapter 2 still contains the internal video introduction",
        failures,
    )
    require(
        "The video will be included only after" not in chapter2,
        "Chapter 2 still contains the video-audit note",
        failures,
    )

    chapter3 = chapter_text(3)
    for phrase in [
        "Mollie Chambers and her coauthors",
        "Chambers and her coauthors",
        "Chambers et al.",
    ]:
        require(phrase not in chapter3, f"Chapter 3 still contains: {phrase}", failures)
    require(
        "fictional practice article by Jordan Lee" in chapter3,
        "Chapter 3 does not identify the replacement example as fictional practice material",
        failures,
    )

    chapter4 = chapter_text(4)
    for phrase in [
        "Original Scholar’s Compass practice passage",
        "Original Scholar’s Compass practice source",
        "The revised HTML chapter will use a responsive embed",
        "From the following original Scholar’s Compass practice sentence",
    ]:
        require(phrase not in chapter4, f"Chapter 4 still contains: {phrase}", failures)
    require(
        "Here is a practice sentence. Select only the words needed" in chapter4,
        "Chapter 4 lacks the revised practice-sentence direction",
        failures,
    )

    require(
        "https://openoregon.pressbooks.pub/wrd/chapter/strategies-for-getting-started/"
        in chapter_text(7),
        "Chapter 7 does not use the updated Open Oregon destination",
        failures,
    )
    require(
        "https://openoregon.pressbooks.pub/wrd/chapter/writing-paragraphs/"
        in chapter_text(9),
        "Chapter 9 does not use the updated Open Oregon destination",
        failures,
    )

    chapter10 = chapter_text(10)
    require(
        "Bloom's Taxonomy Visualizer" in chapter10,
        "Chapter 10 lacks the Bloom's Taxonomy visualizer",
        failures,
    )
    require(
        "The current Scholar’s Compass chapter uses a building-block analogy." not in chapter10,
        "Chapter 10 still contains the internal reminder phrasing",
        failures,
    )

    chapter11 = chapter_text(11)
    soup11 = BeautifulSoup(chapter11, "html.parser")
    require(
        not soup11.select(".citation-adapted"),
        "Chapter 11 still contains repeated attribution boxes",
        failures,
    )
    require(
        len(soup11.select(".sc-consolidated-attribution")) == 1,
        "Chapter 11 does not contain exactly one consolidated attribution",
        failures,
    )

    intro = BeautifulSoup(
        (COURSE / "introduction.html").read_text(encoding="utf-8"), "html.parser"
    )
    require(intro.select_one(".header h1") is not None, "Introduction heading missing", failures)

    for name in ["index.html", "introduction.html", *[f"chapter-{n}.html" for n in range(1, 15)]]:
        page = BeautifulSoup((COURSE / name).read_text(encoding="utf-8"), "html.parser")
        require(
            page.select_one(".sc-reading-progress .sc-reading-progress-bar") is not None,
            f"{name} lacks the shared reading-progress component",
            failures,
        )

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
        time.sleep(1.25)
        base = "http://127.0.0.1:8766/release-candidate-v2/1010"
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            desktop = browser.new_context(viewport={"width": 1280, "height": 900})

            progress_page = desktop.new_page()
            progress_page.goto(f"{base}/chapter-3.html", wait_until="networkidle")
            progress_page.evaluate(
                "window.scrollTo(0, (document.scrollingElement.scrollHeight - innerHeight) * .55)"
            )
            progress_page.wait_for_timeout(300)
            aria_value = int(
                progress_page.locator(".sc-reading-progress").get_attribute("aria-valuenow")
                or "0"
            )
            transform = progress_page.locator(".sc-reading-progress-bar").evaluate(
                "el => getComputedStyle(el).transform"
            )
            require(aria_value > 20, "Desktop reading progress did not advance", failures)
            require(transform != "none", "Desktop progress bar lacks a transform", failures)

            intro_page = desktop.new_page()
            intro_page.goto(f"{base}/introduction.html", wait_until="networkidle")
            chapter_page = desktop.new_page()
            chapter_page.goto(f"{base}/chapter-1.html", wait_until="networkidle")
            intro_color = intro_page.locator(".header h1").evaluate(
                "el => getComputedStyle(el).color"
            )
            chapter_color = chapter_page.locator(".header h1").evaluate(
                "el => getComputedStyle(el).color"
            )
            require(
                intro_color == chapter_color,
                f"Introduction heading color {intro_color} differs from chapter heading {chapter_color}",
                failures,
            )

            bloom_page = desktop.new_page()
            bloom_page.goto(f"{base}/chapter-10.html", wait_until="networkidle")
            bloom_page.locator(".blooms-container").evaluate(
                "el => el.closest('.section').classList.add('active')"
            )
            before = bloom_page.locator("#bloomsDetails").inner_text()
            bloom_page.locator(".blooms-level").first.click()
            after = bloom_page.locator("#bloomsDetails").inner_text()
            require(after != before, "Bloom visualizer did not respond to selection", failures)

            mobile = browser.new_context(viewport={"width": 375, "height": 812})
            mobile_page = mobile.new_page()
            mobile_page.goto(f"{base}/chapter-4.html", wait_until="networkidle")
            mobile_page.evaluate("window.scrollTo(0, 1000)")
            mobile_page.wait_for_timeout(300)
            sticky = mobile_page.locator(".sc-sticky-chapter")
            require(
                sticky.evaluate("el => el.classList.contains('is-visible')"),
                "Mobile sticky chapter title did not appear",
                failures,
            )
            font_size = float(
                sticky.evaluate("el => parseFloat(getComputedStyle(el).fontSize)")
            )
            require(
                font_size <= 12,
                f"Mobile sticky chapter title remains too large: {font_size}px",
                failures,
            )

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


def main() -> int:
    failures = static_tests()
    failures.extend(browser_tests())
    if failures:
        print("ENG 1010 HTML review batch 1: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("ENG 1010 HTML review batch 1: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
