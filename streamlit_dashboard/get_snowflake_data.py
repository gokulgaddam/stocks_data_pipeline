import os
import snowflake.connector
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
def fetch_and_save_daily_stock_summary(output_dir="."):
    
   
    query = """
        SELECT * FROM STOCKS_DAILY_SUMMARY s
        WHERE s.TRADE_DATE = (SELECT MAX(TRADE_DATE) FROM STOCKS_DAILY_SUMMARY)
    """

    ctx = snowflake.connector.connect(
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
        database=os.getenv('SNOWFLAKE_DATABASE'),
        schema=os.getenv('SNOWFLAKE_MART_SCHEMA')
    )

    try:
        df = pd.read_sql(query, ctx)
    finally:
        ctx.close()

    today = datetime.now().strftime('%Y-%m-%d')
    output_path = os.path.join(output_dir, f"daily_stocks_{today}.csv")
    df.to_csv(output_path, index=False)
    
    return output_path

print(fetch_and_save_daily_stock_summary(output_dir="."))