import awesome_streamlit as ast
import os
import pandas as pd
import psycopg2
import src.pages.home
import src.pages.insert_member
import src.pages.show_members
import streamlit as st

# Define what pages are available on the left panel
PAGES = {
    "Home": src.pages.home,
    "Show Members": src.pages.show_members,
    "Add New Member": src.pages.insert_member
}
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", list(PAGES.keys()))

# Capture the module which will render the desired page
page = PAGES[selection]

# Render the chosen page
with st.spinner(f"Loading {selection} ..."):
    ast.shared.components.write_page(page)

# Add some info to the left panel
st.sidebar.title("About")
st.sidebar.info(
    "This app was made with the [steamlit](https://streamlit.io/docs/index.html) framework "
)