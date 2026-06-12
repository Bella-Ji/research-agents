# PRD v2: 논문 작업용 Research Agent Team
**작성일:** 2026-06-12 (v1: 2026-06-08, 실제 에이전트 파일 검토 후 개정)
**대상:** 서현 (충남대 직업건강심리학 박사과정)
**목적:** 기존 Python 기반 research-agents 시스템을 Claude Code 서브에이전트 구조로 통합·고도화

---

## 0. v1 → v2 주요 변경 사항

| 항목 | v1 (가정) | v2 (실제 확인) |
|---|---|---|
| 에이전트 수 | 5개 | **커스텀 8개** + 외부 플러그인 1개 |
| gap-finder | 신규 개발 필요 | **이미 3단계 파이프라인으로 구현됨** (explorer → synthesizer → strategist) → 신규 개발 항목 삭제 |
| draft_reviewer | 기존 에이전트 | **미구현 스텁** (README + 빈 `__init__.py`) → 진짜 신규 개발 항목 |
| writing_analyzer | 미언급 | 존재 (글쓰기 논리 코칭, 3개 모드) → 명세 추가 |
| lit_search | 웹 문헌 검색 | **Obsidian vault 기반** (`*_요약.md` 스캔 + 키워드 스코어링 + Claude 합성) |
| citation_checker | LLM 에이전트로 전환 | **순수 규칙 기반 (API 미사용)** → 스크립트 유지가 정확도에 유리 |
| claude-scientific-writer | 마이그레이션 대상 | **외부 클론 저장소(플러그인)** → 마이그레이션 대상 아님, 의존성으로 취급 |
| 연구 컨텍스트 | 에이전트별 분산 | pdf_summarizer·gap_strategist 프롬프트에 하드코딩 → **공유 컨텍스트 파일로 분리** |

---

## 1. 현황 (실제 파일 기준)

### 1.1 기존 시스템
- **위치:** `research-agents/` (WSL Ubuntu, `run.py` 단일 진입점)
- **구현:** Python + Anthropic API 직접 호출 (lit_search는 haiku 모델 사용 확인)
- **공통 패턴:** `main.py`(CLI) + 역할 모듈 + `markdown_gen.py`(출력) → Obsidian vault에 MD 저장

### 1.2 에이전트 인벤토리

| 에이전트 | 상태 | 역할 | API | 비고 |
|---|---|---|---|---|
| `pdf_summarizer` | ✅ 구현 | PDF → Obsidian 요약 MD (frontmatter + 한줄요약 + 연결점 + 인용문장) | O | 연구 컨텍스트(부당대우→EE→WM, 변인사전) 프롬프트 하드코딩 |
| `lit_search` | ✅ 구현 | vault `*_요약.md` 스캔 → 키워드 스코어링(tags+3/title+2/folder+2/summary+1) → Claude 합성 | O | 웹 검색 아님 |
| `citation_checker` | ✅ 구현 | 초안 MD + Mendeley `library.bib` 대조 APA 7 검사 (인텍스트 + 참고문헌 목록 교차검사) | X | 규칙 기반, 가장 모듈화 잘됨 (parser/checker/bib_loader/reporter) |
| `gap_explorer` | ✅ 구현 | PDF 1편에서 저자 명시 갭 추출 (gap_type 7종 / model_type 6종 분류) | O | `*_갭분석.md` 생성 |
| `gap_synthesizer` | ✅ 구현 | 갭분석 MD들 → 갭 군집화 + 미검증 경로 + 방법론 갭 + 이론 빈도 (`gap_landscape_*.md`) | O | 모형 제안 안 함 (역할 분리) |
| `gap_strategist` | ✅ 구현 | 갭 지형 + **변인사전 내장** → 검증 가능 모형 ≤4개 제안, 교차지연 규칙 자동 판단, 기존 논문 경로(부당대우→EE→WM) 자동 제외 | O | 변인사전·교차지연 규칙이 코드에 하드코딩 |
| `writing_analyzer` | ✅ 구현 | 논문 논리 전개 방식 분석·코칭: `--analyze`(1:1 비교) / `--analyze-multi`(good_papers 종합) / `--revise`(문단 수정) | O | 2단계 파이프라인 |
| `draft_reviewer` | ❌ 미구현 | (계획) 이론 정합성·인용-주장 정렬·학술 어조·구조 검사, `type: theory` 태그 요약 자동 수집 | — | README에 설계만 존재 |
| `claude-scientific-writer` | 외부 | 학술 글쓰기 스킬 모음 (citation-management, scientific-writing, peer-review 등 20+ 스킬) | — | 클론된 외부 플러그인 (.git 포함) |

