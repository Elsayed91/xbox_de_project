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


# def get_games_per_page(link: str) -> list[str]:
#     """
#     Given a link, returns a list of hrefs of games in that link.

#     Args:
#         link: The URL of the page to scrape.

#     Returns:
#         A list of hrefs of games on the page.
#     """
#     soup = get_soup(link)
#     title_elements = soup.find_all("a", class_="title")
#     href_list = [elem.get("href") for elem in title_elements]
#     return href_list


def get_game_urls(link: str, page_count: int) -> Generator[str, None, None]:
    """
    Given a link and number of pages, returns a generator of urls of games in those links.

    Args:
    link (str): The base URL of the page to scrape.
    pages (int): The number of pages to scrape.

    Returns:
    Generator[str, None, None]: A generator of urls of games on the page.
    """
    for page in range(page_count):
        soup = get_soup(link + f"&page={page}")
        title_elements = soup.find_all("a", class_="title")
        for elem in title_elements:
            yield f"{elem.get('href').rsplit('/', 1)[-1]}"


def log_xcom_value(url_list, key):
    # Convert the list to a dictionary
    url_dict = {key: url_list}

    # Convert the dictionary to JSON
    list_json = json.dumps(url_dict)

    # Log the XCom value using print
    print(f"::kube_api:xcom={list_json}")


if __name__ == "__main__":
    console = os.getenv("console", "xbox")
    url = (
        "https://www.metacritic.com/browse/games/release-date/"
        + f"available/{console}/name?&view=detailed"
    )
    pages = get_last_page(url)
    console_url_list = [u for u in get_game_urls(url, pages)]
    log_xcom_value(console_url_list, key=f"{console}-urls")
