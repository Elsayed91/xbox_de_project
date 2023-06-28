#!/bin/bash
# the script performs the following tasks:
#   1. Copies Parquet files for Twitter, VGChartz, and Metacritic to their respective
#   directories in GCS
#   2. Loads data from Twitter Parquet files into BigQuery
#   3. Loads data from VGChartz and Metacritic Parquet files into their respective BigQuery
#   datasets.

LOCAL_DIR=$LOCAL_DIR
echo "$LOCAL_DIR - $DATA_BUCKET"
echo "uploading files to GCP bucket..."
gsutil -m cp $LOCAL_DIR/tweets-*.parquet gs://${DATA_BUCKET}/twitter/
gsutil -m cp $LOCAL_DIR/vgc_*.parquet gs://${DATA_BUCKET}/vgchartz/
gsutil -m cp $LOCAL_DIR/xbox*.parquet gs://${DATA_BUCKET}/metacritic/


echo "Loading twitter data"
for file in $(find $LOCAL_DIR -type f -name 'tweets-*.parquet'); do
    TWITTER_DATASET=${TWITTER_DATASET}
    # Extract the table name from the filename
    table=$(basename $file .parquet)
    # Check if the table exists in BigQuery
    exists=$(bq query --use_legacy_sql=false \
              --format=json \
              --max_rows=1 \
              "SELECT COUNT(*) as table_exists \
              FROM \`$TWITTER_DATASET.INFORMATION_SCHEMA.TABLES\` \
              WHERE table_name = '$table' \
              AND table_type IN ('TABLE', 'BASE TABLE')" | sed -n 's/.*"table_exists":"\([^"]*\)".*/\1/p')
    echo $exists
    if [ $exists -eq 0 ]; then
        # Create the BigQuery table
        bq load --autodetect --source_format=PARQUET $TWITTER_DATASET.$table $file >/dev/null 2>&1
    else
        echo "Table $table already exists, skipping"
    fi
done


echo "Loading metacritic data"
echo $METACRITIC_DATASET
echo ${DATA_BUCKET}
bq load --replace=true --autodetect --source_format=PARQUET $METACRITIC_DATASET.bq_metacritic_gamedata \
  "gs://${DATA_BUCKET}/metacritic/xbox*-games.parquet"
bq load --replace=true --autodetect --source_format=PARQUET $METACRITIC_DATASET.bq_metacritic_critic_review \
  "gs://${DATA_BUCKET}/metacritic/xbox*-critic-reviews.parquet"
bq load --replace=true --autodetect --source_format=PARQUET $METACRITIC_DATASET.bq_metacritic_user_review \
  "gs://${DATA_BUCKET}/metacritic/xbox*-user-reviews.parquet" 

echo "Loading vgchartz data"
bq load --replace=true --autodetect --source_format=PARQUET $VGCHARTZ_DATASET.bq_vgchartz_hw_sales \
  "gs://${DATA_BUCKET}/vgchartz/vgc_hw_sales.parquet" >/dev/null 2>&1
bq load --replace=true --autodetect --source_format=PARQUET $VGCHARTZ_DATASET.bq_vgchartz_game_sales \
  "gs://${DATA_BUCKET}/vgchartz/vgc_game_sales.parquet" >/dev/null 2>&1

bq query --nouse_legacy_sql \
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
