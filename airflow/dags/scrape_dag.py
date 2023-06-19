"""
The tasks in the DAG use the KubernetesJobOperator to run scripts as Kubernetes jobs.
The jobs carry out mainly scraping functions. 

the DAG sequence is t >> backfill_first >> [v1,v2,tg] >> x1

t: the twitter scraping task. scrapes tweets from twitter for the previous month, and
performs sentiment analysis as well.

backfill_first: ensures that twitter data is backfilled before scraping other sites
that do not require backfilling.

[v1,v2,tg]: this is a task group that scrapes the other sites (Vgchartz & Metacritic),
the v1 and v2 are vgchartz tasks, the tg is metacritic game data, user reviews, critic
review task group, all of these run concurrently, reducing the run time substantially.

x1: saves the scraped data to a GCS bucket and then loads it to a bigquery table.

The DAG runs on a cron schedule on the first day of each month. 
Twitter data will be appended, other data will be replaced by latest version.
"""
import os
import sys
from datetime import datetime, timedelta

from airflow.operators.latest_only import LatestOnlyOperator
from airflow.utils.task_group import TaskGroup
from airflow_kubernetes_job_operator.kube_api import KubeResourceKind
from airflow_kubernetes_job_operator.kubernetes_job_operator import (
    KubernetesJobOperator,
)

from airflow import DAG

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

default_args = {
    "owner": "airflow",
    "start_date": datetime(2022, 12, 1),
    "depends_on_past": True,
    "retries": 0,
    "retry_delay": timedelta(minutes=60),
    "concurrency": 0,
    "max_active_runs": 1,
    "in_cluster": True,
    "random_name_postfix_length": 3,
    "name_prefix": "",
}


today = datetime.today().strftime("%Y-%m-%d")
POD_TEMPALTE = os.path.join(os.path.dirname(__file__), "templates", "pod_template.yaml")
BASE = "/git/repo/scrapers"
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
MOUNT_VOLUME_PATH = os.getenv("MOUNT_VOLUME_PATH", "/pvc")

