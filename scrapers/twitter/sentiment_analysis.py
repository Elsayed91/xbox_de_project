"""
A module that contains several functions for extracting sentiment from Twitter data. The
functions are as follows:
get_date_range(since_date_str: str) -> tuple[str, str]: Is used to get the exact date
range for each month, since months have different number of days.


clean_tweet(tweet: str, stopwords: list[str] = []) -> str: This function takes a tweet as
input and returns a cleaned version of it. The tweet is cleaned by removing URLs,
@mentions, hashtags, punctuation, profanity, and non-alphanumeric characters. Optionally,
the function can remove a list of stopwords.

get_sentiment_scores(text: str) -> dict[str, float]: This function calculates the
sentiment scores of the input text using TextBlob and VADER. The function returns a
dictionary containing the following keys: polarity, subjectivity, sentiment (positive,
negative, or neutral), negative score, neutral score, positive score, and compound score.

get_sentiment_label(compound: float) -> str: This function takes a compound sentiment
score as input and returns the sentiment label (positive, negative, or neutral) of the
text.

scrape_tweets(hashtags: list[str], since_date: str, lang: str, exclude_keywords:
list[str], num_tweets: int) -> list[dict]: This function scrapes tweets using snscrape and
returns a pandas DataFrame containing the following information about each tweet:
datetime, tweet ID, original text, username, likes, views, replies, retweets, followers,
and extra hashtags. The function searches for tweets that contain a list of hashtags, are
in the specified language, and do not contain any of the specified keywords. The function
returns a maximum of num_tweets tweets.

main(hashtags: list[str], since_date: str, lang: str, exclude_keywords: list[str],
num_tweets: int) -> None: This function is the main function that runs when the module is
executed. The function calls the scrape_tweets function to scrape tweets and then calls
the get_sentiment_scores function to calculate the sentiment scores of the tweets. The
function prints out the sentiment scores of each tweet.
"""
import logging
import os
import re

import numpy as np
import pandas as pd
import snscrape.modules.twitter as sntwitter
from better_profanity import profanity
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


def get_date_range(since_date_str: str) -> tuple[str, str]:
    """
    Returns a tuple of the first and last date of the previous month from the given date
    string.

    Args:
        since_date_str (str): A string in the format '%Y-%m-%d' representing the starting
        date.

    Returns:
        Tuple[str, str]: A tuple of two strings representing the start and end date of the
        previous month in the format '%Y-%m-%d'.

    Example:
        >>> get_date_range('2022-02-15')
        ('2022-01-01', '2022-01-31')
    """
    import calendar
    import datetime

    # Convert since date string to datetime.date object
    since_date = datetime.datetime.strptime(since_date_str, "%Y-%m-%d").date()

    # Calculate the first day of the previous month
    start_date = datetime.date(
        since_date.year, since_date.month, 1
    ) - datetime.timedelta(days=1)
    start_date = datetime.date(start_date.year, start_date.month, 1)

    # Calculate the last day of the previous month
    last_day_of_month = calendar.monthrange(start_date.year, start_date.month)[1]
    end_date = datetime.date(start_date.year, start_date.month, last_day_of_month)

    # Convert the dates to string format and return them
    # '2022-01-01'
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")


def clean_tweet(tweet: str, stopwords: list[str] = []) -> str:
    """
    Cleans a tweet by removing URLs, @mentions, hashtags, punctuation, profanity, and
    non-alphanumeric characters, and splitting it into words. Optionally remove a list of
    stopwords.

    Args:
        tweet (str): The tweet to be cleaned.
        stopwords (list[str], optional): A list of words to be removed. Defaults to [].

    Returns:
        str: The cleaned tweet.
    """
    import string

    if isinstance(tweet, float):
        return ""

    # Remove URLs, @mentions, and hashtags
    tweet = re.sub(r"(https?://\S+|www\.\S+)", "", tweet)
    tweet = re.sub(r"@\S+", "", tweet)
    tweet = re.sub(r"#[\w-]+", "", tweet)

    # Remove punctuation and brackets
    tweet = tweet.translate(str.maketrans("", "", string.punctuation))
    tweet = re.sub(r"\[.*?\]", "", tweet)

    # Remove profanity and contractions
    tweet = profanity.censor(tweet.lower())
    tweet = re.sub(r"'\w+", "", tweet)

    # Remove non-alphanumeric characters and split into words
    words = re.findall(r"\b\w+\b", tweet)
    words = [w for w in words if w not in stopwords]

    # Join words back into a string
    cleaned_tweet = " ".join(words)

    return cleaned_tweet


def get_sentiment_scores(text: str) -> dict[str, float]:
    """
    Calculate the sentiment scores using TextBlob and VADER.
    Args:
        text (str): The text for which sentiment scores are to be calculated.
    Returns:
        A dictionary containing the following keys:
        Polarity (float): The polarity score of the text.
        Subjectivity (float): The subjectivity score of the text.
        Sentiment (str): The sentiment label of the text, i.e., positive, negative, or
        neutral.
        Negative Score (float): The negative sentiment score of the text.
        Neutral Score (float): The neutral sentiment score of the text.
        Positive Score (float): The positive sentiment score of the text.
        Compound Score (float): The compound sentiment score of the text.
    """
    blob = TextBlob(text)
    polarity, subjectivity = blob.sentiment

    sia = SentimentIntensityAnalyzer()
    scores = sia.polarity_scores(text)
    return {
        "Polarity": polarity,
        "Subjectivity": subjectivity,
        "Sentiment": get_sentiment_label(scores["compound"]),
        "Negative Score": scores["neg"],
        "Neutral Score": scores["neu"],
        "Positive Score": scores["pos"],
        "Compound Score": scores["compound"],
    }


