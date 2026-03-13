"""
run.py — research-agents 통합 실행 진입점

사용법:
  python run.py pdf --batch           # PDF 요약 에이전트 (전체 일괄)
  python run.py pdf --pick            # PDF 요약 에이전트 (대화형 선택)
  python run.py pdf --single "경로"  # PDF 요약 에이전트 (단일 파일)
  python run.py pdf --watch           # PDF 요약 에이전트 (폴더 감시)
  python run.py search                # 문헌 탐색 에이전트 (대화형)
  python run.py search "키워드"      # 문헌 탐색 에이전트 (키워드 직접 전달)
  python run.py tag                   # 이론 태그 추가 도구
"""

import io
import sys
from pathlib import Path

# research-agents 루트를 sys.path에 추가 (config.py, agents/ 접근용)
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    command = sys.argv[1].lower()

    if command == "pdf":
        from agents.pdf_summarizer.main import main as pdf_main
        sys.argv = [sys.argv[0]] + sys.argv[2:]
        pdf_main()

    elif command == "search":
        from agents.lit_search.agent import main as search_main
        if len(sys.argv) > 2:
            keyword = " ".join(sys.argv[2:])
            sys.stdin = io.StringIO(f"{keyword}\nq\n")
        search_main()

    elif command == "tag":
        from tools.theory_tagger import main as tag_main
        tag_main()

    else:
        print(f"알 수 없는 명령어: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
