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


bq query --nouse_legacy_sql \
"CREATE OR REPLACE TABLE \`stellarismusv5.twitter_data.top_hashtags\` AS
SELECT
  h.item as hashtag, count(*) as frequency
FROM `stellarismusv5.twitter_data.bq_tweets`, UNNEST(Extra_Hashtags.list) as h
group by hashtag
ORDER BY frequency DESC;
;

CREATE OR REPLACE TABLE \`stellarismusv5.twitter_data.user_analysis\` AS
SELECT
  Username,
  COUNT(*) AS tweet_count,
  SUM(Likes) AS total_likes,
  SUM(Retweets) AS total_retweets,
  SUM(Followers) AS total_followers
FROM \`stellarismusv5.twitter_data.bq_tweets\`
GROUP BY Username;
"