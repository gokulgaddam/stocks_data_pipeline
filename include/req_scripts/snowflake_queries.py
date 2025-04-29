import snowflake.connector
from snowflake.snowpark import Session
# import snowflake.connector

# conn = snowflake.connector.connect(
#     account='https://ghcuduc-hub21815.snowflakecomputing.com',  # Consider including region if required
#     user='gokulreddy98',
#     password='Gokul98*',
#     role='accountadmin',
#     warehouse='COMPUTE_WH',
#     database='dbt_stocks',
#     schema='raw'
# )

# cursor = conn.cursor()
# cursor.execute("SELECT CURRENT_VERSION()")
# print(cursor.fetchone())
# cursor.close()
# conn.close()



connection_params = {
    "account": "ghcuduc-hub21815",
    "user": 'gokulreddy98',
    "password": 'Gokul98*',
    "role": "accountadmin",
    "warehouse": 'COMPUTE_WH',
    "database": 'dbt_stocks'
}


def get_snowpark_session(schema='raw'):
    try:
        # Update connection parameters with the schema
        connection_params['schema'] = schema
        session = Session.builder.configs(connection_params).create()
        print("Snowpark session created successfully!")
        return session
    except Exception as e:
        print("Failed to create Snowpark session:", e)
        return None


def run_snowflake_query_dq_check(query):
    results = execute_snowflake_query(query)
    if len(results) == 0:
        raise ValueError('The query returned no results!')
    for result in results:
        for column in result:
            if type(column) is bool:
                assert column is True


def execute_snowflake_query(query):
    # Establish a connection to Snowflake
    conn = snowflake.connector.connect(**connection_params)
    try:
        # Create a cursor object to execute queries
        cursor = conn.cursor()
        # Example query: Get the current date from Snowflake
        cursor.execute(query)
        # Fetch and print the result
        result = cursor.fetchall()
        return result
    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()

