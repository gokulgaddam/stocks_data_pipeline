import os
from datetime import datetime, timedelta


from airflow.decorators import dag, task
from airflow.exceptions import AirflowSkipException

from cosmos import (
    DbtTaskGroup,
    ProjectConfig,
    ProfileConfig,
    RenderConfig,
    ExecutionConfig,
)

from include.req_scripts.load_daily_stocks_snowflake   import load_snowflake
from include.req_scripts.load_tickers_to_snowflake     import load_snowflake_tickers


airflow_home         = os.getenv("AIRFLOW_HOME")
PATH_TO_DBT_PROJECT  = f"{airflow_home}/dbt_stocks"
PATH_TO_DBT_PROFILES = f"{airflow_home}/dbt_stocks/profiles.yml"

profile_config = ProfileConfig(
    profile_name          = "dbt_stocks",
    target_name           = "dev",
    profiles_yml_filepath = PATH_TO_DBT_PROFILES,
)

EXEC_CONFIG = ExecutionConfig(
    dbt_executable_path = f"{airflow_home}/dbt_venv/bin/dbt",
)

default_args = {
    "owner"             : "Gokul Reddy",
    "retries"           : 1,
    "execution_timeout" : timedelta(hours=1),
}

@dag(
    dag_id            = "stocks_daily_dag_dbt",
    start_date        = datetime(2025, 4, 9),
    schedule_interval = '0 22 * * *',
    catchup           = False,
    max_active_runs   = 1,
    default_args      = default_args,
    tags              = ["stocks", "dbt", "snowflake"],
)
def stocks_daily_dag():

    @task(task_id="load_tickers_snapshot")
    def load_tickers_snapshot():
        polygon_key = os.getenv("POLYGON_CREDS")
        load_snowflake_tickers(polygon_key)

    @task(task_id="load_prices")
    def load_prices(**context):
        polygon_key    = os.getenv("POLYGON_CREDS")
        execution_date = context["ds"]               # yyyy-mm-dd
        ok = load_snowflake(polygon_key, execution_date, "stock_prices")
        
        if not ok:
            raise AirflowSkipException(
                f"market holiday {execution_date} – skipping run"
            )

    snapshot_group = DbtTaskGroup(
        group_id        = "dbt_snapshot_tickers",
        project_config  = ProjectConfig(PATH_TO_DBT_PROJECT),
        profile_config  = profile_config,
        execution_config= EXEC_CONFIG,
        render_config   = RenderConfig(
            select=[ "path:snapshots"],
        ),
    )

    run_group = DbtTaskGroup(
        group_id        = "dbt_run_marts",
        project_config  = ProjectConfig(PATH_TO_DBT_PROJECT),
        profile_config  = profile_config,
        execution_config= EXEC_CONFIG,
        render_config   = RenderConfig(
            select = ["dim_tickers_current+"],  
        ),
    )

    
    load_tickers_snapshot() >> load_prices() >> snapshot_group >> run_group

stocks_daily_dag()
