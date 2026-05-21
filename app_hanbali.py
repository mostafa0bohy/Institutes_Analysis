import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# إعداد الصفحة
st.set_page_config(layout="wide", page_title="داشبورد التأهيل الفقهي", page_icon="📜")

@st.cache_data
def load_and_clean_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRmiO4XN9kssEddDdU8TuKtXOypsisNKiKejQ-DCDqcgmox6s7DV0zRJ6mxpLqpBA5XQr4JMgFE11_o/pub?gid=826428120&single=true&output=csv"
    
    raw_df = pd.read_csv(url, header=None)
    
    # تحديد صف العنوان
    start_row = raw_df[raw_df.apply(lambda row: "التاريخ" in str(row.values), axis=1)].index[0]
    df = raw_df.iloc[start_row:].reset_index(drop=True)
    df.columns = df.iloc[0]
    df = df.iloc[1:].reset_index(drop=True)
    
    # تنظيف الأعمدة (إزالة أي أعمدة فارغة أو غير مسماة)
    df = df.loc[:, df.columns.notna() & (df.columns != "")]
    
    # تحويل الأرقام (هذا الجزء يحل مشكلة الأرقام غير الظاهرة)
    for col in df.columns:
        if col != "التاريخ":
            # تنظيف النصوص وتحويلها لأرقام
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0)
    
    # تحويل التاريخ
    df["التاريخ"] = pd.to_datetime(df["التاريخ"], errors='coerce')
    df = df.dropna(subset=["التاريخ"])
    
    # --- الفلترة الزمنية (حل مشكلة التواريخ المستقبلية) ---
    today = datetime.now()
    df = df[df["التاريخ"] <= today]
    
    return df

try:
    df = load_and_clean_data()
    
    st.title("📊 لوحة تحكم التأهيل الفقهي - الدفعة 16")
    
    # عرض KPIs
    latest = df.iloc[-1]
    col1, col2, col3 = st.columns(3)
    # استخدام تنسيق f-string مع الفواصل للأرقام لتظهر بوضوح
    col1.metric("إجمالي المسجلين الجدد", f"{int(latest['إجمالي المسجلين الجدد (أنشأ حسابًا على الموقع)']):,}")
    col2.metric("مسجلي اليوم", f"{int(latest['مسجلين اليوم (أنشأ حسابًا على الموقع)']):,}")
    
    # الجراف
    st.subheader("📈 اتجاه التسجيل اليومي")
    fig = px.line(df, x="التاريخ", y="إجمالي المسجلين الجدد (أنشأ حسابًا على الموقع)")
    # تعديل الجراف ليظهر الأرقام بوضوح
    fig.update_traces(mode="lines+markers")
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📋 سجل البيانات")
    st.dataframe(df.style.format({"إجمالي المسجلين الجدد (أنشأ حسابًا على الموقع)": "{:,.0f}"}))

except Exception as e:
    st.error(f"خطأ أثناء العرض: {e}")
