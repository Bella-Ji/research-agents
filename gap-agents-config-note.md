# gap 에이전트 경로 설정 정리 (2026-07-06)

## 무엇을 바꿨나
`config.py` (research-agents 프로젝트 루트, gap-explorer / gap-strategist / gap-synthesizer가 공유하는 파일)에서
`SYNTHESIS_DIR`이 더 이상 `00. 졸업 논문/gap_synthesis`로 하드코딩되어 있지 않음.
이제 `CURRENT_PAPER` 값에 따라 저장 폴더가 자동으로 바뀜.

```python
PAPER_FOLDER_MAP = {
    "dissertation": "00. 졸업 논문",
    "WM paper": "01. 투고 논문 작성(WM)",
}

CURRENT_PAPER = os.getenv("CURRENT_PAPER", "WM paper")
_paper_folder = PAPER_FOLDER_MAP.get(CURRENT_PAPER, CURRENT_PAPER)

CURRENT_STUDY = os.getenv("CURRENT_STUDY", "")  # 나중에 연구1/연구2로 나뉘면 사용
_study_subfolder = Path(CURRENT_STUDY) if CURRENT_STUDY else Path(".")

SYNTHESIS_DIR = Path(os.getenv(
    "SYNTHESIS_DIR",
    str(REFERENCE_ROOT.parent / "01. 논문 작성" / _paper_folder / "gap_synthesis" / _study_subfolder),
))
```

## .env 기본값 변경
`CURRENT_PAPER`를 `dissertation`으로 바꿔둠 (당분간 졸업논문 gap 작업 위주라서).

```
CURRENT_PAPER=dissertation
```

→ 이제 gap-explorer / gap-strategist / gap-synthesizer를 그냥 실행하면 결과물이
`00. 졸업 논문/gap_synthesis/`로 저장됨.

## WM paper 작업으로 잠깐 돌아갈 때
`.env`는 안 건드리고, 명령어 앞에 환경변수를 붙여서 그 실행 한 번만 덮어쓰기:

```bash
CURRENT_PAPER="WM paper" python3 run.py gap-synthesize
```

## 나중에 졸업논문 안에서 연구가 여러 개(연구1, 연구2...)로 나뉘면
`.env`에 한 줄만 추가 (config.py는 다시 안 건드려도 됨):

```
CURRENT_STUDY=연구1
```

→ 결과물이 `00. 졸업 논문/gap_synthesis/연구1/`로 자동 분리됨.
연구2로 넘어갈 때는 이 값을 `연구2`로 바꿔주면 됨 (자동 전환 아님, 손으로 맞춰야 함).

## 헷갈릴 때 체크리스트
- 지금 뭘 위한 gap 작업인지 먼저 확인 (졸업논문? WM paper?)
- `.env`의 `CURRENT_PAPER`가 그거랑 맞는지 확인
- 안 맞으면: `.env` 영구 변경 (당분간 계속 그 논문 작업) vs 명령어 앞에 임시로 붙이기 (오늘만) 중 선택
