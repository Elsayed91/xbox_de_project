CREATE OR REPLACE TABLE `stellarismusv5.metacritic_data.release_console_distribution` AS
SELECT
  EXTRACT(YEAR FROM PARSE_TIMESTAMP('%Y-%m-%d', Release_Date)) AS Year,
  COUNT(*) AS Game_Count,
FROM
  `stellarismusv5.metacritic_data.bq_metacritic_gamedata`
GROUP BY
  Year;
