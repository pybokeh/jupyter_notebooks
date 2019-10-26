from typing import List
import duckdb
import pandas as pd
import streamlit as st

# Simple streamlit example to illustrate retrieving data from a database
# based on 2 inputs provided from the user.
# Using duckdb because it is blazingly fast.  It is a columnar version of sqlite.
# Therefore, aggregates on columns are very fast compared to a row-wise database.
# Since I will be issuing SELECT distinct statements to generate the UI widgets
# upon initial page load, the initial load time probably would have taken longer
# with sqlite.  The initial page load took less than a second despite issuing
# 2 SELECT distinct queries on a 10 million row table.

'''
# Getting data from a duckdb database
'''

@st.cache(allow_output_mutation=True)
def get_distinct_payment_type() -> List[int]:
    """ Function to obtain distinct list of payment types so that we don't
        have to make a hard-coded list of valid values
    """
    conn = duckdb.connect('ytd.duckdb')
    cursor = conn.cursor()
    sql = 'select distinct payment_type from yellow_tripdata_2016_01'
    payment_type_list = cursor.execute(sql).fetchnumpy()['payment_type']
    
    return sorted(payment_type_list)

@st.cache(allow_output_mutation=True)
def get_distinct_passenger_count() -> List[int]:
    """ Function to obtain distinct list of passenger counts so that we don't
        have to make a hard-coded list of valid values
    """
    conn = duckdb.connect('ytd.duckdb')
    cursor = conn.cursor()
    sql = 'select distinct passenger_count from yellow_tripdata_2016_01'
    passenger_count_list = cursor.execute(sql).fetchnumpy()['passenger_count']
    
    return sorted(passenger_count_list)

@st.cache(allow_output_mutation=True, persist=True)
def get_query_results(payment_type: int, passenger_count: int):
    """ Function that accepts 2 inputs:
        - payment_type: int
        - passenger_count: int

        and then returns a pandas dataframe
    """

    conn = duckdb.connect('ytd.duckdb')
    cursor = conn.cursor()
    sql = """
        SELECT *
        FROM yellow_tripdata_2016_01
        WHERE
        payment_type = ?
        and passenger_count = ?
        limit 200
    """
    # Execute prepared statement to avoid SQL injection attacks
    results = cursor.execute(sql, (payment_type, passenger_count)).fetchdf()
    
    return results

# Instead of making a hard-coded list of valid values, we retrieved them from the db
payment_type_list = get_distinct_payment_type()
# Instead of making a hard-coded list of valid values, we retrieved them from the db
passenger_count_list = get_distinct_passenger_count()

# Now build our selectbox widgets based on the generated lists
payment_type = st.selectbox('Select payment_type:', payment_type_list)
passenger_count = st.selectbox('Select passenger count:', passenger_count_list)

# When user clicks the "Execute" button, execute query and return result set
if st.button("Execute"):
    st.write(get_query_results(int(payment_type), int(passenger_count)))