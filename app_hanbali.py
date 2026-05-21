import streamlit as st
import pandas as pd

# إعداد الصفحة
st.set_page_config(layout="wide")
st.title("لوحة تحكم التأهيل الفقهي - النسخة المستقرة")

@st.cache_data
def load_data_robust():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRmiO4XN9kssEddDdU8TuKtXOypsisNKiKejQ-DCDqcgmox6s7DV0zRJ6mxpLqpBA5XQr4JMgFE11_o/pub?gid=826428120&single=true&output=csv"
    
    # 1. قراءة الملف بدون رؤوس أعمدة أولية
    raw_df = pd.read_csv(url, header=None)
    
    # 2. البحث عن الصف الذي يحتوي على "التاريخ" ليكون هو الرأس (Header)
    header_idx = None
    for i in range(len(raw_df)):
        if "التاريخ" in str(raw_df.iloc[i].values):
            header_idx = i
            break
    
    if header_idx is None:
        return None, "لم يتم العثور على عمود 'التاريخ'!"
    
    # 3. إعادة تشكيل الجدول بناءً على الصف المكتشف
    df = raw_df.iloc[header_idx:].reset_index(drop=True)
    df.columns = df.iloc[0]
    df = df.iloc[1:].reset_index(drop=True)
    
    # 4. تنظيف الأعمدة (حذف الأعمدة الفارغة تماماً)
    df = df.dropna(axis=1, how='all')
    
    return df, None

# عرض النتائج
df, error = load_data_robust()

if error:
    st.error(error)
else:
    st.success("تم تحميل البيانات بنجاح!")
    st.write("### معاينة أول 10 صفوف من البيانات:")
    st.dataframe(df.head(10))
    
    st.write("### أسماء الأعمدة المكتشفة:")
    st.write(df.columns.tolist())
