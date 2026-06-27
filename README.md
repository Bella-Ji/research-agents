# research-agents 사용 가이드

> 박사 졸업논문 작성을 위한 Claude Code 서브에이전트 시스템.
> "이 시스템을 처음 보는 미래의 나"를 위한 매뉴얼.

---

## 1. 시스템 한눈에 보기

### 3층 구조

```
슬래시 커맨드 (/find-gaps, /summarize-pdf, …)
        ↓  호출
서브에이전트 (gap-explorer, pdf-summarizer, …)
        ↓  참조
context 파일 (.claude/context/*.md) + 스킬
```

- **커맨드**: 사용자의 진입점. 인자를 받아 적절한 에이전트를 호출한다.
- **에이전트**: 실제 작업을 수행하는 전문가. context 파일을 SSOT로 참조한다.
- **context 파일**: 이론·변인·규칙의 단일 진실 공급원. 이것이 모든 에이전트의 기준이다.

### 에이전트 전체 목록

| 에이전트 | 역할 | 모델 |
|---|---|---|
| `gap-explorer` | PDF 1편 → Limitations/Future Research 갭 추출 → `*_갭분석.md` | Haiku |
| `gap-synthesizer` | 갭분석.md 여러 개 → 공통 패턴 군집화 → `gap_landscape_*.md` | 기본 |
| `gap-strategist` | gap landscape → 연구 모형 제안 → `gap_strategy_*.md` | 기본 |
| `pdf-summarizer` | PDF 1편 → Obsidian 요약 MD → `{stem}_요약.md` | Haiku |
| `lit-searcher` | vault `*_요약.md` Grep → 키워드 문헌 탐색·합성 | Haiku |
| `citation-checker` | APA 7판 인용 형식 검사 (스크립트 실행 + 심각도 정리) | 기본 |
| `draft-reviewer` | 초안 섹션 4축 검토 (이론·인용·어조·구조) → `*_review_*.md` | 기본 |
| `coach-writing` | 논리 전개 방식 분석 → 글쓰기 코칭 보고서 | 기본 |
| `structure-architect` | 논문 뼈대 설계·검증·STRUCTURE.md 관리 | 기본 |

---

## 2. 빠른 시작

```bash
# 폴더 진입
cd "/mnt/c/Users/user/Documents/00.seohyun/Doctor/0. 졸업논문 준비/research-agents"

# 새 세션 시작
claude

# 이전 세션 이어서 (권장)
claude --continue

# 등록된 에이전트 확인
/agents
```

**전제조건**: `.env` 파일에 아래 환경변수 설정 필요.

```
ANTHROPIC_API_KEY=sk-ant-...
REFERENCE_ROOT=/mnt/c/Users/user/Documents/00.seohyun/Doctor/0. 졸업논문 준비/02. reference
MARKDOWN_DIR=...  # Obsidian MD 저장 폴더
```

---

## 3. 사용법

### 3-a. 슬래시 커맨드

| 커맨드 | 인자 | 기본값 | 산출물 위치 |
|---|---|---|---|
| `/find-gaps [폴더]` | PDF 폴더 경로 | `phd/` 전체 | `*_갭분석.md`(PDF 옆) + `gap_landscape_*.md` + `gap_strategy_*.md` (gap_synthesis/) |
| `/summarize-pdf [경로\|--batch]` | PDF 경로 또는 `--batch` | — | `{stem}_요약.md` (PDF 옆) |
| `/search-lit "키워드"` | 검색어 | — | 인라인 합성 답변 |
| `/check-citations "경로"` | MD 파일 또는 폴더 | — | 심각도별 오류 목록 + 수정안 (인라인) |
| `/review-draft "경로" [섹션]` | 초안 MD + 섹션명 | 파일 전체 | `{파일명}_review_YYYYMMDD.md` (초안 옆) |
| `/coach-writing --analyze "PDF경로"` | PDF 경로 | — | `{제목}_writing_analysis.md` (WRITING_DIR/) |
| `/coach-writing --multi [섹션키]` | 섹션키 | 전체 섹션 | `multi_coaching_{섹션키}.md` (WRITING_DIR/) |
| `/coach-writing --revise 섹션키` | 섹션키 | — | `revise_output.md` (WRITING_DIR/) |
| `/outline-dissertation` | — | — | 아웃라인 + STRUCTURE.md 갱신 |

