from airflow.decorators import dag, task
from datetime import datetime
from airflow.models import Variable
from include.req_scripts.load_tickers_to_snowflake import load_snowflake_tickers

# Define DAG using @dag decorator
@dag(
    # The name of your DAG and the name of the Python file should match.
    # Both should start with your GitHub username to avoid duplicate DAG names.
    "tickers_monthly_dag",
    description="loads the tickers data to snoflake",
    default_args={
        "owner": "Gokul Gaddam",
        "start_date": datetime(2025, 4, 7),
        "retries": 1,
       
    },
    max_active_runs=1,
    schedule_interval="@monthly",
    catchup=False,
    tags=["tickers", 'Gokul Gaddam'],
    #template_searchpath=''
)
def snowflake_dag():
    @task(task_id='load_tickers_into_snowflake')
    def load_snowflake_task(polygon_key):
        load_snowflake_tickers(polygon_key)

    credentials = Variable.get("POLYGON_CREDS")
    load_snowflake_task(credentials)

snowflake_dag()
