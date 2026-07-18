#!/usr/bin/env python3
"""Normalize legacy chapter resource/video markup before review patching."""

from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
COURSE = ROOT / "release-candidate-v2" / "1010"


def save(path: Path, soup: BeautifulSoup) -> None:
    path.write_text(soup.decode(formatter="minimal"), encoding="utf-8")


# Chapter 2: normalize the bare resource URL and preserve the video while
# removing the staging language wrapped around it.
path = COURSE / "chapter-2.html"
soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
for paragraph in soup.find_all("p"):
    text = paragraph.get_text(" ", strip=True)
    if "human.libretexts.org" in text and text.startswith("Resource:"):
        url = text.split("Resource:", 1)[1].strip()
        paragraph.clear()
        anchor = soup.new_tag("a", href=url)
        anchor.string = url
        paragraph.append(anchor)
        break

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
save(path, soup)


# Chapter 4: the relocated MLA video is also nested in a paragraph containing
# an internal audit note. Extract the player before removing that note.
path = COURSE / "chapter-4.html"
soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
heading = soup.find(
    "h3",
    string=lambda value: value and "MLA In-Text Citation" in value,
)
iframe = soup.find("iframe", src=lambda value: value and "5qvPqvkgFXY" in value)
if heading is None or iframe is None:
    raise RuntimeError("Could not locate Chapter 4 MLA video resource")
wrapper = iframe.find_parent(class_="sc-video-embed")
wrapper.extract()
for paragraph in list(soup.find_all("p")):
    text = paragraph.get_text(" ", strip=True)
    if (
        "The video previously located in Chapter 13" in text
        or "The revised HTML chapter will use a responsive embed" in text
    ):
        paragraph.decompose()
heading.insert_after(wrapper)
save(path, soup)

print("Normalized legacy Chapter 2 and Chapter 4 resource markup")
