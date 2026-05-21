import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# إعداد الصفحة
st.set_page_config(layout="wide", page_title="داشبورد التأهيل الفقهي الحنبلي", page_icon="📜")

@st.cache_data
def load_and_clean_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRmiO4XN9kssEddDdU8TuKtXOypsisNKiKejQ-DCDqcgmox6s7DV0zRJ6mxpLqpBA5XQr4JMgFE11_o/pub?gid=826428120&single=true&output=csv"
    
    # 1. قراءة البيانات بدون أي رؤوس أعمدة (header=None) لتجنب أخطاء التحليل
    df = pd.read_csv(url, header=None)
    
    # 2. البحث عن السطر الذي يحتوي كلمة "التاريخ" ليكون هو بداية البيانات
    # هذا يحل مشكلة الأسطر الفارغة في الأعلى
    start_row = 0
    for i in range(len(df)):
        if "التاريخ" in str(df.iloc[i].values):
            start_row = i
            break
    
    # إعادة بناء الجدول من تلك النقطة
    df = df.iloc[start_row:].reset_index(drop=True)
    df.columns = df.iloc[0] # تعيين أول سطر كعناوين
    df = df.iloc[1:].reset_index(drop=True) # حذف سطر العنوان المكرر
    
    # 3. حذف أي سطر فارغ تماماً من البيانات
    df = df.dropna(how='all')
    
    # 4. تحويل أعمدة الأرقام لتصبح صالحة للرسم (إزالة أي فواصل أو نصوص)
    for col in df.columns:
        if col != 'التاريخ':
            df[col] = df[col].astype(str).str.replace(r'[^\d.]', '', regex=True)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    return df

try:
    df = load_and_clean_data()
    
    st.write("### معاينة سريعة للبيانات التي تم تنظيفها:")
    st.dataframe(df.head())
    
    # رسم بياني بسيط للتأكد من نجاح العمل
    st.line_chart(df.select_dtypes(include=['number']))

except Exception as e:
    st.error(f"خطأ في معالجة البيانات: {e}")
