"""
This module handles the scraping of Metacritic game data.
It looks for a file, and iterates over all the links within and scraping the respective
games.
The column `gamepass_status` is added to the data for enrichment. 
"""
import datetime
import json
import logging
import os
import time
from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz, process

try:
    from scrape_utils import get_soup, read_txt
except:
    from scrapers.metacritic.scrape_utils import get_soup, read_txt


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

MAX_RETRIES = 8
RETRY_DELAY = 10


def fuzzy_match(name: str, names: list, threshold: int = 95) -> str:
    """
    Finds the best fuzzy match for the given name in a list of names and returns the
    matched name if its score is above the given threshold, otherwise returns None.

    Args:
        name (str): The name to search for.
        names (list): A list of names to search in.
        threshold (int): Optional. The minimum score required for a match.

    Returns:
        str: The best matched name if its score is above the threshold, otherwise None.
    """
    try:
        matched = process.extractOne(name, names, scorer=fuzz.token_sort_ratio)
        if matched[1] >= threshold:
            return matched[0]
        else:
            return None
    except TypeError as e:
        raise TypeError(f"Failed to perform fuzzy matching: {e}")


def add_gamepass_status(
    main_df: pd.DataFrame, fuzzy_matching: bool = False
) -> pd.DataFrame:
    """
    Adds a 'Gamepass_Status' column to the input DataFrame indicating whether each game is
    available on Game Pass.

    Args:
        main_df: The input DataFrame containing a 'Name' column.
        fuzzy_matching: A boolean indicating whether fuzzy matching should be used.

    Returns:
        A copy of the input DataFrame with an additional 'Gamepass_Status' column.
    """
    url = (
        "https://docs.google.com/spreadsheet/ccc?key=1ks"
        + "pw-4paT-eE5-mrCrc4R9tg70lH2ZTFrJOUmOtOytg&output=csv"
    )
    df = pd.read_csv(url, skiprows=[0])
    df = df[["Game", "Status"]]
    game_names = df["Game"].tolist()
    statuses = df["Status"].tolist()
    main_df["Gamepass_Status"] = (
        main_df["Name"]
        .apply(lambda x: fuzzy_match(x, game_names) if fuzzy_matching else x)
        .fillna("Not Included")
    )
    main_df["Gamepass_Status"] = main_df["Gamepass_Status"].fillna("Not Included")
    main_df["Gamepass_Status"] = main_df["Gamepass_Status"].apply(
        lambda x: statuses[game_names.index(x)] if x in game_names else "Not Included"
    )
    return main_df


def scrape_game_data(link: str, max_retries: int = 8) -> dict:
    """
    Scrapes game data from the provided link.
    Includes some error handling and some checks to skip faulty links.

    Args:
        link (str): The URL of the webpage to scrape game data from.
        max_retries (int): The maximum number of retries in case of scraping failure.
            Defaults to 8.

    Returns:
        dict: A dictionary containing the scraped game data, or None if scraping fails.
    """
    retries = 0
    while retries < max_retries:
        soup = get_soup(link)
        if soup == 0:
            break

        script_tag = soup.find("script", type="application/ld+json")

        if script_tag is not None:
            data = json.loads(script_tag.text)
            game_data = extract_game_data(data, soup)
            if game_data is not None:
                if retries > 0:
                    logger.info("Succeeded after %s retries for %s.", retries, link)
                return game_data

        logger.warning("No script tag found for %s. Retrying...", link)
        time.sleep(retries * 3)
        retries += 1

    logger.warning("Skipping link due to scraping failure: %s", link)
    return None


def extract_game_data(data: dict, soup) -> dict:
    """
    Extracts relevant game data from the scraped JSON data.

    Args:
        data (dict): A dictionary containing the JSON data scraped from the webpage.
        soup: The BeautifulSoup object representing the scraped HTML.

    Returns:
        dict: A dictionary containing the extracted game data.
    """
    game_data = {}

    game_data["Name"] = data.get("name")
    game_data["Release Date"] = extract_release_date(data)
    game_data["Maturity Rating"] = extract_maturity_rating(data)
    game_data["Genre"] = extract_genre(data)
    game_data["Platform"] = data.get("gamePlatform")
    game_data["Developer"] = extract_developer(soup)
    game_data["Publisher"] = extract_publisher(data)
    game_data["Meta Score"] = extract_meta_score(data)
    game_data["Critic Reviews Count"] = extract_critic_review_count(soup)
    game_data["User Score"] = extract_user_score(soup)
    game_data["User Rating Count"] = extract_user_rating_count(soup)
    game_data["Summary"] = data.get("description")
    game_data["Image"] = data["image"]

    return game_data


