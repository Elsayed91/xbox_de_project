"""
This module provides functions to scrape game data of a specific console from Metacritic 
and determine whether a game is available on Game Pass.

The `fuzzy_match` function searches for the best fuzzy match for a given name in a list of
names and returns the matched name if its score is above the given threshold, otherwise
returns None. This is done to overcome slight differences in naming of games like
apostrophes.

The `add_gamepass_status` function adds a 'Gamepass_Status' column to the input DataFrame
indicating whether each game is available on Game Pass.

The `scrape_game_data` function scrapes game data from a Metacritic URL and appends
scraped data to a list of dictionaries representing game data and appends any exceptions
to a list.

The `main` function is the entry point for the script and calls the add_gamepass_status
and scrape_game_data functions to scrape game data from Metacritic and determine whether a
game is available on Game Pass, and saves the scraped data to a parquet file.


The scraping logic was inspired by a stackoverflow post, however most of the scraping
logic was changed to allow for better error handling and improved scraping capabilities.
Additionally the script in the post did have some faults.

Reference: 
https://stackoverflow.com/questions/70143803/metacritic-scraping-how-to-properly-extract-developer-data
"""
import datetime
import json
import logging
import os
import time
from datetime import datetime

import pandas as pd
from fuzzywuzzy import fuzz, process

try:
    from scrape_utils import *
except:
    from scrapers.metacritic.scrape_utils import *

logging.basicConfig(
    format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
    level=logging.INFO,
)


def fuzzy_match(name: str, names: list, threshold: int = 60) -> str:
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


def add_gamepass_status(main_df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a 'Gamepass_Status' column to the input DataFrame indicating whether each game is
    available on Game Pass.

    Args:
        main_df: The input DataFrame containing a 'Name' column.

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
        .apply(lambda x: fuzzy_match(x, game_names))
        .fillna("Not Included")
    )
    main_df["Gamepass_Status"] = main_df["Gamepass_Status"].fillna("Not Included")
    main_df["Gamepass_Status"] = main_df["Gamepass_Status"].apply(
        lambda x: statuses[game_names.index(x)] if x in game_names else "Not Included"
    )
    return main_df


import logging
import time


def retry(func, max_retries=3, backoff_factor=2):
    """
    Decorator function for retrying a function with exponential backoff.
    """

    def wrapper(*args, **kwargs):
        retries = 0
        while retries < max_retries:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                retries += 1
                if retries >= max_retries:
                    logging.error(f"Failed after {max_retries} retries. Error: {e}")
                    raise
                else:
                    backoff_time = backoff_factor**retries
                    logging.warning(f"Retrying in {backoff_time} seconds... Error: {e}")
                    time.sleep(backoff_time)

    return wrapper


def scrape_game_data(
    link: str, data_list: list[dict], exception_list: list[str]
) -> None:
    retries = 0
    last_soup = None
    while retries < 3:
        try:
            soup = soup_it(link)
            last_soup = soup  # Store the last successful soup object

            script_tag = soup.find("script", type="application/ld+json")
            if script_tag is not None:
                data = json.loads(script_tag.text)

            game_data = extract_game_data(data, soup)
            if game_data is not None:
                data_list.append(game_data)
                return

        except Exception as e:
            logging.error(f"On game link {link}, Error: {e}", exc_info=True)
            exception_list.append(f"On game link {link}, Error: {e}")

        retries += 1
        if retries < 3:
            logging.warning(f"Retrying in 10 seconds...")
            time.sleep(10)

    # Log the last value of the soup variable after three failed retries
    if last_soup is not None:
        logging.error(f"Failed after 3 retries. Last soup: {last_soup}")
    else:
        logging.error(f"Failed after 3 retries. Soup object is None.")


def extract_game_data(data: dict, soup) -> dict:
    """
    Extracts relevant game data from the scraped soup and JSON data.
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
    """
    release_date_str = data.get("datePublished")
    if release_date_str:
        release_date = datetime.strptime(release_date_str, "%B %d, %Y")
        return release_date.strftime("%Y-%m-%d")
    return ""


def extract_maturity_rating(data: dict) -> str:
    """
    Extracts the maturity rating from the JSON data.
    """
    return data.get("contentRating", "Unspecified").replace("ESRB ", "")


def extract_genre(data: dict) -> str:
    """
    Extracts the genre from the JSON data.
    """
    genre_list = data.get("genre", [])
    return ", ".join(genre_list)


def extract_developer(soup) -> str:
    """
    Extracts the developer from the scraped soup.
    """
    developer = soup.select_one(".developer a")
    if developer:
        return developer.text
    return ""


def extract_publisher(data: dict) -> str:
    """
    Extracts the publisher from the JSON data.
    """
    publisher_list = data.get("publisher", [])
    return ", ".join([x["name"] for x in publisher_list])


def extract_meta_score(data: dict) -> int:
    """
    Extracts the meta score from the JSON data.
    """
    aggregate_rating = data.get("aggregateRating")
    if aggregate_rating:
        return int(aggregate_rating["ratingValue"])
    return None


def extract_critic_review_count(soup) -> int:
    """
    Extracts the critic review count from the scraped soup.
    """
    critic_review_count = soup.find("span", {"class": "count"})
    if critic_review_count:
        return int(critic_review_count.find("a").text.split()[0])
    return 0


def extract_user_score(soup) -> float:
    """
    Extracts the user score from the scraped soup.
    """
    user_score_element = soup.find("div", class_="user")
    if user_score_element:
        user_score_text = user_score_element.text
        if user_score_text != "tbd":
            return float(user_score_text)
    return None


def extract_user_rating_count(soup) -> int:
    """
    Extracts the user rating count from the scraped soup.
    """
    user_rating_count_elements = soup.find_all("div", {"class": "summary"})
    if len(user_rating_count_elements) > 1:
        user_rating_count_element = user_rating_count_elements[1].find("a")
        if user_rating_count_element is not None:
            user_rating_count_text = user_rating_count_element.text.strip().split()[0]
            if user_rating_count_text.isdigit():
                return int(user_rating_count_text)
    return 0


def scrape_game_data_list(game_list: list[str]) -> list[dict]:
    """
    Scrapes game data for the given list of game links.
    Returns a list of scraped game data.
    """
    data_list = []
    exception_list = []

    for game in game_list:
        logging.info(f"Processing {game} data.")
        scrape_game_data(game, data_list, exception_list)

    return data_list


def main(console: str) -> None:
    game_list = read_txt(console)
    game_data_list = scrape_game_data_list(game_list)

    df1 = pd.DataFrame.from_dict(game_data_list)
    df1 = add_gamepass_status(df1)
    df1.to_parquet(f"/etc/scraped_data/{console}-games.parquet")


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    data_list = []
    exception_list = []

    scrape_game_data(
        "https://www.metacritic.com/game/xbox/top-gear-rpm-tuning",
        data_list,
        exception_list,
    )
    print(data_list)
    print(exception_list)
