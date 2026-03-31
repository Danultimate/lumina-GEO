import sys
from pathlib import Path

from langchain_community.document_loaders import TextLoader

from lumina_geo.ingestion.url_scraper import IngestionError

SUPPORTED_EXTENSIONS = {".html", ".tsx", ".jsx"}

# Approximate token limit for Gemini 1.5 Pro (1M tokens ~ 4M chars; we use a safe 800k char limit)
MAX_CHARS = 800_000


def load_repo(directory: str) -> str:
    base = Path(directory)
    if not base.is_dir():
        raise IngestionError(f"Directory not found: {directory}")

    files = [
        p for p in base.rglob("*")
        if p.is_file() and p.suffix in SUPPORTED_EXTENSIONS
    ]

    if not files:
        raise IngestionError(
            f"No supported files ({', '.join(SUPPORTED_EXTENSIONS)}) found in: {directory}"
        )

    print(
        f"[lumina-geo] Found {len(files)} file(s) in {directory}",
        file=sys.stderr,
    )

    parts: list[str] = []
    total_chars = 0

    for file_path in sorted(files):
        try:
            loader = TextLoader(str(file_path), encoding="utf-8")
            docs = loader.load()
            content = "\n".join(doc.page_content for doc in docs)
        except Exception as exc:
            print(
                f"[lumina-geo] Warning: skipping {file_path} — {exc}",
                file=sys.stderr,
            )
            continue

        entry = f"### FILE: {file_path.relative_to(base)}\n\n{content}\n"

        if total_chars + len(entry) > MAX_CHARS:
            print(
                "[lumina-geo] Warning: context limit reached — some files were truncated.",
                file=sys.stderr,
            )
            break

        parts.append(entry)
        total_chars += len(entry)

    if not parts:
        raise IngestionError(f"All files in {directory} failed to load.")

    return "\n---\n".join(parts)