### 1.3 현재 한계
- 에이전트 간 파이프라인이 수동 (gap 3단계도 사람이 순서대로 `run.py` 실행)
- 연구 컨텍스트(변인사전, 교차지연 규칙, 연구 주제)가 pdf_summarizer와 gap_strategist에 **중복 하드코딩** → 연구 주제 변경 시 여러 파일 수정 필요
- Claude Code 서브에이전트·스킬 생태계와 미통합
- draft_reviewer 부재로 초안 검토 워크플로우 공백

---

## 2. 목표

1. 구현된 7개 에이전트를 Claude Code `.claude/agents/` 서브에이전트로 마이그레이션 (LLM 프롬프트는 에이전트 MD로, 결정적 로직은 스크립트로 분리)
2. 연구 컨텍스트를 `.claude/context/` 공유 파일로 일원화 (변인사전, 교차지연 규칙, 연구 주제, 이론 프레임)
3. gap 3단계 파이프라인을 오케스트레이터가 자동 연결 (slash command 1회로 explorer → synthesizer → strategist)
4. `draft_reviewer`를 서브에이전트로 신규 구현 (Python 코드 작성 불필요 — 에이전트 MD + 기존 README 설계 활용)
5. `citation_checker`는 Python 스크립트 유지, 서브에이전트가 Bash로 호출 후 결과 해석·수정 제안만 LLM 담당

---

## 3. 설계

### 3.1 디렉토리 구조 (목표)

```
research-agents/
├── .claude/
│   ├── agents/
│   │   ├── pdf-summarizer.md
│   │   ├── lit-searcher.md
│   │   ├── gap-explorer.md
│   │   ├── gap-synthesizer.md
│   │   ├── gap-strategist.md
│   │   ├── writing-analyzer.md
│   │   ├── draft-reviewer.md        ← 신규
│   │   └── citation-checker.md      ← 스크립트 호출 + 결과 해석 담당
│   ├── commands/
│   │   ├── summarize-pdf.md
│   │   ├── find-gaps.md             ← 3단계 파이프라인 자동 실행
│   │   ├── search-lit.md
│   │   ├── check-citations.md
│   │   ├── review-draft.md
│   │   └── coach-writing.md
│   └── context/
│       ├── research-profile.md      ← 연구 주제, 이론 프레임, 표본, 대상 저널
│       ├── variable-dictionary.md   ← 변인사전 (strategist.py에서 추출)
│       └── crosslag-rules.md        ← 교차지연 판단 규칙 + 제외 경로
├── scripts/
│   └── citation_checker/            ← 기존 Python 유지 (규칙 기반)
└── CLAUDE.md                        ← 오케스트레이터 지침 + 트리거 문구
```

### 3.2 마이그레이션 원칙

| 구분 | 처리 방식 | 해당 에이전트 |
|---|---|---|
| LLM 프롬프트 중심 | Python 제거, 에이전트 MD로 이관 (Claude Code의 Read/Glob/Grep이 extractor·reader 코드 대체) | gap_explorer, gap_synthesizer, gap_strategist, writing_analyzer, draft_reviewer |
| LLM + 전처리 혼합 | 프롬프트는 MD로, PDF 텍스트 추출 등은 Claude Code 내장 Read 활용 (PyMuPDF 의존 제거 가능 여부 검증) | pdf_summarizer, lit_search |
| 결정적 규칙 기반 | **Python 스크립트 유지**, 서브에이전트는 실행 + 결과 해석·수정안 제시만 | citation_checker |
| 외부 플러그인 | 마이그레이션 안 함. 필요 스킬만 선택적으로 참조/설치 | claude-scientific-writer |

### 3.3 에이전트 명세 (변경·신규 중심)

#### gap-explorer / gap-synthesizer / gap-strategist (3단계 파이프라인)
- 기존 분류 체계 유지: gap_type 7종(매개변인부재, 조절변인부재, 종단설계필요, 다층구조미적용, 표본한계, 메커니즘미규명, 복합경로미검증), model_type 6종(cross-lag ~ MSEM+moderation)
- strategist의 변인사전·교차지연 규칙·제외 경로는 `context/` 파일 참조로 전환
- `/find-gaps [PDF 폴더]` 실행 시: explorer 병렬 처리 → synthesizer 군집화 → strategist 모형 제안까지 자동 연결, 중간 산출물(갭분석 MD, landscape MD)은 기존과 동일하게 vault에 저장

