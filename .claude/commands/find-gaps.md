---
description: PDF 폴더에 대해 갭 탐색 3단계 파이프라인(gap-explorer → gap-synthesizer → gap-strategist)을 자동 실행한다
argument-hint: "[PDF 폴더 경로] (생략 시 phd 폴더 전체) [--force]"
---

갭 탐색 3단계 파이프라인을 자동 실행한다: 논문별 갭 추출 → 갭 지형 지도 → 연구 모형 제안.

## 경로 설정 (config.py / .env 기준)

- **REFERENCE_ROOT**: `/mnt/c/Users/user/Documents/00.seohyun/Doctor/0. 졸업논문 준비/02. reference`
- **기본 대상 폴더** (인자 생략 시, config.py `GAP_TARGET_FOLDERS = ["phd"]`): `{REFERENCE_ROOT}/phd` 하위 재귀 탐색
- **SYNTHESIS_DIR** (landscape/strategy 저장): `/mnt/c/Users/user/Documents/00.seohyun/Doctor/0. 졸업논문 준비/01. 논문 작성/00. 졸업 논문/gap_synthesis`

## 인자

`$ARGUMENTS`
- 첫 번째 인자: PDF 폴더 경로 (절대경로 또는 REFERENCE_ROOT 기준 상대경로). 생략 시 기본 대상 폴더 사용
- `--force`: 이미 갭분석 파일이 있는 PDF도 재처리

## 실행 절차

### Step 1 — gap-explorer (논문별, 병렬)

1. 대상 폴더에서 Glob으로 `**/*.pdf` 수집
2. `--force`가 아니면, 같은 폴더에 `{stem}_갭분석.md`가 이미 있는 PDF는 제외
3. 처리 대상이 0편이면 그 사실을 보고하고 Step 2로 넘어갈지 사용자에게 확인 (기존 갭분석 파일만으로 종합할 수도 있음)
4. 남은 PDF마다 **gap-explorer 서브에이전트를 1편당 1개씩 병렬 실행** (Agent 도구, `subagent_type: gap-explorer`). 프롬프트에는 PDF 절대경로와 force 여부를 전달
5. 각 explorer의 보고(생성 파일, 갭 개수)를 취합하여 중간 보고

### Step 2 — gap-synthesizer (종합)

1. 대상 폴더 하위의 **모든** `*_갭분석.md`를 Glob으로 수집 (이번에 새로 만든 것 + 기존 것 포함)
2. **gap-synthesizer 서브에이전트를 1개 실행** (`subagent_type: gap-synthesizer`). 프롬프트에 갭분석 파일 목록(절대경로)을 전달
3. 생성된 `gap_landscape_*.md` 경로를 확보

### Step 3 — gap-strategist (모형 제안)

1. **gap-strategist 서브에이전트를 1개 실행** (`subagent_type: gap-strategist`). 프롬프트에 Step 2에서 생성된 landscape 파일의 절대경로를 전달
2. 생성된 `gap_strategy_*.md` 경로를 확보

### 최종 보고

다음을 정리해 보고한다:
- 처리한 PDF 수 / 스킵한 PDF 수
- 생성된 갭분석 파일 목록
- landscape 파일 경로와 갭 군집 수
- strategy 파일 경로, 제안 모형 목록, 최우선 추천 모형

## 주의

- 학위논문(파일명에 박사/석사/thesis 등)은 explorer가 자동으로 fallback 처리한다
- 방법론 개관 논문은 갭이 나오지 않으므로 결과가 비어 있어도 정상
- `.gap_exploration_history.json`은 건드리지 않는다 (run.py 전용)
- 기존 `python3 run.py gap/synth/strategy` CLI는 검증용으로 병행 유지 — 이 커맨드가 대체하지만 삭제하지 않는다
