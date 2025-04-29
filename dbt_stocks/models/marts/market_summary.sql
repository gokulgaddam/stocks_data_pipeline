{{ config(
    materialized = 'incremental',
    schema       = 'marts',
    unique_key   = 'trade_date'              
) }}


with latest_day AS (
    select max(trade_date) as max_trade_date
    from   {{ ref('stocks_agg_table') }}
),


day_rows AS (
    select *
    from   {{ ref('stocks_agg_table') }} f
    join   latest_day d
      on   f.trade_date = max_trade_date
),


day_summary AS (
    select
        trade_date,

        round(avg( (close_price - open_price)
                   / nullif(open_price,0) * 100 ), 2)  as avg_change_percent,
        sum(volume) as total_volume,
        max_by(symbol, volume)  as most_traded_stock,
        max_by(company_name, volume)  as most_traded_company
    from day_rows
    group by trade_date
)


select *
from   day_summary
{% if is_incremental() %}
    where trade_date not in (
        select trade_date
        from {{ this }}
    )
{% endif %}