**실제 예시:**

```
/find-gaps                                    # phd/ 전체 갭 분석
/find-gaps "02. reference/phd/burnout"        # 특정 폴더만

/summarize-pdf "/mnt/c/.../Bakker2023.pdf"
/summarize-pdf --batch                        # 미처리 PDF 전체

/search-lit "burnout recovery"
/search-lit "DSEM methodology"

/check-citations "/mnt/c/.../WM paper/draft/5. Discussion.md"
/review-draft "/mnt/c/.../5. Discussion.md" "Discussion"
/coach-writing --multi theoretical_implications
/coach-writing --revise discussion
```

### 3-b. 자연어 라우팅

Claude Code가 아래 트리거를 인식하면 자동으로 해당 커맨드를 실행한다.

| 말하는 방식 | 내부 라우팅 |
|---|---|
| "이 논문 요약해줘", "PDF 요약" | `/summarize-pdf` |
| "갭 찾아줘", "연구 갭 분석" | `/find-gaps` |
| "관련 논문 찾아줘", "vault에서 검색" | `/search-lit` |
| "인용 검사", "APA 형식 확인" | `/check-citations` |
| "초안 검토해줘", "논문 피드백" | `/review-draft` |
| "글쓰기 코칭", "논리 분석해줘" | `/coach-writing` |
| "논문 구조 짜줘", "아웃라인" | `/outline-dissertation` |

### 3-c. 에이전트 직접 지명

파이프라인 중 한 단계만 재실행하고 싶을 때:

```
gap-synthesizer 에이전트 써서 gap_landscape_EE.md 다시 만들어줘
— 이번엔 EE 관련 갭분석 파일들만 골라서

pdf-summarizer로 이 PDF 요약해줘: "/mnt/c/.../Sonnentag2018.pdf"

coach-writing 에이전트로 discussion 섹션 revise_output 만들어줘
```

---

## 4. 대표 워크플로우 시나리오

### 시나리오 1 — 새 논문 1편 받았을 때

```
# 1. 요약 생성
/summarize-pdf "/mnt/c/.../새논문.pdf"

# 2. vault 연관 논문 확인
/search-lit "회복경험 번아웃"  ← 새 논문 주제 키워드로 탐색

# 3. 갭이 있는 논문이면 갭 분석도 실행 (개별 재처리)
/find-gaps --force "/mnt/c/.../새논문.pdf"
```

### 시나리오 2 — 연구 주제 탐색 (갭 파이프라인)

```
# 1. phd/ 폴더 PDF 전체 갭 분석 (새 파일만 처리)
/find-gaps

# 2. 결과 확인
→ gap_synthesis/gap_landscape_*.md  ← 갭 군집 지도
→ gap_synthesis/gap_strategy_*.md   ← 추천 연구 모형

# 특정 주제 폴더만 따로 묶고 싶을 때:
gap-synthesizer 에이전트 써서 phd/burnout/ 폴더 갭분석 파일만 골라 landscape 만들어줘
```

### 시나리오 3 — 초안 검토 플로우

```
# 1. 인용 형식 검사
/check-citations "/mnt/c/.../WM paper/draft/5. Discussion.md"

# 2. 내용 검토 (이론 정합성·인용-주장·어조·구조)
/review-draft "/mnt/c/.../5. Discussion.md" "Discussion"

# 3. 글쓰기 논리 개선
/coach-writing --multi discussion       ← good_papers 기준 먼저 생성
/coach-writing --revise discussion      ← 내 문단 수정 제안 받기
```

---

## 5. context 파일 관리 규칙

`.claude/context/` 아래 3개 파일이 단일 진실 공급원(SSOT).
에이전트들은 이 파일을 읽어 이론·변인·규칙을 판단한다. 하드코딩하지 않는다.

| 파일 | 역할 | 수정하는 경우 |
|---|---|---|
| `research-profile.md` | 이론 프레임 표, 표본, 분석 방법, 에이전트별 관점 | 이론 추가·수정 시 |
| `variable-dictionary.md` | 변인코드 사전 (t_EE, ND_WM 등) | 변인 추가·변경 시 |
| `crosslag-rules.md` | DSEM 교차지연 가능 여부 판단 규칙 | 설계 변경 시 |

