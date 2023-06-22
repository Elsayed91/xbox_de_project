# pylint: disable=missing-function-docstring, too-many-function-args, missing-module-docstring

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


example_html = """
<div class="review_content">
    <div class="review_section">
        <div class="review_stats">
            <div class="review_critic">
                <div class="source">
                    <a rel="popup:external" class="external" href="http://www.oxm.co.uk/article.php?id=3993" target="_blank">Official Xbox Magazine UK</a>
                </div>
            </div>
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


def test_extract_metacritic_reviews():
    soup = BeautifulSoup(example_html, "html.parser")

    expected_reviews = [
        {
            "Game": "Example Game",
            "Platform": "Example Platform",
            "Critic": "Official Xbox Magazine UK",
            "Review Source": "http://www.oxm.co.uk/article.php?id=3993",
            "Score": "100",
            "Review": "It's got a world you believe in, a cast you care about and a script stuffed with brilliant moments... Utterly stunning in every resepct. [May 2008, p.79]",
        }
    ]

    with patch(
        "scrapers.metacritic.scrape_metacritic_reviews.extract_game_info"
    ) as mock_extract_game_info:
        mock_extract_game_info.return_value = ("Example Game", "Example Platform")

        reviews = extract_metacritic_reviews(soup)
        assert reviews == expected_reviews


def test_scrape_metacritic_reviews():
    game_link = "https://www.metacritic.com/game/example-game"
    max_retries = 8

    expected_reviews = [
        {
            "Game": "Example Game",
            "Platform": "Example Platform",
            "Critic": "Official Xbox Magazine UK",
            "Review Source": "http://www.oxm.co.uk/article.php?id=3993",
            "Score": "100",
            "Review": "It's got a world you believe in, a cast you care about and a script stuffed with brilliant moments... Utterly stunning in every resepct. [May 2008, p.79]",
        }
    ]

    soup = BeautifulSoup(example_html, "html.parser")

    with patch(
        "scrapers.metacritic.scrape_metacritic_reviews.get_last_page"
    ) as mock_get_last_page:
        mock_get_last_page.return_value = 0

        with patch(
            "scrapers.metacritic.scrape_metacritic_reviews.get_soup"
        ) as mock_get_soup:
            mock_get_soup.return_value = soup

            with patch(
                "scrapers.metacritic.scrape_metacritic_reviews.extract_metacritic_reviews"
            ) as mock_extract_metacritic_reviews:
                mock_extract_metacritic_reviews.return_value = expected_reviews

                reviews = scrape_metacritic_reviews(game_link, max_retries)
                assert reviews == expected_reviews
