# pylint: disable=missing-function-docstring, too-many-function-args, missing-module-docstring
import os
from unittest.mock import MagicMock, patch

import pytest
from bs4 import BeautifulSoup
from scrapers.metacritic.scrape_games_data import *
from scrapers.metacritic.scrape_games_lists import *
from scrapers.metacritic.scrape_metacritic_reviews import *
from scrapers.metacritic.scrape_user_reviews import *
from scrapers.metacritic.scrape_utils import *

########################################################################
# Scrape Utilities
########################################################################


def test_handle_request_success():
    """Test that the `handle_request()` function returns a response object for a valid URL."""
    url = "https://www.google.com"
    response = handle_request(url)
    assert response is not None
    assert response.status_code == 200


def test_handle_request_max_retries_exceeded():
    """Test that the `handle_request()` function returns None if the maximum number of retries is exceeded."""
    url = "https://www.google.com/does-not-exist"
    response = handle_request(url, max_retries=1)
    assert response is None


def test_handle_request_broken_link():
    """Test that the `handle_request()` function returns None if the URL is a broken link."""
    url = "https://www.google.com/invalid-url"
    response = handle_request(url)
    assert response is None


@patch("scrapers.metacritic.scrape_utils.get_soup")
def test_get_last_page(mock_get_soup):
    soup = MagicMock()
    mock_get_soup.return_value = soup

    last_page = MagicMock()
    last_page.find_all.return_value = [MagicMock(text="2")]

    soup.find.return_value = last_page

    page_link = "https://example.com/page"
    result = get_last_page(page_link)

    assert result == 1


@patch("scrapers.metacritic.scrape_utils.handle_request")
def test_get_soup(mock_handle_request):
    mock_handle_request.return_value = MagicMock(content="<html>Example HTML</html>")

    url = "https://example.com"
    soup = get_soup(url)

    assert isinstance(soup, BeautifulSoup)
    assert str(soup) == "<html>Example HTML</html>"


@pytest.fixture
def file_path(tmp_path):
    file_path = tmp_path / "test-urls.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("https://www.example.com\nhttps://www.google.com\n")
    yield file_path
    os.remove(file_path)


def test_read_txt(file_path):
    console = "test"
    url_list = read_txt(console, base_path=str(file_path.parent))
    assert url_list == ["https://www.example.com", "https://www.google.com"]


def test_read_txt_non_existent_file(tmp_path):
    console = "test"
    with pytest.raises(FileNotFoundError):
        read_txt(console, base_path=str(tmp_path))


def get_game_urls():
    # Test with a known URL and number of pages
    urls = list(
        get_game_urls(
            "https://www.metacritic.com/browse/games/release-date/available/switch/name?&view=detailed",
            2,
        )
    )
    assert (
        len(urls) == 300
    )  # There should be 300 game URLs on the first two pages for the Nintendo Switch
    assert all(
        url.startswith("https://www.metacritic.com/game/") for url in urls
    )  # All URLs should be for games on Metacritic


def test_extract_game_info():
    soup = BeautifulSoup(
        """
        <div class="product_title">
            <h1>Grand Theft Auto IV</h1>
        </div>
        <span class="platform">PC</span>
    """,
        "html.parser",
    )

    game, platform = extract_game_info(soup)
    assert game == "Grand Theft Auto IV"
    assert platform == "PC"
