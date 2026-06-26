"""
ref_list_checker.py — 참고문헌 목록 형식 검사 (APA 7판)

검사 항목:
  1. DOI 형식 오류 (말줄임, 구버전, URL 혼용)
  2. 저자 형식 (Last, F. I. 형식)
  3. 연도 형식 (Year). 패턴
  4. 알파벳 순서 위반
  5. BibTeX 교차 검사
  6. 인텍스트 인용 ↔ 참고문헌 목록 완결성 검사
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class RefEntry:
    raw: str
    first_author: str    # 첫 저자 성 (원문)
    year: str
    has_doi: bool
    doi_url: str
    line_num: int


@dataclass
class RefError:
    error_type: str
    severity: str        # "error" | "warning"
    message: str
    suggestion: str = ""


# ── 패턴 ──────────────────────────────────────────────────────────────

# 참고문헌 항목 시작: Last[Name], F. 형식
_ENTRY_START_RE = re.compile(
    r"^(\w[\w\s'-]*),\s+[A-Z]\.",
    re.UNICODE,
)

# 연도: (YYYY) 또는 (YYYYa)
_YEAR_IN_ENTRY_RE = re.compile(r"\((\d{4}[a-z]?)\)")

# DOI/URL 패턴
_DOI_RE = re.compile(
    r"https?://(?:dx\.)?doi\.org/\S+"
    r"|doi:\S+"
    r"|https?://\S+",       # 일반 URL도 탐지 (DOI 대신 URL 사용 감지용)
)


# ── 파싱 ──────────────────────────────────────────────────────────────

def _extract_first_author(raw: str) -> str:
    """'Last[Name], F.' 패턴에서 성 추출"""
    m = re.match(r"^(.+?),\s+[A-Z]\.", raw.strip())
    return m.group(1).strip() if m else raw.split(",")[0].strip()


def _build_entry(raw: str, line_num: int) -> Optional[RefEntry]:
    """raw 텍스트 → RefEntry"""
    # Markdown 이탤릭 제거 후 연도 탐색
    plain = re.sub(r"_([^_]+)_", r"\1", raw)
    year_m = _YEAR_IN_ENTRY_RE.search(plain)
    if not year_m:
        return None

    first_author = _extract_first_author(raw)
    if not first_author:
        return None

    doi_m = _DOI_RE.search(plain)
    doi_url = doi_m.group(0) if doi_m else ""

    return RefEntry(
        raw=raw,
        first_author=first_author,
        year=year_m.group(1),
        has_doi=bool(doi_url),
        doi_url=doi_url,
        line_num=line_num,
    )


def parse_ref_list(md_path: Path) -> list:
    """MD 파일에서 참고문헌 항목(RefEntry) 목록 추출

    in-text 인용 블록(괄호로 시작)은 자동으로 제외한다.
    """
    text = md_path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    entries = []
    current_lines: list = []
    current_start = 0

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()

        if _ENTRY_START_RE.match(stripped):
            # 이전 항목 저장
            if current_lines:
                raw = " ".join(current_lines)
                entry = _build_entry(raw, current_start)
                if entry:
                    entries.append(entry)
            current_lines = [stripped]
            current_start = line_num

        elif current_lines:
            if not stripped:
                # 빈 줄 → 현재 항목 종료
                raw = " ".join(current_lines)
                entry = _build_entry(raw, current_start)
                if entry:
                    entries.append(entry)
                current_lines = []
            elif stripped.startswith(("(", "#", "---", ">")):
                # 인텍스트 인용이나 헤더 → 현재 항목 종료 후 무시
                raw = " ".join(current_lines)
                entry = _build_entry(raw, current_start)
                if entry:
                    entries.append(entry)
                current_lines = []
            else:
                # 항목 이어짐
                current_lines.append(stripped)

    if current_lines:
        raw = " ".join(current_lines)
        entry = _build_entry(raw, current_start)
        if entry:
            entries.append(entry)

    return entries


# ── 형식 검사 ────────────────────────────────────────────────────────

def check_ref_entry(entry: RefEntry, bib_index: dict) -> list:
    """단일 참고문헌 항목 → RefError 목록"""
    from .bib_loader import normalize_name

    errors = []
    raw = entry.raw

    # ── 1. DOI 형식 ───────────────────────────────────────────────
    if entry.has_doi:
        doi = entry.doi_url

        # 구버전 형식 (http://dx.doi.org/ 또는 doi:)
        if re.match(r"http://(?:dx\.)?doi\.org/|^doi:", doi):
            fixed = re.sub(r"^http://(?:dx\.)?doi\.org/", "https://doi.org/", doi)
            fixed = re.sub(r"^doi:", "https://doi.org/", fixed)
            errors.append(RefError(
                "doi_old_format", "error",
                f"구버전 DOI 형식 — 'https://doi.org/'로 수정 필요",
                fixed,
            ))

        # 말줄임: 하이픈 또는 슬래시로 끝나는 DOI
        elif re.search(r"[-/]$", doi):
            errors.append(RefError(
                "doi_truncated", "error",
                f"DOI가 잘린 것 같습니다 → `{doi}`",
                "DOI 전체 주소를 확인·보완하세요",
            ))

        # doi.org/https:// 형태 (URL을 DOI 자리에 붙임)
        elif re.search(r"doi\.org/https?://", doi):
            errors.append(RefError(
                "doi_contains_url", "error",
                f"DOI 형식 오류 — 'https://doi.org/' 뒤에 또 다른 URL이 붙어 있습니다",
                "DOI만 입력하거나, DOI가 없으면 URL만 단독으로 기재하세요",
            ))

        # doi.org 없이 일반 URL만 사용
        elif "doi.org" not in doi:
            errors.append(RefError(
                "doi_is_url", "warning",
                f"DOI 대신 일반 URL 사용 — 가능하면 'https://doi.org/' 형식으로 대체하세요",
                "",
            ))

    # ── 2. 저자 형식 ──────────────────────────────────────────────
    # (Year). 이전까지가 저자 블록 — Last, F. I. 형식인지 확인
    author_block = raw.split("(")[0].strip() if "(" in raw else ""
    if author_block:
        # 쉼표+이니셜 패턴이 없으면 형식 오류
        if not re.search(r",\s+[A-Z]\.", author_block):
            errors.append(RefError(
                "author_format", "error",
                "저자 형식 오류 — APA 7판 기준: 'Last, F. I., & Last, F. I.' 형식",
                "",
            ))

    # ── 3. 연도 형식: (YYYY). ─────────────────────────────────────
    plain = re.sub(r"_([^_]+)_", r"\1", raw)
    if not re.search(r"\(\d{4}[a-z]?\)\.", plain):
        errors.append(RefError(
            "year_format", "error",
            "연도 형식 오류 — '(YYYY).' 패턴이 없습니다 (마침표 확인)",
            "",
        ))

    # ── 4. BibTeX 교차 검사 ───────────────────────────────────────
    year_m = re.match(r"\d{4}", entry.year)
    if year_m:
        key = (normalize_name(entry.first_author), year_m.group())
        if not bib_index.get(key):
            errors.append(RefError(
                "bib_not_found", "warning",
                f"library.bib에서 '{entry.first_author} ({entry.year})' 미확인 — 저자명·연도 정확성 검토",
                "",
            ))

    return errors


def check_alphabetical(entries: list) -> list:
    """알파벳 순서 위반 탐지 → [(prev_entry, curr_entry, message), ...]"""
    violations = []
    for i in range(1, len(entries)):
        prev = entries[i - 1]
        curr = entries[i]
        if curr.first_author.lower() < prev.first_author.lower():
            violations.append((
                prev, curr,
                f"'{curr.first_author} ({curr.year})'가 "
                f"'{prev.first_author} ({prev.year})' 앞에 와야 합니다",
            ))
    return violations


# ── 교차 검사 ─────────────────────────────────────────────────────────

def cross_check(draft_citations: list, ref_entries: list) -> tuple:
    """인텍스트 인용 ↔ 참고문헌 목록 완결성 검사

    Returns:
        missing_in_ref: 본문에 인용됐으나 참고문헌 목록에 없는 Citation 목록 (중복 제거)
        orphan_in_ref:  참고문헌 목록에는 있으나 본문에 인용되지 않은 RefEntry 목록
    """
    from .bib_loader import normalize_name

    def _cite_key(cit):
        ym = re.match(r"\d{4}", cit.year)
        return (normalize_name(cit.first_author), ym.group()) if ym else None

    def _ref_key(entry):
        ym = re.match(r"\d{4}", entry.year)
        return (normalize_name(entry.first_author), ym.group()) if ym else None

    ref_key_set = {_ref_key(e) for e in ref_entries if _ref_key(e)}

    seen: set = set()
    missing_in_ref = []
    for cit in draft_citations:
        key = _cite_key(cit)
        if not key:
            continue
        if key not in ref_key_set and key not in seen:
            seen.add(key)
            missing_in_ref.append(cit)

    draft_key_set = {_cite_key(c) for c in draft_citations if _cite_key(c)}
    orphan_in_ref = [e for e in ref_entries if _ref_key(e) not in draft_key_set]

    return missing_in_ref, orphan_in_ref
