import pandas as pd

import os
import json
import requests

from datetime import datetime, timedelta
from pytz import timezone

from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from airflow.providers.mysql.operators.mysql import MySqlOperator
from airflow.models.variable import Variable

from scripts.request_metadata import get_metadata
from scripts.match_user_processing import match_user_processing
from scripts.match_user_to_sql import match_user_to_sql



default_args = {
    "owner" : "airflow",
    
    "email_on_failure" : False, # to receive email when task is failed
    "email_on_retry" : False, # to receive email when task is retried
    "email" : "admin@localhost.com", # to receive email address 

    "retries" : 3, # numbers of retries before ending up with the status failure
    "retry_delay" : timedelta(minutes = 5), # time delay when task is retried
    } # specify common attributes of "task", not only for DAG 

# def print_hello():
#     print("Hello, Airflow!")
#     print(Variable.get("api_key"))

def slack_success_callback(context):
    slack_msg = SlackWebhookOperator(
        task_id = 'slack_success_notification',
        slack_webhook_conn_id = 'slack_noti',

        message = """
            :large_green_circle: Task Succeeded.
            *Dag*: {dag}  
            *Task*: {task}
            *Task_Time*: {exec_date}  
            """.format(
                dag = context.get('task_instance').dag_id,
                task = context.get('task_instance').task_id,
                exec_date = context.get('execution_date').astimezone(timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')
            )
    )

    return slack_msg.execute(context = context)

def slack_failure_callback(context):
    slack_msg = SlackWebhookOperator(
        task_id = 'slack_failure_notification',
        slack_webhook_conn_id = 'slack_noti',

        message="""
                :red_circle: Task Failed.
                *Dag*: {dag}  
                *Task*: {task}
                *Task_Time*: {exec_date}  
                *Log_Url*: {log_url}
                """.format(
                    dag = context.get('task_instance').dag_id,
                    task = context.get('task_instance').task_id,
                    exec_date = context.get('execution_date').astimezone(timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S'),
                    log_url=context.get('task_instance').log_url,
                ),
        )

    return slack_msg.execute(context = context)

with DAG(
        dag_id = 'match_user_dag', 
        description = 'DAG for match_user', 
        start_date = datetime(2024, 12, 9, 20, tzinfo = timezone('Asia/Seoul')),
        schedule_interval="5 */2 * * *",  # Execute every 2 hours
        default_args = default_args, 
        catchup = False) as dag:

            # print_task = PythonOperator(
            #     task_id = 'print_task', 
            #     python_callable = print_hello,
            #     on_success_callback = slack_success_callback,
            #     on_failure_callback = slack_failure_callback
            # ) 

            get_metadata_task = PythonOperator(
                task_id = 'get_metadata_task',
                python_callable = get_metadata,
                op_kwargs = {
                    '_api_key' : Variable.get("api_key"),
                    '_file_dir' : Variable.get("file_dir"),
                },
                on_success_callback = slack_success_callback,
                on_failure_callback = slack_failure_callback
            )

            match_user_processing_task = PythonOperator(
                task_id = 'match_user_processing_task',
                python_callable = match_user_processing,
                op_kwargs = {
                    '_api_key' : Variable.get("api_key"), 
                    '_file_dir' : Variable.get("file_dir"),
                    '_task_time' : "{{ logical_date.in_timezone('Asia/Seoul').strftime('%Y_%m_%d_%H') }}" 
                },
                on_success_callback = slack_success_callback,
                on_failure_callback = slack_failure_callback
            )

            match_user_to_sql_task = PythonOperator(
                task_id = 'match_user_to_sql',
                python_callable = match_user_to_sql,
                op_kwargs = {
                    '_file_dir' : Variable.get("file_dir"),
                    '_task_time': "{{ logical_date.in_timezone('Asia/Seoul').strftime('%Y_%m_%d_%H') }}",
                    '_user_name' : Variable.get("airflow_user_name"),
                    '_password' : Variable.get("airflow_password"),
                    '_host' : Variable.get("airflow_host"),
                    '_port' : Variable.get("airflow_port"),
                    '_database' : Variable.get("airflow_database")
                },
                on_success_callback = slack_success_callback,
                on_failure_callback = slack_failure_callback
            )

            # print_task
            get_metadata_task >> match_user_processing_task >> match_user_to_sql_task
