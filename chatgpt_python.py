import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ======================================================
# PAGE CONFIG
# ======================================================

st.set_page_config(
    page_title="Institute Dashboard",
    page_icon="📊",
    layout="wide"
)

# ======================================================
# CUSTOM STYLE
# ======================================================

st.markdown("""
<style>

.main {
    background-color: #f5f7fa;
}

h1,h2,h3 {
    color: #0f172a;
}

div[data-testid="stMetric"] {
    background-color: white;
    border-radius: 14px;
    padding: 15px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

div[data-testid="stMetricValue"] {
    color: #059669;
    font-size: 30px;
    font-weight: bold;
}

div[data-testid="stMetricLabel"] {
    font-size: 15px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

# ======================================================
# LOAD DATA
# ======================================================

import requests
from io import StringIO

@st.cache_data(ttl=300)
def load_data():

    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRmiO4XN9kssEddDdU8TuKtXOypsisNKiKejQ-DCDqcgmox6s7DV0zRJ6mxpLqpBA5XQr4JMgFE11_o/pub?gid=826428120&single=true&output=csv"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        url,
        headers=headers
    )

    response.raise_for_status()

    csv_data = StringIO(response.text)

    df = pd.read_csv(csv_data)

    return df

# ======================================================
# CLEAN DATA
# ======================================================

# توحيد أسماء الأعمدة
df.columns = df.columns.str.strip()

# الأعمدة المتوقعة
email_col = None
country_col = None
amount_col = None
date_col = None
payment_col = None

for col in df.columns:

    c = col.lower()

    if "email" in c or "الإيميل" in c:
        email_col = col

    if "country" in c or "الدولة" in c:
        country_col = col

    if "المبلغ" in c or "total" in c:
        amount_col = col

    if "التاريخ" in c or "created" in c:
        date_col = col

    if "payment" in c or "الدفع" in c:
        payment_col = col

# تنظيف التاريخ
if date_col:
    df[date_col] = pd.to_datetime(
        df[date_col],
        errors='coerce'
    )

# تنظيف المبالغ
if amount_col:
    df[amount_col] = (
        df[amount_col]
        .astype(str)
        .str.replace(",", "")
    )

    df[amount_col] = pd.to_numeric(
        df[amount_col],
        errors='coerce'
    ).fillna(0)

# ======================================================
# SIDEBAR FILTERS
# ======================================================

st.sidebar.header("Filters")

if country_col:

    countries = sorted(
        df[country_col]
        .dropna()
        .astype(str)
        .unique()
    )

    selected_country = st.sidebar.selectbox(
        "اختر الدولة",
        ["الكل"] + countries
    )

    if selected_country != "الكل":
        df = df[
            df[country_col] == selected_country
        ]

# ======================================================
# KPIs
# ======================================================

students_count = (
    df[email_col].nunique()
    if email_col else 0
)

total_revenue = (
    df[amount_col].sum()
    if amount_col else 0
)

countries_count = (
    df[country_col].nunique()
    if country_col else 0
)

payments_count = len(df)

# ======================================================
# HEADER
# ======================================================

st.title("📊 Interactive Institute Dashboard")

st.markdown("---")

# ======================================================
# KPI ROW
# ======================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "عدد الطلاب",
    f"{students_count:,}"
)

col2.metric(
    "إجمالي الإيرادات",
    f"{total_revenue:,.0f}"
)

col3.metric(
    "عدد الدول",
    f"{countries_count:,}"
)

col4.metric(
    "عدد العمليات",
    f"{payments_count:,}"
)

st.markdown("---")

# ======================================================
# CHARTS
# ======================================================

tab1, tab2, tab3 = st.tabs([
    "🌍 الدول",
    "💳 المدفوعات",
    "📈 الإيرادات"
])

# ======================================================
# COUNTRY TAB
# ======================================================

with tab1:

    st.subheader("الطلاب حسب الدولة")

    if country_col:

        country_df = (
            df.groupby(country_col)
            .size()
            .reset_index(name='count')
            .sort_values(
                by='count',
                ascending=False
            )
        )

        fig_country = px.bar(
            country_df,
            x=country_col,
            y='count',
            text_auto=True
        )

        fig_country.update_layout(
            height=500
        )

        st.plotly_chart(
            fig_country,
            use_container_width=True
        )

# ======================================================
# PAYMENT TAB
# ======================================================

with tab2:

    st.subheader("طرق الدفع")

    if payment_col:

        payment_df = (
            df.groupby(payment_col)
            .size()
            .reset_index(name='count')
        )

        fig_payment = px.pie(
            payment_df,
            names=payment_col,
            values='count',
            hole=0.5
        )

        fig_payment.update_layout(
            height=500
        )

        st.plotly_chart(
            fig_payment,
            use_container_width=True
        )

# ======================================================
# REVENUE TAB
# ======================================================

with tab3:

    st.subheader("الإيرادات عبر الزمن")

    if date_col and amount_col:

        revenue_df = (
            df.groupby(date_col)[amount_col]
            .sum()
            .reset_index()
        )

        revenue_df = revenue_df.sort_values(
            by=date_col
        )

        fig_rev = px.line(
            revenue_df,
            x=date_col,
            y=amount_col,
            markers=True
        )

        fig_rev.update_layout(
            height=500
        )

        st.plotly_chart(
            fig_rev,
            use_container_width=True
        )

# ======================================================
# RAW DATA
# ======================================================

with st.expander("📄 عرض البيانات الخام"):

    st.dataframe(
        df,
        use_container_width=True
    )

# ======================================================
# FOOTER
# ======================================================

st.markdown("---")

st.caption("Live Dashboard connected to Google Sheets")
