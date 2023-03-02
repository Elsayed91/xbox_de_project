import os
import sys
from datetime import datetime, timedelta

import pendulum
from airflow.decorators import task_group
from airflow.operators.bash import BashOperator
from airflow.utils.task_group import TaskGroup
from airflow_kubernetes_job_operator.kube_api import KubeResourceKind
from airflow_kubernetes_job_operator.kubernetes_job_operator import \
    KubernetesJobOperator

from airflow import DAG

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


default_args = {
    "owner": "airflow",
    "start_date": datetime.date(2022, 1, 1),
    "depends_on_past": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=60),
    "concurrency": 5,
    "max_active_runs": 1,
    "in_cluster": True,
    "random_name_postfix_length": 3,
    "name_prefix": "",
}

today = datetime.date.today()
first_day_of_previous_month = datetime.date(today.year, today.month - 1, 1)
today = datetime.today().strftime("%Y-%m-%d")
POD_TEMPALTE = os.path.join(os.path.dirname(__file__), "templates", "pod_template.yaml")
BASE = "/git/repo/scrapers"

with DAG(
    dag_id="twitter",
    schedule_interval="0 0 1 * *",
    default_args=default_args,
    catchup=True,
    tags=["Twitter"],
    # description="initial load/full refresh data pipeline",
) as dag:

    GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "stellarismusv4")


            
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
                    }]
            },
            envs={
                'start_date': '{{ ds }}'
            }
        )