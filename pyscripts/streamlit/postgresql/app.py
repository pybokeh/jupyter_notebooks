from jinjasql import JinjaSql
from typing import List
import os
import pandas as pd
import psycopg2
import streamlit as st  # version 0.49

# Simple streamlit example to illustrate retrieving data from a database
# based on 2 inputs provided from the user.  It also makes use of the
# JinjaSql library since in this version, a SQL in() clause needs to be
# safely created in such a matter to prevent SQL injection attacks.

'''
# Getting data from a PostgreSQL database
'''

# streamlit's st.cache does not work with os environment variables, so need
# to declare them outside of the st.cache decorator
# Retrieve the user's password that's saved as an environment variable
pwd = os.environ['pwd']

@st.cache(allow_output_mutation=True)
def get_distinct_payment_type() -> List[int]:
    """ Function to obtain distinct list of payment types so that we don't
        have to make a hard-coded list of valid values
    """

    conn = psycopg2.connect('dbname=analysis user=username password=' + pwd)
    cursor = conn.cursor()
    sql = 'select distinct payment_type from yellow_tripdata_2016_01'
    cursor.execute(sql)

    # fetchall() returns a list of tuples so need to make a list of ints
    # instead.  To do that, using list comprehension syntax.
    payment_type_list = [value[0] for value in cursor.fetchall()]
    
    return sorted(payment_type_list)

@st.cache(allow_output_mutation=True)
def get_distinct_passenger_count() -> List[int]:
    """ Function to obtain distinct list of passenger counts so that we don't
        have to make a hard-coded list of valid values
    """

    conn = psycopg2.connect('dbname=analysis user=username password=' + pwd)
    cursor = conn.cursor()
    sql = 'select distinct passenger_count from yellow_tripdata_2016_01'
    cursor.execute(sql)

    # fetchall() returns a list of tuples so need to make a list of ints
    # instead.  To do that, using list comprehension syntax.
    passenger_count_list = [value[0] for value in cursor.fetchall()]
    
    return sorted(passenger_count_list)

@st.cache(allow_output_mutation=True, persist=True)
def get_query_results(payment_type: List[int], passenger_count: List[int]):
    """ Function that accepts 2 inputs:
        - payment_type: list
        - passenger_count: list

        returns a pandas dataframe
    """

    with psycopg2.connect('dbname=analysis user=username password=' + pwd) as conn:
        j = JinjaSql(param_style='pyformat')

        data = {}
        data['payment_type'] = payment_type
        data['passenger_count'] = passenger_count

        template = """
        SELECT
            *
        FROM
            yellow_tripdata_2016_01
        WHERE
            payment_type in {{ payment_type | inclause }}
            and passenger_count in {{ passenger_count | inclause }}
        limit 200
        """

        query, bind_params = j.prepare_query(template, data)

        # Execute prepared statement to avoid SQL injection attacks
        df = pd.read_sql(query, con=conn, params=bind_params)
    
    return df

# Instead of making a hard-coded list of valid values, we retrieved them from the db
payment_type_list = get_distinct_payment_type()

# Instead of making a hard-coded list of valid values, we retrieved them from the db
passenger_count_list = get_distinct_passenger_count()

# Now build our selectbox widgets based on the generated lists
payment_type = st.multiselect('Select payment_type:', payment_type_list)
passenger_count = st.multiselect('Select passenger count:', passenger_count_list)

# When user clicks the "Execute" button, execute query and return result set
if st.button("Execute"):
    # If user does not select at least one item from each multiselect widget,
    # display a warning message
    if len(payment_type) == 0 or len(passenger_count) == 0:
        st.warning("You have to choose at least one item for payment type and passenger count")
    else:
        st.dataframe(get_query_results(payment_type, passenger_count))
