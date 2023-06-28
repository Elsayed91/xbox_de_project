CREATE OR REPLACE TABLE `stellarismusv5.metacritic_data.aggregated_developer_data` AS
WITH DeveloperData AS (
  SELECT
    Developer,
    COUNT(*) AS Total_Games,
    AVG(Meta_Score) AS Average_Meta_Score,
    SUM(Critic_Reviews_Count) AS Total_Critic_Reviews,
    AVG(User_Score) AS Average_User_Score,
    SUM(User_Rating_Count) AS Total_User_Ratings,
    SUM((Critic_Reviews_Count * 0.7 * Meta_Score + User_Rating_Count * 0.3 * User_Score) / (Critic_Reviews_Count + User_Rating_Count)) AS Weighted_Performance
  FROM
    `stellarismusv5.metacritic_data.bq_metacritic_gamedata`
  GROUP BY
    Developer
)
SELECT *
FROM
  DeveloperData;