# pylint: disable=missing-function-docstring, too-many-function-args, missing-module-docstring

import pytest
from bs4 import BeautifulSoup
from scrapers.metacritic.scrape_games_data import *
from scrapers.metacritic.scrape_games_lists import *
from scrapers.metacritic.scrape_metacritic_reviews import *
from scrapers.metacritic.scrape_user_reviews import *
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
    game_data = scrape_game_data(link)
    assert game_data is not None
    assert game_data["Name"] == "The Legend of Zelda: Link's Awakening"
    assert game_data["Release Date"] == "2019-09-20"
    assert game_data["Maturity Rating"] == "E"
    assert game_data["Genre"] == "Action Adventure, Open-World"
    assert game_data["Developer"] == "Nintendo"
    assert game_data["Publisher"] == "Nintendo"
    ## Update these values to the latest ones for accurate testing
    # assert int(game_data["Meta Score"]) == 87
    # assert int(game_data["Critic Reviews Count"]) == 111
    # assert game_data["User Score"] == 8.4
    # assert game_data["User Rating Count"] == 1653
    assert "Summary" in game_data


def test_extract_game_data():
    data = {
        "name": "The Legend of Zelda: Link's Awakening",
        "gamePlatform": "Nintendo Switch",
        "description": "Summary of the game",
        "image": "https://example.com/game_image.jpg",
        "datePublished": "September 20, 2019",  # Updated key for release date
        "contentRating": "ESRB E",
        "genre": ["Action Adventure", "Open-World"],  # Updated genre as a list
        "publisher": [{"name": "Nintendo"}],
        "aggregateRating": {"ratingValue": 87},
    }
    soup = BeautifulSoup(
        """
        <html>
            <div class='developer'><a>Nintendo</a></div>
            <span class='count'><a>111 reviews</a></span>
            <div class='user'>8.4</div>
[<div class="summary"> <p> <span class="desc">
                                            Universal acclaim
                                    </span>
<span class="count"> <span class="separator"> - </span> <span class="based">based
on</span> <a href="/game/xbox-360/grand-theft-auto-iv/critic-reviews"> <span>
                                86
                            </span> Critic Reviews </a>
</span> <span class="help"><a href="/about-metascores">What's this?</a></span> </p>
</div>, <div class="summary"> <p><span class="desc">Generally favorable
reviews</span><span class="count"><span class="separator">- </span><span
class="based">based on</span> <a
href="/game/xbox-360/grand-theft-auto-iv/user-reviews">3735 Ratings</a></span></p> </div>,
<div class="summary feedback has_feedback"> <p class="rating_error"></p> </div>, <div
class="summary feedback"> </div>, <div class="summary"> <p><span class="desc">Generally
favorable reviews</span><span class="count"><span class="separator">- </span><span
class="based">based on</span> <strong>3735 Ratings</strong></span></p> </div>]
        </div> </html>
        """,
        "html.parser",
    )

    game_data = extract_game_data(data, soup)

    assert game_data["Name"] == "The Legend of Zelda: Link's Awakening"
    assert game_data["Release Date"] == "2019-09-20"
    assert game_data["Maturity Rating"] == "E"
    assert game_data["Genre"] == "Action Adventure, Open-World"
    assert game_data["Platform"] == "Nintendo Switch"
    assert game_data["Developer"] == "Nintendo"
    assert game_data["Publisher"] == "Nintendo"
    assert game_data["Meta Score"] == 87
    assert game_data["Summary"] == "Summary of the game"
    assert game_data["Image"] == "https://example.com/game_image.jpg"
    assert game_data["Critic Reviews Count"] == 111
    assert game_data["User Score"] == 8.4
    assert game_data["User Rating Count"] == 3735


def test_extract_release_date():
    data = {"datePublished": "September 20, 2019"}
    assert extract_release_date(data) == "2019-09-20"

    data = {"datePublished": ""}
    assert extract_release_date(data) == ""

    data = {}
    assert extract_release_date(data) == ""


