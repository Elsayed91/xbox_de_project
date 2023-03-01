
import time
import urllib
from timeit import default_timer as timer
from typing import Optional

import pandas as pd
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



def build_url(genre: str, console_type: str, page_num: int) -> str:
    """Builds a URL for the given genre, console type, and page number.

    Args:
        genre (str): The genre of the games to search for.
        console_type (str): The type of console to search for.
        page_num (int): The page number of the search results to retrieve.

    Returns:
        str: The URL for the search results.
    """
    base_url = 'https://www.vgchartz.com/games/games.php?'
    url_params = {
        'page': page_num,
        'results': 200,
        'genre': genre.replace(' ', '%20'),
        'console': console_type,
        'order': 'Sales',
        'ownership': 'Both',
        'direction': 'DESC',
        'showtotalsales': 1,
        'shownasales': 1,
        'showpalsales': 1,
        'showjapansales': 1,
        'showothersales': 1,
        'showpublisher': 1,
        'showdeveloper': 1,
        'showreleasedate': 1,
        'showlastupdate': 1,
        'showshipped': 1
    }
    url = base_url + urllib.parse.urlencode(url_params)
    return url




def scrape_game_info(soup: BeautifulSoup, genre: str) -> tuple[bool, Optional[pd.DataFrame]]:
    """
    Scrape game information from a BeautifulSoup object and return a pandas DataFrame.

    Args:
        soup: A BeautifulSoup object of the HTML page.
        genre: A string representing the genre of the games.

    Returns:
        A tuple containing a boolean value indicating whether or not the DataFrame is
        empty, and the DataFrame of the scraped game information.
    """
    soup_div = soup.find('div', {'id': 'generalBody'})
    if soup_div is None:
        return False, None

    console_list = []
    all_trs = soup_div.find('table').find_all('tr')
    # tr_count = 0
    # for tr in all_trs:
    #     if tr_count > 2:
    #         console_list.append(tr.find_all("td")[3].find('img').attrs['alt'])
    #     tr_count += 1;
    for tr in all_trs[3:]:
        console_list.append(tr.find_all("td")[3].find('img').attrs['alt'])

    # Scrape the game info into DataFrame
    game_info_df = pd.read_html(str(soup_div))[0]

    if game_info_df.empty:
        return False, None

#    clean up the dataframe
    game_info_df.columns = [
                            'Rank',
                            'Gamex',
                            'Game',
                            'Console',
                            'Publisher',
                            'Developer',
                            'Total Shipped',
                            'Total Sales',
                            'NA Sales',
                            'EU Sales',
                            'Japan Sales',
                            'Other Sales',
                            'Release Date',
                            'Last Update',
                            'Genre']

    game_info_df['Genre'] = genre
    game_info_df['Game'] = game_info_df['Game'].str.replace(' Read the review', '')
    game_info_df['Console'] = console_list

    return True, game_info_df

def scrape_vgchartz(console_list: list[str]) -> pd.DataFrame:
    """
    Scrapes game information from VGChartz for a list of game consoles.

    Args:
        console_list: A list of strings representing the names of the consoles to scrape.

    Returns:
        A pandas DataFrame containing game information scraped from VGChartz.
    """
    # get genre and console list
    genre_list = scrape_genre_list()
    print(genre_list)

    # create empty dataframe to store game info
    game_df = pd.DataFrame()

    # loop through genres and consoles and scrape games for each combination
    for genre in genre_list:
        print(f"processing {genre}.")
        for console_type in console_list:
            page_num = 1
            page_exist = True

            # loop through pages for each genre and console combination
            while page_exist:
                url = build_url(genre, console_type, page_num)
                soup = get_page_html(url)
                page_exist, game_info_df = scrape_game_info(soup, genre)
                if game_info_df is not None:
                    game_df = pd.concat([game_df, game_info_df], ignore_index=True)
                    
                    print(f"Appended Dataframe with page {page_num} of {console_type} games in Genre {genre}")

                # increment page number
                page_num += 1
                time.sleep(1)
    return game_df


def clean_data(df):
    
    # convert sales columns to float format
    for col in df.columns:
        if 'Sales' in col or 'Units' in col:
            df[col] = df[col].str.replace('m', '').astype(float)
            
    df['Console'] = df['Console'].str.replace('Series', 'XS')
#     df['Console'] = df['Console'].str.replace('Xbox XS', 'XS')
    df = df.drop(['Gamex','VGChartz Score', 'Critic Score', 'User Score'], axis=1)
    return df

def main():
    df = scrape_vgchartz(console_list = ['XS', 'XOne', 'X360', 'XB'])
    df = clean_data(df)
    df.to_csv('vgc_game_sales.csv', index=False)

if __name__ == '__main__':
    main()