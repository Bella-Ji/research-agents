"""
strategist.py — 갭 지형 지도를 읽고 내 데이터로 채울 수 있는 연구 모형 제안
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

# ── 변인사전 전체 컨텍스트 ─────────────────────────────────────────────

VARIABLE_DICT = """\
[연구자 보유 데이터]
설계: 일기연구 (AW-BW 교대 설계, 약 31일, person N=284, 한국 간호사 표본)

── Level 1 (Within-person, 매일) ──
AW 변인 (퇴근 후 설문, 당일 경험):
  - 부당대우: 환자(t_MPFs/t_MPFm), 상사(t_MBSs/t_MBSm), 동료(t_MBCs/t_MBCm), 전체(t_MSTs/t_MSTm)
  - 정서적 소진: t_EE
  - 잡크래프팅: 자원크래프팅(t_ABRC), 요구크래프팅(t_ABDC), 전체(t_JC)

BW 변인 (다음날 출근 전 설문):
  - 수면시간: jb_SQ
  - 회복경험(전날 밤): ND_REC
  - 회복상태(현재 아침): ND_SBR
  - 일의 의미감: ND_WM

── Level 2 (Between-person, 개인차) ──
  - 직무탈진: p_JB (전체), p_EE (정서적소진), p_PA (자아성취감저하), p_DP (비인간화)
  - 잡크래프팅: p_JC (전체), p_ABRC, p_ABDC
  - 일의 의미감: p_WM
  - 업무부하: p_WL
  - 심리적 안전풍토: PSC
  - 심리적 계약 의무/이행: PCEO, PCEF
  - 인구통계: age, sex, tenure_c
  - 근무특성: C1(병원종류), C4(근무부서), respon(직책), duty(근무형태), night

── 가능한 분석 방법 ──
  - MSEM: 다층 SEM (횡단, 동시점)
  - MSEM+moderation: Cross-level interaction
  - DSEM_cross-lag: 자기회귀 + 교차지연 경로
  - DSEM_mediation: lag-1 시간 매개
  - DSEM+moderation: lag-1 + L2 조절
  - DSEM_moderated_mediation: lag-1 매개 + L2 조절 동시
"""

CROSSLAG_RULES = """\
[교차지연 가능 여부 판단 규칙]
✅ 가능:
  - AW 변인 ↔ AW 변인 (동시점, 교차지연 가능): 부당대우, t_EE, t_JC, t_ABRC, t_ABDC
  - AW 변인 → BW 변인 (24시간 lag-1, 순방향 가능): t_EE→ND_WM, t_EE→ND_REC 등
  - ND_REC ↔ AW 변인 교차지연 가능 (ND_REC는 전날 밤 회고 = AW와 실질적 동시점)
  - BW 변인 ↔ BW 변인 (ND_SBR, ND_WM끼리): 동시점, 교차지연 가능

❌ 불가능:
  - BW 변인 → AW 변인 (역방향, 시간 역행): ND_WM→t_EE 불가
  - ND_REC ↔ ND_SBR 교차지연 불가 (둘 다 BW이지만 ND_REC는 전날 밤, ND_SBR은 현재 아침 → 이미 시간 선행이 있음)
  - jb_SQ (수면시간): 단방향 통제변인으로만 사용

⚠️ 주의:
  - AW EE → BW WM: lag-1 순방향은 가능하지만, 역방향(BW WM → AW EE)은 불가
  - AW/BW 동시점 경로는 교차지연 가능하나, 이미 이론적 시간 선행이 확립된 경로는 재라그 불가
"""

SAMPLE_NOTE = """\
[표본 관련 원칙]
갭 지형 지도에 포함된 논문들의 표본(간호사, 교사, 사무직, 제조업 등)이 연구자 데이터(한국 간호사)와 달라도 상관없다.
직업건강심리학 갭은 특정 직군에 국한되지 않고 조직 구성원 일반에 적용되는 이론적 갭이다.
표본이 다르다는 이유로 갭의 적용 가능성을 낮게 평가하지 말 것.
갭 커버리지 판단 기준은 "우리 데이터의 변인 구조로 검증 가능한가"이지 "같은 직군에서 나온 갭인가"가 아니다.
"""

EXISTING_PAPER_CONTEXT = """\
[기존 연구(제외 대상)]
기존 투고 논문 (WM paper):
  - 경로: 부당대우(MPF/MBS/MBC) → 정서적 소진(EE) → 일의 의미감(WM)
  - 조절: person-level 직무탈진(p_JB) (2단계 조절)
  - 방법: MSEM (다층 구조방정식, 횡단)
  - 제외 이유: 이미 논문화된 주제 — 동일 경로를 DSEM으로 재검증하는 것도 차별성 부족

