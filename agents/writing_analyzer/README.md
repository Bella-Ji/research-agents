# writing_analyzer — 논문 글쓰기 방식 분석 에이전트

학술 논문의 **논리 전개 방식**을 분석하여 내 초안 글쓰기를 코칭하는 에이전트.  
연구 내용(what)이 아닌 논리를 풀어가는 방식(how)에 집중한다.

---

## 기능 3가지

### 1. `--analyze` — 논문 1편 vs 내 초안
PDF 1편을 읽고 내 초안 섹션과 1:1 비교 분석.

```bash
python run.py writing --analyze "C:/경로/논문.pdf"
python run.py writing --analyze "C:/경로/논문.pdf" --sections introduction method
```

### 2. `--analyze-multi` — 여러 논문 종합 코칭
`good_papers/` 폴더의 논문들을 모두 읽고 공통 논리 패턴을 종합하여 코칭 보고서 생성.

```bash
python run.py writing --analyze-multi --sections theoretical_implications
python run.py writing --analyze-multi                  # draft에 있는 전체 섹션
```

### 3. `--revise` — 문단 수정 제안
`revise_input.md`에 문단을 붙여넣으면 논리 진단 + 구체적 수정안 제시.  
(또는 Claude Code에 문단을 직접 붙여넣고 요청해도 됨)

```bash
python run.py writing --revise theoretical_implications
```

---

## 동작 방식

### `--analyze-multi` 2단계 파이프라인

```
good_papers/ 안의 PDF 전체 텍스트 추출
        ↓
[1단계] 논문별 해당 섹션 논리 패턴 추출 (논문당 API 호출 1회)
        ↓
[2단계] 전체 패턴 종합 → 내 초안과 비교 → 코칭 보고서 생성
        ↓
multi_coaching_{섹션키}.md 저장
```

### `--revise` 파이프라인

```
revise_input.md 읽기
        ↓
multi_coaching_{섹션키}.md 로드 (있으면 코칭 기준으로 활용)
        ↓
Claude API: 논리 진단 + 수정안 생성
        ↓
revise_output.md 저장 (매 실행마다 덮어쓰기)
```

---

## 폴더 구조

```
writing_analysis/
  WM paper/                          ← CURRENT_PAPER 기준 서브폴더
    good_papers/                     ← 좋은 논문 PDF 여기에 넣기
      Smith2024.pdf
      Jones2023.pdf
    revise_input.md                  ← 수정 요청 문단 붙여넣는 파일
    revise_output.md                 ← 수정 제안 결과 (자동 생성)
    multi_coaching_introduction.md   ← --analyze-multi 결과
    Pan_et_al_writing_analysis.md    ← --analyze 결과
  [다음 논문 주제]/                  ← 논문 바뀔 때 새 서브폴더 추가
    good_papers/
    ...
```

---

## 출력 MD 구조

### `--analyze-multi` 결과 (`multi_coaching_{섹션}.md`)

```markdown
## 🗺️ 우수 논문들의 공통 논리 청사진
## 🔍 공통 논리 구성 방식
## 📝 내 초안 평가
## ❌ 내 초안에서 빠진 논리적 요소
## 🔧 우선 개선 방향    ← what / why / how
## ✨ 지금 바로 적용할 것
```

### `--revise` 결과 (`revise_output.md`)

```markdown
## 📋 원본 문단
## 🔍 논리 진단
## ❌ 발견된 문제
## ✏️ 수정안              ← 원문과 같은 언어(영어/한국어)로 출력
## 🔄 변경 사항 및 이유
## 💡 다른 방식의 첫 문장
```

---

## 설정 (`.env`)

```
WRITING_ANALYSIS_DIR=C:/.../ 01. 논문 작성/writing_analysis
DRAFT_DIR=C:/.../WM paper/draft        ← 현재 쓰는 논문 초안 폴더
CURRENT_PAPER=WM paper                 ← 현재 쓰는 논문 이름 (서브폴더명)
```

> 다른 논문을 쓸 때는 `DRAFT_DIR`과 `CURRENT_PAPER` 두 줄만 바꾸면 된다.

---

## 섹션 키 목록

| 키 | 해당 draft 파일 |
|---|---|
| `abstract` | `0. Abstract.md` |
| `introduction` | `1. introduction.md` |
| `theoretical_background` | `2. Theoretical background.md` |
| `method` | `3. Method.md` |
| `results` | `4. Results.md` |
| `discussion` | `5. Discussion.md` |
| `theoretical_implications` | `6. Theoretical implications.md` |
| `practical_implications` | `7. Practical implications.md` |
| `limitations` | `8. Limitations and future research directions.md` |
| `conclusions` | `9. Conclusions.md` |

---

## 파일 구성

```
writing_analyzer/
├── main.py          # 실행 진입점 (--analyze / --analyze-multi / --revise)
├── analyzer.py      # Claude API 호출 및 분석 로직
├── draft_reader.py  # Obsidian draft 폴더에서 섹션별 MD 읽기
├── report_gen.py    # 분석 결과 MD 파일 생성
└── __init__.py
```

### 주요 함수

| 파일 | 함수 | 역할 |
|---|---|---|
| analyzer.py | `analyze_section()` | 논문 1편 × 섹션 1개 분석 |
| analyzer.py | `extract_section_logic()` | 멀티 분석용 논리 패턴 추출 |
| analyzer.py | `synthesize_and_coach()` | 패턴 종합 → 코칭 보고서 생성 |
| analyzer.py | `revise_paragraph()` | 문단 진단 + 수정안 생성 |
| draft_reader.py | `read_draft_sections()` | draft 폴더에서 섹션 MD 읽기 |
| report_gen.py | `generate_report()` | 1편 분석 결과 MD 저장 |
| report_gen.py | `generate_multi_report()` | 종합 코칭 보고서 MD 저장 |
| report_gen.py | `generate_revision_report()` | 수정 제안 MD 저장 |
