"""
markdown_gen.py — 요약 결과를 Obsidian MD 파일로 생성
JunyeongLee12의 markdown_gen.py 참고하여 개선
"""

import re
from datetime import date
from pathlib import Path

from config import MARKDOWN_TEMPLATE


def _sanitize_filename(name: str) -> str:
    name = re.sub(r'[<>:"/\\|?*\n\r\t]', "-", name)
    name = re.sub(r"-{2,}", "-", name)
    name = name.strip(" -").replace(" ", "-")
    return name


def _build_filename(pdf_filename: str) -> str:
    """PDF파일명_요약.md 형식의 파일명 생성."""
    stem = Path(pdf_filename).stem
    return f"{stem}_요약.md"


def _format_tags_yaml(tags: list) -> str:
    base  = ["literature", "paper"]
    extra = [t.lower().replace(" ", "-") for t in tags if t]
    all_tags = base + [t for t in extra if t not in base]
    return ", ".join(all_tags)


def _format_hashtags(tags: list) -> str:
    if not tags:
        return ""
    return " ".join(f"#{t.lower().replace(' ', '-')}" for t in tags if t)


def _to_bullets(value) -> str:
    if isinstance(value, list):
        return "\n".join(f"- {item}" for item in value if item)
    return str(value) if value else ""


def _to_quotes(value) -> str:
    if isinstance(value, list):
        return "\n\n".join(f'> "{item}"' for item in value if item)
    return f'> "{value}"' if value else ""


def generate_markdown(summary: dict, paper: dict) -> Path | None:
    """요약 결과로 MD 파일 생성 — PDF와 같은 폴더에 저장."""

    pdf_folder  = Path(paper.get("file_path", "")).parent
    pdf_filename = paper.get("file_name", "untitled.pdf")

    md_name = _build_filename(pdf_filename)
    md_path = pdf_folder / md_name

    # 중복 감지
    if md_path.exists():
        print(f"  [스킵] 이미 존재: {md_name}")
        return None

    tags = summary.get("tags", [])

    content = MARKDOWN_TEMPLATE.format(
        title         = summary.get("title", "").replace('"', '\\"'),
        year          = summary.get("year", "미상"),
        author        = summary.get("author", ""),
        journal       = summary.get("journal", ""),
        doi           = summary.get("doi", ""),
        tags          = _format_tags_yaml(tags),
        hashtags      = _format_hashtags(tags),
        created       = date.today().isoformat(),
        source_folder = paper.get("source_folder", ""),
        pdf_filename  = pdf_filename,
        one_line      = summary.get("one_line", ""),
        abstract      = summary.get("abstract", ""),
        key_claims_en = _to_bullets(summary.get("key_claims_en", [])),
        key_claims_ko = _to_bullets(summary.get("key_claims_ko", [])),
        method        = summary.get("method", ""),
        connection    = summary.get("connection", ""),
        excerpts      = _to_quotes(summary.get("excerpts", [])),
    )

    md_path.write_text(content, encoding="utf-8")
    print(f"  → 생성: {md_name}")
    return md_path
