from snowflake_queries import execute_snowflake_query, get_snowpark_session
from snowflake.snowpark.functions import lit
import requests
import math
import datetime



def load_stocks_to_snowflake():
    session = get_snowpark_session()
    query="""
    SELECT TICKER 
    FROM DBT_STOCKS.RAW.TICKERS
    """
    tickers=execute_snowflake_query(query)
    ticker_list = [ticker[0] for ticker in tickers]
    batch_size=100
    num_batches = math.ceil(len(ticker_list) / batch_size)
    ingestion_date = datetime.datetime.now().isoformat()
    final_df=None
    print("Entering the loop")
    for i in range(num_batches):
        batch_tickers = ticker_list[i * batch_size: (i + 1) * batch_size]
        symbols = ",".join(batch_tickers)
        url = f'http://api.marketstack.com/v2/eod/2025-04-04?access_key=6ac9eaa528245f331e5bba851554ccd6&symbols={symbols}' 
        response = requests.get(url).json()
        
        if 'error' in response:
            print("API Error:", response['error'])
            return
        else:
            # Assume the API returns stock data in the "data" field
            batch_data = response.get('data', [])
            if not batch_data:
                continue
            
            # Create a DataFrame from the batch data
            batch_df = session.create_dataframe(batch_data)
            # Add the ingestion_date column directly to the batch DataFrame
            batch_df = batch_df.withColumn("ingestion_date", lit(ingestion_date))
            
            # Union with the final DataFrame
            if final_df is None:
                final_df = batch_df
            else:
                final_df = final_df.union(batch_df)
    
    if final_df is not None:
        # Write the final accumulated DataFrame to Snowflake
        final_df.write.mode("overwrite").save_as_table("daily_stocks")
        print("Data loaded successfully.")
    else:
        print("No data was loaded.")

# Example usage:
load_stocks_to_snowflake()

