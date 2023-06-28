CREATE OR REPLACE TABLE `stellarismusv5.metacritic_data.top_performing_games` AS
WITH GameData AS (
  SELECT
    Name,
    Meta_Score,
    User_Score,
    (User_Score * 10 - AVG(User_Score) OVER ()) / STDDEV(User_Score) OVER () AS User_Score_Standardized
  FROM
    `stellarismusv5.metacritic_data.bq_metacritic_gamedata`
),
WeightedGameData AS (
  SELECT
    Name,
    Meta_Score,
    User_Score,
    User_Score_Standardized,
    (0.6 * Meta_Score + 0.4 * User_Score_Standardized) AS Weighted_Performance
  FROM
    GameData
)
SELECT
  Name,
  Meta_Score,
  User_Score,
  User_Score_Standardized,
  Weighted_Performance
FROM
  WeightedGameData
ORDER BY
  Weighted_Performance DESC;
