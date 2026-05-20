import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(layout="wide")
st.title("📊 لوحة تحكم معهد خليل")

@st.cache_data
def load_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRTJXOApbP389e07-RnHJtOlC9iMwKdWo4xID1BfwPhoHisk1wl4aS1Gge5P0_2tkoI_IMuAfvaRMdR/pub?gid=1631853462&single=true&output=csv"
    # قراءة البيانات مع اعتبار الصف الثاني هو الرأس
    df = pd.read_csv(url, header=1)
    # تنظيف الأعمدة (إزالة مسافات)
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()
    
    # طباعة الأعمدة لنعرف الأسماء الحقيقية
    st.write("### قائمة الأعمدة المكتشفة في الملف:")
    st.write(df.columns.tolist())
    
    # عرض أول 5 صفوف لنتأكد من وجود بيانات
    st.write("### عينة من البيانات:")
    st.dataframe(df.head())

except Exception as e:
    st.error(f"حدث خطأ: {e}")