with DAG(
    dag_id="scrapers",
    schedule_interval="0 0 1 * *",
    default_args=default_args,
    catchup=True,
    tags=["scraping", "vgchartz", "twitter", "metacritic"],
) as dag:
    t = KubernetesJobOperator(
        task_id=f"scrape-tweets",
        body_filepath=POD_TEMPALTE,
        command=["python", f"{BASE}/twitter/sentiment_analysis.py"],
        jinja_job_args={
            "image": f"eu.gcr.io/{GOOGLE_CLOUD_PROJECT}/scraper:latest",
            "name": f"scrape-tweets",
            "gitsync": True,
            "volumes": [
                {
                    "name": "persistent-volume",
                    "type": "persistentVolumeClaim",
                    "reference": "data-pv-claim",
                    "mountPath": "/etc/scraped_data/",
                }
            ],
        },
        envs={"start_date": "{{ ds }}"},
    )

    backfill_first = LatestOnlyOperator(task_id="ensure_backfill_complete")

    with TaskGroup(group_id=f"process-metacritic-data") as tg:
        consoles = ["xbox360", "xbox-series-x", "xboxone", "xbox"]
        for console in consoles:
            t1 = KubernetesJobOperator(
                task_id=f"scrape-{console}-game-list",
                body_filepath=POD_TEMPALTE,
                command=["python", f"{BASE}/metacritic/scrape_game_list.py"],
                jinja_job_args={
                    "image": f"eu.gcr.io/{GOOGLE_CLOUD_PROJECT}/scraper:latest",
                    "name": f"get-games-list-{console}",
                    "gitsync": True,
                    "volumes": [
                        {
                            "name": "persistent-volume",
                            "type": "persistentVolumeClaim",
                            "reference": "data-pv-claim",
                            "mountPath": "/etc/scraped_data/",
                        }
                    ],
                },
                envs={
                    "console": console,
                },
            )
            with TaskGroup(group_id=f"process-{console}-data") as tg1:
                t2 = KubernetesJobOperator(
                    task_id=f"scrape-{console}-game-data",
                    body_filepath=POD_TEMPALTE,
                    command=["python", f"{BASE}/metacritic/scrape_game_data.py"],
                    jinja_job_args={
                        "image": f"eu.gcr.io/{GOOGLE_CLOUD_PROJECT}/scraper:latest",
                        "name": f"get-{console}-game-data",
                        "gitsync": True,
                        "volumes": [
                            {
                                "name": "persistent-volume",
                                "type": "persistentVolumeClaim",
                                "reference": "data-pv-claim",
                                "mountPath": "/etc/scraped_data/",
                            }
                        ],
                    },
                    envs={"console": console},
                )

                t3 = KubernetesJobOperator(
                    task_id=f"scrape-{console}-user-reviews",
                    body_filepath=POD_TEMPALTE,
                    command=["python", f"{BASE}/metacritic/scrape_game_reviews.py"],
                    jinja_job_args={
                        "image": f"eu.gcr.io/{GOOGLE_CLOUD_PROJECT}/scraper:latest",
                        "name": f"get-{console}-user-reviews",
                        "gitsync": True,
                        "volumes": [
                            {
                                "name": "persistent-volume",
                                "type": "persistentVolumeClaim",
                                "reference": "data-pv-claim",
                                "mountPath": "/etc/scraped_data/",
                            }
                        ],
                    },
                    envs={"console": console, "review_type": "user"},
                )
                t4 = KubernetesJobOperator(
                    task_id=f"scrape-{console}-critic-reviews",
                    body_filepath=POD_TEMPALTE,
                    command=["python", f"{BASE}/metacritic/scrape_game_reviews.py"],
                    jinja_job_args={
                        "image": f"eu.gcr.io/{GOOGLE_CLOUD_PROJECT}/scraper:latest",
                        "name": f"get-{console}-critic-reviews",
                        "gitsync": True,
                        "volumes": [
                            {
                                "name": "persistent-volume",
                                "type": "persistentVolumeClaim",
                                "reference": "data-pv-claim",
                                "mountPath": "/etc/scraped_data/",
                            }
                        ],
                    },
                    envs={"console": console, "review_type": "critic"},
                )
            t1 >> tg1

    v1 = KubernetesJobOperator(
        task_id="scrape-vgchartz-hw-sales",
        body_filepath=POD_TEMPALTE,
        command=["python", f"{BASE}/vgchartz/scrape_hardware_sales.py"],
        jinja_job_args={
            "image": f"eu.gcr.io/{GOOGLE_CLOUD_PROJECT}/scraper:latest",
            "name": "scrape-vg-hw-sales",
            "gitsync": True,
            "volumes": [
                {
                    "name": "persistent-volume",
                    "type": "persistentVolumeClaim",
                    "reference": "data-pv-claim",
                    "mountPath": "/etc/scraped_data/",
                }
            ],
        },
    )

    v2 = KubernetesJobOperator(
        task_id="scrape-vgchartz-game-sales",
        body_filepath=POD_TEMPALTE,
        command=["python", f"{BASE}/vgchartz/scrape_game_sales.py"],
        jinja_job_args={
            "image": f"eu.gcr.io/{GOOGLE_CLOUD_PROJECT}/scraper:latest",
            "name": "scrape-vg-game-sales",
            "gitsync": True,
            "volumes": [
                {
                    "name": "persistent-volume",
                    "type": "persistentVolumeClaim",
                    "reference": "data-pv-claim",
                    "mountPath": "/etc/scraped_data/",
                }
            ],
        },
    )
    x1 = KubernetesJobOperator(
        task_id="load_to_bq",
        body_filepath=POD_TEMPALTE,
        command=["/bin/bash", "/git/repo/airflow/dags/scripts/gs_script.sh"],
        jinja_job_args={
            "image": "google/cloud-sdk:alpine",
            "name": "ingest-and-load-to-bq",
            "gitsync": True,
            "volumes": [
                {
                    "name": "persistent-volume",
                    "type": "persistentVolumeClaim",
                    "reference": "data-pv-claim",
                    "mountPath": MOUNT_VOLUME_PATH,
                }
            ],
        },
        envs={
            "LOCAL_DIR": MOUNT_VOLUME_PATH,
            "TWITTER_DATASET": os.getenv("TWITTER_DATASET", "twitter_data"),
            "VGCHARTZ_DATASET": os.getenv("VGCHARTZ_DATASET", "vgchartz_data"),
            "METACRITIC_DATASET": os.getenv("METACRITIC_DATASET", "metacritic_data"),
            "DATA_BUCKET": os.getenv("DATA_BUCKET", "raw-103kdj49klf22k"),
        },
    )
    t >> backfill_first >> [v1, v2, tg] >> x1
