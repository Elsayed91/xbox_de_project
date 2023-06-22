# pylint: disable=missing-function-docstring, too-many-function-args, missing-module-docstring

import unittest
from datetime import datetime
from unittest import mock
from unittest.mock import MagicMock, patch

import pytest
from bs4 import BeautifulSoup
from scrapers.metacritic.scrape_games_data import *
from scrapers.metacritic.scrape_games_lists import *
from scrapers.metacritic.scrape_metacritic_reviews import *
from scrapers.metacritic.scrape_metacritic_reviews import (
    extract_metacritic_reviews,
    scrape_metacritic_reviews,
)
from scrapers.metacritic.scrape_user_reviews import *
from scrapers.metacritic.scrape_utils import *

################################################################
# Metacritic Critic-Reviews Tests
################################################################


# example_html = """
# <div class="review_content">
#     <div class="review_section">
#         <div class="review_stats">
#             <div class="review_critic">
#                 <div class="source">
#                     <a rel="popup:external" class="external" href="http://www.oxm.co.uk/article.php?id=3993" target="_blank">Official Xbox Magazine UK</a>
#                 </div>
#             </div>
#             <div class="review_grade">
#                 <div class="metascore_w medium game positive indiv perfect">100</div>
#             </div>
#         </div>
#         <div class="review_body">
#             It's got a world you believe in, a cast you care about and a script stuffed with brilliant moments... Utterly stunning in every resepct. [May 2008, p.79]
#         </div>
#     </div>
#     <div class="review_section review_actions">
#         <ul class="review_actions">
#             <li class="review_action author_reviews"><a href="/publication/official-xbox-magazine-uk?filter=games">All this publication's reviews</a></li>
#             <li class="review_action full_review"><a rel="popup:external" class="external" href="http://www.oxm.co.uk/article.php?id=3993" target="_blank">Read full review<i class="fa fa-external-link" aria-hidden="true"></i></a></li>
#         </ul>
#     </div>
# </div>
# """


# def test_extract_metacritic_reviews():
#     soup = BeautifulSoup(example_html, "html.parser")

#     expected_reviews = [
#         {
#             "Game": "Example Game",
#             "Platform": "Example Platform",
#             "Critic": "Official Xbox Magazine UK",
#             "Review Source": "http://www.oxm.co.uk/article.php?id=3993",
#             "Score": "100",
#             "Review": "It's got a world you believe in, a cast you care about and a script stuffed with brilliant moments... Utterly stunning in every resepct. [May 2008, p.79]",
#         }
#     ]

#     with patch(
#         "scrapers.metacritic.scrape_metacritic_reviews.extract_game_info"
#     ) as mock_extract_game_info:
#         mock_extract_game_info.return_value = ("Example Game", "Example Platform")

#         reviews = extract_metacritic_reviews(soup)
#         assert reviews == expected_reviews


# def test_scrape_metacritic_reviews():
#     game_link = "https://www.metacritic.com/game/example-game"
#     max_retries = 8

#     expected_reviews = [
#         {
#             "Game": "Example Game",
#             "Platform": "Example Platform",
#             "Critic": "Official Xbox Magazine UK",
#             "Review Source": "http://www.oxm.co.uk/article.php?id=3993",
#             "Score": "100",
#             "Review": "It's got a world you believe in, a cast you care about and a script stuffed with brilliant moments... Utterly stunning in every resepct. [May 2008, p.79]",
#         }
#     ]

#     example_html = """
#     <div class="review_content">
#         <div class="review_section">
#             <div class="review_stats">
#                 <div class="review_critic"><div class="source"><a rel="popup:external" class="external" href="http://www.oxm.co.uk/article.php?id=3993" target="_blank">Official Xbox Magazine UK</a></div></div>
#                 <div class="review_grade">
#                     <div class="metascore_w medium game positive indiv perfect">100</div>
#                 </div>
#             </div>
#             <div class="review_body">
#                 It's got a world you believe in, a cast you care about and a script stuffed with brilliant moments... Utterly stunning in every resepct. [May 2008, p.79]
#             </div>
#         </div>
#         <div class="review_section review_actions">
#             <ul class="review_actions">
#                 <li class="review_action author_reviews"><a href="/publication/official-xbox-magazine-uk?filter=games">All this publication's reviews</a></li>
#                 <li class="review_action full_review"><a rel="popup:external" class="external" href="http://www.oxm.co.uk/article.php?id=3993" target="_blank">Read full review<i class="fa fa-external-link" aria-hidden="true"></i></a></li>
#             </ul>
#         </div>
#     </div>
#     """

