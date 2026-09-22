# research-agents — CLAUDE.md

박사 졸업논문 작성을 위한 연구 자동화 에이전트 모음.
이 프로젝트에서 작업할 때 이 파일을 먼저 읽을 것.

---

## 연구 맥락

- **현재 기준**: 작업 전에 [.claude/context/research-profile.md](.claude/context/research-profile.md)의 현재 연구 방향과 연구별 표본을 읽는다. 과거 STRUCTURE.md나 코드의 고정 N을 현재 연구의 확정 사실로 사용하지 않는다.
- **기존 투고 논문 (WM paper)**: 부당대우 → 정서적 소진(EE) → 일의 의미감(WM)의 개인 내 매개와 교차수준 조절을 검증한 일기연구, Bayesian MSEM.
- **졸업논문 방향**: 연구 2 미확정. MSEM 모형 8(요구·자원크래프팅→EE→회복경험, PSC 1단계 조절)이 유력 후보이며 N은 미정이다. 기존 DSEM 탐색은 현재 기본 방향으로 전제하지 않는다 (2026-09-22 연구자 설명).
- **핵심 제약**: 새 모형 제안 시 기존 WM 논문과의 중복 회피 규칙을 공통 프로필에서 확인한다. 기존 논문의 학위논문 편입 여부와 새 모형의 중복 회피를 구분한다.

---

## context/ — 단일 진실 공급원 (SSOT)

`.claude/context/` 아래 3개 파일이 연구 맥락의 유일한 기준이다.
에이전트 MD 내부에 이론·변인·규칙을 하드코딩하지 않는다.
**context 파일과 코드가 다르면 context가 정답.**

| 파일 | 역할 |
|---|---|
| `research-profile.md` | 이론 프레임, 표본, 분석 방법, 에이전트별 관점 |
| `variable-dictionary.md` | 변인코드 사전 (t_EE, ND_WM 등 실제 코드 목록) |
| `crosslag-rules.md` | DSEM 교차지연 가능 여부 판단 규칙 |

---

## 에이전트 목록

| 에이전트 | 한 줄 역할 | 슬래시 커맨드 |
|---|---|---|
| `gap-explorer` | PDF 1편 → Limitations/Future Research 갭 추출 | `/find-gaps` (1단계) |
| `gap-synthesizer` | 갭분석.md 여러 개 → 공통 패턴 군집화 | `/find-gaps` (2단계) |
| `gap-strategist` | gap landscape → 연구 모형 제안 | `/find-gaps` (3단계) |
| `pdf-summarizer` | PDF 1편 → Obsidian 요약 MD 생성 | `/summarize-pdf` |
| `lit-searcher` | vault *_요약.md Grep → 키워드 문헌 탐색·합성 | `/search-lit` |
| `citation-checker` | APA 7판 인용 형식 검사 (스크립트 + 정리) | `/check-citations` |
| `draft-reviewer` | 초안 섹션 4축 검토 (이론·인용·어조·구조) | `/review-draft` |
| `coach-writing` | 논리 전개 방식 분석 → 글쓰기 코칭 | `/coach-writing` |
| `structure-architect` | 논문 뼈대 설계·검증·STRUCTURE.md 관리 | `/outline-dissertation` 외 |
| `peer-reviewer` | 논문 전체 피어리뷰 평가 (2-Pass, 5축) | `/peer-review` |

---

## coach-writing / draft-reviewer / peer-reviewer 사용 구분

세 에이전트 모두 문단 단위 피드백을 주지만 판단 기준과 범위가 다르다:

- **coach-writing** — 우수 논문(exemplar)과 비교해 논리 전개 패턴을 코칭. 내용(이론/인용이 맞는지)은 판단하지 않음. "논리 흐름이 안 잡힌다" 싶을 때 사용.
- **draft-reviewer** — research-profile.md 기준 이론 적합성, 인용의 주장 뒷받침 여부, 학술 어조를 문단 단위로 감사. "이 이론 인용이 맞는지" 걱정될 때 사용.
- **peer-reviewer** — 저널 피어리뷰 수준의 논문 전체 평가(기여도, 방법-결과 정합성, 과대해석, 대안 설명, 한계 충분성). "이 논문이 게재할 만큼 설득력 있나" 판단이 필요할 때 사용.

peer-reviewer 실행 전, 관련 vault 자료(gap-explorer/lit-searcher 산출물)가 부족하면 먼저 그 에이전트들을 돌려서 vault를 채워둘 것. peer-reviewer는 기존 vault 파일만 참조하고 실시간 재검색은 하지 않음.

헷갈리면: 비교 대상이 다른 논문이면 coach-writing, 비교 대상이 규칙/이론이면 draft-reviewer, 논문 전체의 설득력을 보고 싶으면 peer-reviewer.

---

## 자연어 트리거 → 슬래시 커맨드 라우팅

아래 트리거 문구가 나오면 해당 커맨드로 즉시 라우팅한다.

| 트리거 문구 | 라우팅 |
|---|---|
| "이 논문 요약해줘", "PDF 요약" | `/summarize-pdf` |
| "갭 찾아줘", "연구 갭", "gap 분석" | `/find-gaps` |
| "관련 논문 찾아줘", "문헌 탐색", "vault 검색" | `/search-lit` |
| "인용 검사", "APA 형식", "citation 확인" | `/check-citations` |
| "초안 검토", "draft 검토", "논문 피드백" | `/review-draft` |
| "글쓰기 코칭", "논리 분석", "writing coach" | `/coach-writing` |
| "논문 구조", "아웃라인", "챕터 구성" | `/outline-dissertation` |

