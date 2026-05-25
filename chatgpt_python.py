import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Institute Dashboard",
    layout="wide"
)

# ======================================================
# LOAD DATA
# ======================================================

@st.cache_data(ttl=300)
def load_data():

    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRmiO4XN9kssEddDdU8TuKtXOypsisNKiKejQ-DCDqcgmox6s7DV0zRJ6mxpLqpBA5XQr4JMgFE11_o/pub?output=tsv"

    df = pd.read_csv(
        url,
        sep="\t"
    )

    return df

df = load_data()

# ======================================================
# CLEAN
# ======================================================

df.columns = df.columns.str.strip()

# ======================================================
# TITLE
# ======================================================

st.title("📊 Institute Dashboard")

st.markdown("---")

# ======================================================
# KPIs
# ======================================================

students_count = len(df)

col1, col2 = st.columns(2)

col1.metric(
    "عدد الصفوف",
    students_count
)

col2.metric(
    "عدد الأعمدة",
    len(df.columns)
)

# ======================================================
# DATA
# ======================================================

st.subheader("البيانات")

st.dataframe(
    df,
    use_container_width=True
)

# ======================================================
# OPTIONAL CHART
# ======================================================

if len(df.columns) >= 2:

    first_col = df.columns[1]

    chart_df = (
        df[first_col]
        .value_counts()
        .head(10)
        .reset_index()
    )

    chart_df.columns = [
        first_col,
        "count"
    ]

    fig = px.bar(
        chart_df,
        x=first_col,
        y="count",
        text_auto=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
