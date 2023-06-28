CREATE OR REPLACE TABLE `stellarismusv5.metacritic_data.top_performing_games` AS
SELECT
  Name,
  Meta_Score,
  Platform
FROM
  `stellarismusv5.metacritic_data.bq_metacritic_gamedata`
ORDER BY
  Meta_Score DESC