---

## 슬래시 커맨드 요약

| 커맨드 | 주요 인자 | 산출물 |
|---|---|---|
| `/find-gaps [폴더]` | 폴더 생략 시 `phd/` | `*_갭분석.md` → `gap_landscape_*.md` → `gap_strategy_*.md` |
| `/summarize-pdf "경로"` | PDF 절대경로 | `*_요약.md` (PDF와 같은 폴더) |
| `/search-lit "키워드"` | 검색어 | 인라인 합성 답변 (파일 저장 없음) |
| `/check-citations "경로"` | MD 파일 또는 폴더 | 심각도별 오류 목록 + 수정안 |
| `/review-draft "경로" [섹션]` | 초안 MD + 섹션명 | `*_review_YYYYMMDD.md` |
| `/coach-writing --analyze\|--multi\|--revise` | 모드별 인자 | `*_writing_analysis.md` / `multi_coaching_*.md` / `revise_output.md` |

---

## 실행 환경

```bash
cd "/mnt/c/Users/user/Documents/00.seohyun/Doctor/0. 졸업논문 준비/research-agents"
claude          # 새 세션
claude --continue  # 이전 세션 이어서
```

`.env` 파일에 `ANTHROPIC_API_KEY`, `REFERENCE_ROOT`, `MARKDOWN_DIR` 설정 필요.

---

## 갭 탐색 파이프라인 (핵심)

3단계 파이프라인. `/find-gaps` 커맨드가 자동 실행한다.

```
PDF 논문들
    ↓  [gap-explorer]  논문마다
*_갭분석.md 파일들
    ↓  [gap-synthesizer]  주제별로 묶어서
gap_landscape_*.md (갭 지형 지도)
    ↓  [gap-strategist]  지형 지도를 보고
gap_strategy_*.md (연구 모형 제안)
```

처리 대상 폴더: `config.py`의 `GAP_TARGET_FOLDERS = ["phd"]`.
`phd/` 하위 폴더 전체를 재귀 탐색한다. 경험적 연구·메타분석만 넣을 것.

---

## 파일 저장 위치

| 파일 | 저장 위치 |
|---|---|
| `*_갭분석.md` | PDF와 같은 폴더 |
| `*_요약.md` | PDF와 같은 폴더 |
| `gap_landscape_*.md` | `01. 논문 작성/00. 졸업 논문/gap_synthesis/` |
| `gap_strategy_*.md` | 동상 |
| `*_review_YYYYMMDD.md` | 초안 파일과 같은 폴더 |
| `multi_coaching_*.md`, `revise_output.md` | `WRITING_ANALYSIS_DIR/CURRENT_PAPER/` |

---

## 기존 Python 시스템 (병행 기간 참고)

마이그레이션 기간 동안 Python 시스템(`run.py`)도 사용 가능하다.

```bash
python3 run.py gap --batch                   # PDF 일괄 갭 분석
python3 run.py pdf --batch                   # PDF 일괄 요약
python3 run.py synth --pick                  # 갭 합성 (주제별 선택)
python3 run.py strategy --latest             # 연구 모형 제안
python3 run.py writing --analyze "경로"     # 글쓰기 분석
python3 run.py cite --all                    # 인용 형식 검사
python3 run.py search "키워드"              # 문헌 탐색
```

<!-- FABLIZE:BEGIN — run Opus like Fable (always-on router). Verified procedures only. Install/update: fablize setup.sh -->
## Operating mode (always on — auto-route by task signal)

Apply what the task signals; with no signal, baseline only. Read each pack only when needed. Routing: smallest matching discipline only, overlap only when genuinely multi-category, mimic observable behavior only.

- **[always]** Lead with the outcome · stay within the requested scope (no incidental refactors) · ground completion claims in this session's tool results · confirm before destructive or hard-to-reverse actions.
- **[2+ sequential stories]** Run `python3 /home/bella/.claude/plugins/cache/fablize/fablize/2.1.0/scripts/goals.py`: create → next → checkpoint (with evidence) → final verification gate (no completion without `--verify-cmd` and `--verify-evidence`). Run from the repo root; state in `./.fablize/` (resume with `status`). Skip for single-step tasks.
- **[debugging / test failure / unknown cause / review]** Follow `/home/bella/.claude/plugins/cache/fablize/fablize/2.1.0/packs/investigation-protocol.txt`: reproduce first → 3+ competing hypotheses → evidence per hypothesis → full causal chain → verify before/after → report rejected hypotheses.
- **[render/executable artifact: HTML, SVG, game, UI, chart]** Follow `/home/bella/.claude/plugins/cache/fablize/fablize/2.1.0/packs/verification-grounding-pack.txt` grounding loop: run it in the real renderer → observe the output → fix what you see → re-run. A static check is not observation.
- **[hard or ambiguous task]** Adaptive thinking scales with difficulty automatically. To go higher, recommend `/effort xhigh` to the user. Depth (capability) cannot be raised: if stuck 2+ times or out-of-spec discovery is needed, report the limit honestly and escalate.
<!-- FABLIZE:END -->
