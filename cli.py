import typer

from lumina_geo import build_report
from lumina_geo.reporting.writer import write_report

app = typer.Typer(help="Lumina-GEO: Audit websites and repos for GEO readiness.")


@app.command()
def audit(
    target: str = typer.Argument(..., help="URL or local directory path to audit"),
    output_dir: str = typer.Option(".", "--output-dir", "-o", help="Directory to write report.json and report.md"),
) -> None:
    """Audit a URL or local repository for AI-Readability and GEO readiness."""
    typer.echo(f"Auditing: {target}")

    report = build_report(target)
    write_report(report, output_dir)

    typer.echo(f"\nComposite Score : {report.composite_score:.1f} / 10")
    typer.echo(f"  Grounding     : {report.grounding.score}/10")
    typer.echo(f"  Sem. Hierarchy: {report.semantic_hierarchy.score}/10")
    typer.echo(f"  Answer-First  : {report.answer_first.score}/10")
    typer.echo(f"\nReports written to: {output_dir}/report.json and {output_dir}/report.md")


if __name__ == "__main__":
    app()
