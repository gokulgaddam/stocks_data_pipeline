{{ config(
    materialized = 'incremental',
    schema       = 'marts',
    unique_key   = ['symbol', 'trade_date']     
) }}

with rolling as (                             
    select
        symbol,
        trade_date,

        avg(close_price) over (
            partition by symbol
            order by trade_date
            rows between 6 preceding and current row
        )                                       as avg_close_7d,

        avg(volume)      over (
            partition by symbol
            order by trade_date
            rows between 6 preceding and current row
        )                                       as avg_volume_7d,

        max(high_price)  over (
            partition by symbol
            order by trade_date
            rows between 6 preceding and current row
        )                                       as high_7d,

        min(low_price)   over (
            partition by symbol
            order by trade_date
            rows between 6 preceding and current row
        )                                       as low_7d,

        stddev(close_price) over (
            partition by symbol
            order by trade_date
            rows between 6 preceding and current row
        )                                       as volatility_7d
    from {{ ref('stocks_daily_summary') }}
)

select *
from rolling
{% if is_incremental() %}
    where (symbol, trade_date) not in (
        select symbol, trade_date
        from {{ this }}
    )
{% endif %}
