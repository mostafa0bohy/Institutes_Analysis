import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# إعداد الصفحة
st.set_page_config(layout="wide", page_title="داشبورد معهد خليل")
st.title("📊 لوحة تحكم أداء المبيعات والتسجيل - معهد خليل")

@st.cache_data
def load_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRTJXOApbP389e07-RnHJtOlC9iMwKdWo4xID1BfwPhoHisk1wl4aS1Gge5P0_2tkoI_IMuAfvaRMdR/pub?gid=1631853462&single=true&output=csv"
    df = pd.read_csv(url, header=1)
    df = df.iloc[1:] # تخطي الصف الفارغ
    df.columns = df.columns.str.strip() # تنظيف الأعمدة من أي مسافات زائدة
    
    # تحويل التاريخ
    df['التاريخ'] = pd.to_datetime(df['التاريخ'], errors='coerce')
    
    # فلترة: حذف التواريخ المستقبلية والصفوف الفارغة
    today = datetime.now()
    df = df[df['التاريخ'] <= today].dropna(subset=['التاريخ'])
    
    # تنظيف الأعمدة الرقمية
    for col in df.columns.drop('التاريخ'):
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    return df

try:
    df = load_data()
    last_row = df.iloc[-1]

    # 1. المربعات الرئيسية (KPIs)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("إجمالي المتقدمين", f"{int(last_row['المتقدمين الجدد (إجمالي)'])}")
    col2.metric("إجمالي الدافعين", f"{int(last_row['إجمالي عدد الكاش'] + last_row['إجمالي المقسطين'])}")
    col3.metric("نسبة الدفع الإجمالية", f"{last_row['نسبة الدفع من إجمالي المستهدفين']:.1f}%")
    col4.metric("الإعفاءات", f"{int(last_row['إعفاء مفعل (تم استخدام كوبون الإعفاء)'])}")

    # 2. الجراف
    st.subheader("اتجاه التسجيل اليومي")
    import plotly.express as px
    fig = px.line(df, x='التاريخ', y=['المتقدمين الجدد (يومي)', 'عدد الطلاب (اليومي)'], markers=True)
    st.plotly_chart(fig, use_container_width=True)

    # 3. تحليل البرامج
    st.subheader("أداء البرامج (نسبة التحويل)")
    prog_cols = [
        'نسبة الدفع من طلاب التأهيل الفقهي', 
        'نسبة الدفع من طلاب النووي', 
        'نسبة الدفع من طلاب ابن مالك', 
        'نسبة الدفع من طلاب التأهيلات', 
        'نسبة الدفع من طلاب بداية اللغوي'
    ]
    st.table(last_row[prog_cols])

except Exception as e:
    st.error(f"حدث خطأ أثناء عرض البيانات: {e}")
