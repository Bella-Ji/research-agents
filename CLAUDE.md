# research-agents — CLAUDE.md

박사 졸업논문 작성을 위한 연구 자동화 에이전트 모음.
이 프로젝트에서 작업할 때 이 파일을 먼저 읽을 것.

---

## 연구 맥락

- **표본**: 한국 간호사 대상 일기연구 (AW-BW 교대 설계, 약 31일, N=284)
- **기존 투고 논문 (WM paper)**: 부당대우 → 정서적 소진(EE) → 일의 의미감(WM), MSEM 분석
- **졸업논문 방향**: DSEM으로 확장 — 시간 역동성, 자기회귀, 교차지연 구조 추가
- **핵심 제약**: 부당대우→EE→WM 경로는 기존 논문과 겹치므로 졸업논문 모형에서 제외

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
