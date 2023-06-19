"""
This module provides utility functions for web scraping Metacritic's data. The functions
in this module include:

soup_it(url: str, headers: dict = None) -> BeautifulSoup: Sends an HTTP GET request to the
given URL and returns the parsed HTML content as a BeautifulSoup object.
get_last_page_num(page_link: str) -> int: Parses the specified web page to determine the
number of pages of results.
get_games_per_page(link: str) -> list[str]: Given a link, returns a list of hrefs of games
in that link.
read_txt(console: str, base_path: str = '/etc/scraped_data') -> list[str]: Reads the URLs
stored in a text file and returns them as a list of strings. The console argument
specifies the name of the console, and the base_path argument specifies the base path
where the files are stored.
"""
import time

import requests
from bs4 import BeautifulSoup


def soup_it(url: str, headers: dict = None) -> BeautifulSoup:
    """
    Sends an HTTP GET request to the given URL and returns the parsed HTML content as a
    BeautifulSoup object.

    Args:
        url (str): The URL to request.
        headers (dict): Optional. A dictionary of HTTP headers to include in the request.

    Returns:
        BeautifulSoup: A BeautifulSoup object representing the parsed HTML content.
    """
    from fake_useragent import UserAgent

    ua = UserAgent(fallback="chrome")
    headers = {"User-Agent": ua.random}
    attempt = 0

    while attempt < 8:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            time.sleep(1)  # Sleep for 1 second after a successful response
            return BeautifulSoup(response.text, "html.parser")
        except Exception as e:
            print(f"Request failed ({e}). Retrying in 5 seconds...")
            time.sleep(5)  # Sleep for 5 seconds after a failed response
            attempt += 1
            backoff = 2**attempt
            time.sleep(backoff)  # Exponential backoff with increasing delay

    print(f"All attempts failed to retrieve data from {url}.")
    return None


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


def read_txt(console: str, base_path: str = "/etc/scraped_data") -> list[str]:
    """
    Reads the URLs stored in a text file and returns them as a list of strings.

    Args:
        console (str): The name of the console.
        base_path (str): the base path where files are stored.

    Returns:
        list[str]: A list of URLs as strings.
    """
    with open(f"{base_path}/{console}-urls.txt", "r") as f:
        url_list = f.readlines()

    # remove any newline characters from the end of each URL
    url_list = [url.strip() for url in url_list]
    return url_list
