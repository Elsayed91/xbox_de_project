"""
This module provides functionality for scraping user reviews for a game.
"""

import logging
import os
import time
from typing import Optional

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


def scrape_user_reviews(
    game_link: str, max_retries: int = 8
) -> Optional[list[dict[str, str]]]:
    """
    Scrapes user reviews for a game from a given game link.

    Args:
        game_link (str): The URL of the game on the website.
        max_retries (int): The maximum number of retries in case of network errors.
            Defaults to 8.

    Returns:
        Optional[list[dict[str, str]]]: The list of user reviews for the game.
        Returns None if review_pages is None.
    """

    url = game_link + "/user-reviews?page="
    review_pages = get_last_page(url)
    if review_pages is None:
        return None
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
            skip_element = soup.find("div", class_="review_top review_top_l")
            if (
                skip_element is not None
                and "There are no user reviews yet" in skip_element.text
            ):
                logger.info("Skipping game %s due to it having no reviews.", game_link)
                break
            page_reviews = extract_user_reviews(soup)
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


x = scrape_user_reviews(
    "https://www.metacritic.com/game/xbox-360/dark-void-survivor-missions/user-reviews?page=0"
)
print(x)


def extract_review_text(review: BeautifulSoup) -> str:
    """
    Extracts the review text from a review element.

    Args:
        review: A BeautifulSoup object representing a review element.

    Returns:
        str: The extracted review text.
    """
    review_body_expanded = review.find("span", class_="blurb blurb_expanded")
    if review_body_expanded:
        return review_body_expanded.text.strip()

    review_body = review.find("div", class_="review_body")
    if review_body:
        review_text_span = review_body.find("span")
        if review_text_span:
            return review_text_span.text.strip()

    return ""


def extract_user_reviews(soup: BeautifulSoup) -> list[dict[str, str]]:
    """
    Extracts user reviews from the HTML soup.

    Args:
        soup: A BeautifulSoup object.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing the extracted review data.
    """
    reviews = []
    if soup is not None:
        game, platform = extract_game_info(soup)

        for review in soup.find_all("div", class_="review_content"):
            if review.find("div", class_="name") is None:
                break

            user_element = review.find("div", class_="name")
            if user_element is None:
                break

            user_span = user_element.find("span")
            user_a = user_element.find("a")
            user = (
                user_span.text.strip()
                if user_span
                else (user_a.text.strip() if user_a else None)
            )

            reviews.append(
                {
                    "Game": game,
                    "Platform": platform,
                    "User": user,
                    "Date": review.find("div", class_="date").text.strip(),
                    "Score": review.find("div", class_="review_grade").text.strip(),
                    "Review": extract_review_text(review),
                }
            )

        if not reviews:
            return None

    return reviews


# if __name__ == "__main__":
#     console = os.getenv("console")
#     local_path = os.getenv("local_path")
#     game_list = read_txt(console, local_path)
#     user_reviews = []
#     for game_url in game_list:
#         data = scrape_user_reviews(game_url)
#         if data is not None:
#             user_reviews.extend(data)
#     df = pd.DataFrame.from_records(user_reviews)
#     df.reset_index(drop=True, inplace=True)
#     df.to_parquet(f"{local_path}{console}-user-reviews.parquet")
#     xd = pd.read_parquet(f"{local_path}{console}-user-reviews.parquet")
