from unittest.mock import MagicMock, patch

import pytest

from lumina_geo.ingestion.url_scraper import IngestionError, scrape_url


@patch("lumina_geo.ingestion.url_scraper.FirecrawlApp")
def test_scrape_url_returns_markdown(mock_app_cls):
    mock_app = MagicMock()
    mock_app.scrape_url.return_value = {"markdown": "# Hello World\n\nSome content."}
    mock_app_cls.return_value = mock_app

    result = scrape_url("https://example.com")

    assert result == "# Hello World\n\nSome content."
    mock_app.scrape_url.assert_called_once_with(
        "https://example.com", params={"formats": ["markdown"]}
    )


@patch("lumina_geo.ingestion.url_scraper.FirecrawlApp")
def test_scrape_url_raises_on_empty_content(mock_app_cls):
    mock_app = MagicMock()
    mock_app.scrape_url.return_value = {"markdown": ""}
    mock_app_cls.return_value = mock_app

    with pytest.raises(IngestionError, match="empty content"):
        scrape_url("https://example.com")
