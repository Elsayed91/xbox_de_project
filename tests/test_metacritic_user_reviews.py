# pylint: disable=missing-function-docstring, too-many-function-args, missing-module-docstring, unused-argument

from unittest.mock import MagicMock, patch

import pytest
from bs4 import BeautifulSoup
from scrapers.metacritic.scrape_user_reviews import (
    extract_review_text,
    extract_user_reviews,
    scrape_user_reviews,
)

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


@pytest.fixture
def example_html():
    return """
<div class="review_content">
   <div class="review_section">
      <div class="review_stats">
         <div class="review_critic">
            <div class="name">
               <a href="/user/xdxdxd">xdxdxd</a>
            </div>
            <div class="date">Dec 12, 2020</div>
         </div>
         <div class="review_grade">
            <div class="metascore_w user medium game positive indiv perfect">10</div>
         </div>
      </div>
      <div class="review_body">
         <span>This game is fantastic! Highly recommended.</span>
      </div>
   </div>
</div>
"""


@pytest.fixture
def expected_reviews():
    return [
        {
            "Game": "Example Game",
            "Platform": "Example Platform",
            "User": "xdxdxd",
            "Date": "Dec 12, 2020",
            "Score": "10",
            "Review": "This game is fantastic! Highly recommended.",
        }
    ]


@pytest.fixture
def patched_extract_game_info():
    with patch(
        "scrapers.metacritic.scrape_user_reviews.extract_game_info"
    ) as mock_extract_game_info:
        mock_extract_game_info.return_value = ("Example Game", "Example Platform")
        yield mock_extract_game_info


@pytest.fixture
def patched_get_last_page():
    with patch(
        "scrapers.metacritic.scrape_user_reviews.get_last_page"
    ) as mock_get_last_page:
        mock_get_last_page.return_value = 0
        yield mock_get_last_page


@pytest.fixture
def patched_get_soup(example_html):
    with patch("scrapers.metacritic.scrape_user_reviews.get_soup") as mock_get_soup:
        soup = BeautifulSoup(example_html, "html.parser")
        mock_get_soup.return_value = soup
        yield mock_get_soup


@pytest.fixture
def patched_extract_user_reviews(expected_reviews):
    with patch(
        "scrapers.metacritic.scrape_user_reviews.extract_user_reviews"
    ) as mock_extract_user_reviews:
        mock_extract_user_reviews.return_value = expected_reviews
        yield mock_extract_user_reviews


def test_extract_user_reviews(
    example_html, expected_reviews, patched_extract_game_info
):
    soup = BeautifulSoup(example_html, "html.parser")
    reviews = extract_user_reviews(soup)

    assert reviews == expected_reviews


def test_scrape_user_reviews(
    example_html,
    expected_reviews,
    patched_get_last_page,
    patched_get_soup,
    patched_extract_user_reviews,
):
    game_link = "https://www.example.com/game-link"
    max_retries = 8
    reviews = scrape_user_reviews(game_link, max_retries)
    assert reviews == expected_reviews
