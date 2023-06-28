CREATE OR REPLACE TABLE \`stellarismusv5.twitter_data.bq_tweets\`
AS
WITH TweetData AS (
  SELECT *
  FROM \`stellarismusv5.twitter_data.tweets-*\`
)
SELECT *
FROM TweetData;