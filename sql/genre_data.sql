"CREATE OR REPLACE TABLE \`${PROJECT}.${METACRITIC_DATASET}.bq_metacritic_genre_data\` AS
WITH GenreData AS (
  SELECT TRIM(genre) AS genre,
    AVG(meta_score) AS average_meta_score,
    AVG(user_score) AS average_user_score,
    COUNT(*) AS game_count
  FROM \`${PROJECT}.${METACRITIC_DATASET}.bq_metacritic_gamedata\`, UNNEST(SPLIT(genre, ',')) AS genre
  GROUP BY genre
)
SELECT *
FROM GenreData;"
