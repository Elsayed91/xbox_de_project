CREATE OR REPLACE TABLE `stellarismusv5.metacritic_data.yearly_performance` AS
WITH YearlyPerformance AS (
  SELECT
    EXTRACT(YEAR FROM PARSE_DATE('%Y-%m-%d', Release_Date)) AS Year,
    AVG(Meta_Score) AS Average_Meta_Score,
    AVG(User_Score) AS Average_User_Score
  FROM
    `stellarismusv5.metacritic_data.bq_metacritic_gamedata`
  WHERE
    Release_Date IS NOT NULL
  GROUP BY
    Year
)
SELECT *
FROM
  YearlyPerformance;