"""
reporter.py — 검사 결과 출력 및 MD 리포트 저장
"""

from pathlib import Path
from datetime import date


def _severity_icon(severity: str) -> str:
    return "❌" if severity == "error" else "⚠️ "


def print_report(results: list, bib_path: Path) -> None:
    """결과를 터미널에 출력.

    results: [(md_path, citations, errors_per_citation), ...]
    errors_per_citation: [(Citation, [CiteError, ...]), ...]
    """
    total_cits = sum(len(cpe) for _, _, cpe in results)
    total_errors = sum(
        sum(1 for e in errs if e.severity == "error")
        for _, _, cpe in results
        for _, errs in cpe
    )
    total_warnings = sum(
        sum(1 for e in errs if e.severity == "warning")
        for _, _, cpe in results
        for _, errs in cpe
    )

    print()
    print("=" * 62)
    print("  📋 APA 7판 인용 검사 리포트")
    print(f"  BibTeX: {bib_path.name}  |  {date.today()}")
    print("=" * 62)
    print(
        f"  총 인용 {total_cits}개  |  "
        f"오류 {total_errors}개  |  경고 {total_warnings}개"
    )

    for md_path, citations, errors_per_citation in results:
        n_cits = len(citations)
        file_errors = [
            (c, errs) for c, errs in errors_per_citation if errs
        ]

        paren_cnt = sum(1 for c in citations if c.context == "paren")
        narr_cnt = sum(1 for c in citations if c.context == "narrative")

        print()
        print("─" * 62)
        print(f"  📄 {md_path.name}")
        print(f"     인용 {n_cits}개 (괄호형 {paren_cnt} / 서술형 {narr_cnt})", end="")

        if not file_errors:
            print("  →  ✅ 이상 없음")
            continue

        f_err = sum(
            1 for _, errs in file_errors
            for e in errs if e.severity == "error"
        )
        f_warn = sum(
            1 for _, errs in file_errors
            for e in errs if e.severity == "warning"
        )
        print(f"  |  ❌ {f_err}  ⚠️  {f_warn}")

        for cit, errs in file_errors:
            for err in errs:
                icon = _severity_icon(err.severity)
                ctx = "괄호형" if cit.context == "paren" else "서술형"
                print()
                print(f"  {icon}  [줄 {cit.line_num:>3}]  [{ctx}]  {err.message}")
                print(f"       원문:  {cit.raw}")
                if err.suggestion and err.suggestion != cit.raw:
                    print(f"       수정:  {err.suggestion}")

    print()
    print("=" * 62)
    ok_count = total_cits - sum(
        1 for _, _, cpe in results
        for c, errs in cpe if errs
    )
    print(f"  ✅ 이상 없음 {ok_count}개  |  문제 {total_errors + total_warnings}건")
    print("=" * 62)
    print()


def print_ref_report(ref_results: dict) -> None:
    """참고문헌 목록 검사 결과 출력"""
    ref_path      = ref_results["ref_path"]
    entry_errors  = ref_results["entry_errors"]
    alpha_viol    = ref_results["alpha_violations"]
    missing       = ref_results["missing_in_ref"]
    orphans       = ref_results["orphan_in_ref"]

    total_entries = len(ref_results["ref_entries"])
    total_errors  = sum(
        1 for _, errs in entry_errors for e in errs if e.severity == "error"
    )
    total_warnings = sum(
        1 for _, errs in entry_errors for e in errs if e.severity == "warning"
    )

    print()
    print("=" * 62)
    print("  📚 참고문헌 목록 검사 리포트 (APA 7판)")
    print(f"  파일: {ref_path.name}  |  항목: {total_entries}개")
    print("=" * 62)
    print(
        f"  형식 오류 {total_errors}건  |  경고 {total_warnings}건  |"
        f"  순서 위반 {len(alpha_viol)}건"
    )
    if missing or orphans:
        print(
            f"  누락(본문→목록 불일치) {len(missing)}건  |"
            f"  미인용(목록→본문 불일치) {len(orphans)}건"
        )

    # ── 항목별 형식 오류 ─────────────────────────────────────────
    item_errors = [(e, errs) for e, errs in entry_errors if errs]
    if item_errors:
        print()
        print("  ── 항목 형식 오류 ──────────────────────────────────")
        for entry, errs in item_errors:
            for err in errs:
                icon = _severity_icon(err.severity)
                print()
                print(f"  {icon}  [줄 {entry.line_num:>3}]  {err.message}")
                # 원문은 첫 80자만 출력
                preview = entry.raw[:80] + ("…" if len(entry.raw) > 80 else "")
                print(f"       원문:  {preview}")
                if err.suggestion:
                    print(f"       수정:  {err.suggestion}")

    # ── 알파벳 순서 위반 ─────────────────────────────────────────
    if alpha_viol:
        print()
        print("  ── 알파벳 순서 위반 ────────────────────────────────")
        for prev, curr, msg in alpha_viol:
            print(f"  ⚠️   [줄 {curr.line_num:>3}]  {msg}")

    # ── 교차 검사: 참고문헌 목록 누락 ────────────────────────────
    if missing:
        print()
        print("  ── 본문 인용 → 참고문헌 목록 누락 ❌ ───────────────")
        print("       (본문에 인용됐으나 참고문헌 목록에 없음)")
        for cit in missing:
            ctx = "괄호형" if cit.context == "paren" else "서술형"
            print(
                f"       • {cit.first_author} ({cit.year})"
                f"  [{ctx}, 줄 {cit.line_num}, {Path(cit.filepath).name}]"
            )

    # ── 교차 검사: 미인용 참고문헌 ───────────────────────────────
    if orphans:
        print()
        print("  ── 참고문헌 목록에 있으나 본문 미인용 ⚠️  ──────────")
        for entry in orphans:
            print(f"       • {entry.first_author} ({entry.year})  [줄 {entry.line_num}]")

    print()
    print("=" * 62)
    ok = total_entries - len(item_errors)
    print(f"  ✅ 형식 이상 없음 {ok}개  |  문제 {total_errors + total_warnings + len(alpha_viol)}건")
    print("=" * 62)
    print()


