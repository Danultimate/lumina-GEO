from pathlib import Path

from lumina_geo.reporting.models import AuditReport


def write_report(report: AuditReport, output_dir: str = ".") -> None:
    base = Path(output_dir)
    base.mkdir(parents=True, exist_ok=True)

    (base / "report.json").write_text(report.model_dump_json(indent=2))
    (base / "report.md").write_text(_render_markdown(report))


def _items(lst: list[str], prefix: str = "-") -> list[str]:
    return [f"{prefix} {i}" for i in lst] if lst else ["- None"]


def _render_markdown(r: AuditReport) -> str:
    ai = r.ai_access
    ai_section = (
        ["### AI Bot Access", "", "**Status: CRITICAL — AI bots are blocked**", ""]
        + _items(ai.blocked_bots)
        + ["", "**Fixes:**"]
        + _items(ai.fixes)
        if ai.checked and ai.critical
        else ["### AI Bot Access", "", "All major AI bots allowed." if ai.checked else "Not checked (repo analysis)."]
    )

    lines = [
        "# Lumina-GEO Audit Report",
        "",
        f"**Target:** {r.url_or_path}",
        f"**Composite Score:** {r.composite_score:.1f} / 10",
        f"**Google AI Overviews:** {r.platform_scores.google_ai_overviews:.1f} / 10",
        f"**ChatGPT / Perplexity:** {r.platform_scores.chatgpt_perplexity:.1f} / 10",
        f"**Generated:** {r.generated_at}",
        "",
        "---",
        "",
        *ai_section,
        "",
        "---",
        "",
        f"## Grounding Lens — {r.grounding.score}/10",
        "",
        f"- **Citation Probability:** {r.grounding.citation_probability}/10",
        f"- **Is Groundable:** {'Yes' if r.grounding.is_groundable else 'No'}",
        "",
        "### Findings",
        *_items(r.grounding.findings),
        "",
        "### Critical Fixes",
        *_items(r.grounding.critical_fixes),
        "",
        "### Schema Gaps",
        *_items(r.grounding.schema_gaps),
        "",
        "---",
        "",
        f"## Semantic Hierarchy Lens — {r.semantic_hierarchy.score}/10",
        "",
        "### Findings",
        *_items(r.semantic_hierarchy.findings),
        "",
        "### Critical Fixes",
        *_items(r.semantic_hierarchy.critical_fixes),
        "",
        "### Logic Breaks",
        *_items(r.semantic_hierarchy.logic_breaks),
        "",
        "---",
        "",
        f"## Answer-First Lens — {r.answer_first.score}/10",
        "",
        "### Findings",
        *_items(r.answer_first.findings),
        "",
        "### Critical Fixes",
        *_items(r.answer_first.critical_fixes),
        "",
        "### Missing Definitions",
        *_items(r.answer_first.missing_definitions),
        "",
        "---",
        "",
        f"## Authority Lens — {r.authority.score}/10",
        "",
        f"- **Named Author:** {'Yes' if r.authority.has_named_author else 'No'}",
        f"- **Statistics with Sources:** {'Yes' if r.authority.has_statistics else 'No'}",
        f"- **Expert Quotes:** {'Yes' if r.authority.has_expert_quotes else 'No'}",
        f"- **Date Signals:** {'Yes' if r.authority.has_date_signals else 'No'}",
        f"- **External Citations:** {'Yes' if r.authority.has_external_citations else 'No'}",
        "",
        "### Authority Signals",
        *_items(r.authority.authority_signals),
        "",
        "### Findings",
        *_items(r.authority.findings),
        "",
        "### Critical Fixes",
        *_items(r.authority.critical_fixes),
        "",
    ]
    return "\n".join(lines)
