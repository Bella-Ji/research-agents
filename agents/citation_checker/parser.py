"""
parser.py — MD 파일에서 APA 인용 추출

괄호형: (Author, Year) / (Author & Author, Year) / (Author et al., Year)
서술형: Author (Year) / Author and Author (Year) / Author et al. (Year)
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class Citation:
    raw: str             # 파일에서 추출한 원문
    context: str         # "paren"(괄호형) or "narrative"(서술형)
    first_author: str    # 첫 번째 명명 저자의 성
    named_authors: list  # et al. 앞에 명시된 저자 목록
    has_et_al: bool
    uses_amp: bool       # '&' 포함 여부
    uses_and: bool       # 'and' 포함 여부
    year: str            # "2020" 또는 "2020a"
    line_num: int
    filepath: str = ""


_YEAR_RE = re.compile(r"\b(\d{4}[a-z]?)\b")

# 비저자 접두어: "for reviews, see", "cf.", "e.g.," 등
_PREFIX_RE = re.compile(
    r"^(?:.*?\b(?:see|cf\.?|e\.g\.,?|i\.e\.,?)\s+)",
    re.IGNORECASE,
)

# 일반 영어 단어 (서술형 오탐 방지)
_NON_AUTHOR = {
    "Figure", "Table", "Appendix", "Equation", "Model", "Study",
    "Section", "Chapter", "Note", "Example", "Summary", "Review",
    "Analysis", "Results", "Discussion", "Conclusion", "Introduction",
    "Method", "Methods", "Theory", "Framework", "Hypothesis",
}


def _parse_author_part(author_part: str) -> tuple:
    """저자 문자열 파싱 → (named_authors, has_et_al, uses_amp, uses_and)"""
    cleaned = _PREFIX_RE.sub("", author_part).strip()

    has_et_al = bool(re.search(r"\bet\s+al\b", cleaned, re.IGNORECASE))
    uses_amp = "&" in cleaned
    uses_and = bool(re.search(r"\band\b", cleaned, re.IGNORECASE))

    # et al. 이전 부분만 저자 추출에 사용
    et_removed = re.split(r"\s+et\s+al\b", cleaned, flags=re.IGNORECASE)[0]

    # &, and, 또는 ", 대문자" 패턴으로 저자 분리
    parts = re.split(
        r"\s*&\s*|\s+and\s+|\s*,\s+(?=[A-ZÀ-Ö])",
        et_removed,
    )
    named_authors = [
        p.strip() for p in parts
        if p.strip() and re.match(r"^[A-Za-zÀ-ÿ]", p.strip())
    ]

    return named_authors, has_et_al, uses_amp, uses_and


def _parse_single(raw: str, context: str, line_num: int, filepath: str) -> Optional[Citation]:
    """개별 인용 문자열 → Citation 객체"""
    raw = raw.strip()

    ym = _YEAR_RE.search(raw)
    if not ym:
        return None
    year = ym.group(1)

    author_part = raw[: ym.start()].strip().rstrip(",").strip()
    if not author_part:
        return None

    named_authors, has_et_al, uses_amp, uses_and = _parse_author_part(author_part)
    if not named_authors:
        return None

    return Citation(
        raw=raw,
        context=context,
        first_author=named_authors[0],
        named_authors=named_authors,
        has_et_al=has_et_al,
        uses_amp=uses_amp,
        uses_and=uses_and,
        year=year,
        line_num=line_num,
        filepath=filepath,
    )


def extract_citations(md_path: Path) -> list:
    """MD 파일에서 모든 인용 추출 (괄호형 + 서술형)"""
    text = md_path.read_text(encoding="utf-8", errors="replace")
    citations = []
    filepath = str(md_path)

    for line_num, line in enumerate(text.splitlines(), 1):

        # ── 괄호형: (Author, Year) 또는 (A & B, Year; C et al., Year) ──
        for pm in re.finditer(r"\(([^()]+)\)", line):
            content = pm.group(1)
            if not _YEAR_RE.search(content):
                continue
            for sub in re.split(r";\s*", content):
                cit = _parse_single(sub, "paren", line_num, filepath)
                if cit:
                    citations.append(cit)

        # ── 서술형: Author et al. (Year) / Author and Author (Year) ──
        # 괄호형 블록을 공백으로 마스킹해 이중 탐지 방지
        masked = re.sub(r"\([^()]*\)", lambda m: " " * len(m.group()), line)

        narr_re = re.compile(
            r"(?<!\w)"
            r"([A-ZÀ-Ö][a-zà-ö][a-zÀ-ÿ-]*)"          # 첫 번째 저자
            r"(?:"
            r"(?:,\s+[A-ZÀ-Ö][a-zà-ö][a-zÀ-ÿ-]+)*"   # 추가 저자 (disambiguation)
            r"(?:\s+et\s+al\.)?"                         # et al. (선택)
            r"|"
            r"\s+(?:and|&)\s+[A-ZÀ-Ö][a-zà-ö][a-zÀ-ÿ-]+"  # 2저자 and/&
            r")?"
            r"\s+\((\d{4}[a-z]?)\)",                    # (연도)
            re.UNICODE,
        )

        for nm in narr_re.finditer(masked):
            first_word = nm.group(1)
            if first_word in _NON_AUTHOR:
                continue

            # 원문 라인에서 실제 텍스트 복원
            raw_text = line[nm.start(): nm.end()]
            year = nm.group(2)
            author_part = raw_text[: raw_text.rfind("(")].strip()

            named_authors, has_et_al, uses_amp, uses_and = _parse_author_part(author_part)
            if not named_authors:
                continue

            citations.append(Citation(
                raw=raw_text,
                context="narrative",
                first_author=named_authors[0],
                named_authors=named_authors,
                has_et_al=has_et_al,
                uses_amp=uses_amp,
                uses_and=uses_and,
                year=year,
                line_num=line_num,
                filepath=filepath,
            ))

    return citations
