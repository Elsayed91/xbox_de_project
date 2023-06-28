CREATE OR REPLACE TABLE `stellarismusv5.metacritic_data.platform_performance` AS
WITH PlatformData AS (
  SELECT
    Platform,
    COUNT(*) AS Total_Games,
    AVG(Meta_Score) AS Average_Meta_Score,
    AVG(User_Score) AS Average_User_Score
  FROM
    `stellarismusv5.metacritic_data.bq_metacritic_gamedata`
  GROUP BY
    Platform
)
SELECT *
FROM
  PlatformData;