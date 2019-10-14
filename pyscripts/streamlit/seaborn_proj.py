import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

'''
# First StreamLit App
'''

@st.cache
def fetch_data():
    return sns.load_dataset('mpg')

mpg = fetch_data()
option = st.sidebar.multiselect('Select origin: ', mpg['origin'].unique())

chart = sns.relplot(x="horsepower", y="mpg", hue="origin", size="weight",
            sizes=(40, 400), alpha=.5, palette="muted",
            height=6, data=mpg.query("origin == @option"))

st.pyplot(chart)