import psycopg2
import os
import pandas as pd
import streamlit as st

# Obtain username/password saved as environment variables
user = os.environ['windowsuser']
pwd = os.environ['windowspwd']

@st.cache(allow_output_mutation=True)
def get_query_results():
    """
        Function to return query results as a streamlit dataframe or
        dataframe as raw HTML
    """

    with psycopg2.connect(host='your_server',
                          port='5432',
                          database='your_database',
                          user=user,
                          password=pwd) as conn:

        sql = """
        SELECT
            *
        FROM
            public.basic_member_info
        """

        df = pd.read_sql(sql, conn, index_col=None)


        def createProfileHref(row):
            """ Function to convert a string URL to a HTML formatted version """
    
            value = '<a href="' + str(row['hondaweb_url']) + '"' + "/>Profile</a>"
    
            return value

        df['profile_href'] = df.apply(createProfileHref, axis='columns')

    return df

def write():
    """ Writes content to the app """
    st.title("Get Members Data from PostgreSQL")

    html = st.checkbox(
        'OPTIONAL: Render output as raw html.  Otherwise, just click on Execute botton.',
        False)

    # Define what happens when user clicks on the "Execute" button
    if st.button("Execute"):
        '''
        ### Query results:
        '''
        if html:
            st.write(get_query_results().to_html(escape=False, index=False), unsafe_allow_html=True)
        else:
            st.dataframe(get_query_results())

if __name__ == "__main__":
    write()