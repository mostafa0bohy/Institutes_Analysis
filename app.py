import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

# 1. إعداد الصفحة
st.set_page_config(layout="wide", page_title="داشبورد معهد خليل")
st.title("📊 لوحة تحكم أداء المبيعات والتسجيل - معهد خليل")

# 2. تحميل ومعالجة البيانات
@st.cache_data
def load_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRTJXOApbP389e07-RnHJtOlC9iMwKdWo4xID1BfwPhoHisk1wl4aS1Gge5P0_2tkoI_IMuAfvaRMdR/pub?gid=1631853462&single=true&output=csv"
    
    # قراءة الملف (الصف الثاني هو الرأس)
    df = pd.read_csv(url, header=1)
    df = df.iloc[1:] # تخطي الصف الفارغ
    df.columns = df.columns.str.strip()
    
    # تحويل التاريخ ومعالجة الأخطاء
    df['التاريخ'] = pd.to_datetime(df['التاريخ'], errors='coerce')
    
    # فلترة: حذف التواريخ المستقبلية والصفوف الفارغة
    today = datetime.now()
    df = df[df['التاريخ'] <= today].dropna(subset=['التاريخ'])
    
    # تنظيف البيانات الرقمية (استبدال الأخطاء بصفر)
    cols_to_numeric = df.columns.drop('التاريخ')
    for col in cols_to_numeric:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    return df
st.write("قائمة الأعمدة الحقيقية:", df.columns.tolist())
try:
    df = load_data()

    # 3. عرض المؤشرات الرئيسية (KPIs)
    last_row = df.iloc[-1]
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("إجمالي المتقدمين", f"{int(last_row['المتقدمين الجدد (إجمالي)'])}")
    col2.metric("الدافعون (كاش + أقساط)", f"{int(last_row['إجمالي عدد الكاش'] + last_row['إجمالي المقسطين'])}")
    col3.metric("نسبة الدفع الإجمالية", f"{last_row['نسبة الدفع من إجمالي المستهدفين']:.1f}%")
    col4.metric("الإعفاءات", f"{int(last_row['إعفاء مفعل (تم استخدام كوبون الإعفاء)'])}")

    # 4. الرسوم البيانية
    st.subheader("اتجاه التسجيل اليومي")
    fig = px.line(df, x='التاريخ', y=['المتقدمين الجدد (يومي)', 'عدد الطلاب (اليومي)'], 
                  markers=True, template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    # 5. تحليل البرامج (جدول)
    st.subheader("أداء البرامج (آخر تحديث)")
    prog_cols = [col for col in df.columns if 'نسبة الدفع من طلاب' in col]
    prog_data = df[prog_cols].tail(1).T
    prog_data.columns = ['نسبة التحويل']
    st.table(prog_data)

    # 6. قسم التوصيات
    st.subheader("💡 توصيات للإدارة")
    if last_row['نسبة الدفع من الجدد'] < 10:
        st.warning("⚠️ تنبيه: معدل التحويل من المتقدمين الجدد يحتاج لتدخل تسويقي.")
    else:
        st.success("✅ أداء المتقدمين الجدد مستقر.")

except Exception as e:
    st.error(f"حدث خطأ في تحميل البيانات: {e}")
