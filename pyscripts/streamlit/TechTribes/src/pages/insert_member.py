"""
    NOTE: This code will be refactored to use sqlaclhemy instead of SQL
"""

import psycopg2
import os
import streamlit as st

# Obtain username/password saved as environment variables
user = os.environ['windowsuser']
pwd = os.environ['windowspwd']

@st.cache(allow_output_mutation=True, persist=True)
def insertMember(first: str, last: str, id: str, is_ahm: bool):
    """
        Function to insert new record / new member into the database

        Parameters:
        - first: str
        - last: str
        - id: str
        - is_ahm: bool

        Return Null
    """

    with psycopg2.connect(host='your_server',
                          port='5432',
                          database='your_database',
                          user=user,
                          password=pwd) as conn:

        cur = conn.cursor()

        base_profile_url = 'https://redacted.somecompany.com/Person.aspx?accountname=i:0%23.f|AccessManagerMembershipProvider|'

        sql = """
        INSERT INTO public.basic_member_info (first_name,
                                                last_name,
                                                hondaweb_id,
                                                hondaweb_url,
                                                is_ahm)
        VALUES (%s, %s, %s, %s, %s)
        """

        if is_ahm:
            profile_url = base_profile_url + first + ' ' + last
            # Need to catch SQL exception
            cur.execute(sql, (first, last, id, profile_url, 'yes'))
        else:
            profile_url = base_profile_url + id
            # Need to catch SQL exception
            cur.execute(sql, (first, last, id, profile_url, 'no'))

        conn.commit()

        return

def write():
    """ Writes content to the app """

    st.title("Add new Tech Tribe Member")

    is_ahm = st.checkbox("Check this box if person is an AHM associate", False)

    if not is_ahm:
        first_name = st.text_input("Enter your first name:")
        last_name = st.text_input("Enter your last name:")
        id = st.text_input("Enter your Windows login ID (ex: \"vc12345\"):").lower()
    else:
        st.write("Visit the AHM person's HondaWeb profile first prior to entering info below:")
        first_name = st.text_input("Enter first name found in HondaWeb profile:")
        last_name = st.text_input("Enter last name found in HondaWeb profile:")
        id = first_name + ' ' + last_name


    # Define what happens when user clicks on the "Execute" button
    if st.button("Execute"):
        '''
        ### Add new member to database
        '''

        # Input Validation - if they omitted any info:
        if first_name == '' or last_name == '' or id == '':
            st.warning("You must enter all information")
        else:
            try:
                insertMember(first_name, last_name, id, is_ahm)
                st.write('**New member successfully added!**')
                st.balloons()
            except psycopg2.IntegrityError as error:
                st.warning("Member already exists in the database")
                st.write('Specific error message:')
                st.write(error)

if __name__ == "__main__":
    write()