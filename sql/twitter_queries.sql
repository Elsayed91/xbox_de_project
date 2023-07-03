{# 1 Table for all tweets #}
CREATE OR REPLACE TABLE `stellarismusv5.twitter_data.bq_tweets`
AS
WITH TweetData AS (
  SELECT *
  FROM `stellarismusv5.twitter_data.tweets-*`
)
SELECT *
FROM TweetData;

{# Hash tag analysis #}
CREATE OR REPLACE TABLE `stellarismusv5.twitter_data.top_hashtags` AS
SELECT
  h.item as hashtag, count(*) as frequency
FROM `stellarismusv5.twitter_data.bq_tweets`, UNNEST(Extra_Hashtags.list) as h
group by hashtag
ORDER BY frequency DESC


{# Metrics #}
CREATE OR REPLACE TABLE `stellarismusv5.twitter_data.user_analysis` AS
SELECT
  Username,
  DATE(Datetime) AS Date,
  COUNT(*) AS Tweet_Count,
  SUM(Likes) AS Total_Likes,
  SUM(Views) AS Total_Views,
  SUM(Replies) AS Total_Replies,
  SUM(Retweets) AS Total_Retweets,
  AVG(Followers) AS Total_Followers,
FROM `stellarismusv5.twitter_data.bq_tweets`
GROUP BY Username, DATE(Datetime)






CREATE OR REPLACE TABLE `stellarismusv5.twitter_data.top_hashtags` AS
SELECT
  h.item as hashtag, count(*) as frequency
FROM `stellarismusv5.twitter_data.bq_tweets`, UNNEST(Extra_Hashtags.list) as h
group by hashtag
ORDER BY frequency DESC

CREATE OR REPLACE TABLE `stellarismusv5.twitter_data.user_analysis` AS
SELECT
  User_Id,
  COUNT(*) AS tweet_count,
  SUM(Likes) AS total_likes,
  SUM(Retweets) AS total_retweets,
  SUM(Followers) AS total_followers
FROM `stellarismusv5.twitter_data.user_analysis`
GROUP BY User_Id;
