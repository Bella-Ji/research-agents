# /search-lit

Obsidian vault의 `*_요약.md` 파일을 키워드로 탐색하여 관련 논문을 찾고 합성한다.

## 사용법

```
/search-lit [키워드]
```

## 동작

`[키워드]`를 lit-searcher 에이전트에 전달한다.
에이전트가 vault를 Grep 탐색하여 관련 논문을 합성·보고한다.

## 예시

```
/search-lit cor
/search-lit emotional exhaustion moderation
/search-lit diary multilevel
/search-lit 부당대우 회복
```

## 참고

- `run.py search "키워드"` 명령과 동일한 vault 대상 (`02. reference/` 전체).
- KEYWORD_MAP 동의어 확장은 lit-searcher 에이전트가 처리한다.
- 기존 Python 코드와 `run.py`는 수정하지 않는다.
