# tools — 공통 유틸리티 도구

`agents/`의 에이전트와 독립적으로 실행되는 단독 유틸리티 모음.

---

## theory_tagger.py

요약 MD 파일의 태그를 확인하여 이론 관련 태그가 있으면 `type: theory` 속성을 자동으로 추가한다.

### 동작 방식

```
02. reference/ 전체 스캔 (*_요약.md)
        ↓
YAML frontmatter의 tags 확인
        ↓
이론 관련 태그 감지 시 → type: theory 추가
이미 있거나 이론 태그 없으면 → 스킵
```

### 감지하는 이론 태그

`cor-theory`, `jd-r-model`, `jd-r`, `cor`, `theory`, `model`, `theoretical-review`,
`conservation-of-resources`, `demands-resources`

### 실행

```bash
# run.py를 통해 실행 (research-agents/ 루트에서)
python run.py tag
```

`pdf --batch` 완료 후 실행하면 새로 생성된 요약 MD에 이론 태그가 자동으로 붙는다.

### type: theory 태그의 활용

- `draft_reviewer`: vault에서 이론 논문만 수집하여 이론 정합성 검사에 활용
- Obsidian에서 `type: theory` 필터로 이론 논문만 모아 보기 가능

---

## 파일 구성

```
tools/
├── theory_tagger.py
└── __init__.py
```
