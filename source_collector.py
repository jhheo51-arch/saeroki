"""공개 웹페이지의 기본 메타데이터를 후보로 바꾸는 최소 수집기."""

from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class PublicMetadata:
    url: str
    title: str
    description: str | None = None
    published_at: str | None = None


class _MetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title_parts: list[str] = []
        self.meta: dict[str, str] = {}
        self.in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "title":
            self.in_title = True
        if tag == "meta":
            key = attributes.get("property") or attributes.get("name")
            value = attributes.get("content")
            if key and value:
                self.meta[key.casefold()] = value.strip()

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data.strip())


def parse_public_metadata(url: str, html: str) -> PublicMetadata:
    parser = _MetadataParser()
    parser.feed(html)
    title = parser.meta.get("og:title") or " ".join(
        part for part in parser.title_parts if part
    )
    description = parser.meta.get("og:description") or parser.meta.get("description")
    published_at = (
        parser.meta.get("article:published_time")
        or parser.meta.get("date")
        or parser.meta.get("pubdate")
    )
    return PublicMetadata(
        url=url,
        title=title.strip(),
        description=description,
        published_at=published_at,
    )


def fetch_public_metadata(url: str, timeout: int = 10) -> PublicMetadata:
    request = Request(url, headers={"User-Agent": "Saeroki/0.1 public metadata check"})
    with urlopen(request, timeout=timeout) as response:
        html = response.read().decode(response.headers.get_content_charset() or "utf-8", "replace")
    return parse_public_metadata(url, html)
