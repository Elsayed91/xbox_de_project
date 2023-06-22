import unittest
from datetime import datetime
from unittest import mock
from unittest.mock import MagicMock, patch

# pylint: disable=missing-function-docstring
import pytest
from bs4 import BeautifulSoup
from scrapers.metacritic.scrape_games_data import *
from scrapers.metacritic.scrape_games_lists import *
from scrapers.metacritic.scrape_metacritic_reviews import *
from scrapers.metacritic.scrape_user_reviews import *
from scrapers.metacritic.scrape_utils import *

# @pytest.fixture
# def example_soup():
#     return BeautifulSoup("<html>Example HTML</html>", "html.parser")


# @pytest.fixture
# def example_reviews():
#     return [
#         {
#             "Game": "Example Game",
#             "Platform": "Example Platform",
#             "Critic": "Example Critic",
#             "Review Source": "https://example.com",
#             "Score": "100",
#             "Review": "Example Review",
#         }
#     ]


def test_extract_user_reviews():
    soup = BeautifulSoup(example_html, "html.parser")

    expected_reviews = [
        {
            "Game": "Example Game",
            "Platform": "Example Platform",
            "User": "Rockstar900",
            "Date": "Dec 21, 2010",
            "Score": "10",
            "Review": "Wow. I really loved this game. It in every way blew me away. A captivating, epic, and deep storyline keeps you into it the entire way through. Me trying to find at least one thing to complain about. Nothing. This game really deserves GOTY. And I really have to say Niko Bellic is the only character in the GTA series that you can truly connect with. Understanding his difficult life and mis-adventures you can really feel his emotions. And for a free-roaming game they really knocked me out. The free roaming really is amazing. Its awesome how they can have such a nice, luminous city and still have amazing and almost flawless graphics. As for the multi-player, I didn't really play it that much but i love the fact that you can roam around Liberty City causing as much mayhem as you want. The ranked matches are good too, with death-match (etc...) it was pretty cool to see that in a GTA game. Surely I can truly say that you have not experienced free-roam/sandbox games until you have played GTA IV.",
        }
    ]

    with patch(
        "scrapers.metacritic.scrape_user_reviews.extract_game_info"
    ) as mock_extract_game_info, patch(
        "scrapers.metacritic.scrape_user_reviews.extract_review_text"
    ) as mock_extract_review_text:
        mock_extract_game_info.return_value = ("Example Game", "Example Platform")
        mock_extract_review_text.return_value = expected_reviews[0]["Review"]

        reviews = extract_user_reviews(soup)
        assert reviews == expected_reviews


def test_scrape_user_reviews():
    example_link = "https://www.metacritic.com/game/example"

    with patch(
        "scrapers.metacritic.scrape_user_reviews.get_last_page"
    ) as mock_get_last_page, patch(
        "scrapers.metacritic.scrape_user_reviews.get_soup"
    ) as mock_get_soup, patch(
        "scrapers.metacritic.scrape_user_reviews.extract_user_reviews"
    ) as mock_extract_user_reviews:
        mock_get_last_page.return_value = 2
        mock_get_soup.side_effect = lambda url: BeautifulSoup(
            example_html, "html.parser"
        )
        mock_extract_user_reviews.return_value = [
            {
                "Game": "Example Game",
                "Platform": "Example Platform",
                "User": "TheChiefOfCOD",
                "Date": "Dec 21, 2010",
                "Score": "10",
                "Review": "Wow. I really loved this game. It in every way blew me away. A captivating, epic, and deep storyline keeps you into it the entire way through. Me trying to find at least one thing to complain about. Nothing. This game really deserves GOTY. And I really have to say Niko Bellic is the only character in the GTA series that you can truly connect with. Understanding his difficult life and mis-adventures you can really feel his emotions. And for a free-roaming game they really knocked me out. The free roaming really is amazing. Its awesome how they can have such a nice, luminous city and still have amazing and almost flawless graphics. As for the multi-player, I didn't really play it that much but i love the fact that you can roam around Liberty City causing as much mayhem as you want. The ranked matches are good too, with death-match (etc...) it was pretty cool to see that in a GTA game. Surely I can truly say that you have not experienced free-roam/sandbox games until you have played GTA IV.",
            }
        ]

        reviews = scrape_user_reviews(example_link)
        assert reviews == mock_extract_user_reviews.return_value


# def test_get_games_per_page():
#     # Mocking the get_soup() function to return the mock response
#     with patch("scrapers.metacritic.scrape_utils.get_soup") as mock_get_soup:
#         mock_response = """
#             <a class="title" href="https://example.com/game1">Game 1</a>
#             <a class="title" href="https://example.com/game2">Game 2</a>
#             <a class="title" href="https://example.com/game3">Game 3</a>
#         """
#         mock_get_soup.return_value = BeautifulSoup(mock_response, "html.parser")

