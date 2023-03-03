import os
import sys
from datetime import datetime, timedelta

import pendulum
from airflow.decorators import task_group
from airflow.operators.bash import BashOperator
from airflow.operators.latest_only import LatestOnlyOperator
from airflow.utils.task_group import TaskGroup
from airflow_kubernetes_job_operator.kube_api import KubeResourceKind
from airflow_kubernetes_job_operator.kubernetes_job_operator import \
    KubernetesJobOperator

from airflow import DAG

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))



default_args = {
    "owner": "airflow",
    "start_date": datetime(2022, 12, 1),
    "depends_on_past": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=60),
    "concurrency": 2,
    "max_active_runs": 1,
    "in_cluster": True,
    "random_name_postfix_length": 3,
    "name_prefix": "",
}



today = datetime.today().strftime("%Y-%m-%d")
POD_TEMPALTE = os.path.join(os.path.dirname(__file__), "templates", "pod_template.yaml")
BASE = "/git/repo/scrapers"

with DAG(
    dag_id="full-refresh",
    schedule_interval= None ,#"0 0 1 * *",
    default_args=default_args,
    catchup=True,
    tags=["full-refresh"],
    description="initial load/full refresh data pipeline",
) as dag:

    GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "stellarismusv4")

    # t = KubernetesJobOperator(
    #         task_id=f"scrape-tweets",
    #         body_filepath=POD_TEMPALTE,
    #         command=["python", f"{BASE}/twitter/sentiment_analysis.py"],
    #         jinja_job_args={
    #             "image": f"eu.gcr.io/{GOOGLE_CLOUD_PROJECT}/scraper:latest",
    #             "name": f"scrape-tweets",
    #             "gitsync": True,
    #             "volumes": [
    #                 {
    #                     "name": "persistent-volume",
    #                     "type": "persistentVolumeClaim",
    #                     "reference": "data-pv-claim",
    #                     "mountPath": "/etc/scraped_data/",
    #                 }]
    #         },
    #         envs={
    #             'start_date': '{{ ds }}'
    #         }
    #     )
    
    # backfill_first = LatestOnlyOperator(task_id="latest_only")
    
    
    with TaskGroup(group_id=f'process-metacritic-data') as tg:
        consoles = [ "xbox360","xbox-series-x", "xboxone","xbox" ]
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
                        }]
                },
                envs={

                    "console": console,
                }
            )
            with TaskGroup(group_id=f'process-{console}-data') as tg1:
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
                
                # t3 = KubernetesJobOperator(
                #     task_id=f"scrape-{console}-user-reviews",
                #     body_filepath=POD_TEMPALTE,
                #     command=["python", f"{BASE}/metacritic/scrape_game_reviews.py"],
                #     jinja_job_args={
                #         "image": f"eu.gcr.io/{GOOGLE_CLOUD_PROJECT}/scraper:latest",
                #         "name": f"get-{console}-user-reviews",
                #         "gitsync": True,
                #         "volumes": [
                #             {
                #                 "name": "persistent-volume",
                #                 "type": "persistentVolumeClaim",
                #                 "reference": "data-pv-claim",
                #                 "mountPath": "/etc/scraped_data/",
                #             }
                #         ],
                #     },
                #     envs={

                #         "console": console,
                #         "review_type": "user"
                #     }
                # )
                # t4 = KubernetesJobOperator(
                #     task_id=f"scrape-{console}-critic-reviews",
                #     body_filepath=POD_TEMPALTE,
                #     command=["python", f"{BASE}/metacritic/scrape_game_reviews.py"],
                #     jinja_job_args={
                #         "image": f"eu.gcr.io/{GOOGLE_CLOUD_PROJECT}/scraper:latest",
                #         "name": f"get-{console}-critic-reviews",
                #         "gitsync": True,
                #         "volumes": [
                #             {
                #                 "name": "persistent-volume",
                #                 "type": "persistentVolumeClaim",
                #                 "reference": "data-pv-claim",
                #                 "mountPath": "/etc/scraped_data/",
                #             }
                #         ],
                #     },
                #     envs={

                #         "console": console,
                #         "review_type": "critic"
                #     }
                # )
            t1>>tg1
            
    # v1 = KubernetesJobOperator(
    #         task_id=f"scrape-vgchartz-hw-sales",
    #         body_filepath=POD_TEMPALTE,
    #         command=["python", f"{BASE}/vgchartz/scrape_hardware_sales.py"],
    #         jinja_job_args={
    #             "image": f"eu.gcr.io/{GOOGLE_CLOUD_PROJECT}/scraper:latest",
    #             "name": f"scrape-vg-hw-sales",
    #             "gitsync": True,
    #             "volumes": [
    #                 {
    #                     "name": "persistent-volume",
    #                     "type": "persistentVolumeClaim",
    #                     "reference": "data-pv-claim",
    #                     "mountPath": "/etc/scraped_data/",
    #                 }]
    #         },
    #     )
    
    # v2 = KubernetesJobOperator(
    #         task_id=f"scrape-vgchartz-game-sales",
    #         body_filepath=POD_TEMPALTE,
    #         command=["python", f"{BASE}/vgchartz/scrape_game_sales.py"],
    #         jinja_job_args={
    #             "image": f"eu.gcr.io/{GOOGLE_CLOUD_PROJECT}/scraper:latest",
    #             "name": f"scrape-vg-game-sales",
    #             "gitsync": True,
    #             "volumes": [
    #                 {
    #                     "name": "persistent-volume",
    #                     "type": "persistentVolumeClaim",
    #                     "reference": "data-pv-claim",
    #                     "mountPath": "/etc/scraped_data/",
    #                 }]
    #         },
    #     )

    # # t >> backfill_first >> 
    # [v1,v2,tg]

