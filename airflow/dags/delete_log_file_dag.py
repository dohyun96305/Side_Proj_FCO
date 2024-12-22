import pendulum

from datetime import datetime, timedelta
from pytz import timezone

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator



default_args = {
    "owner" : "airflow",
    
    "email_on_failure" : False, # to receive email when task is failed
    "email_on_retry" : False, # to receive email when task is retried
    "email" : "admin@localhost.com", # to receive email address 

    "retries" : 3, # numbers of retries before ending up with the status failure
    "retry_delay" : timedelta(minutes = 5), # time delay when task is retried
    } # specify common attributes of "task", not only for DAG 

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
        dag_id = 'delete_log_file', 
        description = 'delete log file', 
        start_date = datetime(2024, 12, 9, 20, tzinfo = timezone('Asia/Seoul')),
        schedule_interval="0 6 * * *",  # Execute every 6:00 AM
        default_args = default_args, 
        catchup = False) as dag:
    
    delete_log_task = BashOperator(
        task_id = 'delete_log',
        
        bash_command = """
            find /opt/airflow/logs/ -type f -mtime +0 -exec rm -rf {} \;
            find /opt/airflow/logs/ -type d -mtime +0 -empty -exec rm -rf {} \;        
        """,

        on_success_callback = slack_success_callback,
        on_failure_callback = slack_failure_callback
    )

    delete_file_task = BashOperator(
        task_id = 'delete_file',
        
        bash_command = """
            find /opt/airflow/dags/files/* -type f -not -name '.gitkeep' -mtime +0 -exec rm {} \;
        """,

        on_success_callback = slack_success_callback,
        on_failure_callback = slack_failure_callback
    )

    delete_log >> delete_file