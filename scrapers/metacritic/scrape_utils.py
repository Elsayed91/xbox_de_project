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
from fake_useragent import UserAgent


def generate_random_header(url: str) -> dict:
    """
    Generates a random User-Agent header and tests it on the provided URL.
    If the header successfully works, it is returned; otherwise, None is returned.

    Args:
        url (str): The URL to test the generated header against.

    Returns:
        dict or None: A dictionary containing the User-Agent header if it works, or None if it doesn't.
    """
    ua = UserAgent(fallback="chrome")
    headers = {"User-Agent": ua.random}

    session = requests.Session()
    session.headers.update(headers)

    try:
        response = session.get(f"https://{url}")
        response.raise_for_status()  # Raise an exception for non-2xx status codes
        return headers
    except requests.exceptions.RequestException:
        return None


def soup_it(url: str, headers: dict) -> BeautifulSoup:
    """
    Sends an HTTP GET request to the given URL with the provided headers and returns the
    parsed HTML content as a BeautifulSoup object.

    Args:
        url (str): The URL to request.
        headers (dict): Optional. A dictionary of HTTP headers to include in the request.

    Returns:
        BeautifulSoup: A BeautifulSoup object representing the parsed HTML content.
    """
    session = requests.Session()

    session.headers.update(headers)

    max_retries = 5  # Maximum number of retries
    delay = 10  # Initial delay in seconds

    for retry in range(max_retries):
        try:
            response = session.get(url)
            response.raise_for_status()  # Raise an exception for non-2xx status codes
            return BeautifulSoup(response.text, "html.parser")
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                print(
                    f"Received HTTP 429 error while processing URL {url}. Retrying in {delay} seconds..."
                )
                time.sleep(delay)
                delay += 10  # Increment delay for exponential backoff
            else:
                raise e  # Reraise the exception if it's not a rate limit issue
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            break

    print(f"Failed to retrieve data after {max_retries} attempts.")
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
    if last_page:
        page_nums = last_page[0].find_all("a", {"class": "page_num"})
        if len(page_nums) >= 2:
            last_page_num = int(page_nums[1].text)
        elif len(page_nums) == 1:
            last_page_num = int(page_nums[0].text)
        else:
            last_page_num = 1
        return last_page_num - 1
    else:
        return 1


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
