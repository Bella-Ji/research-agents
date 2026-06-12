"""
synthesizer.py — 복수 갭분석 결과를 종합하여 연구 모형 제안
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

SYNTHESIS_PROMPT = """\
당신은 직업건강심리학(Occupational Health Psychology) 전문 연구자입니다.
아래는 여러 논문의 연구 갭 분석 결과입니다.
이 갭들을 종합하여 "갭 지형 지도(gap landscape)"를 만드세요.
당신의 역할은 갭을 분류하고 군집화하는 것이며, 연구 모형을 제안하는 것이 아닙니다.
반드시 지정된 JSON 형식으로만 응답하세요. 다른 설명 없이 JSON만 출력하세요.

[표본 관련 원칙]
논문의 표본(간호사, 교사, 사무직, 제조업 등)이 달라도 갭의 가치를 차별하지 말 것.
직업건강심리학 갭은 이론적 수준에서 직군을 초월하여 적용된다.
표본이 다른 논문들의 갭도 동등하게 군집화하고 종합할 것.

[갭 분석 결과 — {n_papers}편]
{papers_content}

---

아래 JSON 형식으로 출력하세요:

{{
  "gap_clusters": [
    {{
      "cluster_name": "갭 군집명 (한국어, 짧게)",
      "cluster_name_en": "Gap cluster name (English)",
      "description_ko": "이 군집이 무엇을 다루는지 2-3문장 설명 (한국어)",
      "gap_type": "매개변인부재 | 조절변인부재 | 종단설계필요 | 다층구조미적용 | 표본한계 | 메커니즘미규명 | 복합경로미검증",
      "model_types_needed": ["cross-lag", "mediation", "moderated_mediation", ...],
      "theories_involved": ["COR", "JD-R", ...],
      "n_papers": 논문 수(정수),
      "papers": ["논문명1", "논문명2"],
      "representative_gaps": ["군집을 대표하는 갭 원문 1", "갭 원문 2"]
    }}
  ],

  "underexplored_paths": [
    {{
      "path_ko": "여러 논문에서 언급됐지만 검증되지 않은 구체적인 경로 (한국어)",
      "path_en": "Underexplored path (English)",
      "mentioned_in": ["논문명1", "논문명2"]
    }}
  ],

  "methodological_gaps": [
    {{
      "gap_ko": "방법론적 갭 (한국어) — 예: DSEM 미사용, lag 구조 미검증 등",
      "gap_en": "Methodological gap (English)",
      "mentioned_in": ["논문명1"]
    }}
  ],

  "dominant_theories": [
    {{
      "theory": "이론명",
      "frequency": 언급 논문 수(정수),
      "papers": ["논문명1"]
    }}
  ],

  "summary_ko": "전체 갭 지형을 2-3문장으로 요약 (한국어) — 어떤 갭이 가장 많고, 어떤 이론이 지배적이며, 방법론적으로 무엇이 부족한지"
}}
"""

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
    try:
        client = _get_client()
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=5000,
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

    # strip ```json ... ``` wrappers first
    stripped = re.sub(r"```(?:json)?\s*", "", text)
    stripped = re.sub(r"\s*```", "", stripped)

    match = re.search(r"\{.*\}", stripped, re.DOTALL)
    if match:
        stripped = match.group(0)

    try:
        return json.loads(stripped)
    except Exception:
        return None


def _format_papers_content(papers: list[dict]) -> str:
    parts = []
    for i, p in enumerate(papers, 1):
        parts.append(f"=== 논문 {i}: {p['name']} (폴더: {p['folder']}) ===")
        parts.append(p["content"])
        parts.append("")
    return "\n".join(parts)


def synthesize(papers: list[dict]) -> dict | None:
    """복수의 갭분석 결과를 종합하여 모형 제안 반환."""
    if not papers:
        print("  [오류] 분석할 논문이 없습니다.")
        return None

    papers_content = _format_papers_content(papers)
    prompt = SYNTHESIS_PROMPT.format(
        n_papers=len(papers),
        papers_content=papers_content,
    )

    print(f"  🤖 {len(papers)}편 종합 분석 중...")
    raw = _call_claude(prompt)
    if not raw:
        print("  [실패] API 호출 실패")
        return None

    parsed = _parse_json(raw)
    if not parsed:
        print("  [실패] JSON 파싱 실패")
        return None

    print("  ✅ 종합 분석 완료")
    return parsed
