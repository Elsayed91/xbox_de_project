
import argparse
import datetime
import json
import os
import random as rand
import re
import time
from datetime import datetime

import pandas as pd
import requests
from fuzzywuzzy import fuzz, process

try: 
    from scrape_utils import *
except:
    from scrapers.metacritic.scrape_utils import *


def fuzzy_match(name: str, names: list, threshold: int = 60) -> str:
    """
    Finds the best fuzzy match for the given name in a list of names and returns the
    matched name if its score is above the given threshold, otherwise returns None.

    Args:
        name (str): The name to search for.
        names (list): A list of names to search in.
        threshold (int): Optional. The minimum score required for a match.

    Returns:
        str: The best matched name if its score is above the threshold, otherwise None.
    """
    try:
        matched = process.extractOne(name, names, scorer=fuzz.token_sort_ratio)
        if matched[1] >= threshold:
            return matched[0]
        else:
            return None
    except TypeError as e:
        raise TypeError(f"Failed to perform fuzzy matching: {e}")



def add_gamepass_status(main_df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a 'Gamepass_Status' column to the input DataFrame indicating whether each game is
    available on Game Pass.

    Args:
        main_df: The input DataFrame containing a 'Name' column.

    Returns:
        A copy of the input DataFrame with an additional 'Gamepass_Status' column.
    """
    url = 'https://docs.google.com/spreadsheet/ccc?key=1kspw-4paT-eE5-mrCrc4R9tg70lH2ZTFrJOUmOtOytg&output=csv'
    df = pd.read_csv(url, skiprows=[0])
    df = df[['Game', 'Status']]
    game_names = df['Game'].tolist()
    statuses = df['Status'].tolist()
    main_df['Gamepass_Status'] = main_df['Name'].apply(lambda x: fuzzy_match(x, game_names)).fillna('Not Included')
    main_df['Gamepass_Status'] = main_df['Gamepass_Status'].fillna('Not Included')
    main_df['Gamepass_Status'] = main_df['Gamepass_Status'].apply(lambda x: statuses[game_names.index(x)] if x in game_names else 'Not Included')
    return main_df



def scrape_game_data(link: str, data_list: list[dict], exception_list: list[str]) -> None:
    """
    Given a link, appends scraped data to a list of dictionaries representing game data
    and appends any exceptions to a list.

    Args:
        link (str): The URL of the game to scrape.
        data_list (List[Dict]): A list of dictionaries representing game data.
        exception_list (List[str]): A list of strings representing exceptions.

    Returns:
        None
    """
    try:
        soup = soup_it(link)
        game_sublink = link.replace("https://www.metacritic.com", "")
        data = json.loads(soup.select_one('script[type="application/ld+json"]').text)
        try:
            user_score = soup.find('div', class_="user").text
            user_score = float(user_score) if user_score != 'tbd' else None
        except:
            user_score = None
        print(user_score)
        
        try:
            critic_review_count = int(soup.find('span', {'class': 'count'}).find('a').text.split()[0])
        except:
            critic_review_count = 0
            
        print(critic_review_count)
        try:
            user_rating_count = int(soup.find_all('div', {'class': 'summary'})[1].find('a').text.strip().split()[0])
        except:
            user_rating_count = 0
        print(user_rating_count)
        
        print(f"dev is {soup.select_one('.developer a').text}")
        game_data = {
            'Name': data.get('name'),
            'Release Date': datetime.strptime(data.get('datePublished'), "%B %d, %Y").strftime("%Y-%m-%d"),
            'Maturity Rating': data.get('contentRating', "Unspecified").replace("ESRB ", ""),
            'Genre': ", ".join(data.get('genre', [])),
            'Developer': soup.select_one('.developer a').text,
            'Publisher': ", ".join([x['name'] for x in data['publisher']]),
            'Meta Score': int(data['aggregateRating']['ratingValue']) if 'aggregateRating' in data else None,
            'Critic Reviews Count': critic_review_count,
            'User Score': user_score,
            'User Rating Count' : user_rating_count,
            'Summary': data.get('description'),
            'Image': data['image']
        }
        data_list.append(game_data)
    except BaseException as e:
        print(f"On game link {link}, Error : {e}")
        exception_list.append(f"On game link {link}, Error : {e}")
            
            

def main(console: str) -> None:
    """
    Given a URL, scrapes game data from all pages and writes the data to a CSV file.

    Args:
        url (str): The URL of the first page to scrape.
        console (str): The console name to include in the CSV filename.

    Returns:
        None
    """
    data_list = []
    exception_list = []
    game_list = read_txt(console)
    import time 
    for game in game_list:
        time.sleep(1)
        print(f"processing {game} data.")
        scrape_game_data(game, data_list, exception_list)
        
    
    df1 = (pd.DataFrame.from_dict(data_list))
    df1 = add_gamepass_status(df1)
    df1.to_parquet(f'/etc/scraped_data/{console}-games.parquet')





if __name__ == "__main__":
    
    main(os.getenv("console"))
