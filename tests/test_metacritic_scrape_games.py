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
# Scrape Games Data
########################################################################


def test_fuzzy_match():
    # Test fuzzy matching with different thresholds

    game_names = ["Halo", "Forza Horizon", "Gears of War"]

    # Test exact match (threshold = 0)
    assert fuzzy_match("Halo 3", game_names) == "Halo"

    # Test looser match (threshold = 20)
    assert fuzzy_match("Gears", game_names, threshold=20) == "Gears of War"

    # Test stricter match (threshold = 80)
    assert fuzzy_match("Halo 3", game_names, threshold=80) == "Halo"


@pytest.fixture
def example_df() -> pd.DataFrame:
    # Create an example DataFrame for testing
    return pd.DataFrame({"Name": ["xdxdxdxd", "Terraria", "CrossfireX"]})


def test_add_gamepass_status(example_df):
    # Test the add_gamepass_status function

    # Generate output DataFrame
    output_df = add_gamepass_status(example_df)

    # Assert column names in the output DataFrame
    assert set(output_df.columns) == {"Name", "Gamepass_Status"}

    # Assert Gamepass status for specific rows
    assert output_df.loc[0, "Gamepass_Status"] == "Not Included"
    assert output_df.loc[1, "Gamepass_Status"] == "Active"
    assert output_df.loc[2, "Gamepass_Status"] == "Removed"


def test_scrape_game_data():
    # Test the scrape_game_data function with a specific link

    link = "https://www.metacritic.com/game/switch/the-legend-of-zelda-links-awakening"

    # Scrape game data
    game_data = scrape_game_data(link)

    # Assert the extracted game data
    assert game_data is not None
    assert game_data["Name"] == "The Legend of Zelda: Link's Awakening"
    assert game_data["Release Date"] == "2019-09-20"
    assert game_data["Maturity Rating"] == "E"
    assert game_data["Genre"] == "Action Adventure, Open-World"
    assert game_data["Developer"] == "Nintendo"
    assert game_data["Publisher"] == "Nintendo"
    # Update the following assertions to the latest values for accurate testing
    # assert int(game_data["Meta Score"]) == 87
    # assert int(game_data["Critic Reviews Count"]) == 111
    # assert game_data["User Score"] == 8.4
    # assert game_data["User Rating Count"] == 1653
    assert "Summary" in game_data


def test_extract_game_data():
    # Test the extract_game_data function with specific input data and soup

    # Sample input data
    data = {
        "name": "The Legend of Zelda: Link's Awakening",
        "gamePlatform": "Nintendo Switch",
        "description": "Summary of the game",
        "image": "https://example.com/game_image.jpg",
        "datePublished": "September 20, 2019",
        "contentRating": "ESRB E",
        "genre": ["Action Adventure", "Open-World"],
        "publisher": [{"name": "Nintendo"}],
        "aggregateRating": {"ratingValue": 87},
    }

    # Sample input soup
    soup = BeautifulSoup(
        """
<html>
   <div class='developer'><a>Nintendo</a></div>
   <span class='count'><a>111 reviews</a></span>
   <div class='user'>8.4</div>
   [
   <div class="summary">
      <p> <span class="desc">
         Universal acclaim
         </span>
         <span class="count"> <span class="separator"> - </span> <span class="based">based
         on</span> <a href="/game/xbox-360/grand-theft-auto-iv/critic-reviews"> <span>
         86
         </span> Critic Reviews </a>
         </span> <span class="help"><a href="/about-metascores">What's this?</a></span> 
      </p>
   </div>
   , 
   <div class="summary">
      <p><span class="desc">Generally favorable
         reviews</span><span class="count"><span class="separator">- </span><span
            class="based">based on</span> <a
            href="/game/xbox-360/grand-theft-auto-iv/user-reviews">3735 Ratings</a></span>
      </p>
   </div>
   ]
   </div> 
</html>
        """,
        "html.parser",
    )

    # Extract game data
    game_data = extract_game_data(data, soup)

    # Assert the extracted game data
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
    # Test the extract_release_date function with different input data
    data = {"datePublished": "September 20, 2019"}
    assert extract_release_date(data) == "2019-09-20"

    data = {"datePublished": ""}
    assert extract_release_date(data) == ""

    data = {}
    assert extract_release_date(data) == ""


def test_extract_maturity_rating():
    # Test the extract_maturity_rating function with different input data
    data = {"contentRating": "ESRB E"}
    assert extract_maturity_rating(data) == "E"

    data = {"contentRating": ""}
    assert extract_maturity_rating(data) == ""

    data = {}
    assert extract_maturity_rating(data) == "Unspecified"


def test_extract_genre():
    # Test the extract_genre function with different input data
    data = {"genre": ["Action", "Adventure"]}
    assert extract_genre(data) == "Action, Adventure"

    data = {"genre": []}
    assert extract_genre(data) == ""

    data = {}
    assert extract_genre(data) == ""


def test_extract_developer():
    # Test the extract_developer function with different input soup
    soup = BeautifulSoup(
        "<html><div class='developer'><a>Nintendo</a></div></html>", "html.parser"
    )
    assert extract_developer(soup) == "Nintendo"

    soup = BeautifulSoup("<html></html>", "html.parser")
    assert extract_developer(soup) == ""


def test_extract_publisher():
    # Test the extract_publisher function with different input data
    data = {"publisher": [{"name": "Nintendo"}, {"name": "Sony"}]}
    assert extract_publisher(data) == "Nintendo, Sony"

    data = {"publisher": []}
    assert extract_publisher(data) == ""

    data = {}
    assert extract_publisher(data) == ""


def test_extract_meta_score():
    # Test the extract_meta_score function with different input data
    data = {"aggregateRating": {"ratingValue": 87}}
    assert extract_meta_score(data) == 87

    data = {"aggregateRating": {}}
    assert extract_meta_score(data) is None

    data = {}
    assert extract_meta_score(data) is None


def test_extract_critic_review_count():
    # Test the extract_critic_review_count function with different input soup
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
    # Test the extract_user_score function with different input soup
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
    # Test the extract_user_rating_count function with different input soup
    soup = BeautifulSoup(
        """
        <html>
<html>
   <div class='developer'><a>Nintendo</a></div>
   <span class='count'><a>111 reviews</a></span>
   <div class='user'>8.4</div>
   [
   <div class="summary">
      <p> <span class="desc">
         Universal acclaim
         </span>
         <span class="count"> <span class="separator"> - </span> <span class="based">based
         on</span> <a href="/game/xbox-360/grand-theft-auto-iv/critic-reviews"> <span>
         86
         </span> Critic Reviews </a>
         </span> <span class="help"><a href="/about-metascores">What's this?</a></span> 
      </p>
   </div>
   , 
   <div class="summary">
      <p><span class="desc">Generally favorable
         reviews</span><span class="count"><span class="separator">- </span><span
            class="based">based on</span> <a
            href="/game/xbox-360/grand-theft-auto-iv/user-reviews">3735 Ratings</a></span>
      </p>
   </div>
   ]
   </div> 
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
