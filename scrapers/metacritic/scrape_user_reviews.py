"""
This module provides functionality for scraping user reviews for a game.
"""

import json
import logging
import os
import time

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


def scrape_user_reviews(game_link: str, max_retries: int = 8) -> None:
    url = game_link + "/user-reviews?page="
    review_pages = get_last_page(url)
    if review_pages is None:
        return None
    reviews = []
    for page in range(review_pages + 1):
        game_url = url + str(page)
        print(game_url)
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
            page_reviews = extract_user_reviews(soup)
            reviews.extend(page_reviews)
            if retries > 0:
                logger.info("Succeeded after %s retries for %s.", retries, game_link)
            break
    return reviews


def extract_review_text(review):
    review_body_expanded = review.find("span", class_="blurb blurb_expanded")
    if review_body_expanded:
        return review_body_expanded.text.strip()

    review_body = review.find("div", class_="review_body")
    if review_body:
        review_text_span = review_body.find("span")
        if review_text_span:
            return review_text_span.text.strip()

    return ""


def extract_user_reviews(soup) -> list[dict]:
    reviews = []
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

        print(user)
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

    return reviews


if __name__ == "__main__":
    console = os.getenv("console")
    local_path = os.getenv("local_path")
    game_list = read_txt(console, local_path)
    user_reviews = []
    for game_url in game_list[:10]:
        data = scrape_user_reviews(game_url)
        if data is not None:
            user_reviews.extend(data)

    df = pd.DataFrame.from_records(user_reviews)
    df.to_parquet(f"{local_path}{console}-user-reviews.parquet")

