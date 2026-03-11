"""
main.py — PDF 논문 → Obsidian MD 변환기 (메인 실행 파일)

사용법:
  python main.py --batch          # 지정 폴더 전체 일괄 처리
  python main.py --pick           # 대화형으로 논문 선택
  python main.py --single "경로"  # 특정 논문 1편
  python main.py --watch          # 새 PDF 자동 감시
"""

import argparse
import json
import sys
import time
import textwrap
from datetime import datetime
from pathlib import Path

from config import REFERENCE_ROOT, TARGET_FOLDERS, JSON_PATH, MARKDOWN_DIR
from extractor import extract_one
from summarizer import summarize_paper
from markdown_gen import generate_markdown


# ── 이력 관리 ─────────────────────────────────────────────────────────

def load_history() -> dict:
    if JSON_PATH.exists():
        try:
            return json.loads(JSON_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_history(history: dict):
    JSON_PATH.write_text(
        json.dumps(history, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def is_processed(pdf_path: Path, history: dict) -> bool:
    return str(pdf_path) in history


def mark_processed(pdf_path: Path, history: dict):
    history[str(pdf_path)] = datetime.now().isoformat()
    save_history(history)


# ── 단일 PDF 처리 ─────────────────────────────────────────────────────

def process_pdf(pdf_path: Path, history: dict, force: bool = False):
    """PDF 1편 처리: 추출 → 요약 → MD 생성"""

    if not force and is_processed(pdf_path, history):
        print(f"  ⏭️  이미 처리됨: {pdf_path.name}")
        return

    print(f"\n📄 처리 중: {pdf_path.name}")

    # 1. 텍스트/메타데이터 추출
    try:
        paper = extract_one(pdf_path)
    except Exception as e:
        print(f"  [오류] 추출 실패: {e}")
        return

    if not paper.get("full_text"):
        print("  [건너뜀] 텍스트 없음 (스캔 PDF이거나 손상)")
        return

    # 2. Claude API로 요약 생성
    print("  🤖 Claude 분석 중...")
    summary = summarize_paper(paper)

    # 3. MD 파일 생성
    result = generate_markdown(summary, paper)

    if result:
        mark_processed(pdf_path, history)


# ── 모드별 실행 ───────────────────────────────────────────────────────

def run_batch():
    """지정 폴더 전체 일괄 처리"""
    history = load_history()

    print("=" * 60)
    print("📚 일괄 처리 모드")
    print(f"출력 폴더: {MARKDOWN_DIR}")
    print("=" * 60)

    all_pdfs = []
    for folder_name in TARGET_FOLDERS:
        folder = REFERENCE_ROOT / folder_name
        if not folder.exists():
            continue
        pdfs = [p for p in sorted(folder.rglob("*.pdf"))
                if not is_processed(p, history)]
        if pdfs:
            print(f"  📁 {folder_name}: {len(pdfs)}개 처리 예정")
        all_pdfs.extend(pdfs)

    total = len(all_pdfs)
    if total == 0:
        print("\n✅ 모두 처리 완료 상태입니다!")
        return

    print(f"\n총 {total}개 처리 시작\n")
    for i, pdf_path in enumerate(all_pdfs, 1):
        print(f"[{i}/{total}]", end=" ")
        process_pdf(pdf_path, history)

    print("\n✅ 일괄 처리 완료!")


def run_single(path_str: str, force: bool = True):
    """특정 논문 1편 처리"""
    history = load_history()
    pdf_path = Path(path_str)
    if not pdf_path.exists():
        print(f"❌ 파일 없음: {path_str}")
        return
    process_pdf(pdf_path, history, force=force)


def run_pick():
    """대화형 선택 모드"""
    history = load_history()

    print("=" * 60)
    print("🔍 논문 선택 모드")
    print("=" * 60)

    # 폴더 선택
    valid_folders = []
    print("\n[폴더 선택]")
    for i, name in enumerate(TARGET_FOLDERS, 1):
        folder = REFERENCE_ROOT / name
        if folder.exists():
            pdfs = list(folder.rglob("*.pdf"))
            done = sum(1 for p in pdfs if is_processed(p, history))
            print(f"  {i:2d}. {name}  ({done}/{len(pdfs)} 완료)")
            valid_folders.append(folder)
        else:
            print(f"  {i:2d}. {name}  [없음]")

    try:
        idx = int(input("\n폴더 번호: ")) - 1
        selected_folder = valid_folders[idx]
    except (ValueError, IndexError):
        print("❌ 잘못된 입력")
        return

    # 논문 목록
    pdfs = sorted(selected_folder.rglob("*.pdf"))
    if not pdfs:
        print("❌ PDF 없음")
        return

    print(f"\n[{selected_folder.name}]")
    for i, p in enumerate(pdfs, 1):
        done = "✅" if is_processed(p, history) else "  "
        print(f"  {done} {i:3d}. {p.name}")

    print("\n번호 입력 (예: 1 / 1,3,5 / all / todo)")
    choice = input("선택: ").strip().lower()

    if choice == "all":
        selected = pdfs
    elif choice == "todo":
        selected = [p for p in pdfs if not is_processed(p, history)]
    else:
        try:
            indices = [int(x.strip()) - 1 for x in choice.split(",")]
            selected = [pdfs[i] for i in indices]
        except (ValueError, IndexError):
            print("❌ 잘못된 입력")
            return

    print(f"\n{len(selected)}개 처리 시작\n")
    for pdf_path in selected:
        process_pdf(pdf_path, history, force=True)

    print("\n✅ 완료!")


def run_watch():
    """새 PDF 자동 감시"""
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "watchdog",
                               "--break-system-packages", "-q"])
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler

    history = load_history()

    class PDFHandler(FileSystemEventHandler):
        def on_created(self, event):
            if not event.is_directory and event.src_path.lower().endswith(".pdf"):
                pdf_path = Path(event.src_path)
                for folder_name in TARGET_FOLDERS:
                    if folder_name.lower() in str(pdf_path).lower():
                        print(f"\n🆕 새 PDF 감지: {pdf_path.name}")
                        time.sleep(2)
                        process_pdf(pdf_path, history)
                        break

    print("=" * 60)
    print("👀 폴더 감시 모드 (Ctrl+C로 종료)")
    print(f"감시: {REFERENCE_ROOT}")
    print("=" * 60)

    observer = Observer()
    observer.schedule(PDFHandler(), str(REFERENCE_ROOT), recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n👋 종료")
    observer.join()


# ── 메인 ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="PDF 논문 → Obsidian MD 변환기",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            예시:
              python main.py --batch
              python main.py --pick
              python main.py --single "C:/경로/논문.pdf"
              python main.py --watch
        """)
    )
    parser.add_argument("--batch",  action="store_true", help="전체 일괄 처리")
    parser.add_argument("--pick",   action="store_true", help="대화형 선택")
    parser.add_argument("--single", type=str, metavar="경로", help="특정 논문 1편")
    parser.add_argument("--watch",  action="store_true", help="새 PDF 자동 감시")

    args = parser.parse_args()

    if   args.batch:  run_batch()
    elif args.pick:   run_pick()
    elif args.single: run_single(args.single)
    elif args.watch:  run_watch()
    else:             parser.print_help()


if __name__ == "__main__":
    main()