#### draft-reviewer (신규 구현)
- 기존 README 설계 그대로 구현: ① `type: theory` 태그 요약 MD 자동 수집 → 이론 맥락 구성 ② 이론 정합성 검사 ③ 인용-주장 정렬 (근거 없는 주장 감지) ④ 학술 어조 (hedging 등) ⑤ 구조 검사 (topic sentence → 근거 → 연결) ⑥ Before/After 수정 제안
- citation-checker와 역할 구분: 인용 **형식**은 citation-checker, 인용 **내용 정합성**은 draft-reviewer

#### citation-checker (하이브리드)
- Python 스크립트가 형식 오류 검출 → 서브에이전트가 리포트를 읽고 우선순위 정리 + 일괄 수정안 제시
- 장점: 규칙 검사의 정확도/재현성 유지 + LLM의 맥락 판단 결합

#### writing-analyzer
- 3개 모드를 slash command 인자로 통합: `/coach-writing --multi [섹션]`, `/coach-writing --revise [문단]`
- good_papers 종합 코칭 결과(`multi_coaching_*.md`)를 revise 모드가 기준으로 재사용하는 기존 2단계 구조 유지

### 3.4 Slash Command 설계

| 커맨드 | 동작 | 호출 에이전트 |
|---|---|---|
| `/summarize-pdf [경로\|--batch]` | PDF → Obsidian 요약 MD | pdf-summarizer |
| `/find-gaps [폴더]` | 갭 추출 → 지형 지도 → 모형 제안 (전 과정 자동) | gap-explorer → gap-synthesizer → gap-strategist |
| `/search-lit [키워드]` | vault 요약 스캔 + 합성 | lit-searcher |
| `/check-citations [파일]` | 스크립트 실행 + 수정안 | citation-checker |
| `/review-draft [파일\|섹션]` | 초안 검토 (이론 정합성·논리·어조) | draft-reviewer |
| `/coach-writing [모드] [대상]` | 글쓰기 논리 코칭 | writing-analyzer |

---

## 4. 단계별 실행 계획

**Phase 1 — 컨텍스트 분리 (반나절)**
strategist.py와 summarizer.py에서 변인사전·교차지연 규칙·연구 프로필을 추출해 `context/` 3개 파일 생성. 이후 모든 단계의 기반.

**Phase 2 — gap 파이프라인 마이그레이션 (1일)**
효과가 가장 크고 구조가 명확한 3단계 파이프라인부터. `/find-gaps` 커맨드까지 완성해 기존 Python 결과와 출력 비교 검증.

**Phase 3 — pdf-summarizer, lit-searcher (1일)**
PDF Read로 PyMuPDF 대체 가능 여부 검증. lit_search 스코어링은 Grep 기반으로 단순화하거나 스크립트 유지 중 택일.

**Phase 4 — draft-reviewer 신규 구현 + citation-checker 하이브리드 (1일)**

**Phase 5 — writing-analyzer 마이그레이션 + CLAUDE.md 오케스트레이터 정비 (반나절)**

**검증 기준:** 각 Phase마다 동일 입력에 대해 기존 Python 출력과 비교, vault 저장 경로·파일명 규칙(`*_요약.md`, `*_갭분석.md`, `gap_landscape_*`, `gap_strategy_*`) 유지 확인.

---

## 5. 리스크 및 결정 필요 사항

1. **PyMuPDF 의존**: Claude Code의 PDF Read가 스캔본·복잡 레이아웃에서 충분한지 검증 필요. 불충분 시 extractor.py를 scripts/로 이동해 유지.
2. **API 비용**: 서브에이전트 병렬 실행(특히 `/find-gaps` batch) 시 토큰 사용량 증가. explorer는 haiku급 모델 지정 권장 (에이전트 MD frontmatter `model` 필드).
3. **run.py 병행 운영**: 마이그레이션 기간 동안 기존 CLI 유지 (Phase별 검증용). 전체 검증 후 제거 여부 결정.
4. **claude-scientific-writer 활용 범위**: citation-management, scientific-writing, peer-review 스킬은 유용하나 의료(clinical) 계열 스킬은 불필요 — 필요 스킬만 `.claude/skills/`로 선별 복사할지 결정 필요.
