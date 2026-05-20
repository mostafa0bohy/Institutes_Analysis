import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(layout="wide")

@st.cache_data
def load_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRTJXOApbP389e07-RnHJtOlC9iMwKdWo4xID1BfwPhoHisk1wl4aS1Gge5P0_2tkoI_IMuAfvaRMdR/pub?gid=1631853462&single=true&output=csv"
    
    # تحميل البيانات بدون رؤوس أعمدة أولاً لتجنب الأخطاء
    raw_df = pd.read_csv(url, header=None)
    
    # نحدد الصف الثاني (index 1) كرؤوس أعمدة
    raw_df.columns = raw_df.iloc[1].str.strip()
    # نأخذ البيانات من الصف الرابع فصاعداً (index 3)
    df = raw_df.iloc[3:].reset_index(drop=True)
    
    # تنظيف الأسماء (إزالة السطور الجديدة)
    df.columns = df.columns.str.replace('\n', ' ', regex=True).str.strip()
    
    # تحويل التاريخ
    df['التاريخ'] = pd.to_datetime(df['التاريخ'], errors='coerce')
    
    # تنظيف الأرقام
    for col in df.columns.drop('التاريخ'):
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
    return df

try:
    df = load_data()
    
    # فلترة التواريخ المستقبلية
    df = df[df['التاريخ'] <= datetime.now()]
    
    last_row = df.iloc[-1]

    # عرض البيانات
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("المتقدمون الجدد", int(last_row['المتقدمين الجدد (إجمالي)']))
    col2.metric("الدافعون", int(last_row['إجمالي عدد الكاش'] + last_row['إجمالي المقسطين']))
    col3.metric("نسبة الدفع", f"{last_row['نسبة الدفع من إجمالي المستهدفين']:.1f}%")
    col4.metric("الإعفاءات", int(last_row['إعفاء مفعل (تم استخدام كوبون الإعفاء)']))

    # الجراف
    st.subheader("اتجاه التسجيل اليومي")
    fig = px.line(df, x='التاريخ', y=['المتقدمين الجدد (يومي)', 'عدد الطلاب (اليومي)'])
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"خطأ: {e}")
