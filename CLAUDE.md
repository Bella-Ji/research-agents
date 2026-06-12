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

## 실행 환경

```bash
# 프로젝트 루트로 이동 후 실행
cd "/mnt/c/Users/user/Documents/00.seohyun/Doctor/0. 졸업논문 준비/research-agents"
python3 run.py [에이전트] [옵션]
```

`.env` 파일에 `ANTHROPIC_API_KEY`, `REFERENCE_ROOT`, `MARKDOWN_DIR` 설정 필요.

---

## 갭 탐색 파이프라인 (핵심)

논문 갭을 찾아 졸업논문 연구 모형을 도출하는 3단계 파이프라인.

```
PDF 논문들
    ↓  [gap_explorer]  논문마다
*_갭분석.md 파일들
    ↓  [gap_synthesizer]  주제별로 묶어서
gap_landscape_*.md (갭 지형 지도)
    ↓  [gap_strategist]  지형 지도를 보고
gap_strategy_*.md (연구 모형 제안)
```

### 실행 주기

| 단계 | 언제 실행 |
|---|---|
| gap_explorer | 논문 추가할 때마다 |
| gap_synthesizer | 논문이 어느 정도 쌓인 후, 주제별로 |
| gap_strategist | synthesizer 실행 후 |

---

## gap_explorer

### 역할
PDF 논문 1편을 읽고, 저자가 Limitations / Future Research에 직접 쓴 연구 갭을 추출한다.
추측하거나 확장하지 않는다. 저자가 명시한 내용만 가져온다.

### 입출력
- **입력**: PDF 논문
- **출력**: PDF와 같은 폴더에 `*_갭분석.md` 생성

### 출력 구조
```markdown
## 🔍 연구 갭
### 갭 1 — [gap_type] [model_type_needed]
- KO / EN 요약
- 원문: > "저자가 쓴 영어 문장 직접 인용"

## 📚 이론 프레임
```

### gap_type 분류
- `매개변인부재` — how/why 설명하는 매개 없음
- `조절변인부재` — 경계 조건 검증 안 됨
- `종단설계필요` — 횡단 연구라 시간 순서 불명
- `다층구조미적용` — within/between 수준 분리 안 됨
- `표본한계` — 특정 직군/국가에 한정
- `메커니즘미규명` — 경로는 있지만 작동 원리 모름
- `복합경로미검증` — 여러 변인 동시 검증 없음

### model_type_needed 분류
- `cross-lag` — 시간 지연 경로 필요
- `cross-lag+moderation` — 시간 지연 + 조절
- `mediation` — 매개 경로
- `moderated_mediation` — 조절된 매개
- `MSEM` — 다층 구조방정식 (횡단)
- `MSEM+moderation` — 다층 + cross-level interaction

### 실행 명령
```bash
python3 run.py gap --single "경로/논문.pdf"  # 단일 파일
python3 run.py gap --batch                   # 미처리 전체 일괄
python3 run.py gap --pick                    # 대화형 선택
python3 run.py gap --watch                   # 새 파일 자동 감지
```

### 처리 규칙
- 학위논문(박사/석사)은 자동 건너뜀 — 파일명에 "박사논문" 포함 시 fallback 처리됨
- 표본이 간호사가 아닌 논문도 동등하게 처리 (직군 무관 — 교사, 사무직, 제조업 등 모두 OK)
- 메타분석 포함 가능 — Future Research 섹션이 풍부해서 오히려 갭이 잘 나옴
- 이미 처리된 파일은 재처리 안 함 (`--single`은 force 재처리)
- 처리 대상 폴더: `config.py`의 `GAP_TARGET_FOLDERS`에 지정된 폴더만 탐색

### 폴더 관리 (중요)
**현재 처리 대상 폴더** (`config.py` → `GAP_TARGET_FOLDERS`):
```python
GAP_TARGET_FOLDERS = ["phd"]
```

`phd/` 하위 폴더 전체를 재귀 탐색한다. 새 주제 폴더(예: `phd/JD-R/`)를 만들고 PDF를 넣으면 자동으로 처리 대상에 포함된다.

**주의**: 방법론 개관 논문(DSEM 문법 설명, 교재, 코드북 등)은 갭이 나오지 않으므로 `phd/` 안에 넣지 말 것.
경험적 연구(empirical study)와 메타분석만 `phd/`에 관리할 것.

---

## gap_synthesizer

### 역할
gap_explorer가 만든 `*_갭분석.md` 파일 여러 개를 읽고,
공통 패턴을 군집화하여 갭 지형 지도(gap landscape)를 만든다.
**모형을 제안하지 않는다.** 갭을 분류하고 정리하는 역할만 한다.

### 입출력
- **입력**: `*_갭분석.md` 파일들 (gap_explorer 출력)
- **출력**: `SYNTHESIS_DIR/gap_landscape_YYYYMMDD_HHMMSS.md`

### 출력 구조
```markdown
## 🗺️ 요약
## 🔍 갭 군집         ← 공통 패턴 군집 (군집명, 유형, 이론, 해당 논문)
## 🔗 미검증 경로     ← 여러 논문에서 언급됐지만 검증 안 된 경로
## 🔬 방법론적 갭     ← DSEM 미사용, lag 구조 미검증 등
## 📚 이론 빈도       ← 이론별 등장 논문 수
```

