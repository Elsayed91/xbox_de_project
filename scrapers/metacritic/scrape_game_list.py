"""
The module scrapes a Metacritic to generate a list of urls for games released for a
specific gaming console.
It gets the desired console name from environment variables, constructs a URL for the
console, gets the last page number, generates a list of URLs of games for that console,
and writes the URLs to a file.
"""
import json
import os
import sys
from typing import Generator

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from scrape_utils import *


def get_last_page_num(page_link: str) -> int:
    """
    Parses the specified web page to determine the number of pages of results.

    Args:
        page_link: The URL of the web page to parse.

    Returns:
        The number of pages of results.
    """
    soup = soup_it(page_link)

    last_page = soup.find_all("li", {"class": "page last_page"})
    if last_page is not None and len(last_page) > 0:
        page_nums = last_page[0].find_all("a", {"class": "page_num"})
        if page_nums is not None and len(page_nums) > 0:
            if len(page_nums) >= 2:
                last_page_num = int(page_nums[1].text)
            elif len(page_nums) == 1:
                last_page_num = int(page_nums[0].text)
            else:
                last_page_num = 1
            return last_page_num - 1

    return 0


def get_games_per_page(link: str) -> list[str]:
    """
    Given a link, returns a list of hrefs of games in that link.

    Args:
    link (str): The URL of the page to scrape.

    Returns:
    List[str]: A list of hrefs of games on the page.
    """
    soup = soup_it(link)
    title_elements = soup.find_all("a", class_="title")
    href_list = [elem.get("href") for elem in title_elements]
    return href_list


def game_urls(link: str, pages: int) -> Generator[str, None, None]:
    """
    Given a link and number of pages, returns a generator of urls of games in those links.

    Args:
    link (str): The base URL of the page to scrape.
    pages (int): The number of pages to scrape.

    Returns:
    Generator[str, None, None]: A generator of urls of games on the page.
    """
    for page in range(pages):
        soup = soup_it(link + f"&page={page}")
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
    url_dict = {"urls": url_list}
    list_json = json.dumps(url_dict)

    # Log the XCom value using print
    print("::kube_api:xcom={}".format(list_json))
    # with open(f"/etc/scraped_data/{console}-urls.txt", "w") as f:
    #     for url in url_list:
    #         f.write(url + "\n")
