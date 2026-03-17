# draft_reviewer — 논문 초안 검토 에이전트

> **상태: 미구현** — 졸업논문 작성 시점에 개발 예정

---

## 계획된 기능

논문 초안 섹션을 Claude API로 분석하여 논리 흐름·이론 정합성·학술 표현을 자동 검토한다.

1. 초안 `.md` 파일 입력
2. `02. reference/`의 `type: theory` 태그가 붙은 요약 MD를 자동 수집 → 이론 맥락으로 활용
3. 이론 정합성 검사 (초안에서 사용된 이론이 vault의 이론 논문과 일관된지)
4. 인용-주장 정렬 확인 (근거 없는 주장 감지)
5. 학술 어조 점검 (단정적 표현, hedging language 부족 등)
6. 구조 검사 (topic sentence → 근거 → 연결어 흐름)
7. 수정 제안 출력 (Before / After 형식)

> `type: theory` 태그는 `theory_tagger`(`tools/`)가 자동으로 부착한다.
> 특정 이론명을 하드코딩하지 않으므로 연구 주제가 바뀌어도 그대로 사용 가능.

---

## 실행 (예정)

```bash
python run.py review --file "draft/introduction.md"
python run.py review --section "theoretical background"
```

---

## 파일 구성

```
draft_reviewer/
└── __init__.py    # 미구현
```
