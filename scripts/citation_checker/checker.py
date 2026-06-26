"""
checker.py — APA 7판 인용 형식 검사 규칙

검사 항목:
  1. et al. 형식 오류 (마침표 누락, 대문자)
  2. 괄호형 '&' vs 서술형 'and' 혼용
  3. library.bib 미등록
  4. et al. 과용/누락 (저자 수 기준)
"""

import re
from dataclasses import dataclass
from typing import Optional

from .bib_loader import normalize_name


@dataclass
class CiteError:
    error_type: str   # 오류 코드
    severity: str     # "error" | "warning"
    message: str      # 한국어 설명
    suggestion: str   # 수정 제안


def _fix_et_al(text: str) -> str:
    """et al. 형식 자동 수정 (제안용)"""
    text = re.sub(r"\bEt\s+al\b", "et al", text)
    text = re.sub(r"\bet\s+al\b(?!\.)", "et al.", text)
    return text


def check_citation(cit, bib_index: dict) -> list:
    """단일 Citation 검사 → CiteError 목록"""
    errors = []
    raw = cit.raw

    # ────────────────────────────────────────────────
    # 1. et al. 형식 오류 (라이브러리 없이 판단)
    # ────────────────────────────────────────────────
    if re.search(r"\bet\s*al\b", raw, re.IGNORECASE):
        # 마침표 누락: "et al," 또는 "et al " (뒤에 마침표 없음)
        if re.search(r"\bet\s+al\b(?!\.)", raw, re.IGNORECASE):
            errors.append(CiteError(
                error_type="format_et_al_period",
                severity="error",
                message="'et al' 뒤에 마침표(.) 누락",
                suggestion=_fix_et_al(raw),
            ))
        # 대문자 'Et'
        if re.search(r"\bEt\s+al\b", raw):
            errors.append(CiteError(
                error_type="format_et_al_case",
                severity="error",
                message="'Et al.' → 소문자 'et al.'로 수정 (APA 7판)",
                suggestion=_fix_et_al(raw),
            ))

    # ────────────────────────────────────────────────
    # 2. '&' vs 'and' 혼용
    # ────────────────────────────────────────────────
    explicit_two = (len(cit.named_authors) == 2 and not cit.has_et_al)

    if cit.context == "paren" and cit.uses_and and explicit_two:
        # 괄호 안에서 'and' → '&' 로 수정
        fixed = re.sub(r"\band\b", "&", raw)
        errors.append(CiteError(
            error_type="format_amp_paren",
            severity="error",
            message="괄호형 2저자 인용에 'and' 사용 — '&'로 수정 (APA 7판 §6.21)",
            suggestion=fixed,
        ))

    if cit.context == "narrative" and cit.uses_amp:
        # 서술형에서 '&' → 'and' 로 수정
        fixed = raw.replace("&", "and")
        errors.append(CiteError(
            error_type="format_and_narrative",
            severity="error",
            message="서술형 인용에 '&' 사용 — 'and'로 수정 (APA 7판 §6.21)",
            suggestion=fixed,
        ))

    # ────────────────────────────────────────────────
    # 3. library.bib 조회
    # ────────────────────────────────────────────────
    year_digits = re.match(r"\d{4}", cit.year)
    if not year_digits:
        return errors
    year = year_digits.group()

    key = (normalize_name(cit.first_author), year)
    found = bib_index.get(key, [])

    if not found:
        errors.append(CiteError(
            error_type="library_not_found",
            severity="error",
            message=f"library.bib 미등록: '{cit.first_author} ({cit.year})'",
            suggestion="Mendeley에 논문이 등록되어 있는지 확인하세요",
        ))
        return errors

    # ────────────────────────────────────────────────
    # 4. et al. 적절성 (실제 저자 수 기준)
    # ────────────────────────────────────────────────
    # 동일 첫 저자 + 연도 항목이 여러 개면 disambiguation 형태 → et al. 검사 스킵
    if len(found) > 1:
        return errors

    entry = found[0]
    n = entry.author_count

    if cit.has_et_al and n == 1:
        errors.append(CiteError(
            error_type="et_al_unnecessary",
            severity="error",
            message=f"단독 저자인데 'et al.' 사용 (저자: {entry.authors[0]})",
            suggestion=f"({entry.authors[0]}, {cit.year})",
        ))

    elif cit.has_et_al and n == 2:
        a1 = entry.authors[0]
        a2 = entry.authors[1] if len(entry.authors) > 1 else "?"
        amp = "&" if cit.context == "paren" else "and"
        errors.append(CiteError(
            error_type="et_al_unnecessary",
            severity="error",
            message=f"2저자인데 'et al.' 사용 — APA 7판은 2저자까지 모두 표기",
            suggestion=f"({a1} {amp} {a2}, {cit.year})",
        ))

    elif not cit.has_et_al and n >= 3 and len(cit.named_authors) == 1:
        # 단독 저자명 표기 + 3인 이상 → et al. 누락
        errors.append(CiteError(
            error_type="et_al_missing",
            severity="warning",
            message=f"저자 {n}명인데 'et al.' 없음 (APA 7판: 3인 이상 → et al.)",
            suggestion=f"({entry.authors[0]} et al., {cit.year})",
        ))

    return errors
