from datetime import datetime, timedelta

import pandas as pd
import pytest
from pandas.api.types import is_datetime64_any_dtype as is_datetime
from pandas.api.types import is_string_dtype as is_string
from scrapers.twitter.sentiment_analysis import *


def test_get_date_range():
    assert get_date_range("2022-02-15") == ("2022-01-01", "2022-01-31")
    assert get_date_range("2021-12-31") == ("2021-11-01", "2021-11-30")
    assert get_date_range("2020-02-29") == ("2020-01-01", "2020-01-31")


# def test_clean_tweet():
#     # Test basic cleaning of a tweet
#     assert clean_tweet("Hello, world!") == "hello world"

#     # Test handling of contractions
#     assert clean_tweet("I'm excited to go to the park!") == "im excited to go to the park"

#     # Test handling of apostrophes in contractions
#     assert clean_tweet("I don't like Mondays.") == "i dont like mondays"

#     # Test removal of mentions and hashtags
#     assert (clean_tweet("This tweet contains a @mention and a #hashtag.")
#             == "this tweet contains a and a")

#     # Test removal of URLs
#     assert (clean_tweet("Check out this link: https://www.example.com.") ==
#             "check out this link")

#     # Test removal of brackets
#     assert clean_tweet("This [text] is in brackets!") == "this text is in brackets"

#     # Test handling of stopwords
#     assert (clean_tweet("This tweet contains stopwords.", stopwords=["contains"])
#             == "this tweet stopwords")

#     # Test handling of an empty string
#     assert clean_tweet("") == ""

#     # Test handling of a float input
#     assert clean_tweet(1.23) == ""

#     # Test handling of a string with only punctuation
#     assert clean_tweet("?!.,;:") == ""

#     # Test handling of a string with only stopwords
#     assert clean_tweet("a with some", stopwords=["a", "with", "some"]) == ""

# def test_get_sentiment_scores():
#     text = 'i am so happy with my xbox'
#     expected_scores = {'Polarity': 0.8,
#                 'Subjectivity': 1.0,
#                 'Sentiment': 'positive',
#                 'Negative Score': 0.0,
#                 'Neutral Score': 0.559,
#                 'Positive Score': 0.441,
#                 'Compound Score': 0.6948}
#     assert get_sentiment_scores(text) == expected_scores


# def test_get_sentiment_labels():
#     # positive label
#     compound = 0.5
#     expected_label = 'positive'
#     assert get_sentiment_label(compound) == expected_label

#     # negative label
#     compound = -0.5
#     expected_label = 'negative'
#     assert get_sentiment_label(compound) == expected_label
#     # neutral label
#     compound = 0.01
#     expected_label = 'neutral'
#     assert get_sentiment_label(compound) == expected_label

# def is_string(column):
#     return all(isinstance(x, str) for x in column)

# def test_scrape_tweets_returns_dataframe():
#     assert isinstance(scrape_tweets(hashtags=['python'], since_date='2022-01-01', until_date='2022-01-02', lang='en', exclude_keywords=[], num_tweets=10), pd.DataFrame)

# def test_scrape_tweets_columns():
#     columns = ['Datetime', 'Tweet Id', 'Original Text', 'Username', 'Likes', 'Views',
#                'Replies', 'Retweets', 'Followers', 'Extra Hashtags']
#     df = scrape_tweets(hashtags=['python'], since_date='2022-01-01', until_date='2022-01-02', lang='en', exclude_keywords=[], num_tweets=10)
#     assert df.columns.tolist() == columns


# def test_scrape_tweets_data_types():
#     import numpy as np
#     df = scrape_tweets(hashtags=['python'], since_date='2022-01-01', until_date='2022-01-02', lang='en', exclude_keywords=[], num_tweets=10)
#     assert is_datetime(df['Datetime'])
#     assert is_string(df['Original Text'])
#     assert is_string(df['Username'])
#     assert isinstance(df['Likes'][0], np.integer)
#     assert isinstance(df['Views'][0], np.integer)
#     assert isinstance(df['Replies'][0], np.integer)
#     assert isinstance(df['Retweets'][0], np.integer)
#     assert isinstance(df['Followers'][0], np.integer)
#     assert isinstance(df['Extra Hashtags'][0], list)

# def test_scrape_tweets_num_tweets():
#     df = scrape_tweets(hashtags=['python'], since_date='2022-01-01', until_date='2022-01-02', lang='en', exclude_keywords=[], num_tweets=10)
#     assert len(df) == 10

