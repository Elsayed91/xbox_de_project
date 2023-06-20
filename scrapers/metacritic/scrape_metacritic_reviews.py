import json
import logging
import os
import time

import pandas as pd

try:
    from scrape_utils import *
except:
    from scrapers.metacritic.scrape_utils import *

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def scrape_metacritic_reviews(game_link: str, max_retries: int = 8) -> None:
    url = game_link + "/critic-reviews?page="
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
            page_reviews = extract_metacritic_reviews(soup)
            reviews.extend(page_reviews)
            if retries > 0:
                logger.info("Succeeded after %s retries for %s.", retries, game_link)
            break
    return reviews


def extract_game_info(soup):
    try:
        game = soup.find("div", class_="product_title").find("h1").text.strip()
        platform = soup.find("span", class_="platform").text.strip()
    except AttributeError:
        script_tag = soup.find("script", type="application/ld+json")
        data = json.loads(script_tag.text)
        game = data.get("name")
        platform = data.get("gamePlatform")
    return game, platform


def extract_metacritic_reviews(soup) -> list[dict]:
    reviews = []
    game, platform = extract_game_info(soup)

    for review in soup.find_all("div", class_="review_content"):
        if review.find("div", class_="source") == None:
            break
        review_source_element = review.find("div", class_="source").find("a")
        review_source = review_source_element["href"] if review_source_element else None

        reviews.append(
            {
                "Game": game,
                "Platform": platform,
                "Critic": review.find("div", class_="review_critic").text.strip(),
                "Review Source": review_source,
                "Score": review.find("div", class_="metascore_w").text.strip(),
                "Review": review.find("div", class_="review_body").text.strip(),
            }
        )

    return reviews


def scrape_user_reviews(game_link: str) -> None:
    url = game_link + "/user-reviews?page="
    review_pages = get_last_page(url)

    for page in range(review_pages + 1):
        game_url = url + str(page)
        soup = get_soup(game_url)
        reviews = extract_user_reviews(soup)
        return reviews


def extract_user_reviews(soup) -> list[dict]:
    reviews = []
    game = soup.find("div", class_="product_title").find("h1").text.strip()
    platform = soup.find("span", class_="platform").text.strip()

    for review in soup.find_all("div", class_="review_content"):
        if review.find("div", class_="name") is None:
            break

        user_element = review.find("div", class_="name")
        if user_element is None:
            break

        user_span = user_element.find("span")
        user = user_span.text.strip() if user_span else None

        reviews.append(
            {
                "Game": game,
                "Platform": platform,
                "User": user,
                "Date": review.find("div", class_="date").text.strip(),
                "Score": review.find("div", class_="review_grade").text.strip(),
                "Review": review.find(
                    "span", class_="blurb blurb_expanded"
                ).text.strip()
                if review.find("span", class_="blurb blurb_expanded")
                else review.find("div", class_="review_body").find("span").text.strip(),
            }
        )

    return reviews


if __name__ == "__main__":
    console = os.getenv("console")
    local_path = os.getenv("local_path")

    game_list = retrieve_xcom_game_list(console)
    metacritic_reviews = []
    for game_url in game_list:
        data = scrape_metacritic_reviews(game_url)
        if data is not None:
            metacritic_reviews.extend(data)
    df = pd.DataFrame.from_records(metacritic_reviews)

    df.to_parquet(f"{local_path}{console}-critic-reviews.parquet")
