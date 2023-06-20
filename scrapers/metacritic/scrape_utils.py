"""
xdd
"""

import logging
import time
from typing import Generator

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def handle_request(url, max_retries: int = 8, retry_delay: int = 5):
    """
    xdd
    """
    delay = retry_delay
    for _ in range(max_retries):
        try:
            user_agent = UserAgent(fallback="chrome")
            headers = {"User-Agent": user_agent.random}
            response = requests.get(url, headers=headers, timeout=retry_delay)
            if response.status_code == 429:
                # Too many requests, sleep and retry
                logger.warning("Too many requests. Retrying after %s seconds...", delay)
                time.sleep(delay)
                delay *= 2  # Exponential backoff
                continue
            if response.status_code == 404:
                # Broken link, skip and return None
                logger.warning("Broken link. Skipping: %s", url)
                return None
            return response

        except requests.exceptions.RequestException as err:
            logger.error("Request failed: %s", err)
            # Retry on network errors
            time.sleep(delay)
            delay *= 2  # Exponential backoff
            continue

    logger.error("Max retries exceeded. Failed to fetch: %s", url)
    return None


def get_soup(url: str) -> BeautifulSoup:
    """
    Retrieves the BeautifulSoup object by making a request to the specified URL.

    Args:
        url (str): The URL of the web page to retrieve and parse.

    Returns:
        BeautifulSoup: The BeautifulSoup object representing the parsed HTML content.
    """
    response = handle_request(url)
    if response is None:
        logger.warning("Got a None Response for %s.", url)
        return 0

    return BeautifulSoup(response.content, "html.parser")


def get_last_page(page_link: str) -> int:
    """
    Parses the specified web page to determine the number of pages of results.

    Args:
        page_link: The URL of the web page to parse.

    Returns:
        The number of pages of results.
    """

    soup = get_soup(page_link)
    last_page = soup.find("li", class_="page last_page")
    if last_page is not None:
        page_nums = last_page.find_all("a", class_="page_num")
        if page_nums:
            return int(page_nums[-1].text) - 1

    return 0


def get_games_per_page(link: str) -> list[str]:
    """
    Given a link, returns a list of hrefs of games in that link.

    Args:
        link: The URL of the page to scrape.

    Returns:
        A list of hrefs of games on the page.
    """
    soup = get_soup(link)
    title_elements = soup.find_all("a", class_="title")
    href_list = [elem.get("href") for elem in title_elements]
    return href_list


def get_game_urls(link: str, pages: int) -> Generator[str, None, None]:
    """
    Given a link and number of pages, returns a generator of urls of games in those links.

    Args:
    link (str): The base URL of the page to scrape.
    pages (int): The number of pages to scrape.

    Returns:
    Generator[str, None, None]: A generator of urls of games on the page.
    """
    for page in range(pages):
        soup = get_soup(link + f"&page={page}")
        title_elements = soup.find_all("a", class_="title")
        for elem in title_elements:
            yield f"{elem.get('href')}"
