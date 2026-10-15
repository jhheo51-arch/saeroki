"""공개 웹페이지의 기본 메타데이터를 후보로 바꾸는 최소 수집기."""

from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from datetime import datetime, timezone
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from saeroki import Candidate


@dataclass(frozen=True)
class PublicMetadata:
    url: str
    title: str
    description: str | None = None
    published_at: str | None = None


@dataclass(frozen=True)
class PublicLink:
    url: str
    title: str


def parse_rss(xml_text: str, source_name: str, category: str, checked_at: str) -> list[Candidate]:
    """RSS 2.0 또는 Atom의 글 항목을 후보로 바꿉니다."""
    root = ET.fromstring(xml_text)
    candidates: list[Candidate] = []
    for index, item in enumerate(root.iter()):
        if item.tag.rsplit("}", 1)[-1] not in {"item", "entry"}:
            continue
        values: dict[str, str] = {}
        for child in item:
            key = child.tag.rsplit("}", 1)[-1]
            text = (child.text or "").strip()
            if key == "link" and not text:
                text = str(child.attrib.get("href") or "").strip()
            if text and key not in values:
                values[key] = text
        url = values.get("link") or values.get("id")
        title = values.get("title")
        if not url or not title or not url.startswith(("http://", "https://")):
            continue
        content_type = "newsletter" if "뉴스레터" in category else "technology_blog" if "기술" in category or "블로그" in category else None
        candidates.append(Candidate(
            id=f"rss-{index + 1}", title=title, url=url.split("#", 1)[0], tags=[category],
            source=source_name, checked_at=checked_at,
            published_at=values.get("pubDate") or values.get("published") or values.get("updated"),
            content_type=content_type,
        ))
    return candidates


def fetch_rss(url: str, source_name: str, category: str, timeout: int = 10) -> list[Candidate]:
    request = Request(url, headers={"User-Agent": "Saeroki/0.1 RSS check"})
    with urlopen(request, timeout=timeout) as response:
        xml_text = response.read().decode(response.headers.get_content_charset() or "utf-8", "replace")
    return parse_rss(xml_text, source_name, category, datetime.now(timezone.utc).isoformat())


def content_type_for_record(record: dict[str, object]) -> str | None:
    explicit = record.get("content_type")
    if isinstance(explicit, str) and explicit:
        return explicit
    category = str(record.get("category") or "").casefold()
    if "뉴스레터" in category:
        return "newsletter"
    if "기술" in category or "블로그" in category:
        return "technology_blog"
    return None


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


class _LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, list[str]]] = []
        self.current_href: str | None = None
        self.current_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            self.current_href = dict(attrs).get("href")
            self.current_text = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self.current_href:
            title = " ".join(part for part in self.current_text if part).strip()
            if title:
                self.links.append((self.current_href, title))
            self.current_href = None
            self.current_text = []

    def handle_data(self, data: str) -> None:
        if self.current_href:
            self.current_text.append(data.strip())


_NON_CONTENT_LINK_TITLES = {
    "뉴닉",
    "뉴닉 소개",
    "뉴스레터 구독",
    "광고제휴",
    "채용",
    "서비스 이용약관",
    "개인정보처리방침",
    "고객센터",
    "slack에 추가",
}


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


def fetch_public_links(url: str, timeout: int = 10) -> list[PublicLink]:
    request = Request(url, headers={"User-Agent": "Saeroki/0.1 public list check"})
    with urlopen(request, timeout=timeout) as response:
        html = response.read().decode(response.headers.get_content_charset() or "utf-8", "replace")
    parser = _LinkParser()
    parser.feed(html)
    base_host = urlparse(url).netloc
    seen: set[str] = set()
    links: list[PublicLink] = []
    for href, title in parser.links:
        absolute = urljoin(url, href).split("#", 1)[0]
        if urlparse(absolute).scheme not in {"http", "https"}:
            continue
        if urlparse(absolute).netloc != base_host or absolute in seen:
            continue
        if title.casefold() in _NON_CONTENT_LINK_TITLES:
            continue
        seen.add(absolute)
        links.append(PublicLink(absolute, title))
    return links


def fetch_public_json(url: str, timeout: int = 10) -> object:
    request = Request(url, headers={"User-Agent": "Saeroki/0.1 public JSON check"})
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode(response.headers.get_content_charset() or "utf-8"))


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
            if record.get("collection_mode") == "rss":
                candidates.extend(fetch_rss(url, str(record.get("name") or url), str(record.get("category") or "미분류"), timeout))
                continue
            if record.get("collection_mode") == "json_articles":
                api_url = record.get("api_url")
                if not isinstance(api_url, str):
                    raise ValueError("api_url이 없습니다")
                payload = fetch_public_json(api_url, timeout=timeout)
                articles = payload.get("articles", []) if isinstance(payload, dict) else []
                for article in articles:
                    if not isinstance(article, dict) or not article.get("id"):
                        continue
                    meta = article.get("meta") if isinstance(article.get("meta"), dict) else {}
                    author_info = meta.get("user") if isinstance(meta.get("user"), dict) else {}
                    candidates.append(
                        Candidate(
                            id=f"newneek-{article['id']}",
                            title=str(article.get("title") or article.get("headline") or "제목 없음"),
                            url=f"https://newneek.co/@newneek/article/{article['id']}",
                            tags=[str(record.get("category") or "뉴스레터")],
                            source=str(record.get("name") or "뉴닉"),
                            checked_at=checked_at,
                            popularity=meta.get("countReads") if isinstance(meta.get("countReads"), int) else None,
                            author=str(author_info.get("name")) if author_info.get("name") else None,
                            published_at=str(article.get("dtPublished")) if article.get("dtPublished") else None,
                            content_type=content_type_for_record(record),
                        )
                    )
                continue
            if record.get("collection_mode") == "public_list":
                links = fetch_public_links(url, timeout=timeout)
                for link_index, link in enumerate(links):
                    candidates.append(
                        Candidate(
                            id=f"source-{index + 1}-{link_index + 1}",
                            title=link.title,
                            url=link.url,
                            tags=[str(record.get("category") or "미분류")],
                            source=str(record.get("name") or url),
                            checked_at=checked_at,
                            content_type=content_type_for_record(record),
                        )
                    )
                continue
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
                content_type=content_type_for_record(record),
            )
        )
    return candidates, errors
