import jaydebeapi as jdba
import os
import pandas as pd
import streamlit as st

'''
Web App to Obtain Some Data
'''

user = os.environ[‘some_user_var’]
pwd = os.environ[‘some_pwd_var’]

st.cache(ignore_hash=True)
def fetch_db_data():
    conn = jdba.connect(‘com.ibm.db2.jcc.DB2Driver’, ‘jdbc:db2://some_server:50000/some_database’,
    [user, pwd], jars=[‘D:/JDBC_Drivers/folder1/db2jcc4.jar’, ‘D:/JDBC_Drivers/folder1/db2jcc.jar’])

    return conn

conn = fetch_db_data()

sql = “”"
SELECT
*
FROM
some_table
FETCH FIRST 200 ROWS ONLY
“”"

df = pd.read_sql(sql, conn, index_col=None)

st.write(df)