→ 아래 경로는 제안 금지:
  (1) 부당대우 → EE → WM (직접 경로 또는 매개)
  (2) 부당대우 → WM (직접 경로)
  (3) EE → WM (단독 경로, 위 모형 일부)
"""

STRATEGY_PROMPT = """\
당신은 직업건강심리학(OHP) 전문 방법론자입니다.
아래 갭 지형 지도를 분석하여, 연구자의 데이터로 실제 채울 수 있는 연구 갭과 모형을 제안하세요.
모형 제안 시 실제 변인명과 분석 방법을 구체적으로 사용하세요.
반드시 지정된 JSON 형식으로만 응답하세요. 다른 설명 없이 JSON만 출력하세요.

{variable_dict}

{crosslag_rules}

{sample_note}

{existing_paper}

[갭 지형 지도]
{landscape_content}

---

규칙:
- viable_models는 최대 4개만 제안 (가장 중요한 것만)
- 모든 텍스트 필드는 한 줄 이내로 작성
- 불필요한 설명은 생략하고 핵심만 기술

아래 JSON 형식으로 출력하세요:

{{
  "gap_coverage": [
    {{
      "cluster_name": "갭 군집명 (지형 지도에서 가져올 것)",
      "coverage": "Full | Partial | None",
      "matched_variables": ["t_EE", "p_JB", ...],
      "missing_variables": ["직접 측정 없는 변인명"],
      "coverage_reason": "왜 Full/Partial/None인지 (한국어, 구체적으로)"
    }}
  ],

  "viable_models": [
    {{
      "model_id": "M1",
      "model_name": "모형명 (짧게)",
      "fills_gap": "채우는 갭 군집명",
      "path": "변인A[AW/BW] → 변인B[AW/BW] (조절: 변인C) — 실제 변인코드 사용",
      "model_type": "cross-lag | mediation | moderated_mediation | cross-lag+moderation",
      "analysis_method": "MSEM | MSEM+moderation | DSEM_cross-lag | DSEM_mediation | DSEM+moderation | DSEM_moderated_mediation",
      "temporal_structure": "시간 구조 (예: t_EE[AW_t] → ND_REC[BW_t+1])",
      "variables_used": ["t_EE", "ND_REC", "ND_WM", "p_JB"],
      "theoretical_basis": "이론 (COR, JD-R 등, 한 줄)",
      "novelty": "차별점 한 줄 (한국어)",
      "crosslag_feasible": true,
      "crosslag_reason": "교차지연 가능/불가 이유 (한 줄)",
      "priority": "High | Medium | Low",
      "priority_reason": "우선순위 이유 (한 줄, 한국어)"
    }}
  ],

  "excluded_paths": [
    {{
      "path": "제외된 경로",
      "reason": "제외 이유"
    }}
  ],

  "top_recommendation": "최우선 추천 모형 ID와 이유 (한국어, 3-4문장) — 이론적 기여도, 데이터 적합성, 방법론 차별성 종합 평가"
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
            max_tokens=8000,
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


def strategize(landscapes: list[dict]) -> dict | None:
    if not landscapes:
        print("  [오류] 분석할 갭 지형 지도가 없습니다.")
        return None

    landscape_content = "\n\n".join(
        f"=== {lp['name']} ===\n{lp['content']}" for lp in landscapes
    )

    prompt = STRATEGY_PROMPT.format(
        variable_dict=VARIABLE_DICT,
        crosslag_rules=CROSSLAG_RULES,
        sample_note=SAMPLE_NOTE,
        existing_paper=EXISTING_PAPER_CONTEXT,
        landscape_content=landscape_content,
    )

    print(f"  🤖 갭 전략 분석 중 ({len(landscapes)}개 지형 지도)...")
    raw = _call_claude(prompt)
    if not raw:
        print("  [실패] API 호출 실패")
        return None

    parsed = _parse_json(raw)
    if not parsed:
        print("  [실패] JSON 파싱 실패")
        return None

    print("  ✅ 전략 분석 완료")
    return parsed
