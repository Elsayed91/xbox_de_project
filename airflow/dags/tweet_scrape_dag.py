"""
This DAG utilizes the KubernetesJobOperator to execute scripts as Kubernetes jobs. The
primary purpose of these jobs is to perform scraping tasks.

The DAG follows the sequence: 
    twitter_task >> backfill_first >> gcp_task

Task 'twitter_task': This task involves scraping tweets from Twitter for the previous
month and performing sentiment analysis on them.

Task 'backfill_first': This task ensures that the Twitter data is backfilled before
scraping other sites that do not require backfilling.

Task 'gcp_task': This final task saves the scraped data to a Google Cloud Storage (GCS)
bucket and subsequently loads it into a BigQuery table.

The DAG is scheduled to run on a cron schedule, specifically on the first day of each
month.
"""
# pylint: disable=pointless-statement
# pylint: disable=wrong-import-order

import os
import sys
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.latest_only import LatestOnlyOperator
from airflow_kubernetes_job_operator.kubernetes_job_operator import (
    KubernetesJobOperator,
)

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

default_args = {
    "owner": "airflow",
    "start_date": datetime(2022, 12, 1),
    "depends_on_past": False,
    "retries": 3,
    "retry_delay": timedelta(seconds=60),
    "concurrency": 3,
    # "max_active_runs": 1,
    "in_cluster": True,
    "random_name_postfix_length": 3,
    "name_prefix": "",
    "max_active_tasks_per_dag": 4,
}


today = datetime.today().strftime("%Y-%m-%d")
POD_TEMPALTE = os.path.join(os.path.dirname(__file__), "templates", "pod_template.yaml")
BASE = "/git/repo/scrapers"
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
COMMON_VOLUME_CONFIG = {
    "name": "persistent-volume",
    "type": "persistentVolumeClaim",
    "reference": "data-pv-claim",
    "mountPath": "/etc/scraped_data/",
}
LOCAL_PATH = "/etc/scraped_data/"

with DAG(
    dag_id="twitter_scraper",
    schedule_interval="0 0 1 * *",
    default_args=default_args,
    catchup=True,
    tags=["scraping", "twitter"],
) as dag:
    twitter_task = KubernetesJobOperator(
        task_id="scrape-tweets",
        body_filepath=POD_TEMPALTE,
        command=["python", f"{BASE}/twitter/sentiment_analysis.py"],
        jinja_job_args={
            "image": f"eu.gcr.io/{GOOGLE_CLOUD_PROJECT}/scraper:latest",
            "name": "scrape-tweets",
            "gitsync": True,
            "volumes": [COMMON_VOLUME_CONFIG],
        },
        envs={"start_date": "{{ ds }}", "local_path": LOCAL_PATH, "num_tweets": 10000},
    )

    backfill_first = LatestOnlyOperator(task_id="ensure_backfill_complete")

    gcp_task = KubernetesJobOperator(
        task_id="load_to_gcp",
        body_filepath=POD_TEMPALTE,
        command=["/bin/bash", "/git/repo/airflow/dags/scripts/twitter_gcp_script.sh"],
        jinja_job_args={
            "image": "google/cloud-sdk:alpine",
            "name": "ingest-and-load-to-bq",
            "gitsync": True,
            "volumes": [COMMON_VOLUME_CONFIG],
        },
        envs={
            "LOCAL_DIR": LOCAL_PATH,
            "TWITTER_DATASET": os.getenv("TWITTER_DATASET"),
            "DATA_BUCKET": os.getenv("DATA_BUCKET"),
            "PROJECT": GOOGLE_CLOUD_PROJECT,
        },
    )
    twitter_task >> backfill_first >> gcp_task
