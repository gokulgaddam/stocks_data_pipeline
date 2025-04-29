{{ config(materialized='incremental', schema='marts',  unique_key=['symbol', 'trade_date']) }}

with src as (

    select
        symbol,
        company_name,
        trade_date,   
        open_price,
        close_price,
        high_price,
        low_price,
        volume,
        vwap,
        close_price - open_price              as price_change,
        round((close_price - open_price)  
              / nullif(open_price,0) * 100,2) as percent_change,
        round(high_price - low_price,2)       as volatility

    from {{ ref('stocks_agg_table') }}

)

select *
from src
{% if is_incremental() %}
    where (symbol, trade_date) not in (
        select symbol, trade_date
        from {{ this }}
    )
{% endif %}
