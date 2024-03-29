"""
This module provides functions for retrieving and parsing HTML content from the web.
This includes a handler for requests, a BeautifulSoup object creator and a pager counter.
"""

import json
import logging
import os
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def handle_request(
    url: str, max_retries: int = 8, retry_delay: int = 5
) -> Optional[requests.Response]:
    """
    Handles a single HTTP request.
    Uses Exponential backoff when waiting between attempts.

    Args:
        url: The URL to request.
        max_retries: The maximum number of times to retry the request.
        retry_delay: The delay between retries, in seconds.

    Returns:
        The response object, or None if the request failed.
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
                delay *= 2
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
    # handle broken links like "https://www.metacritic.com/game/xbox-360/h0w-2-p1ng-a-trademarkremoved/user-reviews?page="
    if soup == 0:
        return None
    last_page = soup.find("li", class_="page last_page")
    if last_page is not None:
        page_nums = last_page.find_all("a", class_="page_num")
        if page_nums:
            return int(page_nums[-1].text) - 1

    return 0


def read_txt(console: str, base_path: str) -> list[str]:
    """
    Reads the URLs stored in a text file and returns them as a list of strings.

    Args:
        console (str): The name of the console.
        base_path (str): the base path where files are stored.

    Returns:
        list[str]: A list of URLs as strings.
    """
    try:
        with open(f"{base_path}{console}-urls.txt", "r", encoding="utf-8") as f:
            url_list = f.readlines()
    except:
        file_path = os.path.join(base_path, f"{console}-urls.txt")
        with open(file_path, "r", encoding="utf-8") as f:
            url_list = f.readlines()
    url_list = [url.strip() for url in url_list]
    return url_list


def extract_game_info(soup: BeautifulSoup) -> tuple[str, str]:
    """
    Extracts the game name and platform from the HTML soup.

    Args:
        soup: A BeautifulSoup object.

    Returns:
        A tuple of the game name and platform.
    """
    # try:
    #     game = soup.find("div", class_="product_title").find("h1").text.strip()
    #     platform = soup.find("span", class_="platform").text.strip()

    # except AttributeError:
    #     script_tag = soup.find("script", type="application/ld+json")
    #     data = json.loads(script_tag.text)
    #     game = data.get("name")
    #     platform = data.get("gamePlatform")
    # except Exception:
    #     print("An error occurred at extract_game_info. Soup:", soup)
    #     raise
    game = None
    platform = None

    # Try to find the game and platform in the HTML using the first method.
    try:
        game = soup.find("div", class_="product_title").find("h1").text.strip()
        platform = soup.find("span", class_="platform").text.strip()
    except:
        pass

    # If the game and platform were not found in the HTML using the first method, try to find them using the second method.
    if game is None or platform is None:
        if soup is not None:
            script_tag = soup.find("script", type="application/ld+json")
            data = json.loads(script_tag.text)
            game = data.get("name")
            platform = data.get("gamePlatform")

    # Assert that the game and platform are not None.
    assert game is not None, "Game cannot be None"
    assert platform is not None, "Platform cannot be None"

    return game, platform
