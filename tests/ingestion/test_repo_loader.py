import pytest

from lumina_geo.ingestion.repo_loader import load_repo
from lumina_geo.ingestion.url_scraper import IngestionError


def test_load_repo_finds_html_fixtures(tmp_path):
    html_file = tmp_path / "index.html"
    html_file.write_text("<h1>Hello</h1>")

    result = load_repo(str(tmp_path))

    assert "Hello" in result
    assert "index.html" in result


def test_load_repo_raises_on_empty_dir(tmp_path):
    with pytest.raises(IngestionError, match="No supported files"):
        load_repo(str(tmp_path))


def test_load_repo_raises_on_missing_dir():
    with pytest.raises(IngestionError, match="Directory not found"):
        load_repo("/nonexistent/path")


def test_load_repo_includes_tsx_and_jsx(tmp_path):
    (tmp_path / "App.tsx").write_text("export const App = () => <div>App</div>;")
    (tmp_path / "Button.jsx").write_text("export const Button = () => <button>Click</button>;")

    result = load_repo(str(tmp_path))

    assert "App.tsx" in result
    assert "Button.jsx" in result
