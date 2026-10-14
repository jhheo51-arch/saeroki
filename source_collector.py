"""공개 웹페이지의 기본 메타데이터를 후보로 바꾸는 최소 수집기."""

from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.request import Request, urlopen

from saeroki import Candidate


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


def load_source_records(path: str | Path) -> list[dict[str, object]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("출처 파일의 최상위 값은 목록이어야 합니다")
    return data


def collect_confirmed_sources(
    records: list[dict[str, object]],
    timeout: int = 10,
) -> tuple[list[Candidate], list[dict[str, str]]]:
    """공개 확인 상태인 출처의 메타데이터만 후보로 변환합니다."""
    candidates: list[Candidate] = []
    errors: list[dict[str, str]] = []
    checked_at = datetime.now(timezone.utc).isoformat()
    for index, record in enumerate(records):
        url = record.get("url")
        status = str(record.get("status") or record.get("access_status") or "")
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            continue
        if status != "confirmed_public":
            continue
        try:
            metadata = fetch_public_metadata(url, timeout=timeout)
        except Exception as error:  # noqa: BLE001
            errors.append({"url": url, "error": str(error)})
            continue
        title = metadata.title or str(record.get("name") or url)
        source_name = str(record.get("name") or url)
        tags = [str(record.get("category") or "미분류")]
        candidates.append(
            Candidate(
                id=f"source-{index + 1}",
                title=title,
                url=metadata.url,
                tags=tags,
                source=source_name,
                checked_at=checked_at,
                published_at=metadata.published_at,
            )
        )
    return candidates, errors
