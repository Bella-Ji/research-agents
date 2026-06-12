"""
reader.py — gap_landscape_*.md 파일 탐색 및 로드
"""

from pathlib import Path

from config import SYNTHESIS_DIR

MAX_CHARS_PER_LANDSCAPE = 8000


def find_landscapes() -> list[dict]:
    """SYNTHESIS_DIR에서 gap_landscape_*.md 파일 목록 반환 (최신순)."""
    if not SYNTHESIS_DIR.exists():
        return []
    files = sorted(SYNTHESIS_DIR.glob("gap_landscape_*.md"), reverse=True)
    return [{"path": f, "name": f.stem} for f in files]


def load_landscapes(items: list[dict]) -> list[dict]:
    loaded = []
    for item in items:
        path: Path = item["path"]
        try:
            content = path.read_text(encoding="utf-8")
            truncated = content[:MAX_CHARS_PER_LANDSCAPE]
            if len(content) > MAX_CHARS_PER_LANDSCAPE:
                truncated += "\n...(이하 생략)"
            loaded.append({"name": item["name"], "content": truncated})
        except Exception as e:
            print(f"  [오류] 파일 읽기 실패 {path.name}: {e}")
    return loaded
