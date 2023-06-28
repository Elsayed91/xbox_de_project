#!/bin/bash
# the script performs the following tasks:
#   1. Copies Parquet files for VGChartz and Metacritic to their respective directories in GCS
#   2. Loads data from VGChartz and Metacritic Parquet files into their respective BigQuery datasets.


LOCAL_DIR=$LOCAL_DIR
echo "$LOCAL_DIR - $DATA_BUCKET"
echo "uploading files to GCP bucket..."
gsutil -m cp $LOCAL_DIR/vgc_*.parquet gs://${DATA_BUCKET}/vgchartz/
gsutil -m cp $LOCAL_DIR/xbox*.parquet gs://${DATA_BUCKET}/metacritic/



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

