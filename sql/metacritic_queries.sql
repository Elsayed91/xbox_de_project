CREATE OR REPLACE TABLE `stellarismusv5.metacritic_data.aggregated_developer_data2` AS
WITH DeveloperStats AS (
  SELECT
    developer,
    COUNT(Name) AS total_games,
    AVG(User_Score_Weighted) AS avg_weighted_user_score,
    AVG(Critic_Score_Weighted) AS avg_weighted_critic_score
  FROM
    `stellarismusv5.metacritic_data.calculated_scores_balanced_scaled_weight`
  GROUP BY
    developer
),
RankedDevelopers AS (
  SELECT
    developer,
    total_games AS dev_game_count,
    avg_weighted_user_score,
    avg_weighted_critic_score,
    (0.7 * avg_weighted_user_score) + (0.3 * total_games / (SELECT MAX(total_games) FROM DeveloperStats)) AS developer_user_rank,
    (0.7 * avg_weighted_critic_score) + (0.3 * total_games / (SELECT MAX(total_games) FROM DeveloperStats)) AS developer_critic_rank,
  FROM
    DeveloperStats
)
SELECT
  developer,
  dev_game_count,
  avg_weighted_user_score,
  avg_weighted_critic_score,
  developer_user_rank,
  developer_critic_rank,
FROM
  RankedDevelopers
  Order by developer_user_rank DESC



CREATE OR REPLACE TABLE stellarismusv5.metacritic_data.calculated_scores_balanced_scaled_weight AS
SELECT
  Name,
  Platform,
  Developer,
  Gamepass_Status,
  -- Calculate the User score + User rating count score with balanced scaled review count weight
  (User_Score + LEAST((User_Rating_Count / 97.0), 1.0) * 3.0 * 1.96 * 1.96 / (2 * User_Rating_Count) -
    LEAST((User_Rating_Count / 97.0), 1.0) * 3.0 * 1.96 * SQRT( 
        GREATEST((User_Score * (1 - User_Score)) / GREATEST(User_Rating_Count, 1), 0) 
        + LEAST(((User_Rating_Count / 97.0) * 3.0 * 1.96 * (User_Rating_Count / 97.0) * 3.0 * 1.96) / (4 * GREATEST(User_Rating_Count, 1) * GREATEST(User_Rating_Count, 1)), 0.1)
    )) /
    (1 + LEAST((User_Rating_Count / 97.0), 1.0) * 3.0 * 1.96 * 1.96 / GREATEST(User_Rating_Count, 1)) AS User_Score_Weighted,
  -- Calculate the Critic score + Critic rating count score with balanced scaled review count weight
  (Meta_Score + LEAST((Critic_Reviews_Count / 13.0), 1.0) * 2.0 * 1.96 * 1.96 / (2 * Critic_Reviews_Count) -
    LEAST((Critic_Reviews_Count / 13.0), 1.0) * 2.0 * 1.96 * SQRT( 
        GREATEST((Meta_Score * (1 - Meta_Score)) / GREATEST(Critic_Reviews_Count, 1), 0) 
        + LEAST(((Critic_Reviews_Count / 13.0) * 2.0 * 1.96 * (Critic_Reviews_Count / 13.0) * 2.0 * 1.96) / (4 * GREATEST(Critic_Reviews_Count, 1) * GREATEST(Critic_Reviews_Count, 1)), 0.1)
    )) /
    (1 + LEAST((Critic_Reviews_Count / 13.0), 1.0) * 2.0 * 1.96 * 1.96 / GREATEST(Critic_Reviews_Count, 1)) AS Critic_Score_Weighted
FROM
  stellarismusv5.metacritic_data.bq_metacritic_gamedata
WHERE
  User_Score IS NOT NULL
  AND User_Rating_Count > 0
  AND Meta_Score IS NOT NULL
  AND Critic_Reviews_Count > 0;


CREATE OR REPLACE TABLE `${PROJECT}.${METACRITIC_DATASET}.bq_metacritic_genre_data` AS
WITH GenreData AS (
  SELECT TRIM(genre) AS genre,
    AVG(meta_score) AS average_meta_score,
    AVG(user_score) AS average_user_score,
    COUNT(*) AS game_count
  FROM `${PROJECT}.${METACRITIC_DATASET}.bq_metacritic_gamedata`, UNNEST(SPLIT(genre, ',')) AS genre
  GROUP BY genre
)
SELECT *
FROM GenreData;



CREATE OR REPLACE TABLE `stellarismusv5.metacritic_data.release_console_distribution` AS
SELECT
  EXTRACT(YEAR FROM PARSE_TIMESTAMP('%Y-%m-%d', Release_Date)) AS Year,
  COUNT(*) AS Game_Count,
FROM
  `stellarismusv5.metacritic_data.bq_metacritic_gamedata`
GROUP BY
  Year;


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