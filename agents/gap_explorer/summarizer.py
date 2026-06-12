"""
summarizer.py — Claude API로 연구 갭 분석 및 검증 가능성 판단
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
아래 논문 텍스트를 읽고 두 종류의 갭을 분리하여 추출하세요.
추측하거나 확대해석하지 말고, 저자가 직접 쓴 내용만 추출하세요.
반드시 지정된 JSON 형식으로만 응답하세요. 다른 설명 없이 JSON만 출력하세요.

[텍스트 구조 안내]
- 앞부분: Abstract + Introduction (서론)
- 뒷부분: Discussion / Limitations / Future Research (중간 섹션은 생략됨)

[추출 규칙]
1. intro_gaps: 서론에서 저자가 "선행연구에서 이런 갭이 있었다 → 그래서 이 연구를 했다"고 정당화한 선행연구 갭
   - 이 논문이 이미 해결한 닫힌 갭 (논리구조 학습용)
   - paper_contribution: 해당 갭에 대해 이 논문이 어떻게 기여했는지 한 줄 요약
2. core_gaps: Discussion / Limitations / Future Research에서 저자가 "앞으로 해야 한다"고 명시한 열린 갭
   - 아직 채워지지 않은 미래 연구 과제 (핵심 갭)
   - gap_type, model_type_needed로 상세 분류

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

  "intro_gaps": [
    {{
      "gap_ko": "서론에서 선행연구 대비 이 논문이 채운 갭 한 줄 요약 (한국어)",
      "gap_en": "동일 내용 영어",
      "paper_contribution_ko": "이 논문이 해당 갭을 어떻게 해결했는지 한 줄 요약 (한국어)",
      "paper_contribution_en": "동일 내용 영어",
      "source": "서론 원문 직접 인용 (영어 그대로)"
    }}
  ],

  "core_gaps": [
    {{
      "gap_ko": "저자가 명시한 미래 연구 갭 한 줄 요약 (한국어)",
      "gap_en": "동일 내용 영어",
      "gap_type": "매개변인부재 | 조절변인부재 | 종단설계필요 | 다층구조미적용 | 표본한계 | 메커니즘미규명 | 복합경로미검증",
      "model_type_needed": "cross-lag | cross-lag+moderation | mediation | moderated_mediation | MSEM | MSEM+moderation | 기타",
      "source": "Limitations/Future Research 원문 직접 인용 (영어 그대로)"
    }}
  ],

  "theories": ["해당 이론명만 포함: COR, JD-R, Effort-Recovery, AET, Self-Regulation, Interpersonal Stressor, DSEM 중 해당하는 것"],

  "tags": ["topic-tag-1", "topic-tag-2", "topic-tag-3"]
}}

[model_type_needed 판단 기준]
- cross-lag: "시간 경로가 필요하다", "lag 효과를 검증해야 한다", "종단 연구가 필요하다"
- cross-lag+moderation: 위 + 조절변인 추가 검증 필요
- mediation: "매개 메커니즘이 필요하다", "how/why 설명이 부족하다"
- moderated_mediation: 매개 + 조절 동시 검증 필요
- MSEM: 다층 구조만 필요 (lag 없이)
- MSEM+moderation: 다층 + cross-level interaction 필요
- 기타: 위 어디에도 해당하지 않는 경우
"""

MAX_FRONT_LENGTH = 4000
MAX_BACK_LENGTH  = 11000

_REF_PATTERN = re.compile(
    r'\n(?:References|REFERENCES|Bibliography|BIBLIOGRAPHY|참고문헌)\s*\n'
)

_client_cache = None


def _get_client():
    global _client_cache
    if _client_cache is None:
        _client_cache = anthropic.Anthropic(
            api_key=ANTHROPIC_API_KEY,
            timeout=CLAUDE_TIMEOUT,
        )
    return _client_cache


def _extract_analysis_text(full_text: str) -> str:
    ref_match = _REF_PATTERN.search(full_text)
    if ref_match:
        full_text = full_text[:ref_match.start()]

    if len(full_text) <= MAX_FRONT_LENGTH + MAX_BACK_LENGTH:
        return full_text

    front = full_text[:MAX_FRONT_LENGTH]
    back  = full_text[-MAX_BACK_LENGTH:]
    return front + "\n\n[...중간 생략...]\n\n" + back


def _call_claude(prompt: str) -> str | None:
    try:
        client = _get_client()
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4000,
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
    import json

    stripped = re.sub(r"```(?:json)?\s*", "", text)
    stripped = re.sub(r"\s*```", "", stripped)

    match = re.search(r"\{.*\}", stripped, re.DOTALL)
    if match:
        stripped = match.group(0)

    try:
        return json.loads(stripped)
    except Exception:
        return None


def _fallback_result(paper: dict) -> dict:
    meta = paper.get("metadata", {})
    return {
        "title":   meta.get("title", "") or paper.get("file_name", "").replace(".pdf", ""),
        "author":  meta.get("author", ""),
        "year":    paper.get("year_from_meta", ""),
        "journal": meta.get("subject", ""),
        "doi":     "",
        "intro_gaps": [],
        "core_gaps":  [],
        "theories":   [],
        "tags":       [paper.get("source_folder", "").replace(" ", "-")],
    }


def analyze_paper(paper: dict) -> dict:
    from agents.pdf_summarizer.extractor import is_thesis

    fallback = _fallback_result(paper)

    if is_thesis(paper):
        print("  [스킵] 학위논문 감지 — fallback 사용")
        return fallback

    meta      = paper.get("metadata", {})
    full_text = paper.get("full_text", "")
    text      = _extract_analysis_text(full_text)

    prompt = ANALYSIS_PROMPT.format(
        file_name=paper.get("file_name", ""),
        meta_title=meta.get("title", ""),
        meta_author=meta.get("author", ""),
        source_folder=paper.get("source_folder", ""),
        abstract=paper.get("abstract", "")[:500],
        text=text,
    )

    raw = _call_claude(prompt)
    if not raw:
        print("  [Fallback] API 실패 — 메타데이터만 사용")
        return fallback

    parsed = _parse_json(raw)
    if not parsed:
        print("  [Fallback] JSON 파싱 실패 — 메타데이터만 사용")
        return fallback

    for key, val in fallback.items():
        if key not in parsed or not parsed[key]:
            parsed[key] = val

    print("  ✅ Claude 갭 분석 완료")
    return parsed
