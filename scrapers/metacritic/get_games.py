import os
import sys
from typing import Generator

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from scrape_utils import *


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
        title_elements = soup.find_all('a', class_='title')
        for elem in title_elements:
            yield f"https://www.metacritic.com{elem.get('href')}"

if __name__=='__main__':
    pages = get_last_page_num(url)
    url_list = [u for u in game_urls(url, pages)]
    import json
    game_list_json = json.dumps(url_list)
    print(f"::kube_api:xcom={{\"game_list\":{game_list_json}}}")