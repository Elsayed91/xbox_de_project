"""
xdd
"""

import ast
import logging
import sys
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

    return None


def read_txt(console: str, base_path: str) -> list[str]:
    """
    Reads the URLs stored in a text file and returns them as a list of strings.

    Args:
        console (str): The name of the console.
        base_path (str): the base path where files are stored.

    Returns:
        list[str]: A list of URLs as strings.
    """
    with open(f"{base_path}{console}-urls.txt", "r") as f:
        url_list = f.readlines()

    # remove any newline characters from the end of each URL
    url_list = [url.strip() for url in url_list]
    return url_list
