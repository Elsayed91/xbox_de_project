CREATE OR REPLACE TABLE `stellarismusv5.metacritic_data.metascore_user_score_comparison` AS
SELECT
  Name,
  Meta_Score,
  User_Score * 10 AS User_Score_Adjusted
FROM
  `stellarismusv5.metacritic_data.bq_metacritic_gamedata`;