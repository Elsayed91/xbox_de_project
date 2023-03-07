from unittest import mock
from unittest.mock import patch

import pytest

from scrapers.metacritic.scrape_game_data import *
from scrapers.metacritic.scrape_game_list import *
from scrapers.metacritic.scrape_game_reviews import *
from scrapers.metacritic.scrape_utils import *


def test_fuzzy_match():
    names = ["Halo", "Forza Horizon", "Gears of War"]
    assert fuzzy_match("Halo 3", names) == "Halo"
    assert fuzzy_match("Gears", names, threshold=20) == "Gears of War"
    assert fuzzy_match("Halo 3", names, threshold=80) == "Halo"


@pytest.fixture
def example_df() -> pd.DataFrame:
    return pd.DataFrame({"Name": ["xdxdxdxd", "Terraria", "CrossfireX"]})


def test_add_gamepass_status(example_df):
    output_df = add_gamepass_status(example_df)

    assert set(output_df.columns) == {"Name", "Gamepass_Status"}
    assert output_df.loc[0, "Gamepass_Status"] == "Not Included"
    assert output_df.loc[1, "Gamepass_Status"] == "Active"
    assert output_df.loc[2, "Gamepass_Status"] == "Removed"


def test_scrape_game_data():
    link = "https://www.metacritic.com/game/switch/the-legend-of-zelda-links-awakening"
    data_list = []
    exception_list = []
    scrape_game_data(link, data_list, exception_list)
    assert len(data_list) == 1
    assert data_list[0]["Name"] == "The Legend of Zelda: Link's Awakening"
    assert data_list[0]["Release Date"] == "2019-09-20"
    assert data_list[0]["Maturity Rating"] == "E"
    assert data_list[0]["Genre"] == "Action Adventure, Open-World"
    assert data_list[0]["Developer"] == "Nintendo"
    assert data_list[0]["Publisher"] == "Nintendo"
    # these will work as long as you update them to the latest value
    # assert int(data_list[0]['Meta Score']) == 87
    # assert int(data_list[0]['Critic Reviews Count']) == 111
    # assert data_list[0]['User Rating'] == '8.4'
    # assert data_list[0]['User Rating Count'] == '1580'
    assert "Summary" in data_list[0]
    assert len(exception_list) == 0


def test_game_urls():
    # Test with a known URL and number of pages
    urls = list(
        game_urls(
            "https://www.metacritic.com/browse/games/release-date/available/switch/name?&view=detailed",
            2,
        )
    )
    assert (
        len(urls) == 200
    )  # There should be 200 game URLs on the first two pages for the Nintendo Switch
    assert all(
        url.startswith("https://www.metacritic.com/game/") for url in urls
    )  # All URLs should be for games on Metacritic


def test_soup_it():
    soup = soup_it("https://www.google.com")
    assert isinstance(soup, BeautifulSoup)
    url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
    soup = soup_it(url)

    assert isinstance(soup, BeautifulSoup)
    assert soup.title.string == "Python (programming language) - Wikipedia"


def test_get_last_page_num():
    # Mocking the soup_it() function to return the mock response
    with patch("scrapers.metacritic.scrape_utils.soup_it") as mock_soup_it:
        mock_response = """
            <li class="page last_page"><a href="/games?page=6&amp;region=US" class="page_num" data-page="5">6</a></li>
        """
        mock_soup_it.return_value = BeautifulSoup(mock_response, "html.parser")

        # Test with last page link
        page_link = "https://example.com/games?page=6&region=US"
        assert get_last_page_num(page_link) == 5


def test_get_games_per_page():
    # Mocking the soup_it() function to return the mock response
    with patch("scrapers.metacritic.scrape_utils.soup_it") as mock_soup_it:
        mock_response = """
            <a class="title" href="https://example.com/game1">Game 1</a>
            <a class="title" href="https://example.com/game2">Game 2</a>
            <a class="title" href="https://example.com/game3">Game 3</a>
        """
        mock_soup_it.return_value = BeautifulSoup(mock_response, "html.parser")

        link = "https://example.com/games?page=1&region=US"
        expected_output = [
            "https://example.com/game1",
            "https://example.com/game2",
            "https://example.com/game3",
        ]
        assert get_games_per_page(link) == expected_output


