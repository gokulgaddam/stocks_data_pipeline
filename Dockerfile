FROM quay.io/astronomer/astro-runtime:11.3.0

USER root
# COPY ./dbt_project ./dbt_project
# COPY --chown=astro:0 . .

# install dbt into a virtual environment
#WORKDIR "/usr/local/airflow"

RUN python -m venv dbt_venv && source dbt_venv/bin/activate && \
    pip install --no-cache-dir -r dbt_stocks/dbt-requirements.txt  && \
    cd dbt_stocks && dbt deps && cd .. && \
    deactivate
# RUN set -ex \
#  && python -m venv /usr/local/airflow/dbt_venv \
#  && /usr/local/airflow/dbt_venv/bin/pip install --no-cache-dir \
#       -r dags/dbt/dbt_stocks/dbt-requirements.txt \
#  && /usr/local/airflow/dbt_venv/bin/dbt deps \
#       --project-dir dags/dbt/dbt_stocks
