# Research Profile (연구 프로필)

> 모든 에이전트가 공유하는 연구 컨텍스트. 연구 주제가 바뀌면 이 파일만 수정한다.

## 연구자
- 충남대학교 심리학과 박사과정 (직업건강심리학, Occupational Health Psychology)
- 지도교수·공저자: 이선희 (Sunhee Lee)

## 연구 설계
- **일기연구 (Daily Diary / Experience Sampling)**: AW-BW 교대 설계, 약 31일
- **표본**: 한국 간호사, person N = 284
- AW(After Work): 퇴근 직후 측정 — 당일 근무 중 경험 (부당대우, 정서적 소진, 잡크래프팅)
- BW(Before Work): 다음 날 출근 전 측정 — 전날 밤 회복경험(ND_REC), 현재 아침 회복상태(ND_SBR), 일의 의미감(ND_WM)
- AW의 `NXT_shift` = BW의 `JB_shift` 대응 → 동일인의 연속된 24시간 경험 포착

## 분석 방법
- Mplus 기반 다층 SEM (MSEM), DSEM (Bayesian 추정)
- 가능한 모형: MSEM / MSEM+moderation / DSEM_cross-lag / DSEM_mediation / DSEM+moderation / DSEM_moderated_mediation

## 이론 프레임
| 이론 | 관련 변인 | 활용 포인트 |
|---|---|---|
| COR (Conservation of Resources) | 부당대우, EE, WM, REC, SBR | 자원 손실 나선: 부당대우 → EE↑ → WM↓. 회복 = 자원 보충 기제 |
| JD-R (Job Demands-Resources) | 부당대우(요구), JC·PSC(자원), EE | 요구→소진 / 자원→동기부여 이중 경로 |
| Effort-Recovery | REC, SBR, jb_SQ, EE | 퇴근 후 회복경험 → 다음 날 회복상태 → WM 회복 |
| 심리적 계약 이론 | PCEO, PCEF, PSC | 조직의 안전 의무 불이행 시 EE 증가 |
| 자기결정이론 / 의미감 이론 | p_WM, ND_WM | 일의 의미감의 소진 완충 가능성 |

## 기존 투고 논문 (WM paper) — 이중 역할
- **주제**: 직장 내 부당대우 → 정서적 소진(t_EE) → 일의 의미감(ND_WM) 매개 경로를 person-level 직무탈진(p_JB)이 조절하는 조절된 매개 모형 (MSEM, 횡단)

**(a) 문헌 요약 시 (pdf-summarizer 등)**: 이 모형이 **현재 연구 주제**. 논문과의 연결점(connection)·인용 문장 추출은 이 모형의 구성개념(부당대우, EE, WM, burnout, COR, JD-R, DSEM)을 기준으로 판단한다.

**(b) 새 모형 제안 시 (gap 파이프라인)**: 이 모형은 **중복 회피 대상**. 아래 경로는 자동 제외:
  - `부당대우 → t_EE → ND_WM` (매개 전체)
  - `부당대우 → ND_WM` (직접 효과)
  - `t_EE → ND_WM` (단독 경로 — 위 모형의 일부)
  - 제외 사유: 이미 논문화된 주제이며, 동일 경로를 DSEM으로 재검증하는 것도 차별성 부족

## 출력 규칙
- 인용: APA 7판
- 대상 저널: JAP, JOHP, Work & Stress
- 요약·갭분석은 한국어+영어 병기, 원문 인용은 영어 그대로