def get_sentiment_label(compound: float) -> str:
    """
    Get sentiment label (positive, negative, or neutral) from compound score value.
    Args:
        compound (float): The compound sentiment score of the text.
    Returns:
        A string representing the sentiment label of the text, i.e., positive, negative,
        or neutral.
    """
    if compound > 0.1:
        return "positive"
    elif compound < -0.1:
        return "negative"
    else:
        return "neutral"


def scrape_tweets(
    hashtags: list[str],
    since_date: str,
    until_date: str,
    lang: str,
    exclude_keywords: list[str],
    num_tweets: int,
    hashtag_operator: str = "OR",
) -> list[dict]:
    """
    Use snscrape to scrape tweets and extract relevant data.>
    Args:
        hashtags (list[str]): A list of hashtags to search for.
        since_date (str): A string representing the date from which to start searching for
        tweets (YYYY-MM-DD format).
        lang (str): The language of the tweets to search for.
        exclude_keywords (list[str]): A list of keywords to exclude from the search results.
        num_tweets (int): The number of tweets to scrape.
        hastag_oerator(str):  OR or AND in the query. defaults to OR.
    Returns:
        A pandas DataFrame
    """
    query = (
        f" {hashtag_operator} ".join(hashtags)
        + f" lang:{lang} since:{since_date}"
        + f" until:{until_date}"
        + "".join([f" -{kw}" for kw in exclude_keywords])
    )
    tweets_list = []
    logger.info(f"processing tweets from {since_date} until {until_date}.")
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
        if i >= num_tweets:
            break
        tweet_dict = {
            "Datetime": tweet.date,
            "Tweet Id": tweet.id,
            "Original Text": tweet.rawContent,
            "Username": tweet.user.username,
            "Likes": tweet.likeCount,
            "Views": int(tweet.viewCount) if tweet.viewCount is not None else 0,
            "Replies": tweet.replyCount,
            "Retweets": tweet.retweetCount,
            "Followers": tweet.user.followersCount,
            "Extra Hashtags": [
                tag.lower()
                for tag in re.findall(r"#(\w+)", tweet.rawContent)
                if tag.lower() not in [h.lower().replace("#", "") for h in hashtags]
            ],
        }
        tweets_list.append(tweet_dict)

    return pd.DataFrame(tweets_list)


def main(
    hashtags: list[str],
    since_date: str,
    until_date: str,
    lang: str,
    exclude_keywords: list[str],
    num_tweets: int,
) -> pd.DataFrame:
    """
    main function that utilizes scrape_tweets, clean_tweets and get_sentiment_scores
    to get a dataframe of tweets with desired data.
    """
    tweets_df = scrape_tweets(
        hashtags, since_date, until_date, lang, exclude_keywords, num_tweets
    )

    # Clean text and add column to DataFrame
    if not tweets_df.empty:
        tweets_df["Cleaned Text"] = tweets_df["Original Text"].apply(clean_tweet)

        # Get sentiment scores and add columns to DataFrame
        sentiment_scores = tweets_df["Cleaned Text"].apply(get_sentiment_scores)
        tweets_df = pd.concat([tweets_df, sentiment_scores.apply(pd.Series)], axis=1)

        # Add additional columns
        tweets_df = tweets_df[
            [
                "Datetime",
                "Tweet Id",
                "Original Text",
                "Cleaned Text",
                "Polarity",
                "Subjectivity",
                "Sentiment",
                "Negative Score",
                "Neutral Score",
                "Positive Score",
                "Compound Score",
                "Likes",
                "Views",
                "Replies",
                "Retweets",
                "Followers",
                "Extra Hashtags",
            ]
        ]

    return tweets_df


if __name__ == "__main__":
    hashtags = [
        "#xbox",
        "#xboxseriesx",
        "#xboxseriess",
        "#xboxone",
        "#xboxgames",
        "#xboxgamepass",
        "#xboxlive",
        "#xboxcommunity",
        "#xboxlivegold",
        "#xboxgamepassultimate",
        "#gamepassultimate",
    ]
    start_date = os.getenv("start_date")
    start_date_str, end_date_str = get_date_range(start_date)
    lang = os.getenv("lang", "en")
    exclude_keywords = [
        "sale",
        "discount",
        "buy",
        "shop",
        "promote",
        "click",
        "shopify",
    ]
    num_tweets = os.getenv("num_tweets", 1000)
    df = main(
        hashtags, start_date_str, end_date_str, lang, exclude_keywords, num_tweets
    )
    data_vol = os.getenv("data_volume", "/etc/scraped_data")
    df.to_parquet(f"{data_vol}/tweets-{start_date_str}.parquet")
    logger.info(f"saved data to file tweets-{start_date_str}.parquet")
