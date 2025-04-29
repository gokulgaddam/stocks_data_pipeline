
-- depends_on: {{ ref('tickers_scd2') }}
{{ config(materialized='table', schema='silver') }}

select *
from {{ ref('tickers_scd2') }}
where dbt_valid_to is null        