def test_extract_maturity_rating():
    data = {"contentRating": "ESRB E"}
    assert extract_maturity_rating(data) == "E"

    data = {"contentRating": ""}
    assert extract_maturity_rating(data) == ""

    data = {}
    assert extract_maturity_rating(data) == "Unspecified"


def test_extract_genre():
    data = {"genre": ["Action", "Adventure"]}
    assert extract_genre(data) == "Action, Adventure"

    data = {"genre": []}
    assert extract_genre(data) == ""

    data = {}
    assert extract_genre(data) == ""


def test_extract_developer():
    soup = BeautifulSoup(
        "<html><div class='developer'><a>Nintendo</a></div></html>", "html.parser"
    )
    assert extract_developer(soup) == "Nintendo"

    soup = BeautifulSoup("<html></html>", "html.parser")
    assert extract_developer(soup) == ""


def test_extract_publisher():
    data = {"publisher": [{"name": "Nintendo"}, {"name": "Sony"}]}
    assert extract_publisher(data) == "Nintendo, Sony"

    data = {"publisher": []}
    assert extract_publisher(data) == ""

    data = {}
    assert extract_publisher(data) == ""


def test_extract_meta_score():
    data = {"aggregateRating": {"ratingValue": 87}}
    assert extract_meta_score(data) == 87

    data = {"aggregateRating": {}}
    assert extract_meta_score(data) is None

    data = {}
    assert extract_meta_score(data) is None


def test_extract_critic_review_count():
    soup = BeautifulSoup(
        """
        <html>
            <span class="count"><a>111 reviews</a></span>
            <div class="summary">Some other information</div>
        </html>
        """,
        "html.parser",
    )
    assert extract_critic_review_count(soup) == 111

    soup = BeautifulSoup(
        """
        <html>
            <div class="summary">Some other information</div>
        </html>
        """,
        "html.parser",
    )
    assert extract_critic_review_count(soup) == 0


def test_extract_user_score():
    soup = BeautifulSoup(
        """
        <html>
            <div class="user">8.4</div>
            <div class="summary">Some other information</div>
        </html>
        """,
        "html.parser",
    )
    assert extract_user_score(soup) == 8.4

    soup = BeautifulSoup(
        """
        <html>
            <div class="user">tbd</div>
            <div class="summary">Some other information</div>
        </html>
        """,
        "html.parser",
    )
    assert extract_user_score(soup) is None

    soup = BeautifulSoup(
        """
        <html>
            <div class="summary">Some other information</div>
        </html>
        """,
        "html.parser",
    )
    assert extract_user_score(soup) is None


def test_extract_user_rating_count():
    soup = BeautifulSoup(
        """
        <html>
[<div class="summary"> <p> <span class="desc">
                                            Universal acclaim
                                    </span>
<span class="count"> <span class="separator"> - </span> <span class="based">based
on</span> <a href="/game/xbox-360/grand-theft-auto-iv/critic-reviews"> <span>
                                86
                            </span> Critic Reviews </a>
</span> <span class="help"><a href="/about-metascores">What's this?</a></span> </p>
</div>, <div class="summary"> <p><span class="desc">Generally favorable
reviews</span><span class="count"><span class="separator">- </span><span
class="based">based on</span> <a
href="/game/xbox-360/grand-theft-auto-iv/user-reviews">3735 Ratings</a></span></p> </div>,
<div class="summary feedback has_feedback"> <p class="rating_error"></p> </div>, <div
class="summary feedback"> </div>, <div class="summary"> <p><span class="desc">Generally
favorable reviews</span><span class="count"><span class="separator">- </span><span
class="based">based on</span> <strong>3735 Ratings</strong></span></p> </div>]
        </html>
        """,
        "html.parser",
    )
    assert extract_user_rating_count(soup) == 3735

    soup = BeautifulSoup(
        """
        <html>
            <div class="summary">Some other information</div>
        </html>
        """,
        "html.parser",
    )
    assert extract_user_rating_count(soup) == 0
