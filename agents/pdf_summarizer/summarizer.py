"""
summarizer.py — Claude API로 논문 요약 생성
JunyeongLee12의 2단계 파이프라인 + fallback 시스템 참고하여 개선
"""

import re
import time

import anthropic

from config import (
    ANTHROPIC_API_KEY,
    CLAUDE_MODEL,
    CLAUDE_TIMEOUT,
    CLAUDE_REQUEST_DELAY,
)

# ── 프롬프트 ──────────────────────────────────────────────────────────

ANALYSIS_PROMPT = """\
당신은 직업건강심리학(Occupational Health Psychology) 전문 연구자입니다.
아래 논문을 읽고, 반드시 지정된 JSON 형식으로만 응답하세요. 다른 설명 없이 JSON만 출력하세요.

[연구 맥락 — 이 논문의 활용 목적]
- 연구 주제: 직장 내 부당대우 → 정서적 소진 → 일의 의미감의 매개 경로를, person-level 직무소진(job burnout)이 조절하는 조절된 매개 모형
- 이론 프레임: COR theory (Hobfoll), JD-R model (Bakker & Demerouti)
- 조절변인: 직무 소진 (job burnout, person-level)
- 연구 대상: 한국 간호사/의료 종사자
- 분석 방법: DSEM (다층 구조방정식모형), 일기 연구
- 핵심 주장은 5~7개, 인용 문장은 4~5개 추출하세요.
- 조절 효과(moderating effect)가 있으면 반드시 별도로 추출하고, 없으면 "해당 없음"으로 표기하세요.

[서지정보 (참고용)]
- 파일명: {file_name}
- PDF 메타 제목: {meta_title}
- PDF 메타 저자: {meta_author}
- 폴더 (주제): {source_folder}
- 자동 추출 초록: {abstract}

[논문 텍스트]
{text}

---

아래 JSON 형식으로 출력하세요:

{{
  "title": "논문 제목 (영어)",
  "author": "저자명 (Last, F. 형식, 여러 명이면 쉼표 구분)",
  "year": "출판 연도 4자리",
  "journal": "저널명",
  "doi": "DOI (없으면 빈 문자열)",
  "one_line": "한 문장 핵심 요약 (한국어)",
  "abstract": "초록 전문 또는 요약 (영어, 원문 그대로)",
  "key_claims_en": ["핵심 주장 1 (영어)", "주장 2", "주장 3", "주장 4", "주장 5"],
  "key_claims_ko": ["핵심 주장 1 (한국어)", "주장 2", "주장 3", "주장 4", "주장 5"],
  "moderation": "조절 효과 관련 내용 (한국어: 조절변인, 조절 방향, 유의성 여부. 없으면 '해당 없음')",
  "method": "연구 방법론 요약 (한국어: 설계, 표본, 측정도구, 분석방법)",
  "connection": "내 연구와의 연결점 (한국어: COR, JD-R, 부당대우, EE, WM, burnout, DSEM 중 관련 개념)",
  "excerpts": ["직접 인용할 만한 영어 문장 1", "문장 2", "문장 3", "문장 4", "문장 5"],
  "tags": ["tag1", "tag2", "tag3"]
}}
"""

MAX_TEXT_LENGTH = 15000  # Claude 입력 한도 (비용 절감)
_client_cache = None


def _get_client():
    global _client_cache
    if _client_cache is None:
        _client_cache = anthropic.Anthropic(
            api_key=ANTHROPIC_API_KEY,
            timeout=CLAUDE_TIMEOUT,
        )
    return _client_cache


def _call_claude(prompt: str) -> str | None:
    """Claude API 호출. 실패 시 None 반환."""
    try:
        client = _get_client()
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=2500,
            messages=[{"role": "user", "content": prompt}],
        )
        time.sleep(CLAUDE_REQUEST_DELAY)
        return message.content[0].text
    except anthropic.RateLimitError:
        print("  [Rate Limit] 잠시 후 재시도...")
        time.sleep(30)
        return None
    except anthropic.APITimeoutError:
        print("  [타임아웃] Claude API 응답 없음")
        return None
    except Exception as e:
        print(f"  [오류] Claude API 호출 실패: {e}")
        return None


def _parse_json(text: str) -> dict | None:
    """응답에서 JSON 블록 추출 및 파싱."""
    import json

    # ```json ... ``` 블록 추출 시도
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        text = match.group(1)
    else:
        # 중괄호 블록 직접 추출
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            text = match.group(0)

    try:
        return json.loads(text)
    except Exception:
        return None


def _fallback_summary(paper: dict) -> dict:
    """API 없이 메타데이터 + 정규식으로 기본 요약 생성."""
    meta = paper.get("metadata", {})
    return {
        "title":  meta.get("title", "") or paper.get("file_name", "").replace(".pdf", ""),
        "author": meta.get("author", ""),
        "year":   paper.get("year_from_meta", ""),
        "journal": meta.get("subject", ""),
        "doi": "",
        "one_line": "[요약 생성 실패 — 직접 작성해주세요]",
        "abstract": paper.get("abstract", "[초록 추출 실패]"),
        "key_claims_en": [],
        "key_claims_ko": [],
        "moderation": "[직접 작성]",
        "method": "[직접 작성]",
        "connection": "[직접 작성]",
        "excerpts": [],
        "tags": [paper.get("source_folder", "").replace(" ", "-")],
    }


def summarize_paper(paper: dict) -> dict:
    """논문 데이터를 분석하여 요약 딕셔너리를 반환.

    Args:
        paper: extractor.extract_one() 반환값

    Returns:
        요약 딕셔너리 (API 실패 시 fallback 반환)
    """
    from agents.pdf_summarizer.extractor import is_thesis

    fallback = _fallback_summary(paper)

    # 학위논문은 AI 분석 스킵
    if is_thesis(paper):
        print("  [스킵] 학위논문 감지 — fallback 사용")
        return fallback

    meta = paper.get("metadata", {})
    full_text = paper.get("full_text", "")
    truncated = full_text[:MAX_TEXT_LENGTH]

    prompt = ANALYSIS_PROMPT.format(
        file_name=paper.get("file_name", ""),
        meta_title=meta.get("title", ""),
        meta_author=meta.get("author", ""),
        source_folder=paper.get("source_folder", ""),
        abstract=paper.get("abstract", "")[:500],
        text=truncated,
    )

    raw = _call_claude(prompt)
    if not raw:
        print("  [Fallback] API 실패 — 메타데이터만 사용")
        return fallback

    parsed = _parse_json(raw)
    if not parsed:
        print("  [Fallback] JSON 파싱 실패 — 메타데이터만 사용")
        return fallback

    # fallback 값으로 빈 필드 채우기
    for key, val in fallback.items():
        if key not in parsed or not parsed[key]:
            parsed[key] = val

    print("  ✅ Claude 분석 완료")
    return parsed
