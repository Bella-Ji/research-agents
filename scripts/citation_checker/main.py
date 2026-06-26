"""
main.py — citation_checker 실행 진입점

사용법 (run.py를 통해):
  python run.py cite --file "draft/1. introduction.md"
  python run.py cite --all                            # DRAFT_ROOT 전체 인텍스트 검사
  python run.py cite --dir "01. 논문 작성/WM paper/draft"
  python run.py cite --ref "draft/10. reference.md"  # 참고문헌 목록만 검사
  python run.py cite --all --ref "draft/10. reference.md"  # 전체 교차 검사
  python run.py cite --all --ref "..." --save         # 결과를 MD 파일로 저장

직접 실행:
  python -m agents.citation_checker.main --file "경로"
"""

import argparse
import sys
import textwrap
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from config import BIB_PATH, DRAFT_ROOT
from agents.citation_checker.bib_loader import load_bib, build_index
from agents.citation_checker.parser import extract_citations
from agents.citation_checker.checker import check_citation
from agents.citation_checker.ref_list_checker import (
    parse_ref_list, check_ref_entry, check_alphabetical, cross_check,
)
from agents.citation_checker.reporter import (
    print_report, print_ref_report, save_report,
)


def _collect_md_files(target: Path) -> list:
    if target.is_file():
        return [target] if target.suffix == ".md" else []
    return sorted(target.rglob("*.md"))


def _load_bib(bib_path: Path):
    if not bib_path.exists():
        print(f"❌ BibTeX 파일 없음: {bib_path}")
        print("   Mendeley Desktop → Tools → Options → BibTeX → Enable BibTeX syncing")
        sys.exit(1)
    print(f"📖 BibTeX 로드 중: {bib_path.name} ...", end=" ", flush=True)
    entries = load_bib(bib_path)
    bib_index = build_index(entries)
    print(f"{len(entries)}개 항목")
    return bib_index


def run_intext_check(md_files: list, bib_index: dict) -> tuple:
    """인텍스트 인용 검사 → (results, all_citations)"""
    results = []
    all_citations = []
    for md_path in md_files:
        citations = extract_citations(md_path)
        all_citations.extend(citations)
        errors_per_citation = [
            (cit, check_citation(cit, bib_index))
            for cit in citations
        ]
        results.append((md_path, citations, errors_per_citation))
    return results, all_citations


def run_ref_check(ref_path: Path, bib_index: dict,
                  draft_citations: list = None) -> dict:
    """참고문헌 목록 검사 → ref_results dict"""
    print(f"📄 참고문헌 목록 파싱: {ref_path.name} ...", end=" ", flush=True)
    ref_entries = parse_ref_list(ref_path)
    print(f"{len(ref_entries)}개 항목")

    entry_errors = [
        (entry, check_ref_entry(entry, bib_index))
        for entry in ref_entries
    ]
    alpha_violations = check_alphabetical(ref_entries)

    missing_in_ref, orphan_in_ref = [], []
    if draft_citations is not None:
        missing_in_ref, orphan_in_ref = cross_check(draft_citations, ref_entries)

    return {
        "ref_path": ref_path,
        "ref_entries": ref_entries,
        "entry_errors": entry_errors,
        "alpha_violations": alpha_violations,
        "missing_in_ref": missing_in_ref,
        "orphan_in_ref": orphan_in_ref,
    }


def main():
    parser = argparse.ArgumentParser(
        description="APA 7판 인용 형식 검사",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            예시:
              python run.py cite --file "draft/1. introduction.md"
              python run.py cite --all
              python run.py cite --dir "01. 논문 작성/WM paper/draft"
              python run.py cite --ref "draft/10. reference.md"
              python run.py cite --all --ref "draft/10. reference.md"
              python run.py cite --all --ref "..." --save
        """),
    )
    parser.add_argument("--file", type=str, metavar="경로", help="특정 MD 파일 (인텍스트 검사)")
    parser.add_argument("--all",  action="store_true",     help=f"DRAFT_ROOT 전체")
    parser.add_argument("--dir",  type=str, metavar="경로", help="특정 폴더 내 전체 MD")
    parser.add_argument("--ref",  type=str, metavar="경로", help="참고문헌 목록 MD 파일")
    parser.add_argument("--bib",  type=str, metavar="경로", help=f"BibTeX 경로 (기본: {BIB_PATH})")
    parser.add_argument("--save", action="store_true",     help="결과를 MD 파일로 저장")
    args = parser.parse_args()

    bib_path = Path(args.bib) if args.bib else BIB_PATH
    bib_index = _load_bib(bib_path)

    # ── 인텍스트 검사 대상 수집 ──────────────────────────────────
    intext_results, all_citations = [], []
    md_files = []

    if args.file:
        md_files = _collect_md_files(Path(args.file))
    elif args.dir:
        md_files = _collect_md_files(Path(args.dir))
    elif args.all:
        md_files = _collect_md_files(DRAFT_ROOT)

    # --ref 파일이 있으면 참고문헌 목록은 인텍스트 검사에서 제외
    ref_path = Path(args.ref) if args.ref else None
    if ref_path:
        md_files = [f for f in md_files if f.resolve() != ref_path.resolve()]

    if md_files:
        print(f"\n🔍 인텍스트 인용 검사: {len(md_files)}개 파일")
        intext_results, all_citations = run_intext_check(md_files, bib_index)
        print_report(intext_results, bib_path)

    # ── 참고문헌 목록 검사 ───────────────────────────────────────
    ref_results = None
    if ref_path:
        if not ref_path.exists():
            print(f"❌ 참고문헌 파일 없음: {ref_path}")
            sys.exit(1)
        print(f"\n📋 참고문헌 목록 검사")
        ref_results = run_ref_check(
            ref_path, bib_index,
            draft_citations=all_citations if all_citations else None,
        )
        print_ref_report(ref_results)

    if not md_files and not ref_path:
        parser.print_help()
        sys.exit(0)

    # ── 저장 ─────────────────────────────────────────────────────
    if args.save:
        base = (ref_path or md_files[0]).parent
        out = base / "citation_check_report.md"
        save_report(intext_results, ref_results, bib_path, out)


if __name__ == "__main__":
    main()
