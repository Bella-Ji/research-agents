# gap_explorer

PDF 논문 1편을 읽고, 저자가 명시한 연구 갭을 추출합니다.

## 역할

논문의 Limitations / Future Research 섹션에서 저자가 직접 쓴 문장을 추출합니다.
추측하거나 확장하지 않고, 저자가 명시한 내용만 가져옵니다.

## 출력

논문 PDF와 같은 폴더에 `*_갭분석.md` 파일 생성

```
📄 논문.pdf
📝 논문_갭분석.md   ← 생성됨
```

### 출력 구조

```
## 🔍 연구 갭
### 갭 1 — 메커니즘미규명 [cross-lag]
- KO: 요약 (한국어)
- EN: 요약 (영어)
- 원문: > "저자가 쓴 영어 문장 직접 인용"

## 📚 이론 프레임
COR, JD-R, Effort-Recovery ...
```

### gap_type 분류

| 값 | 의미 |
|---|---|
| `매개변인부재` | 왜(how/why) 설명하는 매개 변인이 없음 |
| `조절변인부재` | 누구에게/언제 효과가 달라지는지 경계 조건 없음 |
| `종단설계필요` | 횡단 연구라 시간 순서 검증 불가 |
| `다층구조미적용` | 개인 내 / 개인 간 수준 분리 안 됨 |
| `표본한계` | 특정 직군/국가/시점에 한정 |
| `메커니즘미규명` | 경로는 있지만 작동 원리 모름 |
| `복합경로미검증` | 여러 변인을 동시에 검증한 연구 없음 |

### model_type_needed 분류

| 값 | 의미 |
|---|---|
| `cross-lag` | 시간 지연 경로 (A → B 다음날) |
| `cross-lag+moderation` | 시간 지연 + 조절 |
| `mediation` | 매개 경로 |
| `moderated_mediation` | 조절된 매개 |
| `MSEM` | 다층 구조방정식 (횡단) |
| `MSEM+moderation` | 다층 + cross-level interaction |

## 실행

```bash
# 단일 파일
python3 run.py gap --single "경로/논문.pdf"

# 폴더 전체 (미처리 파일만)
python3 run.py gap --batch

# 대화형 선택
python3 run.py gap --pick

# 새 파일 자동 감지
python3 run.py gap --watch
```

## 처리 대상 폴더

`config.py`의 `GAP_TARGET_FOLDERS`에 지정된 폴더 하위를 재귀 탐색합니다.
기본값: `02. reference/phd/` 및 그 하위 폴더 전체

## 참고

- 학위논문(박사/석사 학위)은 자동으로 건너뜁니다
- 표본이 간호사가 아닌 논문도 동등하게 처리합니다
- 이미 처리된 PDF는 이력 파일(`.gap_exploration_history.json`)로 관리하여 재처리하지 않습니다
- 재처리가 필요하면 `--single` 옵션을 사용하세요 (force=True 자동 적용)