def save_report(
    intext_results: list,
    ref_results,        # dict or None
    bib_path: Path,
    output_path: Path,
) -> None:
    """결과를 Markdown 파일로 저장."""
    lines = [
        f"# APA 7판 인용 검사 리포트\n",
        f"- **날짜**: {date.today()}",
        f"- **BibTeX**: `{bib_path.name}`\n",
    ]

    # ── 인텍스트 인용 섹션 ───────────────────────────────────────
    if intext_results:
        total_cits = sum(len(cpe) for _, _, cpe in intext_results)
        total_errs = sum(
            1 for _, _, cpe in intext_results
            for _, errs in cpe for e in errs if e.severity == "error"
        )
        lines.append(f"## 인텍스트 인용 검사\n")
        lines.append(f"**총 인용**: {total_cits}개 &nbsp;|&nbsp; **오류**: {total_errs}건\n")

        for md_path, citations, errors_per_citation in intext_results:
            file_errors = [(c, errs) for c, errs in errors_per_citation if errs]
            lines.append(f"### {md_path.name}\n")
            if not file_errors:
                lines.append("✅ 이상 없음\n")
                continue
            for cit, errs in file_errors:
                for err in errs:
                    icon = "❌" if err.severity == "error" else "⚠️"
                    ctx = "괄호형" if cit.context == "paren" else "서술형"
                    lines.append(
                        f"#### {icon} 줄 {cit.line_num} — {err.message}\n"
                        f"- **유형**: {ctx} / `{err.error_type}`\n"
                        f"- **원문**: `{cit.raw}`\n"
                    )
                    if err.suggestion and err.suggestion != cit.raw:
                        lines.append(f"- **수정**: `{err.suggestion}`\n")

    # ── 참고문헌 목록 섹션 ───────────────────────────────────────
    if ref_results:
        lines.append(f"---\n## 참고문헌 목록 검사 ({ref_results['ref_path'].name})\n")

        for entry, errs in ref_results["entry_errors"]:
            if not errs:
                continue
            for err in errs:
                icon = "❌" if err.severity == "error" else "⚠️"
                preview = entry.raw[:80] + ("…" if len(entry.raw) > 80 else "")
                lines.append(
                    f"#### {icon} 줄 {entry.line_num} — {err.message}\n"
                    f"- **원문**: `{preview}`\n"
                )
                if err.suggestion:
                    lines.append(f"- **수정**: `{err.suggestion}`\n")

        for _, curr, msg in ref_results["alpha_violations"]:
            lines.append(f"#### ⚠️ 순서 위반 줄 {curr.line_num} — {msg}\n")

        if ref_results["missing_in_ref"]:
            lines.append("### ❌ 본문 인용 → 참고문헌 목록 누락\n")
            for cit in ref_results["missing_in_ref"]:
                lines.append(
                    f"- `{cit.first_author} ({cit.year})`"
                    f" [{Path(cit.filepath).name}, 줄 {cit.line_num}]\n"
                )

        if ref_results["orphan_in_ref"]:
            lines.append("### ⚠️ 참고문헌 목록에 있으나 본문 미인용\n")
            for entry in ref_results["orphan_in_ref"]:
                lines.append(f"- `{entry.first_author} ({entry.year})` [줄 {entry.line_num}]\n")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  → 리포트 저장: {output_path}")
