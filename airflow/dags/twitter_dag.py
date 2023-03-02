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
    "start_date": pendulum.yesterday(),
    "depends_on_past": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=60),
    "concurrency": 5,
    "max_active_runs": 1,
    "in_cluster": True,
    "random_name_postfix_length": 3,
    "name_prefix": "",
}


today = datetime.today().strftime("%Y-%m-%d")
POD_TEMPALTE = os.path.join(os.path.dirname(__file__), "templates", "pod_template.yaml")
BASE = "/git/repo/scrapers"

with DAG(
    dag_id="vgchartz",
    schedule_interval=None,
    default_args=default_args,
    catchup=False,
    tags=["vgchartz"],
    # description="initial load/full refresh data pipeline",
) as dag:

    GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "stellarismusv4")

    v1 = KubernetesJobOperator(
            task_id=f"scrape-vgchartz-hw-sales",
            body_filepath=POD_TEMPALTE,
            command=["python", f"{BASE}/vgchartz/scrape_hardware_sales.py"],
            jinja_job_args={
                "image": f"eu.gcr.io/{GOOGLE_CLOUD_PROJECT}/scraper:latest",
                "name": f"scrape-vg-hw-sales",
                "gitsync": True,
                "volumes": [
                    {
                        "name": "persistent-volume",
                        "type": "persistentVolumeClaim",
                        "reference": "data-pv-claim",
                        "mountPath": "/etc/scraped_data/",
                    }]
            },
        )
    
    v2 = KubernetesJobOperator(
            task_id=f"scrape-vgchartz-game-sales",
            body_filepath=POD_TEMPALTE,
            command=["python", f"{BASE}/vgchartz/scrape_game_sales.py"],
            jinja_job_args={
                "image": f"eu.gcr.io/{GOOGLE_CLOUD_PROJECT}/scraper:latest",
                "name": f"scrape-vg-game-sales",
                "gitsync": True,
                "volumes": [
                    {
                        "name": "persistent-volume",
                        "type": "persistentVolumeClaim",
                        "reference": "data-pv-claim",
                        "mountPath": "/etc/scraped_data/",
                    }]
            },
        )
            
    v1
    v2