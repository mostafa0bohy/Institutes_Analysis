import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go

# 1. إعدادات الداشبورد
st.set_page_config(layout="wide", page_title="داشبورد التأهيل الفقهي - لايف")

# رابط الـ Web App الخاص بك
API_URL = "https://script.google.com/macros/s/AKfycbzeWqeaOCcOmNMxA7nNmsLwIGnLGJZWY5yRC2zVhsIzH3DOuI3d4KORbQ7aEAxt_V7I/exec"

# 2. دالة جلب البيانات (تحديث تلقائي كل 5 دقائق)
@st.cache_data(ttl=300)
def fetch_live_data():
    response = requests.get(API_URL)
    data = response.json()
    
    # تحويل البيانات إلى DataFrame
    # نفترض أن الصف الأول هو العناوين
    df = pd.DataFrame(data[1:], columns=data[0])
    
    # تنظيف الأسماء (إزالة الفراغات)
    df.columns = df.columns.str.strip()
    
    # تحويل الأعمدة الرقمية (من العمود الثاني للنهاية)
    # نستخدم حلقة للتأكد من أن كل عمود هو عبارة عن Series حقيقية
    for col in df.columns[1:]:
        # نحول القيم إلى نصوص أولاً ثم نزيل أي رموز غير رقمية
        df[col] = df[col].astype(str).str.replace(r'[^\d.]', '', regex=True)
        # ثم نحولها لأرقام
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
    return df

try:
    df = fetch_live_data()
    latest = df.iloc[-1]

    st.title("📊 داشبورد التأهيل الفقهي (تحديث لحظي)")

    # 3. المؤشرات الرئيسية (KPIs)
    col1, col2, col3, col4 = st.columns(4)
    # ملاحظة: تم ضبط الأرقام بناءً على ترتيب أعمدة الشيت التي وصلتني
    col1.metric("إجمالي المسجلين", f"{int(latest[1]):,}")
    col2.metric("مسجل اليوم", f"{int(latest[2]):,}")
    # جمع بيانات البهوتي (حسب الترتيب في شيتك)
    buhuti_total = latest[3] + latest[5] + latest[7]
    col3.metric("إجمالي منتسبي البهوتي", f"{int(buhuti_total):,}")
    col4.metric("من خارج البهوتي", f"{int(latest[9]):,}")

    # 4. الرسوم البيانية
    st.markdown("---")
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("📈 نمو التسجيل التراكمي")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.iloc[:,0], y=df.iloc[:,9], name='خارج البهوتي', stackgroup='one'))
        fig.add_trace(go.Scatter(x=df.iloc[:,0], y=df.iloc[:,3], name='قدامى البهوتي', stackgroup='one'))
        fig.add_trace(go.Scatter(x=df.iloc[:,0], y=df.iloc[:,5], name='حاليين', stackgroup='one'))
        fig.add_trace(go.Scatter(x=df.iloc[:,0], y=df.iloc[:,7], name='متوقفين', stackgroup='one'))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("🎯 توزيع الدفعة")
        fig_pie = px.pie(values=[latest[9], latest[3], latest[5], latest[7]], 
                         names=['خارج البهوتي', 'قدامى', 'حاليين', 'متوقفين'],
                         hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

except Exception as e:
    st.error("⚠️ فشل في تحميل البيانات. تأكد من أن Google Apps Script يعمل بشكل صحيح.")
    st.write(e)