#     soup = BeautifulSoup(example_html, "html.parser")

#     with patch(
#         "scrapers.metacritic.scrape_metacritic_reviews.get_last_page"
#     ) as mock_get_last_page:
#         mock_get_last_page.return_value = 0

#         with patch(
#             "scrapers.metacritic.scrape_metacritic_reviews.get_soup"
#         ) as mock_get_soup:
#             mock_get_soup.return_value = soup

#             with patch(
#                 "scrapers.metacritic.scrape_metacritic_reviews.extract_metacritic_reviews"
#             ) as mock_extract_metacritic_reviews:
#                 mock_extract_metacritic_reviews.return_value = expected_reviews

#                 reviews = scrape_metacritic_reviews(game_link, max_retries)
#                 assert reviews == expected_reviews


@pytest.fixture
def example_html():
    return """
<div class="review_content">
    <div class="review_section">
        <div class="review_stats">
            <div class="review_critic"><div class="source"><a rel="popup:external" class="external" href="http://www.oxm.co.uk/article.php?id=3993" target="_blank">Official Xbox Magazine UK</a></div></div>
            <div class="review_grade">
                <div class="metascore_w medium game positive indiv perfect">100</div>
            </div>
        </div>
        <div class="review_body">
            It's got a world you believe in, a cast you care about and a script stuffed with brilliant moments... Utterly stunning in every resepct. [May 2008, p.79]
        </div>
    </div>
    <div class="review_section review_actions">
        <ul class="review_actions">
            <li class="review_action author_reviews"><a href="/publication/official-xbox-magazine-uk?filter=games">All this publication's reviews</a></li>
            <li class="review_action full_review"><a rel="popup:external" class="external" href="http://www.oxm.co.uk/article.php?id=3993" target="_blank">Read full review<i class="fa fa-external-link" aria-hidden="true"></i></a></li>
        </ul>
    </div>
</div>
"""


@pytest.fixture
def expected_reviews():
    return [
        {
            "Game": "Example Game",
            "Platform": "Example Platform",
            "Critic": "Official Xbox Magazine UK",
            "Review Source": "http://www.oxm.co.uk/article.php?id=3993",
            "Score": "100",
            "Review": "It's got a world you believe in, a cast you care about and a script stuffed with brilliant moments... Utterly stunning in every resepct. [May 2008, p.79]",
        }
    ]


@pytest.fixture
def patched_extract_game_info():
    with patch(
        "scrapers.metacritic.scrape_metacritic_reviews.extract_game_info"
    ) as mock_extract_game_info:
        mock_extract_game_info.return_value = ("Example Game", "Example Platform")
        yield mock_extract_game_info


@pytest.fixture
def patched_get_last_page():
    with patch(
        "scrapers.metacritic.scrape_metacritic_reviews.get_last_page"
    ) as mock_get_last_page:
        mock_get_last_page.return_value = 0
        yield mock_get_last_page


@pytest.fixture
def patched_get_soup(example_html):
    with patch(
        "scrapers.metacritic.scrape_metacritic_reviews.get_soup"
    ) as mock_get_soup:
        soup = BeautifulSoup(example_html, "html.parser")
        mock_get_soup.return_value = soup
        yield mock_get_soup


@pytest.fixture
def patched_extract_metacritic_reviews(expected_reviews):
    with patch(
        "scrapers.metacritic.scrape_metacritic_reviews.extract_metacritic_reviews"
    ) as mock_extract_metacritic_reviews:
        mock_extract_metacritic_reviews.return_value = expected_reviews
        yield mock_extract_metacritic_reviews


def test_extract_metacritic_reviews(
    example_html, expected_reviews, patched_extract_game_info
):
    soup = BeautifulSoup(example_html, "html.parser")
    reviews = extract_metacritic_reviews(soup)
    assert reviews == expected_reviews


