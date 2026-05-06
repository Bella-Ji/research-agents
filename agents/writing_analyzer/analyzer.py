"""
analyzer.py — Claude API로 논문 글쓰기 방식 분석
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
from agents.writing_analyzer.draft_reader import SECTION_DISPLAY

ANALYSIS_PROMPT = """\
당신은 학술 논문 글쓰기 코치입니다.
아래 논문과 내 초안을 비교하여 **글쓰기 방식과 구조**를 분석해주세요.
연구 내용(what)이 아닌 글쓰기 방식(how)에만 집중하세요.

[분석 대상 논문 전문]
{paper_text}

---

[비교 섹션: {section_display}]

[내 초안]
{my_draft}

---

반드시 JSON만 출력하세요. 다른 설명 없이 JSON만:

{{
  "paper_structure": "이 논문의 {section_display}의 논리 흐름과 단락 구성 분석 (한국어, 4-6문장)",
  "paper_rhetorical_moves": [
    "이 섹션에서 효과적으로 사용된 글쓰기 전략 1",
    "전략 2",
    "전략 3",
    "전략 4"
  ],
  "paper_style": "문체, 문장 구조, 연결어·전환어 사용 패턴 (한국어, 3-4문장)",
  "comparison": "내 초안과의 구조·논리 전개 차이 (한국어, 4-5문장)",
  "my_strengths": "내 초안이 잘 하고 있는 점 (한국어, 2-3문장)",
  "improvements": [
    "구체적 개선 방향 1",
    "개선 방향 2",
    "개선 방향 3"
  ],
  "takeaways": [
    "지금 바로 적용 가능한 배울 점 1",
    "배울 점 2",
    "배울 점 3"
  ]
}}
"""

MAX_PAPER_TEXT = 14000
MAX_DRAFT_TEXT = 3000
MAX_COACHING_CONTEXT = 3000

# ── 문단 수정 프롬프트 ────────────────────────────────────────────────

REVISION_PROMPT = """\
당신은 학술 논문 글쓰기 코치입니다.
아래 문단의 논리 구조를 분석하고, 구체적인 수정안을 제시해주세요.
연구 내용의 옳고 그름이 아닌 **논리 전개 방식과 문장 구성**에만 집중하세요.

[섹션 맥락: {section_display}]
{coaching_context_block}
[수정 요청 문단]
{paragraph}

---

반드시 JSON만 출력하세요:

{{
  "diagnosis": "이 문단의 논리적 문제 진단 (한국어, 2-4문장)",
  "issues": [
    "구체적 문제 1",
    "구체적 문제 2",
    "구체적 문제 3"
  ],
  "revised_paragraph": "수정된 문단 전체 (원문과 동일한 언어로 작성)",
  "what_changed": [
    "변경 사항 1 — 이유",
    "변경 사항 2 — 이유",
    "변경 사항 3 — 이유"
  ],
  "alternative_opening": "다른 방식의 첫 문장 예시 (원문과 동일한 언어로 작성)"
}}
"""

# ── 멀티 논문 분석 프롬프트 ───────────────────────────────────────────

EXTRACTION_PROMPT = """\
당신은 학술 논문 글쓰기 분석가입니다.
아래 논문에서 [{section_display}] 섹션의 논리 전개 방식을 분석하세요.
연구 내용이 아닌 **논리를 풀어가는 방식**에만 집중하세요.

[논문 전문]
{paper_text}

---

반드시 JSON만 출력하세요:

{{
  "opening_move": "이 섹션이 어떻게 시작하는가 — 첫 단락의 논리적 역할 (한국어, 2-3문장)",
  "argument_sequence": ["논리 전개 단계 1", "단계 2", "단계 3", "단계 4"],
  "claim_support_pattern": "주장과 근거를 어떻게 연결하는가 (한국어, 2-3문장)",
  "transition_strategy": "단락 간 전환 방식과 연결어 패턴 (한국어, 1-2문장)",
  "closing_move": "섹션을 어떻게 마무리하는가 (한국어, 1-2문장)",
  "effective_logic": "특히 논리적으로 효과적인 부분 (한국어, 2문장)"
}}
"""

SYNTHESIS_PROMPT = """\
당신은 학술 논문 글쓰기 코치입니다.
아래 우수 논문들의 [{section_display}] 섹션 논리 전개 분석 결과를 종합하여,
내 초안을 구체적으로 코칭해주세요.

