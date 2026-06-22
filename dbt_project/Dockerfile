FROM python:3.11-slim

WORKDIR /dbt

COPY requirements.txt .
RUN pip install --no-cache-dir dbt-core==1.8.7 dbt-snowflake==1.8.4

COPY dbt_project/ .

ENV DBT_PROFILES_DIR=.

CMD [ "dbt", "run" ]