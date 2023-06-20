"""

"""
import json
import logging
import os

# from scrape_game_data import scrape_game_data
# from scrape_user_reviews import scrape_user_reviews
from scrape_utils import get_game_urls, get_last_page

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def log_xcom_value(url_list, key):
    # Convert the list to a dictionary
    url_dict = {key: url_list}

    # Convert the dictionary to JSON
    list_json = json.dumps(url_dict)

    # Log the XCom value using print
    print("::kube_api:xcom={}".format(list_json))


if __name__ == "__main__":
    console = os.getenv("console", "xbox")
    url = (
        "https://www.metacritic.com/browse/games/release-date/"
        + f"available/{console}/name?&view=detailed"
    )
    pages = get_last_page(url)
    url_list = [u for u in get_game_urls(url, pages)]
    log_xcom_value(url_list, key=f"{console}-urls")