### 실행 명령
```bash
python3 run.py synth --all              # 전체 갭분석 파일 종합
python3 run.py synth --pick             # 논문 직접 선택 (주제별 묶기 가능)
python3 run.py synth --folder "폴더명"  # 특정 폴더만
```

### --pick 선택 흐름
```
폴더 단위 선택 → 그 안에서 논문 개별 선택
예: DSEM-empirical 폴더에서 3편, COR 폴더에서 2편 → 합쳐서 종합
```

### 기제
선택한 논문들의 갭분석 파일 전체를 하나의 프롬프트에 담아 Claude에게 한 번에 전달한다.
Claude가 여러 논문을 동시에 보면서 공통 패턴을 찾는다.

### 활용 패턴
```
synth --pick → EE-회복 관련 논문만 선택 → gap_landscape_EE.md
synth --pick → DSEM 방법론 논문만 선택 → gap_landscape_DSEM.md
→ 주제별 landscape를 여러 개 만들어 축적 가능
```

### 참고
- 파일당 2,500자까지 읽음 (토큰 비용 관리)
- 15편 초과 시 비용 경고
- 표본이 다른 논문도 동등하게 처리

---

## gap_strategist

### 역할
gap_synthesizer가 만든 `gap_landscape_*.md`를 읽고,
연구자의 데이터로 실제 채울 수 있는 연구 갭과 모형을 제안한다.

### 입출력
- **입력**: `gap_landscape_*.md` 파일들 (gap_synthesizer 출력)
- **출력**: `SYNTHESIS_DIR/gap_strategy_YYYYMMDD_HHMMSS.md`

### 출력 구조
```markdown
## ⭐ 최우선 추천     ← 이론적 기여도·데이터 적합성·방법론 차별성 종합
## 🗺️ 갭 커버리지    ← Full / Partial / None 판단 + 이유
## 🧩 제안 모형       ← 최대 4개, 실제 변인코드 사용
## 🚫 제외 경로       ← 기존 논문 겹침 or 시간 역행 경로
```

### 실행 명령
```bash
python3 run.py strategy --latest  # 가장 최근 landscape 사용
python3 run.py strategy --pick    # landscape 선택 (여러 개 조합 가능)
python3 run.py strategy --all     # 전체 landscape 종합
```

### 활용 패턴
```
# EE-회복 landscape만 보고 싶을 때
strategy --pick → gap_landscape_EE.md 선택

# 전체 landscape 종합해서 모형 받을 때
strategy --all → 모든 landscape 동시 투입
```

### 내장 규칙

**교차지연 가능 여부**

| 경로 | 판단 | 이유 |
|---|---|---|
| AW 변인 ↔ AW 변인 | ✅ | 동시점, 교차지연 가능 |
| AW → BW (lag-1) | ✅ | 24시간 순방향 |
| ND_REC ↔ AW 변인 | ✅ | ND_REC는 전날 밤 회고, 실질적 AW 동시점 |
| BW → AW | ❌ | 시간 역행 |
| ND_REC ↔ ND_SBR | ❌ | 암묵적 시간 선행 있음 |
| jb_SQ | 통제만 | 단방향 통제변인 |

**자동 제외 경로**
- `부당대우 → EE → WM` (기존 투고 논문 주제)
- `부당대우 → WM` (기존 논문 직접 효과)

**갭 커버리지 기준**
- 판단 기준: 우리 변인 구조로 검증 가능한가
- 표본 동일 여부는 고려하지 않음

---

## 변인 요약

```
AW (퇴근 후):  t_MPFs/m, t_MBSs/m, t_MBCs/m, t_MSTs/m  ← 부당대우
               t_EE                                        ← 정서적 소진
               t_ABRC, t_ABDC, t_JC                       ← 잡크래프팅

BW (다음날 아침): jb_SQ, ND_REC, ND_SBR, ND_WM           ← 회복·의미감

L2 (개인차):   p_JB, p_EE, p_PA, p_DP                    ← 직무탈진
               p_JC, p_ABRC, p_ABDC                       ← 잡크래프팅
               p_WM, p_WL                                  ← 의미감·업무부하
               PSC, PCEO, PCEF                             ← 조직 변인
```

---

## 파일 저장 위치

| 파일 | 저장 위치 |
|---|---|
| `*_갭분석.md` | PDF와 같은 폴더 |
| `gap_landscape_*.md` | `SYNTHESIS_DIR` (01. 논문 작성/00. 졸업 논문/gap_synthesis/) |
| `gap_strategy_*.md` | `SYNTHESIS_DIR` (동일) |

---

## 기타 에이전트

| 명령 | 역할 |
|---|---|
| `python3 run.py pdf --batch` | PDF → Obsidian 요약 MD (WM paper용) |
| `python3 run.py writing --analyze "경로"` | 논문 글쓰기 방식 분석 |
| `python3 run.py cite --all` | 인텍스트 인용 형식 검사 |
| `python3 run.py search "키워드"` | Vault 내 문헌 탐색 |
