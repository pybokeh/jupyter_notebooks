import psycopg2
import os
import pandas as pd
import streamlit as st

# Obtain username/password saved as environment variables
user = os.environ['windowsuser']
pwd = os.environ['windowspwd']

@st.cache(allow_output_mutation=True)
def get_query_results():
    with psycopg2.connect(host='your_server',
                          port='5432',
                          database='your_db',
                          user=user,
                          password=pwd) as conn:

        sql = """
        SELECT
            *
        FROM
            public.basic_member_info
        """

        df = pd.read_sql(sql, conn, index_col=None)


        def createProfileHref(url: str):
            """ Function to convert a string URL to a HTML formatted version """
    
            value = '<a href="' + url + '"' + "/>Profile</a>"
    
            return value

        df['profile_href'] = df['hondaweb_url'].apply(createProfileHref)

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
