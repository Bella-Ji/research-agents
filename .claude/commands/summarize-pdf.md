# /summarize-pdf

PDF 논문을 요약하여 `{stem}_요약.md`를 PDF와 같은 폴더에 생성한다.

## 사용법

```
/summarize-pdf [경로]     # 단일 PDF 처리
/summarize-pdf --batch    # 대상 폴더 전체 미처리 PDF 순회
```

## 동작

### 단일 모드: `/summarize-pdf [경로]`

`[경로]`의 PDF 파일을 pdf-summarizer 에이전트에 전달한다.
에이전트가 `{stem}_요약.md`를 PDF와 같은 폴더에 생성한다.

### 배치 모드: `/summarize-pdf --batch`

아래 대상 폴더를 재귀 탐색하여 `{stem}_요약.md`가 없는 PDF를 순차 처리한다.

**대상 폴더** (config.py `PDF_TARGET_FOLDERS = ["WM"]`):
```
/mnt/c/Users/user/Documents/00.seohyun/Doctor/0. 졸업논문 준비/02. reference/WM/
```

**중복 판단**: 같은 폴더에 `{PDF파일명 stem}_요약.md`가 이미 존재하면 건너뜀.

**미처리 PDF 탐색**:
```bash
find "/mnt/c/Users/user/Documents/00.seohyun/Doctor/0. 졸업논문 준비/02. reference/WM" \
  -name "*.pdf" | while IFS= read -r pdf; do
  stem="${pdf%.pdf}"
  [ ! -f "${stem}_요약.md" ] && echo "$pdf"
done
```

미처리 목록을 확인한 뒤 각 PDF에 대해 pdf-summarizer를 순차 호출한다.

## 주의사항

- `run.py pdf` 명령과 동일한 출력 형식을 유지한다 (파일명, 폴더 위치, MARKDOWN_TEMPLATE 구조).
- 기존 Python 코드와 `run.py`는 수정하지 않는다.
