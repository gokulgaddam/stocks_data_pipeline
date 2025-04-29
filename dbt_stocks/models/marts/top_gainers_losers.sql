{{ config(
    materialized = 'incremental',
    schema       = 'marts',
    unique_key   = ['symbol', 'trade_date', 'rank_type']   
) }}

with ranked as (                       
    select
        symbol,
        company_name,
        trade_date,
        percent_change,

        row_number() over (           
            partition by trade_date
            order by percent_change desc
        ) as rnk_gain,

        row_number() over (          
            partition by trade_date
            order by percent_change asc
        ) as rnk_lose
    from {{ ref('stocks_daily_summary') }}
),

top5 as (                             
    select
        symbol,
        company_name,
        trade_date,
        percent_change,
        'gainer'      as rank_type,
        rnk_gain      as rank_pos
    from ranked
    where rnk_gain <= 5

    union all

    select
        symbol,
        company_name,
        trade_date,
        percent_change,
        'loser'       as rank_type,
        rnk_lose      as rank_pos
    from ranked
    where rnk_lose <= 5
)

select *
from top5
{% if is_incremental() %}
    where (symbol, trade_date) not in (
        select symbol, trade_date
        from {{ this }}
    )
{% endif %}
