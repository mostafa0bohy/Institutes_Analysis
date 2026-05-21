import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="داشبورد التأهيل الفقهي - لايف")

# رابط الـ Web App الذي حصلت عليه من خطوة Google Apps Script
API_URL = "https://script.google.com/macros/s/AKfycbzeWqeaOCcOmNMxA7nNmsLwIGnLGJZWY5yRC2zVhsIzH3DOuI3d4KORbQ7aEAxt_V7I/exec"

@st.cache_data(ttl=300) # تحديث البيانات تلقائياً كل 5 دقائق
def fetch_live_data():
    response = requests.get(API_URL)
    data = response.json()
    df = pd.DataFrame(data[1:], columns=data[0])
    # تنظيف البيانات
    df.iloc[:, 1:] = df.iloc[:, 1:].apply(pd.to_numeric, errors='coerce').fillna(0)
    return df

try:
    df = fetch_live_data()
    latest = df.iloc[-1]

    st.title("📊 داشبورد التأهيل الفقهي (تحديث لحظي)")

    # المؤشرات الرئيسية
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("إجمالي الحسابات", f"{int(latest[1]):,}")
    col2.metric("مسجلي اليوم", f"{int(latest[2]):,}")
    col3.metric("مرتبطي البهوتي", f"{int(latest[3] + latest[5] + latest[7]):,}")
    col4.metric("خارج البهوتي", f"{int(latest[9]):,}")

    # الرسم البياني
    st.subheader("نمو التسجيل التراكمي")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.iloc[:,0], y=df.iloc[:,9], name='خارج البهوتي', stackgroup='one'))
    fig.add_trace(go.Scatter(x=df.iloc[:,0], y=df.iloc[:,3], name='قدامى البهوتي', stackgroup='one'))
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error("فشل الاتصال بالشيت. تأكد من نشر الـ Web App بشكل صحيح.")