def test_scrape_metacritic_reviews(
    example_html,
    expected_reviews,
    patched_get_last_page,
    patched_get_soup,
    patched_extract_metacritic_reviews,
):
    game_link = "https://www.metacritic.com/game/example-game"
    max_retries = 8
    reviews = scrape_metacritic_reviews(game_link, max_retries)
    assert reviews == expected_reviews


################################################################
# Metacritic User-Reviews Tests
################################################################


txt = "GTA 4 is absolute masterpiece that was so ahead of time that even \
                    over decade later it still beats overhyped trash like \
                        Cyberpunk 2077."


def test_extract_review_text():
    soup = BeautifulSoup(
        f"""
        <div class="review_content">
            <div class="review_body">
                <span>{txt}</span>
            </div>
        </div>
    """,
        "html.parser",
    )

    review_text = extract_review_text(soup)
    assert review_text == txt


from unittest.mock import patch

import pytest
from scrapers.metacritic.scrape_user_reviews import (
    extract_user_reviews,
    scrape_user_reviews,
)


@pytest.fixture
def example_html2():
    return """
    <div class="review_content">
        <div class="review_section">
            <div class="review_stats">
                <div class="review_critic">
                    <div class="name">
                        <a href="/user/Rockstar900">Rockstar900</a>
                    </div>
                    <div class="date">Dec 12, 2020</div>
                </div>
                <div class="review_grade">
                    <div class="metascore_w user medium game positive indiv perfect">10</div>
                </div>
            </div>
            <div class="review_body">
                <span>GTA 4 is absolute masterpiece that was so ahead of time that even over decade later it still beats overhyped trash like Cyberpunk 2077.</span>
            </div>
        </div>
        <div class="review_section review_actions">
            <ul class="review_actions">
                <li class="review_action review_helpful">
                    <div class="review_helpful">
                        <div class="rating_thumbs">
                            <div class="helpful_summary thumb_count">
                                <a href="/login">
                                    <span class="total_ups">30</span>
                                    of
                                    <span class="total_thumbs">33</span>
                                    users found this helpful
                                </a>
                            </div>
                            <div style="clear:both;"></div>
                        </div>
                    </div>
                </li>
                <li class="review_action">
                    <a href="/user/Rockstar900">All this user's reviews</a>
                </li>
            </ul>
        </div>
    </div>
    """


@patch("scrapers.metacritic.scrape_user_reviews.extract_game_info")
def test_scrape_user_reviews(patched_extract_game_info):
    patched_extract_game_info.return_value = ("Grand Theft Auto IV", "PlayStation 4")

    result = scrape_user_reviews("https://www.example.com/game-link")
    expected_result = [
        {
            "Game": "Grand Theft Auto IV",
            "Platform": "PlayStation 4",
            "User": "Rockstar900",
            "Date": "Dec 12, 2020",
            "Score": "10",
            "Review": "GTA 4 is absolute masterpiece that was so ahead of time that even over decade later it still beats overhyped trash like Cyberpunk 2077.",
        }
    ]

    assert result == expected_result


@patch("scrapers.metacritic.scrape_user_reviews.extract_user_reviews")
def test_extract_user_reviews(patched_extract_user_reviews):
    patched_extract_user_reviews.return_value = [
        {
            "Game": "Grand Theft Auto IV",
            "Platform": "PlayStation 4",
            "User": "Rockstar900",
            "Date": "Dec 12, 2020",
            "Score": "10",
            "Review": "GTA 4 is absolute masterpiece that was so ahead of time that even over decade later it still beats overhyped trash like Cyberpunk 2077.",
        }
    ]

    result = extract_user_reviews(example_html2())
    expected_result = [
        {
            "Game": "Grand Theft Auto IV",
            "Platform": "PlayStation 4",
            "User": "Rockstar900",
            "Date": "Dec 12, 2020",
            "Score": "10",
            "Review": "GTA 4 is absolute masterpiece that was so ahead of time that even over decade later it still beats overhyped trash like Cyberpunk 2077.",
        }
    ]

    assert result == expected_result