**변인사전 동기화 절차**:
1. Obsidian 원본(또는 연구 노트)에서 변인 정보 확인
2. `variable-dictionary.md` 직접 편집
3. 에이전트들은 다음 실행부터 자동으로 반영 (에이전트 MD 수정 불필요)

---

## 6. 산출물 위치 지도

| 작업 | 산출물 | 저장 위치 |
|---|---|---|
| `/find-gaps` | `{논문명}_갭분석.md` | PDF와 같은 폴더 |
| `/find-gaps` | `gap_landscape_YYYYMMDD_HHMMSS.md` | `01. 논문 작성/00. 졸업 논문/gap_synthesis/` |
| `/find-gaps` | `gap_strategy_YYYYMMDD_HHMMSS.md` | 동상 |
| `/summarize-pdf` | `{stem}_요약.md` | PDF와 같은 폴더 |
| `/review-draft` | `{파일명}_review_YYYYMMDD.md` | 초안 파일과 같은 폴더 |
| `/coach-writing --analyze` | `{논문명}_writing_analysis.md` | `WRITING_ANALYSIS_DIR/CURRENT_PAPER/` |
| `/coach-writing --multi` | `multi_coaching_{섹션}.md` | 동상 |
| `/coach-writing --revise` | `revise_output.md` | 동상 |
| `/search-lit` | (파일 없음) | 인라인 답변 |
| `/check-citations` | (파일 없음, `--save` 옵션 시 저장) | 인라인 또는 대상 파일 옆 |

---

## 7. 문제 해결

**에이전트가 `/agents`에 안 보임**
→ `/exit` 후 `claude --continue` 재시작. 새 에이전트 파일은 세션 재시작 후 인식된다.

**인용 자체검증 실패 보고가 뜰 때**
→ pdf-summarizer가 PDF에서 추출한 인용 텍스트와 원문이 불일치한다는 신호. 에이전트가 인용을 직접 수정하거나 생략했을 수 있다. 해당 논문 `*_요약.md`의 "📎 인용 가능한 문장" 섹션을 열어 원문 PDF와 대조 확인.

**gap-explorer가 갭을 0개 찾음**
→ 정상 케이스: 방법론 개관 논문, 서평, 교재는 Limitations 섹션이 없어 갭이 나오지 않는다. `phd/` 폴더에는 경험적 연구와 메타분석만 넣을 것.

**coach-writing --revise가 기준 파일 없다고 안내함**
→ `--multi 섹션키`를 먼저 실행해 `multi_coaching_{섹션}.md`를 만들면 더 정확한 코칭이 가능하다. 파일 없이도 기본 진단은 실행된다.

**기존 Python 시스템으로 같은 작업 돌리기 (병행 기간)**

```bash
python3 run.py gap --batch          # 갭 분석 (gap-explorer 상당)
python3 run.py synth --pick         # 갭 합성 (gap-synthesizer 상당)
python3 run.py strategy --latest    # 모형 제안 (gap-strategist 상당)
python3 run.py pdf --batch          # PDF 요약 (pdf-summarizer 상당)
python3 run.py search "키워드"     # 문헌 탐색 (lit-searcher 상당)
python3 run.py cite --all           # 인용 검사 (citation-checker 상당)
python3 run.py writing --analyze "경로"  # 글쓰기 분석 (coach-writing 상당)
```

자세한 Python 시스템 문서: `README_python.md` 참고.

---

## 파일 구조

```
research-agents/
├── CLAUDE.md                 # 오케스트레이터 (라우팅 규칙, 에이전트 목록)
├── README.md                 # 이 파일
├── README_python.md          # 기존 Python 시스템 문서 (병행 기간 참고용)
├── run.py                    # Python 시스템 진입점 (병행 기간 유지)
├── config.py                 # 공통 설정 (.env 로드)
├── .env                      # API 키 + 경로 설정 (git 제외)
├── .claude/
│   ├── agents/               # 서브에이전트 정의 MD (9개)
│   ├── commands/             # 슬래시 커맨드 정의 MD
│   └── context/              # SSOT — 이론·변인·규칙 (3개)
├── agents/                   # Python 에이전트 모듈 (병행 기간 유지)
└── scripts/
    └── citation_checker/     # citation-checker 에이전트가 호출하는 스크립트
```
