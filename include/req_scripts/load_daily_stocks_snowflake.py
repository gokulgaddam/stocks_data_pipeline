
import requests
from include.req_scripts.snowflake_queries import get_snowpark_session
from snowflake.snowpark.types import StructType, StructField, StringType, FloatType, TimestampType
from snowflake.snowpark.functions import current_timestamp
from datetime import datetime
import pandas as pd


def load_snowflake(polygon_key, date, table):
    session = get_snowpark_session()
    
    date_to_be_pulled=datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
    print("date pulling the data:" +date + "apikey::"+ polygon_key)
    url = 'https://api.polygon.io/v2/aggs/grouped/locale/us/market/stocks/'+date_to_be_pulled+'?adjusted=true&apiKey=' + polygon_key
    example_stock =   {
      "T": "KIMpL",
      "c": 25.9102,
      "h": 26.25,
      "l": 25.91,
      "n": 74,
      "o": 26.07,
      "t": 1602705600000,
      "v": 4369,
      "vw": 26.0407
    }
    response = requests.get(url).json()
    if response['status'] == 'ERROR':
        print(response['error'])
        raise ValueError("Polygon API error: Could not pull stock data.")
        return 0

    if response['queryCount']==0:
        print("Market_holiday")
        return 0
    stocks = response['results']
    

    while 'next_url' in response:
        print('calling again')
        url = response['next_url'] + '&apiKey=' + polygon_key
        print(url)
        response = requests.get(url).json()
        if response['status']=='ERROR':
            print("API Error")
        else:
            stocks.extend(response['results'])

    print('we found', len(stocks), 'tickers')
    
    # for stock in stocks:
    #     stock['T'] = str(stock.get('T', ''))  # ensure string, default to ''
    #     for field in ['c', 'h', 'l', 'o', 'vw']:
    #         stock[field] = float(stock.get(field, 0))

   
    columns = []
    for (key, value) in example_stock.items():
        if 'utc' in key:
            columns.append(key + ' TIMESTAMP')
        elif type(value) is str:
            columns.append(key + ' VARCHAR')
        elif type(value) is bool:
            columns.append(key + ' BOOLEAN')
        elif type(value) is float:
            columns.append(key + ' FLOAT')

    df=pd.DataFrame(stocks)
    df = df.dropna()
    df=df.drop_duplicates()
    df['T']=df['T'].astype(str)
    columns_str = ' , '.join(columns)
    create_ddl = f'CREATE TABLE IF NOT EXISTS {table} ({columns_str})'
    print(create_ddl)
    session.sql(create_ddl)

    df=session.create_dataframe(df, schema=None)
    
    df = df.with_column("ingestion_date", current_timestamp())
    df.write.mode("overwrite").save_as_table("stock_prices")
    return 1








