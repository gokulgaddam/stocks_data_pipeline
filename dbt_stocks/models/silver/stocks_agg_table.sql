{{ 
    config(
    materialized = 'incremental',
    schema       = 'silver',
    unique_key=['symbol', 'trade_date']
      
) }}

with joined as (                 -- ①  JOIN BEFORE ANY FILTER

    select
        sp."T"                               as symbol,
        cast(to_timestamp_ltz(sp."t" / 1000) as date)  as trade_date,
        
        sp."o"                               as open_price,
        sp."c"                               as close_price,
        sp."h"                               as high_price,
        sp."l"                               as low_price,
        sp."v"                               as volume,
        sp."vw"                              as vwap,
        sp."n"                               as trade_count,
        sp."INGESTION_DATE",

        d.name               as company_name,
        d.market,
        d.primary_exchange,
        d.type               as security_type,
        d.active
    from {{ source('raw', 'stock_prices') }}      sp
    inner join {{ ref('dim_tickers_current') }}    d
           on sp."T" = d.ticker                   -- join first!
)

-- ②  AFTER the join, keep only rows from dates newer than the last stored
select *
from joined
{% if is_incremental() %}
    where (symbol, trade_date) not in (
        select symbol, trade_date
        from {{ this }}
    )
{% endif %}
