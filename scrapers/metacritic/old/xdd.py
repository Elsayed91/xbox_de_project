import json
import random
import time
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup


class MetacriticScraper:
    BASE_URL = "https://www.metacritic.com"

    def __init__(self, game_links):
        self.game_links = game_links
        self.game_data = []

    def delay_request(self):
        time.sleep(random.uniform(1, 3))

    def retry_request(self, url):
        self.delay_request()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            return self.retry_request(url)

    def scrape_game_data(self, link):
        url = self.BASE_URL + link
        response = self.retry_request(url)
        soup = BeautifulSoup(response, "html.parser")
        script_tag = soup.find("script", type="application/ld+json")
        if script_tag is not None:
            data = json.loads(script_tag.text)
            game_data = self.extract_game_data(data, soup)
            self.game_data.append(game_data)
            print(f"Scraped game data for {link}")

    def extract_game_data(self, data, soup):
        game_data = {}

        game_data["Name"] = data.get("name")
        game_data["Release Date"] = self.extract_release_date(data)
        game_data["Maturity Rating"] = self.extract_maturity_rating(data)
        game_data["Genre"] = self.extract_genre(data)
        game_data["Platform"] = data.get("gamePlatform")
        game_data["Developer"] = self.extract_developer(soup)
        game_data["Publisher"] = self.extract_publisher(data)
        game_data["Meta Score"] = self.extract_meta_score(data)
        game_data["Critic Reviews Count"] = self.extract_critic_review_count(soup)
        game_data["User Score"] = self.extract_user_score(soup)
        game_data["User Rating Count"] = self.extract_user_rating_count(soup)
        game_data["Summary"] = data.get("description")
        game_data["Image"] = data["image"]

        return game_data

    def extract_release_date(self, data):
        release_date_str = data.get("datePublished")
        if release_date_str:
            release_date = datetime.strptime(release_date_str, "%B %d, %Y")
            return release_date.strftime("%Y-%m-%d")
        return ""

    def extract_maturity_rating(self, data):
        return data.get("contentRating", "Unspecified").replace("ESRB ", "")

    def extract_genre(self, data):
        genre_list = data.get("genre", [])
        return ", ".join(genre_list)

    def extract_developer(self, soup):
        developer = soup.select_one(".developer a")
        if developer:
            return developer.text
        return ""

    def extract_publisher(self, data):
        publisher_list = data.get("publisher", [])
        return ", ".join([x["name"] for x in publisher_list])

    def extract_meta_score(self, data):
        aggregate_rating = data.get("aggregateRating")
        if aggregate_rating:
            return int(aggregate_rating["ratingValue"])
        return None

    def extract_critic_review_count(self, soup):
        critic_review_count = soup.find("span", {"class": "count"})
        if critic_review_count:
            return int(critic_review_count.find("a").text.split()[0])
        return 0

    def extract_user_score(self, soup):
        user_score_element = soup.find("div", class_="user")
        if user_score_element:
            user_score_text = user_score_element.text
            if user_score_text != "tbd":
                return float(user_score_text)
        return None

    def extract_user_rating_count(self, soup):
        user_rating_count_elements = soup.find_all("div", {"class": "summary"})
        if len(user_rating_count_elements) > 1:
            user_rating_count_element = user_rating_count_elements[1].find("a")
            if user_rating_count_element is not None:
                user_rating_count_text = user_rating_count_element.text.strip().split()[
                    0
                ]
                if user_rating_count_text.isdigit():
                    return int(user_rating_count_text)
        return 0

    def scrape_games(self):
        for link in self.game_links:
            self.scrape_game_data(link)

        return pd.DataFrame(self.game_data)


if __name__ == "__main__":
    game_links = [
        "/game/xbox-360/banjo-kazooie",
        "/game/xbox-360/babel-rising---skys-the-limit",
        "/game/xbox-series-x/elden-ring",
    ]

    scraper = MetacriticScraper(game_links)
    game_data_df = scraper.scrape_games()
    print(game_data_df)
