import os
import sys
from datetime import datetime, timedelta

import pendulum
from airflow.decorators import task_group
from airflow.operators.bash import BashOperator
from airflow_kubernetes_job_operator.kube_api import KubeResourceKind
from airflow_kubernetes_job_operator.kubernetes_job_operator import \
    KubernetesJobOperator

from airflow import DAG

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


default_args = {
    "owner": "airflow",
    "start_date": pendulum.yesterday(),
    "depends_on_past": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=60),
    "concurrency": 20,
    "max_active_runs": 5,
    "in_cluster": True,
    "random_name_postfix_length": 3,
    "name_prefix": "",
}


today = datetime.today().strftime("%Y-%m-%d")
POD_TEMPALTE = os.path.join(os.path.dirname(__file__), "templates", "pod_template.yaml")
BASE = "/git/repo/scrapers"

with DAG(
    dag_id="full-refresh",
    schedule_interval=None,
    default_args=default_args,
    catchup=False,
    tags=["full-refresh"],
    description="initial load/full refresh data pipeline",
) as dag:

    GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "stellarismusv4")

# "xbox-series-x", "xbox-one","xbox"
    consoles = [  "xbox360", ]
    for console in consoles:
        
        t1 = KubernetesJobOperator(
            task_id=f"scrape-{console}-game-list",
            body_filepath=POD_TEMPALTE,
            command=["python", f"{BASE}/metacritic/scrape_game_list.py"],
            arguments=[
                "--console",
                console
            ],
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
            },
            envs={

                "console": console,
            }
        )
        
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
            envs={
                # "game_list": f"{{{{ ti.xcom_pull(key=\'game_list_{console}\') }}}}",

                "console": console
            }
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
            envs={

                "console": console,
                "review_type": "user"
            }
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
            envs={

                "console": console,
                "review_type": "critic"
            }
        )

        t1>>[t2, t3, t4]
        