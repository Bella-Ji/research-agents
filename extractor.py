"""
extractor.py — PDF에서 텍스트와 메타데이터 추출
JunyeongLee12/paper_auto_organization의 extractor.py 참고하여 개선
"""

import os
import re
from pathlib import Path

import fitz  # PyMuPDF

MAX_PAGES = 50  # 최대 추출 페이지 수


def extract_one(pdf_path: Path) -> dict:
    """단일 PDF에서 텍스트와 메타데이터를 추출.

    Returns:
        {file_name, file_size_kb, metadata, page_count, full_text, abstract}
    """
    doc = fitz.open(str(pdf_path))
    meta = doc.metadata or {}

    pages = min(doc.page_count, MAX_PAGES)
    full_text = ""
    for i in range(pages):
        full_text += doc[i].get_text()

    doc.close()

    # PDF 메타데이터에서 연도 추출 시도
    year = ""
    date_str = meta.get("creationDate", "")
    year_match = re.search(r"((?:19|20)\d{2})", date_str)
    if year_match:
        year = year_match.group(1)
    # 파일명에서 연도 추출 시도 (fallback)
    if not year:
        year_match = re.search(r"((?:19|20)\d{2})", pdf_path.name)
        if year_match:
            year = year_match.group(1)

    # Abstract 자동 추출 (정규식)
    abstract = _extract_abstract(full_text)

    return {
        "file_name": pdf_path.name,
        "file_path": str(pdf_path),
        "file_size_kb": round(os.path.getsize(pdf_path) / 1024, 1),
        "source_folder": pdf_path.parent.name,
        "metadata": {
            "title":  meta.get("title", ""),
            "author": meta.get("author", ""),
            "subject": meta.get("subject", ""),
            "creation_date": meta.get("creationDate", ""),
        },
        "year_from_meta": year,
        "page_count": doc.page_count if not doc.is_closed else pages,
        "full_text": full_text,
        "abstract": abstract,
    }


def _extract_abstract(text: str) -> str:
    """정규식으로 Abstract 섹션 자동 추출."""
    match = re.search(
        r"(?:Abstract|ABSTRACT|초록)[:\s]*(.+?)"
        r"(?:\n\n|\nKeyword|\nKEYWORD|\nIntroduction|\nINTRODUCTION|\n1[.\s])",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if match:
        abstract = match.group(1).strip()
        # 너무 길면 잘라내기
        return abstract[:2000] if len(abstract) > 2000 else abstract
    return ""


def is_thesis(paper: dict) -> bool:
    """학위논문 여부 판별 — 50페이지 이상이거나 학위 관련 키워드 포함."""
    if paper.get("page_count", 0) >= 50:
        return True
    keywords = ("학위", "석사", "박사", "thesis", "dissertation")
    check = " ".join([
        paper.get("metadata", {}).get("title", ""),
        paper.get("metadata", {}).get("subject", ""),
        paper.get("file_name", ""),
    ]).lower()
    return any(kw in check for kw in keywords)
