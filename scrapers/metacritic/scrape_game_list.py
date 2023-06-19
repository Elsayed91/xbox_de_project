"""
The module scrapes a Metacritic to generate a list of urls for games released for a
specific gaming console.
It gets the desired console name from environment variables, constructs a URL for the
console, gets the last page number, generates a list of URLs of games for that console,
and writes the URLs to a file.
"""
import os
import sys
from typing import Generator

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from scrape_utils import *


def game_urls(link: str, headers: dict, pages: int) -> Generator[str, None, None]:
    """
    Given a link and number of pages, returns a generator of urls of games in those links.

    Args:
    link (str): The base URL of the page to scrape.
    pages (int): The number of pages to scrape.

    Returns:
    Generator[str, None, None]: A generator of urls of games on the page.
    """
    for page in range(pages):
        soup = soup_it(link + f"&page={page}", headers)
        title_elements = soup.find_all("a", class_="title")
        for elem in title_elements:
            yield f"https://www.metacritic.com{elem.get('href')}"


if __name__ == "__main__":
    console = os.getenv("console")
    url = (
        "https://www.metacritic.com/browse/games/release-date/"
        + f"available/{console}/name?&view=detailed"
    )
    pages = get_last_page_num(url)
    url_list = [u for u in game_urls(url, pages)]
    with open(f"/etc/scraped_data/{console}-urls.txt", "w") as f:
        for url in url_list:
            f.write(url + "\n")
