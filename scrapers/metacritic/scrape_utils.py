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
    ua = UserAgent(fallback='chrome')
    headers = {
            'User-Agent': ua.random
        }
    response = requests.get(url, headers=headers)
    return BeautifulSoup(response.text, "html.parser")

def get_last_page_num(page_link: str) -> int:
    """
    Parses the specified web page to determine the number of pages of results.

    Args:
        page_link: The URL of the web page to parse.

    Returns:
        The number of pages of results.
    """
    soup = soup_it(page_link)
    last_page = soup.find_all('li', {'class': 'page last_page'})
    if last_page:
        page_nums = last_page[0].find_all('a', {'class': 'page_num'})
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
    title_elements = soup.find_all('a', class_='title')
    href_list = [elem.get('href') for elem in title_elements]
    return href_list