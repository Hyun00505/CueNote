"""
CueNote Core - Web Extractor
URL에서 텍스트와 이미지를 추출하는 모듈
"""
import re
from urllib.parse import urljoin, urlparse
from typing import Optional

import httpx
import trafilatura
from trafilatura.settings import use_config

from .config import logger

# trafilatura 설정
_traf_config = use_config()
_traf_config.set("DEFAULT", "MIN_OUTPUT_SIZE", "200")
_traf_config.set("DEFAULT", "MIN_EXTRACTED_SIZE", "100")


async def fetch_url(url: str, timeout: float = 15.0) -> str:
    """
    URL에서 HTML을 가져옵니다.

    Args:
        url: 가져올 URL
        timeout: 요청 타임아웃 (초)

    Returns:
        HTML 문자열

    Raises:
        ValueError: 잘못된 URL
        httpx.HTTPError: HTTP 요청 실패
    """
    # URL 유효성 검사
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"올바른 URL을 입력해주세요: {url}")

    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"HTTP/HTTPS URL만 지원합니다: {url}")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=timeout,
        verify=False,  # SSL 인증서 검증 생략 (일부 사이트 호환)
    ) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.text


def extract_content(html: str, url: str) -> dict:
    """
    HTML에서 본문 텍스트, 제목, 이미지 URL을 추출합니다.

    Args:
        html: HTML 문자열
        url: 원본 URL (상대 경로 → 절대 경로 변환용)

    Returns:
        {
            "title": str,
            "text": str,
            "images": list[str],
        }
    """
    # trafilatura로 본문 추출
    text = trafilatura.extract(
        html,
        include_images=True,
        include_links=True,
        include_tables=True,
        output_format="txt",
        config=_traf_config,
    )

    if not text:
        # fallback: trafilatura 실패 시 기본 추출
        text = trafilatura.extract(
            html,
            include_images=False,
            include_links=False,
            config=_traf_config,
        )

    # 제목 추출
    title = _extract_title(html)

    return {
        "title": title or "",
        "text": text or "",
        "images": [],
    }


def _extract_title(html: str) -> str:
    """HTML에서 제목(title 태그)을 추출합니다."""
    match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    if match:
        title = match.group(1).strip()
        # HTML 엔티티 디코딩
        title = title.replace("&amp;", "&")
        title = title.replace("&lt;", "<")
        title = title.replace("&gt;", ">")
        title = title.replace("&quot;", '"')
        title = title.replace("&#39;", "'")
        return title
    return ""


def _extract_image_urls(html: str, base_url: str, max_images: int = 20) -> list[str]:
    """
    HTML에서 주요 이미지 URL을 추출합니다.
    아이콘, 로고 등 작은 이미지는 필터링합니다.
    """
    img_pattern = re.compile(
        r'<img[^>]+src=["\']([^"\']+)["\']',
        re.IGNORECASE,
    )

    seen = set()
    images = []

    for match in img_pattern.finditer(html):
        src = match.group(1).strip()

        # 데이터 URI 스킵
        if src.startswith("data:"):
            continue

        # 상대 경로 → 절대 경로
        abs_url = urljoin(base_url, src)

        # 중복 체크
        if abs_url in seen:
            continue
        seen.add(abs_url)

        # 아이콘/로고 필터링 (파일명 기반)
        lower = abs_url.lower()
        skip_patterns = [
            "favicon", "icon", "logo", "badge", "avatar",
            "pixel", "tracking", "spacer", "blank",
            "1x1", "sprite", ".svg",
        ]
        if any(p in lower for p in skip_patterns):
            continue

        images.append(abs_url)

        if len(images) >= max_images:
            break

    return images


def build_markdown(
    title: str,
    text: str,
    images: list[str],
    source_url: str,
) -> str:
    """
    추출된 콘텐츠를 마크다운 초안으로 조합합니다.

    Args:
        title: 페이지 제목
        text: 본문 텍스트
        images: 이미지 URL 목록
        source_url: 원본 URL

    Returns:
        마크다운 문자열
    """
    parts = []

    # 제목
    if title:
        parts.append(f"# {title}\n")

    # 출처
    parts.append(f"> 📎 출처: [{source_url}]({source_url})\n")

    # 본문
    if text:
        parts.append(text)

    return "\n".join(parts)
