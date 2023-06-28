"""
This DAG utilizes the KubernetesJobOperator to execute scripts as Kubernetes jobs. The
primary purpose of these jobs is to perform scraping tasks.

The DAG follows the sequence: 
    twitter_task >> backfill_first >> metacritic_tg >> vgchartz_tg >> gcp_task

Task 'twitter_task': This task involves scraping tweets from Twitter for the previous
month and performing sentiment analysis on them.

Task 'backfill_first': This task ensures that the Twitter data is backfilled before
scraping other sites that do not require backfilling.

Task group 'metacritic_tg': This task group consists of multiple tasks that scrape data
from Metacritic. It scrapes the data for each game as well as the user and critic reviews.

Task group 'vgchartz_tg': This task group consists of 2 tasks that scrape data
from Vgchartz. 

Task 'gcp_task': This final task saves the scraped data to a Google Cloud Storage (GCS)
bucket and subsequently loads it into a BigQuery table.

The DAG is scheduled to run on a cron schedule, specifically on the first day of each
month. The Twitter data is appended during each run, while the other data is replaced with
the latest version.
"""
# pylint: disable=pointless-statement
# pylint: disable=wrong-import-order

import os
import sys
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.latest_only import LatestOnlyOperator
from airflow.utils.task_group import TaskGroup
from airflow_kubernetes_job_operator.kubernetes_job_operator import (
    KubernetesJobOperator,
)

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

default_args = {
    "owner": "airflow",
    "start_date": datetime(2022, 12, 1),
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(seconds=60),
    "concurrency": 4,
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
    dag_id="scrapers",
    schedule_interval="0 1 1 * *",
    default_args=default_args,
    tags=["scraping", "vgchartz", "metacritic"],
) as dag:
    with TaskGroup(group_id="process-metacritic-data") as metacritic_tg:
        consoles = ["xbox360", "xbox-series-x", "xboxone", "xbox"]
        for console in consoles:
            t1 = KubernetesJobOperator(
                task_id=f"scrape-{console}-game-list",
                body_filepath=POD_TEMPALTE,
                command=["python", f"{BASE}/metacritic/scrape_games_lists.py"],
                jinja_job_args={
                    "image": f"eu.gcr.io/{GOOGLE_CLOUD_PROJECT}/scraper:latest",
                    "name": f"get-games-list-{console}",
                    "gitsync": True,
                    "volumes": [COMMON_VOLUME_CONFIG],
                },
                envs={"console": console, "local_path": LOCAL_PATH},
            )

            with TaskGroup(group_id=f"process-{console}-data") as tg1:
                t2 = KubernetesJobOperator(
                    task_id=f"scrape-{console}-game-data",
                    body_filepath=POD_TEMPALTE,
                    command=["python", f"{BASE}/metacritic/scrape_games_data.py"],
                    jinja_job_args={
                        "image": f"eu.gcr.io/{GOOGLE_CLOUD_PROJECT}/scraper:latest",
                        "name": f"get-{console}-game-data",
                        "gitsync": True,
                        "volumes": [COMMON_VOLUME_CONFIG],
                    },
                    envs={"console": console, "local_path": LOCAL_PATH},
                )

                t3 = KubernetesJobOperator(
                    task_id=f"scrape-{console}-user-reviews",
                    body_filepath=POD_TEMPALTE,
                    command=["python", f"{BASE}/metacritic/scrape_user_reviews.py"],
                    jinja_job_args={
                        "image": f"eu.gcr.io/{GOOGLE_CLOUD_PROJECT}/scraper:latest",
                        "name": f"get-{console}-user-reviews",
                        "gitsync": True,
                        "volumes": [COMMON_VOLUME_CONFIG],
                    },
                    envs={"console": console, "local_path": LOCAL_PATH},
                )
                t4 = KubernetesJobOperator(
                    task_id=f"scrape-{console}-critic-reviews",
                    body_filepath=POD_TEMPALTE,
                    command=[
                        "python",
                        f"{BASE}/metacritic/scrape_metacritic_reviews.py",
                    ],
                    jinja_job_args={
                        "image": f"eu.gcr.io/{GOOGLE_CLOUD_PROJECT}/scraper:latest",
                        "name": f"get-{console}-critic-reviews",
                        "gitsync": True,
                        "volumes": [COMMON_VOLUME_CONFIG],
                    },
                    envs={"console": console, "local_path": LOCAL_PATH},
                )
            t1 >> tg1
    with TaskGroup(group_id="process-vgchartz-data") as vgchartz_tg:
        v1 = KubernetesJobOperator(
            task_id="scrape-vgchartz-hw-sales",
            body_filepath=POD_TEMPALTE,
            command=["python", f"{BASE}/vgchartz/scrape_hardware_sales.py"],
            jinja_job_args={
                "image": f"eu.gcr.io/{GOOGLE_CLOUD_PROJECT}/scraper:latest",
                "name": "scrape-vg-hw-sales",
                "gitsync": True,
                "volumes": [COMMON_VOLUME_CONFIG],
            },
            envs={"local_path": LOCAL_PATH},
        )

        v2 = KubernetesJobOperator(
            task_id="scrape-vgchartz-game-sales",
            body_filepath=POD_TEMPALTE,
            command=["python", f"{BASE}/vgchartz/scrape_game_sales.py"],
            jinja_job_args={
                "image": f"eu.gcr.io/{GOOGLE_CLOUD_PROJECT}/scraper:latest",
                "name": "scrape-vg-game-sales",
                "gitsync": True,
                "volumes": [COMMON_VOLUME_CONFIG],
            },
            envs={"local_path": LOCAL_PATH},
        )
    gcp_task = KubernetesJobOperator(
        task_id="load_to_gcp",
        body_filepath=POD_TEMPALTE,
        command=["/bin/bash", "/git/repo/airflow/dags/scripts/gcp_script.sh"],
        jinja_job_args={
            "image": "google/cloud-sdk:alpine",
            "name": "ingest-and-load-to-bq",
            "gitsync": True,
            "volumes": [COMMON_VOLUME_CONFIG],
        },
        envs={
            "LOCAL_DIR": LOCAL_PATH,
            "VGCHARTZ_DATASET": os.getenv("VGCHARTZ_DATASET"),
            "METACRITIC_DATASET": os.getenv("METACRITIC_DATASET"),
            "DATA_BUCKET": os.getenv("DATA_BUCKET"),
            "PROJECT": GOOGLE_CLOUD_PROJECT,
        },
    )
    [metacritic_tg, vgchartz_tg] >> gcp_task
