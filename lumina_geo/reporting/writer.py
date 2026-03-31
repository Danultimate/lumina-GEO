from pathlib import Path

from lumina_geo.reporting.models import AuditReport


def write_report(report: AuditReport, output_dir: str = ".") -> None:
    base = Path(output_dir)
    base.mkdir(parents=True, exist_ok=True)

    (base / "report.json").write_text(report.model_dump_json(indent=2))
    (base / "report.md").write_text(_render_markdown(report))


def _render_markdown(r: AuditReport) -> str:
    lines = [
        "# Lumina-GEO Audit Report",
        "",
        f"**Target:** {r.url_or_path}",
        f"**Composite Score:** {r.composite_score:.1f} / 10",
        f"**Generated:** {r.generated_at}",
        "",
        "---",
        "",
        f"## Grounding Lens — {r.grounding.score}/10",
        "",
        f"- **Citation Probability:** {r.grounding.citation_probability}/10",
        f"- **Is Groundable:** {'Yes' if r.grounding.is_groundable else 'No'}",
        "",
        "### Findings",
        *[f"- {f}" for f in r.grounding.findings],
        "",
        "### Critical Fixes",
        *[f"- {f}" for f in r.grounding.critical_fixes],
        "",
        "### Schema Gaps",
        *[f"- {g}" for g in r.grounding.schema_gaps],
        "",
        "---",
        "",
        f"## Semantic Hierarchy Lens — {r.semantic_hierarchy.score}/10",
        "",
        "### Findings",
        *[f"- {f}" for f in r.semantic_hierarchy.findings],
        "",
        "### Critical Fixes",
        *[f"- {f}" for f in r.semantic_hierarchy.critical_fixes],
        "",
        "### Logic Breaks",
        *[f"- {b}" for b in r.semantic_hierarchy.logic_breaks],
        "",
        "---",
        "",
        f"## Answer-First Lens — {r.answer_first.score}/10",
        "",
        "### Findings",
        *[f"- {f}" for f in r.answer_first.findings],
        "",
        "### Critical Fixes",
        *[f"- {f}" for f in r.answer_first.critical_fixes],
        "",
        "### Missing Definitions",
        *[f"- {d}" for d in r.answer_first.missing_definitions],
        "",
    ]
    return "\n".join(lines)
