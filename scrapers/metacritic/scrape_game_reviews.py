import os
import random as rand
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup

try: 
    from scrape_utils import *
except:
    from scrapers.metacritic.scrape_utils import *

def scrape_metacritic_reviews(game_link: str, critic_review_list: list, exception_list: list) -> None:
    """
    Scrapes critic reviews for a game from Metacritic and appends them to the
    critic_review_list.
    
    Args:
        game_link (str): The Metacritic URL for the game.
        critic_review_list (list): The list to which the critic reviews will be appended.
        exception_list (list): The list to which exceptions will be appended if they
        occur.
    
    Returns:
        None
    """
    try: 
        url =  game_link + "/critic-reviews?page="
        pages = get_last_page_num(url)
        for page in range(pages):
            print(page)
            game_url = url + str(page)

            soup = soup_it(game_url)
            print(f"processing critic review for {game_url}")
            game = soup.find('div', class_='product_title').find('h1').text.strip()
            platform = soup.find('span', class_='platform').text.strip()
            for review in soup.find_all('div', class_='review_content'):
                if review.find('div', class_='source') == None:
                            break 
                        
                critic_review_list.append({
                    'Game': game,
                    'Platform': platform,
                    'Critic': review.find('div', class_='source').find('a').text,
                    'Review Source': review.find('div', class_='source').find('a')['href'],
                    'Date': review.find('div', class_='date').text,
                    'Score': review.find('div', class_='review_grade').find_all('div')[0].text,
                    'Review': review.find('div', class_='review_body').text.strip()
                })
    except BaseException as e:
        exception_list.append(f"On game link {game_url}, Error : {e}")

def scrape_user_reviews(game_link: str, review_list: list, exception_list: list) -> None:
    """
    Scrapes user reviews for a game from Metacritic and appends them to the review_list.
    
    Args:
        game_link (str): The Metacritic URL for the game.
        review_list (list): The list to which the user reviews will be appended.
        exception_list (list): The list to which exceptions will be appended if they occur.
    
    Returns:
        None
    """
    try:
        url =  game_link + "/user-reviews?page="
        pages = get_last_page_num(url)
        for page in range(pages):
            game_url = url + str(page)

            soup = soup_it(game_url)
            print(f"processing user review for {game_url}")
            game = soup.find('div', class_='product_title').find('h1').text.strip()
            platform = soup.find('span', class_='platform').text.strip()
            for review in soup.find_all('div', class_='review_content'):
                if review.find('div', class_='name') == None:
                            break 
                review_list.append({
                    'Game': game,
                    'Platform': platform,
                    'User': review.find('div', class_='name').find('a').text,
                    'Date': review.find('div', class_='date').text,
                    'Score': review.find('div', class_='review_grade').find_all('div')[0].text,
                    'Review': review.find('span', class_='blurb blurb_expanded').text if review.find('span', class_='blurb blurb_expanded') else review.find('div', class_='review_body').find('span').text
                })
    except BaseException as e:
            exception_list.append(f"On game link {game_url}, Error : {e}")
            
def main(console: str, review_type: str) -> None:
    """
    Main function that scrapes either user reviews or critic reviews for the games in game_list.
    
    Args:
        game_list (list): The list of Metacritic URLs for the games.
        console (str): The console name for which the data is being scraped.
        review_type (str): The type of review to scrape: "user" or "critic".
    
    Returns:
        None
    """
    if review_type.lower() == "user":
        scrape_reviews = scrape_user_reviews
        file_name = f"{console}-user-reviews.csv"
    elif review_type.lower() == "critic":
        scrape_reviews = scrape_metacritic_reviews
        file_name = f"{console}-critic-reviews.csv"
    else:
        print("Invalid review type. Please enter either 'user' or 'critic'.")
        return

    data_list = []
    exception_list = []
    game_list = read_txt(console)
    for game in game_list:
        print(f"processing {review_type} reviews for {game}")
        scrape_reviews(game, data_list, exception_list)
    
    df = pd.DataFrame.from_dict(data_list)
    df.to_parquet(f'/etc/scraped_data/{file_name}.parquet')

if __name__ == '__main__':
    main(os.getenv("console"), os.getenv("review_type"))
    