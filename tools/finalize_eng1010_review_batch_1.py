#!/usr/bin/env python3
"""Restore shared shell identifiers after applying HTML review batch 1."""

from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
COURSE = ROOT / "release-candidate-v2" / "1010"

for path in [
    COURSE / "index.html",
    COURSE / "introduction.html",
    *[COURSE / f"chapter-{number}.html" for number in range(1, 15)],
]:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    bar = soup.select_one(".sc-reading-progress-bar")
    if bar is None:
        raise RuntimeError(f"Reading progress bar missing from {path.name}")
    bar["id"] = "scrollProgress"
    path.write_text(soup.decode(formatter="minimal"), encoding="utf-8")

print("Restored shared reading-progress identifiers")
