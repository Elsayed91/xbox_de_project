import json
import os
import sys
from datetime import datetime, timedelta

import pendulum
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
    "concurrency": 1,
    "max_active_runs": 3,
    "in_cluster": True,
    "random_name_postfix_length": 2,
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


    t1 = KubernetesJobOperator(
        task_id="get_games_list",
        body_filepath=POD_TEMPALTE,
        command=["python", f"{BASE}/metacritic/get_games.py"],
        # arguments=[
        #     "--data-source",

        # ],
        jinja_job_args={
            "image": f"eu.gcr.io/{GOOGLE_CLOUD_PROJECT}/scraper:latest",
            "name": "get-games-list",
            "gitsync": True,
        },
    )
    
    t2 = KubernetesJobOperator(
        task_id="scrape-games-data",
        body_filepath=POD_TEMPALTE,
        command=["python", f"{BASE}/metacritic/scrape_games_data.py"],
        # arguments=[
        #     "--data-source",

        # ],
        jinja_job_args={
            "image": f"eu.gcr.io/{GOOGLE_CLOUD_PROJECT}/scraper:latest",
            "name": "get-games-data",
            "gitsync": True,
        },
        envs={
            "game_list": json.loads('{{ ti.xcom_pull(key=\'game_list\') }}')
        }
    )

    
    t1>>t2