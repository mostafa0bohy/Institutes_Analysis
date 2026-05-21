import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("أداة فحص أسماء الأعمدة - شيت التأهيل الفقهي")

@st.cache_data
def load_and_inspect():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRmiO4XN9kssEddDdU8TuKtXOypsisNKiKejQ-DCDqcgmox6s7DV0zRJ6mxpLqpBA5XQr4JMgFE11_o/pub?gid=826428120&single=true&output=csv"
    
    # قراءة الملف الخام
    raw_df = pd.read_csv(url, header=None)
    
    # استخراج العناوين من الصفوف المحتملة (الصف الأول والثاني والثالث)
    header_row_0 = raw_df.iloc[0].astype(str).tolist()
    header_row_1 = raw_df.iloc[1].astype(str).tolist()
    header_row_2 = raw_df.iloc[2].astype(str).tolist()
    
    return header_row_0, header_row_1, header_row_2

try:
    h0, h1, h2 = load_and_inspect()
    
    st.write("### العناوين في الصف الأول (Index 0):")
    st.write(h0)
    
    st.write("### العناوين في الصف الثاني (Index 1):")
    st.write(h1)
    
    st.write("### العناوين في الصف الثالث (Index 2):")
    st.write(h2)

except Exception as e:
    st.error(f"حدث خطأ: {e}")
