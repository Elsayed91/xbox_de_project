"""
This module provides functionality for scraping Metacritic reviews for a game.
"""
import logging
import os
import time
from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup

try:
    from scrape_utils import extract_game_info, get_last_page, get_soup, read_txt
except:
    from scrapers.metacritic.scrape_utils import (
        extract_game_info,
        get_last_page,
        get_soup,
        read_txt,
    )

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def scrape_metacritic_reviews(game_link: str, max_retries: int = 8) -> list[str]:
    """
    Scrapes metacritic reviews for a game from Metacritic.

    Given the URL of a game on Metacritic and the maximum number of retries,
    this function retrieves and returns the critic reviews for the game.

    Args:
        game_link (str): The URL of the game on Metacritic.
        max_retries (int): The maximum number of retries in case of network errors.
        Defaults to 8.

    Returns:
        list[str]: The list of critic reviews for the game.
    """
    url = game_link + "/critic-reviews?page="
    review_pages = get_last_page(url)
    if review_pages is None:
        return []
    reviews = []
    for page in range(review_pages + 1):
        game_url = url + str(page)
        logger.info("processing %s", game_url)
        retries = 0
        while retries < max_retries:
            soup = get_soup(game_url)
            if soup == 0:
                # Skip the link if soup is 0
                break
            if soup is None:
                logger.warning("No script tag found for %s. Retrying...", game_link)
                time.sleep(retries * 3)
                retries += 1
                continue
            # Check if the skip element is found
            skip_element = soup.find("div", class_="review_top review_top_l")
            if (
                skip_element is not None
                and "There are no critic reviews yet." in skip_element.text
            ):
                logger.info("Skipping game %s due to it having no reviews.", game_link)
                break

            page_reviews = extract_metacritic_reviews(soup)
            if page_reviews is None:
                logger.warning("No reviews found for %s. Retrying...", game_url)
                time.sleep(retries * 3)
                retries += 1
                continue
            reviews.extend(page_reviews)
            if retries > 0:
                logger.info("Succeeded after %s retries for %s.", retries, game_link)
            break
    return reviews


def extract_metacritic_reviews(soup: BeautifulSoup) -> list[dict[str, str]]:
    """
    Extracts the Metacritic reviews from the HTML soup.

    Args:
        soup: A BeautifulSoup object.

    Returns:
        A list of dictionaries containing the review data.
    """
    reviews = []

    if soup is not None:
        game, platform = extract_game_info(soup)

        for review in soup.find_all("div", class_="review_content"):
            if review.find("div", class_="source") is None:
                break
            review_source_element = review.find("div", class_="source").find("a")
            review_source = (
                review_source_element["href"] if review_source_element else None
            )
            date_element = review.find("div", class_="date")
            date = None
            if date_element:
                date_string = date_element.text.strip()
                try:
                    date = datetime.strptime(date_string, "%b %d, %Y").strftime(
                        "%Y-%m-%d"
                    )
                except ValueError:
                    pass

            reviews.append(
                {
                    "Game": game,
                    "Platform": platform,
                    "Critic": review.find("div", class_="source").text.strip(),
                    "Review Source": review_source,
                    "Score": review.find("div", class_="metascore_w").text.strip(),
                    "Review": review.find("div", class_="review_body").text.strip(),
                    "Date": date,
                }
            )

        if not reviews:
            return None

    return reviews


if __name__ == "__main__":
    console = os.getenv("console")
    local_path = os.getenv("local_path")

    game_list = read_txt(console, local_path)
    metacritic_reviews = []
    for game_url in game_list:
        data = scrape_metacritic_reviews(game_url)
        if data is not None:
            metacritic_reviews.extend(data)
    df = pd.DataFrame.from_records(metacritic_reviews)
    df.reset_index(drop=True, inplace=True)
    df.to_parquet(f"{local_path}{console}-critic-reviews.parquet")
