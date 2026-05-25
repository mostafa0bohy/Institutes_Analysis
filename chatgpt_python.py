import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

@st.cache_data(ttl=300)
def load_data():

    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRmiO4XN9kssEddDdU8TuKtXOypsisNKiKejQ-DCDqcgmox6s7DV0zRJ6mxpLqpBA5XQr4JMgFE11_o/pub?output=tsv"

    df = pd.read_csv(url)

    return df

df = load_data()

st.write(df)