#         link = "https://example.com/games?page=1&region=US"
#         expected_output = [
#             "https://example.com/game1",
#             "https://example.com/game2",
#             "https://example.com/game3",
#         ]
#         assert get_games_per_page(link) == expected_output


# def test_get_last_page_num_with_valid_link():
#     """
#     Test get_last_page_num() with a valid link.
#     """
#     mock_response = """
#         <html>
#             <body>
#                 <div class="pagination">
#                     <li><a href="/page1" class="page_num">1</a></li>
#                     <li><a href="/page2" class="page_num">2</a></li>
#                     <li><a href="/page3" class="page_num">3</a></li>
#                     <li class="page last_page"><a href="/page4" class="page_num">4</a></li>
#                 </div>
#             </body>
#         </html>
#     """
#     with patch("scrapers.metacritic.scrape_utils.soup_it") as mock_soup_it:
#         mock_soup_it.return_value = BeautifulSoup(mock_response, "html.parser")
#         page_link = "https://example.com/search?q=keyword"
#         expected_output = 3
#         assert get_last_page_num(page_link) == expected_output


# def test_get_last_page_num_with_invalid_link():
#     """
#     Test get_last_page_num() with an invalid link.
#     """
#     mock_response = """
#         <html>
#             <body>
#                 <div class="pagination">
#                     <li><a href="/page1" class="page_num">1</a></li>
#                 </div>
#             </body>
#         </html>
#     """
#     with patch("scrapers.metacritic.scrape_utils.soup_it") as mock_soup_it:
#         mock_soup_it.return_value = BeautifulSoup(mock_response, "html.parser")
#         page_link = "https://example.com/search?q=keyword"
#         expected_output = 1
#         assert get_last_page_num(page_link) == expected_output


# def test_get_games_per_page_with_valid_link():
#     """
#     Test get_games_per_page() with a valid link.
#     """
#     mock_response = """
#         <html>
#             <body>
#                 <div class="game-list">
#                     <div class="game-item">
#                         <a href="/game1" class="title">Game 1</a>
#                     </div>
#                     <div class="game-item">
#                         <a href="/game2" class="title">Game 2</a>
#                     </div>
#                     <div class="game-item">
#                         <a href="/game3" class="title">Game 3</a>
#                     </div>
#                 </div>
#             </body>
#         </html>
#     """
#     with patch("scrapers.metacritic.scrape_utils.soup_it") as mock_soup_it:
#         mock_soup_it.return_value = BeautifulSoup(mock_response, "html.parser")
#         link = "https://example.com/search?q=keyword&page=1"
#         expected_output = ["/game1", "/game2", "/game3"]
#         assert get_games_per_page(link) == expected_output


# def test_get_games_per_page_with_invalid_link():
#     """
#     Test get_games_per_page() with an invalid link.
#     """
#     mock_response = """
#         <html>
#             <body>
#                 <div class="game-list">
#                 </div>
#             </body>
#         </html>
#     """
#     with patch("scrapers.metacritic.scrape_utils.soup_it") as mock_soup_it:
#         mock_soup_it.return_value = BeautifulSoup(mock_response, "html.parser")
#         link = "https://example.com/search?q=keyword&page=1"
#         expected_output = []
#         assert get_games_per_page(link) == expected_output


# import unittest


# class TestScraperFunctions(unittest.TestCase):
#     def test_scrape_metacritic_reviews(self):
#         # Test case 1
#         critic_review_list = []
#         exception_list = []
#         game_link = "https://www.metacritic.com/game/pc/pharaoh-a-new-era"
#         scrape_metacritic_reviews(game_link, critic_review_list, exception_list)
#         self.assertGreater(len(critic_review_list), 0)
#         self.assertEqual(len(exception_list), 0)

#         # Test case 2
#         critic_review_list = []
#         exception_list = []
#         game_link = "https://www.metacritic.com/game/pc/pharaoh-a-new-era"
#         scrape_metacritic_reviews(game_link, critic_review_list, exception_list)
#         self.assertGreater(len(critic_review_list), 0)
#         self.assertEqual(len(exception_list), 0)

#     def test_scrape_user_reviews(self):
#         # Test case 1
#         review_list = []
#         exception_list = []
#         game_link = "https://www.metacritic.com/game/pc/pharaoh-a-new-era"
#         scrape_user_reviews(game_link, review_list, exception_list)
#         self.assertGreater(len(review_list), 0)
#         self.assertEqual(len(exception_list), 0)

#         # Test case 2
#         review_list = []
#         exception_list = []
#         game_link = "https://www.metacritic.com/game/pc/pharaoh-a-new-era"
#         scrape_user_reviews(game_link, review_list, exception_list)
#         self.assertGreater(len(review_list), 0)
#         self.assertEqual(len(exception_list), 0)