연구 내용이 아닌 **논리를 풀어가는 방식**에만 집중하세요.

[우수 논문 {n}편의 논리 전개 분석]
{all_analyses}

[내 초안 — {section_display}]
{my_draft}

---

반드시 JSON만 출력하세요:

{{
  "common_logic_blueprint": [
    "우수 논문들의 공통 논리 전개 단계 1",
    "단계 2",
    "단계 3",
    "단계 4",
    "단계 5"
  ],
  "common_patterns": "공통적으로 나타나는 논리 구성 방식 (한국어, 4-5문장)",
  "my_draft_evaluation": "내 초안의 논리 전개 평가 — 강점과 약점 (한국어, 4-5문장)",
  "missing_elements": [
    "내 초안에서 빠진 논리적 요소 1",
    "요소 2",
    "요소 3"
  ],
  "priority_improvements": [
    {{"what": "개선할 점", "why": "왜 중요한가", "how": "구체적 방법"}},
    {{"what": "개선할 점 2", "why": "왜 중요한가", "how": "구체적 방법"}},
    {{"what": "개선할 점 3", "why": "왜 중요한가", "how": "구체적 방법"}}
  ],
  "rewrite_suggestions": [
    "지금 바로 적용할 수 있는 구체적 제안 1",
    "제안 2",
    "제안 3"
  ]
}}
"""

_client_cache = None


def _get_client() -> anthropic.Anthropic:
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
            max_tokens=2000,
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
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        text = match.group(1)
    else:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            text = match.group(0)
    try:
        return json.loads(text)
    except Exception:
        return None


def analyze_section(
    paper_text: str,
    section_key: str,
    my_draft: str,
) -> dict | None:
    """논문의 특정 섹션과 내 초안을 비교 분석.

    Args:
        paper_text: 분석 대상 논문 전문
        section_key: 섹션 키 (예: "introduction")
        my_draft: 해당 섹션 내 초안 내용

    Returns:
        분석 결과 딕셔너리. 실패 시 None.
    """
    section_display = SECTION_DISPLAY.get(section_key, section_key)

    prompt = ANALYSIS_PROMPT.format(
        paper_text=paper_text[:MAX_PAPER_TEXT],
        section_display=section_display,
        my_draft=my_draft[:MAX_DRAFT_TEXT],
    )

    raw = _call_claude(prompt)
    if not raw:
        return None

    parsed = _parse_json(raw)
    if not parsed:
        print(f"  [경고] {section_display} JSON 파싱 실패")
        return None

    return parsed


def extract_section_logic(
    paper_text: str,
    section_key: str,
    paper_name: str,
) -> dict | None:
    """논문 한 편에서 특정 섹션의 논리 전개 패턴만 추출.

    멀티 분석의 1단계 — 개별 논문 처리용.
    """
    section_display = SECTION_DISPLAY.get(section_key, section_key)

    prompt = EXTRACTION_PROMPT.format(
        section_display=section_display,
        paper_text=paper_text[:MAX_PAPER_TEXT],
    )

    raw = _call_claude(prompt)
    if not raw:
        return None

    parsed = _parse_json(raw)
    if not parsed:
        print(f"  [경고] {paper_name} JSON 파싱 실패")
        return None

    parsed["paper_name"] = paper_name
    return parsed


def synthesize_and_coach(
    section_key: str,
    extractions: list[dict],
    my_draft: str,
) -> dict | None:
    """추출된 패턴들을 종합하여 내 초안 코칭 보고서 생성.

    멀티 분석의 2단계 — 종합 코칭용.
    """
    import json as _json

    section_display = SECTION_DISPLAY.get(section_key, section_key)

    analyses_text = ""
    for i, ext in enumerate(extractions, 1):
        name = ext.get("paper_name", f"논문{i}")
        analyses_text += f"\n--- [{i}] {name} ---\n"
        analyses_text += _json.dumps(
            {k: v for k, v in ext.items() if k != "paper_name"},
            ensure_ascii=False, indent=2
        )
        analyses_text += "\n"

    prompt = SYNTHESIS_PROMPT.format(
        section_display=section_display,
        n=len(extractions),
        all_analyses=analyses_text,
        my_draft=my_draft[:MAX_DRAFT_TEXT],
    )

    raw = _call_claude(prompt)
    if not raw:
        return None

    parsed = _parse_json(raw)
    if not parsed:
        print("  [경고] 종합 코칭 JSON 파싱 실패")
        return None

    return parsed


def analyze_multi_papers(
    paper_texts: dict[str, str],
    section_key: str,
    my_draft: str,
) -> dict | None:
    """여러 논문에서 패턴 추출 후 종합 코칭 보고서 생성.

    Args:
        paper_texts: {논문파일명: 전문텍스트}
        section_key: 분석할 섹션 키
        my_draft: 해당 섹션 내 초안

    Returns:
        종합 코칭 딕셔너리. 실패 시 None.
    """
    section_display = SECTION_DISPLAY.get(section_key, section_key)
    total = len(paper_texts)

    # Step 1: 논문별 논리 패턴 추출
    print(f"\n  [1단계] {total}편 논리 패턴 추출 중...")
    extractions = []
    for i, (name, text) in enumerate(paper_texts.items(), 1):
        print(f"    [{i}/{total}] {name[:50]}...")
        result = extract_section_logic(text, section_key, name)
        if result:
            extractions.append(result)
            print(f"    ✅ 완료")
        else:
            print(f"    ⚠️  실패 — 건너뜀")

    if not extractions:
        print("  ❌ 추출 성공한 논문이 없습니다.")
        return None

    print(f"\n  [2단계] {len(extractions)}편 종합 → {section_display} 코칭 보고서 생성 중...")
    coaching = synthesize_and_coach(section_key, extractions, my_draft)

    if not coaching:
        return None

    coaching["source_papers"] = [e.get("paper_name", "") for e in extractions]
    coaching["section_key"] = section_key
    return coaching


def revise_paragraph(
    paragraph: str,
    section_key: str,
    coaching_context: str | None = None,
) -> dict | None:
    """문단 하나를 받아 논리 구조 진단 + 수정안 반환.

    Args:
        paragraph: 수정 요청 문단 텍스트
        section_key: 섹션 키 (예: "theoretical_implications")
        coaching_context: 사전 코칭 보고서 내용 (없어도 동작)

    Returns:
        수정 제안 딕셔너리. 실패 시 None.
    """
    section_display = SECTION_DISPLAY.get(section_key, section_key)

    if coaching_context:
        ctx_block = (
            f"[우수 논문 기반 코칭 기준 — {section_display}]\n"
            f"{coaching_context[:MAX_COACHING_CONTEXT]}\n\n"
        )
    else:
        ctx_block = ""

    prompt = REVISION_PROMPT.format(
        section_display=section_display,
        coaching_context_block=ctx_block,
        paragraph=paragraph,
    )

    raw = _call_claude(prompt)
    if not raw:
        return None

    parsed = _parse_json(raw)
    if not parsed:
        print("  [경고] 수정 제안 JSON 파싱 실패")
        return None

    return parsed


def analyze_paper(
    paper_text: str,
    draft_sections: dict[str, str],
) -> dict[str, dict]:
    """여러 섹션에 대해 순차 분석 수행.

    Returns:
        {section_key: analysis_dict}
    """
    results: dict[str, dict] = {}
    total = len(draft_sections)

    for i, (key, draft_content) in enumerate(draft_sections.items(), 1):
        display = SECTION_DISPLAY.get(key, key)
        print(f"  [{i}/{total}] {display} 분석 중...")
        result = analyze_section(paper_text, key, draft_content)
        if result:
            results[key] = result
            print(f"  ✅ {display} 완료")
        else:
            print(f"  ⚠️  {display} 분석 실패 — 건너뜀")

    return results
