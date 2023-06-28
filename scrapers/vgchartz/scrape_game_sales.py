"""
This module provides functions for scraping video game sales data from VGChartz.com. It
includes functions for getting the page HTML, scraping the genre list, building a URL for
the search results, cleaning the scraped data, and scraping the game information. The main
function, scrape_vgchartz, takes a list of console names and an optional list of genres as
input and returns a pandas DataFrame containing the scraped data.
"""
import os
import time
import urllib
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
    return BeautifulSoup(response.content, "html.parser")


def scrape_genre_list() -> list[str]:
    """
    Scrapes the genre list from vgchartz.com.

    Returns:
        A list of genre names.
    """
    url = "https://www.vgchartz.com/gamedb/"
    soup = get_page_html(url)
    result_select = soup.find("select", {"name": "genre"})
    result_options = result_select.find_all("option")
    genre_list = []
    genre_list = [result["value"] for result in result_options if result["value"]]
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
    base_url = "https://www.vgchartz.com/games/games.php?"
    url_params = {
        "page": page_num,
        "results": 200,
        "genre": genre.replace(" ", "%20"),
        "console": console_type,
        "order": "Sales",
        "ownership": "Both",
        "direction": "DESC",
        "showtotalsales": 1,
        "shownasales": 1,
        "showpalsales": 1,
        "showjapansales": 1,
        "showothersales": 1,
        "showpublisher": 1,
        "showdeveloper": 1,
        "showreleasedate": 1,
        "showlastupdate": 1,
        "showshipped": 1,
    }
    url = base_url + urllib.parse.urlencode(url_params)
    return url


import pandas as pd


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the scraped data by converting sales columns to float format,
    replacing 'Series' in the 'Console' column with 'XS', dropping the 'Gamex' column,
    converting 'Release_Date' and 'Last_Update' columns to date format, and adding a 'Release_Year' column.
    Additionally, update the values in the 'Console' column.

    Args:
        df: A pandas DataFrame containing scraped video game sales data.

    Returns:
        A pandas DataFrame with cleaned data.
    """

    for col in df.columns:
        if "Sales" in col or "Units" in col:
            df[col] = df[col].str.replace("m", "").astype(float)

    df["Console"] = df["Console"].replace(
        {"XS": "Xbox Series X", "XOne": "Xbox One", "X360": "Xbox 360", "XB": "Xbox"}
    )

    df["Release_Date"] = pd.to_datetime(df["Release_Date"], format="%dth %b %y")
    df["Last_Update"] = pd.to_datetime(df["Last_Update"], format="%dth %b %y")
    df["Release_Year"] = df["Release_Date"].dt.year

    df = df.dropna(subset=["Release_Year"])

    df = df.drop(["Gamex"], axis=1)
    return df


def scrape_game_info(
    soup: BeautifulSoup, genre: str
) -> tuple[bool, Optional[pd.DataFrame]]:
    """
    Scrape game information from a BeautifulSoup object and return a pandas DataFrame.

    Args:
        soup: A BeautifulSoup object of the HTML page.
        genre: A string representing the genre of the games.

    Returns:
        A tuple containing a boolean value indicating whether or not the DataFrame is
        empty, and the DataFrame of the scraped game information.
    """
    soup_div = soup.find("div", {"id": "generalBody"})
    if soup_div is None:
        return False, None

    console_list = []
    all_trs = soup_div.find("table").find_all("tr")
    for tr in all_trs[3:]:
        console_list.append(tr.find_all("td")[3].find("img").attrs["alt"])

    # Scrape the game info into DataFrame
    game_info_df = pd.read_html(str(soup_div))[0]

    if game_info_df.empty:
        return False, None

    #    clean up the dataframe
    game_info_df.columns = [
        "Rank",
        "Gamex",
        "Game",
        "Console",
        "Publisher",
        "Developer",
        "Total Shipped",
        "Total Sales",
        "NA Sales",
        "EU Sales",
        "Japan Sales",
        "Other Sales",
        "Release Date",
        "Last Update",
        "Genre",
    ]

    game_info_df["Genre"] = genre
    game_info_df["Game"] = game_info_df["Game"].str.replace(" Read the review", "")
    game_info_df["Console"] = console_list

    return True, game_info_df


def scrape_vgchartz(
    console_list: list[str], genre_list: Optional[list[str]] = None
) -> pd.DataFrame:
    """
    Scrapes game information from VGChartz for a list of game consoles.

    Args:
        console_list: A list of strings representing the names of the consoles to scrape.
        genre_list: Optional list of strings representing the genres to scrape. If None,
        all genres will be scraped.

    Returns:
        A pandas DataFrame containing game information scraped from VGChartz.
    """
    # get genre list if not provided
    if genre_list is None:
        genre_list = scrape_genre_list()

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

                    print(
                        f"Appended Dataframe with page {page_num} of {console_type} games in Genre {genre}"
                    )

                # increment page number
                page_num += 1
                time.sleep(1)
    return game_df


if __name__ == "__main__":
    local_path = os.getenv("local_path")
    df = scrape_vgchartz(console_list=["XS", "XOne", "X360", "XB"])
    df = clean_data(df)
    df.to_parquet(f"{local_path}vgc_game_sales.parquet")
