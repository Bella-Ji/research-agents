"""
bib_loader.py — Mendeley library.bib 파싱

BibTeX 파일을 읽어 저자 목록과 연도를 추출하고,
(정규화된_첫번째저자, 연도) 인덱스를 생성한다.
"""

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class BibEntry:
    key: str
    authors: list       # 성(Last name) 목록
    year: str
    title: str
    author_count: int


def _extract_field(body: str, field: str) -> str:
    """BibTeX entry body에서 필드 값 추출 (중첩 중괄호 지원)"""
    m = re.search(r"\b" + re.escape(field) + r"\s*=\s*", body, re.IGNORECASE)
    if not m:
        return ""
    pos = m.end()
    if pos >= len(body):
        return ""

    if body[pos] == "{":
        depth = 0
        start = pos + 1
        for i in range(pos, len(body)):
            if body[i] == "{":
                depth += 1
            elif body[i] == "}":
                depth -= 1
                if depth == 0:
                    return body[start:i]
        return ""
    elif body[pos] == '"':
        end = body.find('"', pos + 1)
        return body[pos + 1:end] if end != -1 else ""
    else:
        m2 = re.match(r"(\S+)", body[pos:])
        return m2.group(1).rstrip(",") if m2 else ""


def _clean_latex(text: str) -> str:
    """LaTeX 특수문자 정리: {\'{e}} → e 등"""
    text = re.sub(r"\{\\[^a-zA-Z]*([a-zA-Z])\}", r"\1", text)
    text = re.sub(r"\{\\[^}]+\}", "", text)
    return text.replace("{", "").replace("}", "").replace("\\", "").strip()


def _parse_authors(author_str: str) -> list:
    """BibTeX author 필드 → 성(Last name) 목록

    BibTeX 형식: "Last, First and Last, First and ..."
    """
    parts = re.split(r"\s+and\s+", author_str.strip(), flags=re.IGNORECASE)
    last_names = []
    for part in parts:
        part = _clean_latex(part.strip())
        if not part:
            continue
        if "," in part:
            last = part.split(",")[0].strip()
        else:
            tokens = part.split()
            last = tokens[-1] if tokens else part
        if last:
            last_names.append(last)
    return last_names


def normalize_name(name: str) -> str:
    """저자명 비교용 정규화: 소문자 + 영문자만"""
    name = name.lower()
    table = str.maketrans(
        "áàäâãéèëêíìïîóòöôõúùüûñç",
        "aaaaaeeeeiiiioooooouuuunc",
    )
    name = name.translate(table)
    return re.sub(r"[^a-z]", "", name)


def load_bib(bib_path: Path) -> list:
    """BibTeX 파일 파싱 → BibEntry 목록"""
    text = bib_path.read_text(encoding="utf-8", errors="replace")
    entries = []

    entry_re = re.compile(r"@\w+\{([^,\s]+)\s*,", re.MULTILINE)
    starts = list(entry_re.finditer(text))

    for i, m in enumerate(starts):
        key = m.group(1)
        body_start = m.end()
        body_end = starts[i + 1].start() if i + 1 < len(starts) else len(text)
        body = text[body_start:body_end]

        year_str = _extract_field(body, "year").strip()
        author_str = _extract_field(body, "author")
        title_str = _extract_field(body, "title")

        if not re.match(r"^\d{4}$", year_str):
            continue

        authors = _parse_authors(author_str) if author_str else []
        entries.append(BibEntry(
            key=key,
            authors=authors,
            year=year_str,
            title=re.sub(r"[{}]", "", title_str).strip(),
            author_count=len(authors),
        ))

    return entries


def build_index(entries: list) -> dict:
    """(normalize_name(첫번째저자), 연도) → [BibEntry, ...] 인덱스"""
    index: dict = {}
    for entry in entries:
        if not entry.authors:
            continue
        key = (normalize_name(entry.authors[0]), entry.year)
        index.setdefault(key, []).append(entry)
    return index
