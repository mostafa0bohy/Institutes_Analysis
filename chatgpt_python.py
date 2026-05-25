import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

@st.cache_data(ttl=300)
def load_data():

    url = "PUT_YOUR_PUBLISHED_CSV_LINK_HERE"

    df = pd.read_csv(url)

    return df

df = load_data()

st.write(df)