# def test_scrape_tweets_datetime():
#     from datetime import datetime

#     from pytz import timezone
#     df = scrape_tweets(hashtags=['python'], since_date='2022-01-01', until_date='2022-01-02', lang='en', exclude_keywords=[], num_tweets=10)
#     assert isinstance(df['Datetime'][0], datetime)
#     assert df['Datetime'][0] >= datetime(2022, 1, 1, tzinfo=timezone('UTC'))

# def test_scrape_tweets_excluded_keywords():
#     df = scrape_tweets(hashtags=['python'], since_date='2022-01-01', until_date='2022-01-02', lang='en', exclude_keywords=['programming'], num_tweets=10)
#     assert (all(keyword not in text for keyword in ['programming']
#                 for text in df['Original Text']))


# def test_main():
#     # Define parameters
#     hashtags = ['python']
#     since_date = '2022-01-01'
#     until_date = '2022-01-02'
#     lang = 'en'
#     exclude_keywords = []
#     num_tweets = 5
#     expected_columns = ['Datetime', 'Tweet Id', 'Original Text', 'Cleaned Text', 'Polarity', 'Subjectivity', 'Sentiment', 'Negative Score', 'Neutral Score', 'Positive Score', 'Compound Score', 'Likes', 'Views', 'Replies', 'Retweets', 'Followers', 'Extra Hashtags']

#     # Run main function and get DataFrame
#     tweets_df = main(hashtags, since_date, until_date, lang, exclude_keywords, num_tweets)

#     # Test if the function returns a pandas DataFrame
#     assert isinstance(tweets_df, pd.DataFrame)
#     # Test if the function returns a DataFrame with the expected columns
#     assert set(tweets_df.columns) == set(expected_columns)

#     # Test if the function returns a DataFrame with the expected number of rows
#     assert len(tweets_df) == num_tweets


#     # Check data types of DataFrame columns
#     assert all(isinstance(tweets_df[column].iloc[0], expected_type) for column, expected_type in
#         zip(expected_columns, [pd.Timestamp, np.int64, str, str, float, float, str, float, float, float, float, np.int64, np.int64, np.int64, np.int64, np.int64, list]))

#     # Check that sentiment scores are between -1 and 1
#     assert all(all(-1 <= score <= 1 for score in tweets_df[column]) for column in ['Polarity', 'Subjectivity', 'Negative Score', 'Neutral Score', 'Positive Score', 'Compound Score'])


# def test_integration_scrape_tweets_returns_non_empty_dataframe():
#     hashtags = ['#xbox']
#     since_date = '2022-01-01'
#     until_date = '2022-01-02'
#     lang = 'en'
#     exclude_keywords = []
#     num_tweets = 10

#     df = main(hashtags, since_date, until_date, lang, exclude_keywords, num_tweets)
#     assert not df.empty

# def test_integration_main_returns_non_empty_dataframe_with_expected_columns():
#     hashtags = ['#xbox']
#     since_date = '2022-01-01'
#     until_date = '2022-01-02'
#     lang = 'en'
#     exclude_keywords = []
#     num_tweets = 10

#     df = main(hashtags, since_date, until_date, lang, exclude_keywords, num_tweets)
#     expected_columns = [
#         'Datetime', 'Tweet Id', 'Original Text', 'Cleaned Text', 'Polarity',
#         'Subjectivity', 'Sentiment', 'Negative Score', 'Neutral Score', 'Positive Score',
#         'Compound Score', 'Username', 'Likes', 'Views', 'Replies', 'Retweets', 'Followers', 'Extra Hashtags'
#     ]
#     assert not df.empty
#     assert list(df.columns) == expected_columns

# def test_integration_main_handles_invalid_inputs():
#     # Invalid hashtag
#     hashtags = ['#nonexistenthashta123321321321dsg']
#     since_date = '2022-01-01'
#     until_date = '2022-01-02'
#     lang = 'en'
#     exclude_keywords = []
#     num_tweets = 10

#     df = main(hashtags, since_date, until_date, lang, exclude_keywords, num_tweets)
#     assert df.empty

#     # Invalid language
#     hashtags = ['#xbox']
#     since_date = '2022-01-01'
#     until_date = '2022-01-02'
#     lang = 'nonexistentlanguage'

#     exclude_keywords = []
#     num_tweets = 10

#     df = main(hashtags, since_date, until_date, lang, exclude_keywords, num_tweets)
#     assert df.empty
