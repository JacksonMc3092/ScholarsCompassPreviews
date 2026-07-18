#!/usr/bin/env python3
"""Normalize legacy Chapter 2 resource and video markup before review patching."""

from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "release-candidate-v2" / "1010" / "chapter-2.html"

soup = BeautifulSoup(PATH.read_text(encoding="utf-8"), "html.parser")

# Convert the bare resource URL paragraph into a simple link so the main patcher
# can replace it with the final accessible button.
for paragraph in soup.find_all("p"):
    text = paragraph.get_text(" ", strip=True)
    if "human.libretexts.org" in text and text.startswith("Resource:"):
        url = text.split("Resource:", 1)[1].strip()
        paragraph.clear()
        anchor = soup.new_tag("a", href=url)
        anchor.string = url
        paragraph.append(anchor)
        break

# The generated legacy markup nests the video wrapper and the audit note inside
# one paragraph. Extract the wrapper, remove both staging paragraphs, and place
# the preserved player directly after the Video resource heading.
heading = soup.find("h3", string=lambda value: value and value.strip() == "Video resource")
iframe = soup.find("iframe", src=lambda value: value and "gXRwTI7Dv3s" in value)
if heading is None or iframe is None:
    raise RuntimeError("Could not locate Chapter 2 video resource")
wrapper = iframe.find_parent(class_="sc-video-embed")
wrapper.extract()
for paragraph in list(soup.find_all("p")):
    text = paragraph.get_text(" ", strip=True)
    if (
        "The current chapter includes the video" in text
        or "The video will be included only after it is verified" in text
    ):
        paragraph.decompose()
heading.insert_after(wrapper)

PATH.write_text(soup.decode(formatter="minimal"), encoding="utf-8")
print("Normalized Chapter 2 legacy resource markup")
