#!/bin/bash
# the script performs the following tasks:
#   1. Copies Parquet twitter data files to GCP.
#   2. Loads data from Twitter Parquet files into BigQuery


LOCAL_DIR=$LOCAL_DIR
echo "$LOCAL_DIR - $DATA_BUCKET"
echo "uploading files to GCP bucket..."
gsutil -m cp $LOCAL_DIR/tweets-*.parquet gs://${DATA_BUCKET}/twitter/



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

