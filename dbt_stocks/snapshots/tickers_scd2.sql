{% snapshot tickers_scd2 %}
{{ config(
    target_schema           = 'silver',
    unique_key              = 'ticker',
    strategy                = 'timestamp',
    updated_at              = 'last_updated_utc',
    invalidate_hard_deletes = true
) }}

with src as (

    select
        ticker,
        name,
        market,
        locale,
        primary_exchange,
        type,
        currency_name,
        active,
        cik,
        composite_figi,
        share_class_figi,
        last_updated_utc,

        row_number() over (
            partition by ticker
            order by last_updated_utc desc, locale asc
        ) as rn
    from {{ source('raw', 'TICKERS_STG') }}

)

select *
from src
where rn = 1               -- ← keeps just one row per ticker

{% endsnapshot %}