def extract_release_date(data: dict) -> str:
    """
    Extracts the release date from the JSON data.

    Args:
        data (dict): A dictionary containing the JSON data.

    Returns:
        str: The extracted release date in the format 'YYYY-MM-DD'.
    """
    release_date_str = data.get("datePublished")
    if release_date_str:
        release_date = datetime.strptime(release_date_str, "%B %d, %Y")
        return release_date.strftime("%Y-%m-%d")
    return ""


def extract_maturity_rating(data: dict) -> str:
    """
    Extracts the maturity rating from the JSON data.

    Args:
        data (dict): A dictionary containing the JSON data.

    Returns:
        str: The extracted maturity rating.
    """
    return data.get("contentRating", "Unspecified").replace("ESRB ", "")


def extract_genre(data: dict) -> str:
    """
    Extracts the genre from the JSON data.

    Args:
        data (dict): A dictionary containing the JSON data.

    Returns:
        str: The extracted genre as a comma-separated string.
    """
    genre_list = data.get("genre", [])
    return ", ".join(genre_list)


def extract_developer(soup: BeautifulSoup) -> str:
    """
    Extracts the developer from the scraped soup.

    Args:
        soup: The BeautifulSoup object representing the scraped HTML.

    Returns:
        str: The extracted developer.
    """
    developer = soup.select_one(".developer a")
    if developer:
        return developer.text
    return ""


def extract_publisher(data: dict) -> str:
    """
    Extracts the publisher from the JSON data.

    Args:
        data (dict): A dictionary containing the JSON data.

    Returns:
        str: The extracted publisher as a comma-separated string.
    """
    publisher_list = data.get("publisher", [])
    return ", ".join([x["name"] for x in publisher_list])


def extract_meta_score(data: dict) -> int:
    """
    Extracts the meta score from the JSON data.

    Args:
        data (dict): A dictionary containing the JSON data.

    Returns:
        int: The extracted meta score as an integer.
    """
    aggregate_rating = data.get("aggregateRating")
    if aggregate_rating:
        return int(aggregate_rating["ratingValue"])
    return None


def extract_critic_review_count(soup: BeautifulSoup) -> int:
    """
    Extracts the critic review count from the scraped data.

    Args:
        soup: The BeautifulSoup object representing the scraped HTML.

    Returns:
        int: The extracted critic review count.
    """
    critic_review_count = soup.find("span", {"class": "count"})
    if critic_review_count:
        return int(critic_review_count.find("a").text.split()[0])
    return 0


def extract_user_score(soup: BeautifulSoup) -> float:
    """
    Extracts the user score from the scraped data.

    Args:
        soup: The BeautifulSoup object representing the scraped HTML.

    Returns:
        float: The extracted user score as a float.
    """
    user_score_element = soup.find("div", class_="user")
    if user_score_element:
        user_score_text = user_score_element.text
        if user_score_text != "tbd":
            return float(user_score_text)
    return None


def extract_user_rating_count(soup: BeautifulSoup) -> int:
    """
    Extracts the user rating count from the scraped data.

    Args:
        soup: The BeautifulSoup object representing the scraped HTML.

    Returns:
        int: The extracted user rating count.

    """
    user_rating_count_elements = soup.find_all("div", {"class": "summary"})
    if len(user_rating_count_elements) > 1:
        user_rating_count_element = user_rating_count_elements[1].find("a")

        if user_rating_count_element is not None:
            user_rating_count_text = user_rating_count_element.text.strip().split()[0]
            if user_rating_count_text.isdigit():
                return int(user_rating_count_text)
    return 0


def calculate_weighted_score(row: pd.Series) -> float:
    """
    Calculates the weighted score based on the provided equation.

    Args:
        row: A pandas Series containing the necessary data for calculation.

    Returns:
        The calculated weighted score.
    """
    critic_reviews_count = row["Critic Reviews Count"] or 0
    meta_score = row["Meta Score"] or 0
    user_rating_count = row["User Rating Count"] or 0
    user_score = row["User Score"] or 0
    return weighted_score


if __name__ == "__main__":
    console = os.getenv("console")
    local_path = os.getenv("local_path")
    game_list = read_txt(console, local_path)
    game_data = []
    for game_url in game_list:
        data = scrape_game_data(game_url)
        if data is not None:
            game_data.append(data)
    df1 = pd.DataFrame.from_records(game_data)
    df1["Weighted Score"] = df1.apply(calculate_weighted_score, axis=1)
    df1 = add_gamepass_status(df1)
    df1.to_parquet(f"{local_path}{console}-games.parquet")
    print("done")
