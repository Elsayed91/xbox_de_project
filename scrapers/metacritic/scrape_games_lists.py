"""

"""
import json
import logging
import os
from typing import Generator

# from scrape_game_data import scrape_game_data
# from scrape_user_reviews import scrape_user_reviews
from scrape_utils import get_last_page, get_soup

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_game_urls(link: str, pages: int) -> Generator[str, None, None]:
    """
    Given a link and number of pages, returns a generator of urls of games in those links.

    Args:
    link (str): The base URL of the page to scrape.
    pages (int): The number of pages to scrape.

    Returns:
    Generator[str, None, None]: A generator of urls of games on the page.
    """
    for page in range(pages + 1):
        soup = get_soup(link + f"&page={page}")
        title_elements = soup.find_all("a", class_="title")
        for elem in title_elements:
            yield elem.get("href").rsplit("/", 1)[-1]


def log_xcom_value(urls, key):
    # Convert the list to a dictionary
    url_dict = {key: urls}

    # Convert the dictionary to JSON
    list_json = json.dumps(url_dict)

    # Log the XCom value using print
    print(f"::kube_api:xcom={list_json}")


if __name__ == "__main__":
    console = os.getenv("console")
    local_path = os.getenv("local_path")
    url = (
        "https://www.metacritic.com/browse/games/release-date/"
        + f"available/{console}/name?&view=detailed"
    )
    pages_count = get_last_page(url)
    url_list = [u for u in get_game_urls(url, pages_count)]
    with open(f"{local_path}{console}-urls.txt", "w") as f:
        for url in url_list:
            f.write(url + "\n")