def test_get_last_page_num_with_valid_link():
    """
    Test get_last_page_num() with a valid link.
    """
    mock_response = """
        <html>
            <body>
                <div class="pagination">
                    <li><a href="/page1" class="page_num">1</a></li>
                    <li><a href="/page2" class="page_num">2</a></li>
                    <li><a href="/page3" class="page_num">3</a></li>
                    <li class="page last_page"><a href="/page4" class="page_num">4</a></li>
                </div>
            </body>
        </html>
    """
    with patch("scrapers.metacritic.scrape_utils.soup_it") as mock_soup_it:
        mock_soup_it.return_value = BeautifulSoup(mock_response, "html.parser")
        page_link = "https://example.com/search?q=keyword"
        expected_output = 3
        assert get_last_page_num(page_link) == expected_output


def test_get_last_page_num_with_invalid_link():
    """
    Test get_last_page_num() with an invalid link.
    """
    mock_response = """
        <html>
            <body>
                <div class="pagination">
                    <li><a href="/page1" class="page_num">1</a></li>
                </div>
            </body>
        </html>
    """
    with patch("scrapers.metacritic.scrape_utils.soup_it") as mock_soup_it:
        mock_soup_it.return_value = BeautifulSoup(mock_response, "html.parser")
        page_link = "https://example.com/search?q=keyword"
        expected_output = 1
        assert get_last_page_num(page_link) == expected_output


def test_get_games_per_page_with_valid_link():
    """
    Test get_games_per_page() with a valid link.
    """
    mock_response = """
        <html>
            <body>
                <div class="game-list">
                    <div class="game-item">
                        <a href="/game1" class="title">Game 1</a>
                    </div>
                    <div class="game-item">
                        <a href="/game2" class="title">Game 2</a>
                    </div>
                    <div class="game-item">
                        <a href="/game3" class="title">Game 3</a>
                    </div>
                </div>
            </body>
        </html>
    """
    with patch("scrapers.metacritic.scrape_utils.soup_it") as mock_soup_it:
        mock_soup_it.return_value = BeautifulSoup(mock_response, "html.parser")
        link = "https://example.com/search?q=keyword&page=1"
        expected_output = ["/game1", "/game2", "/game3"]
        assert get_games_per_page(link) == expected_output


def test_get_games_per_page_with_invalid_link():
    """
    Test get_games_per_page() with an invalid link.
    """
    mock_response = """
        <html>
            <body>
                <div class="game-list">
                </div>
            </body>
        </html>
    """
    with patch("scrapers.metacritic.scrape_utils.soup_it") as mock_soup_it:
        mock_soup_it.return_value = BeautifulSoup(mock_response, "html.parser")
        link = "https://example.com/search?q=keyword&page=1"
        expected_output = []
        assert get_games_per_page(link) == expected_output


@pytest.fixture
def file_path(tmp_path):
    file_path = tmp_path / "test-urls.txt"
    with open(file_path, "w") as f:
        f.write("https://www.example.com\nhttps://www.google.com\n")
    yield file_path
    os.remove(file_path)


def test_read_txt(file_path):
    console = "test"
    url_list = read_txt(console, base_path=str(file_path.parent))
    assert url_list == ["https://www.example.com", "https://www.google.com"]


import unittest


class TestScraperFunctions(unittest.TestCase):
    def test_scrape_metacritic_reviews(self):
        # Test case 1
        critic_review_list = []
        exception_list = []
        game_link = "https://www.metacritic.com/game/pc/pharaoh-a-new-era"
        scrape_metacritic_reviews(game_link, critic_review_list, exception_list)
        self.assertGreater(len(critic_review_list), 0)
        self.assertEqual(len(exception_list), 0)

        # Test case 2
        critic_review_list = []
        exception_list = []
        game_link = "https://www.metacritic.com/game/pc/pharaoh-a-new-era"
        scrape_metacritic_reviews(game_link, critic_review_list, exception_list)
        self.assertGreater(len(critic_review_list), 0)
        self.assertEqual(len(exception_list), 0)

    def test_scrape_user_reviews(self):
        # Test case 1
        review_list = []
        exception_list = []
        game_link = "https://www.metacritic.com/game/pc/pharaoh-a-new-era"
        scrape_user_reviews(game_link, review_list, exception_list)
        self.assertGreater(len(review_list), 0)
        self.assertEqual(len(exception_list), 0)

        # Test case 2
        review_list = []
        exception_list = []
        game_link = "https://www.metacritic.com/game/pc/pharaoh-a-new-era"
        scrape_user_reviews(game_link, review_list, exception_list)
        self.assertGreater(len(review_list), 0)
        self.assertEqual(len(exception_list), 0)
