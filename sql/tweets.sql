CREATE OR REPLACE TABLE `stellarismusv5.twitter_data.top_hashtags` AS
SELECT hashtag, COUNT(*) AS frequency
FROM `stellarismusv5.twitter_data.tweets`, UNNEST(Extra_Hashtags.list) AS hashtag
GROUP BY hashtag
ORDER BY frequency DESC;


CREATE OR REPLACE TABLE `stellarismusv5.twitter_data.top_hashtags` AS
SELECT hashtag, COUNT(*) AS frequency
FROM `stellarismusv5.twitter_data.tweets`, UNNEST(Extra_Hashtags.list) AS hashtag
GROUP BY hashtag
ORDER BY frequency DESC;