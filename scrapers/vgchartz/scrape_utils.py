import requests
from bs4 import BeautifulSoup


def get_page_html(url: str) -> BeautifulSoup:
    """
    Sends an HTTP request to the given URL, and returns the response content as a
    BeautifulSoup object.

    Args:
        url (str): The URL to scrape.

    Returns:
        BeautifulSoup: A BeautifulSoup object representing the parsed HTML content of the
        page.
    """
    response = requests.get(url)
    return  BeautifulSoup(response.content, 'html.parser')


def scrape_genre_list() -> list[str]:
    """
    Scrapes the genre list from vgchartz.com.

    Returns:
        A list of genre names.
    """
    url = 'https://www.vgchartz.com/gamedb/'
    soup = get_page_html(url)
    result_select = soup.find('select', {'name': 'genre'})
    result_options = result_select.find_all('option')
    genre_list = []
    genre_list = [result['value'] for result in result_options if result['value']]
    
    return genre_list