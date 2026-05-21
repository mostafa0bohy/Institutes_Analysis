import streamlit as st
import pandas as pd
import plotly.express as px

# إعداد الصفحة
st.set_page_config(layout="wide", page_title="داشبورد التأهيل الفقهي", page_icon="📜")

# دالة تحميل وتنظيف البيانات
@st.cache_data
def load_final_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRmiO4XN9kssEddDdU8TuKtXOypsisNKiKejQ-DCDqcgmox6s7DV0zRJ6mxpLqpBA5XQr4JMgFE11_o/pub?gid=826428120&single=true&output=csv"
    
    # تحميل الخام
    raw_df = pd.read_csv(url, header=None)
    
    # تحديد صف العنوان
    start_row = raw_df[raw_df.apply(lambda row: "التاريخ" in str(row.values), axis=1)].index[0]
    df = raw_df.iloc[start_row:].reset_index(drop=True)
    df.columns = df.iloc[0]
    df = df.iloc[1:].reset_index(drop=True)
    
    # تنظيف الأعمدة (إزالة أي أعمدة فارغة أو غير مسماة)
    df = df.loc[:, df.columns.notna() & (df.columns != "")]
    
    # إزالة التكرار في الأسماء (إضافة لاحقة)
    cols = pd.Series(df.columns)
    for dup in cols[cols.duplicated()].unique():
        cols[cols[cols == dup].index.values.tolist()] = [f"{dup}_{i}" if i != 0 else dup for i in range(sum(cols == dup))]
    df.columns = cols
    
    # تحويل البيانات الرقمية
    for col in df.columns:
        if col != "التاريخ":
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0)
    
    # تحويل التاريخ
    df["التاريخ"] = pd.to_datetime(df["التاريخ"], errors='coerce')
    return df.dropna(subset=["التاريخ"])

# عرض الداشبورد
st.title("📊 لوحة تحكم التأهيل الفقهي - الدفعة 16")

try:
    df = load_final_data()
    
    # 1. عرض ملخص عام (KPIs)
    col1, col2, col3 = st.columns(3)
    latest = df.iloc[-1]
    col1.metric("إجمالي المسجلين الجدد", int(latest["إجمالي المسجلين الجدد (أنشأ حسابًا على الموقع)"]))
    col2.metric("مسجلي اليوم", int(latest["مسجلين اليوم (أنشأ حسابًا على الموقع)"]))
    col3.metric("نسبة الطلاب الجدد", f"{latest.get('نسبة المسجلين الجدد غير المسجلين في البهوتي ', 0):.1f}%")
    
    # 2. الرسم البياني للاتجاه
    st.subheader("📈 اتجاه التسجيل اليومي")
    fig = px.line(df, x="التاريخ", y="إجمالي المسجلين الجدد (أنشأ حسابًا على الموقع)")
    st.plotly_chart(fig, use_container_width=True)
    
    # 3. جدول البيانات المفصل
    st.subheader("📋 سجل البيانات التفصيلي")
    st.dataframe(df)

except Exception as e:
    st.error(f"حدث خطأ أثناء تحميل الداشبورد: {e}")
