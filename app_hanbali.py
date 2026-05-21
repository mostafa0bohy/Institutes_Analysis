import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# إعداد الصفحة
st.set_page_config(layout="wide", page_title="الداشبورد التفاعلي | التأهيل الفقهي", page_icon="📈")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 5% 5% 5% 10%;
        border-radius: 8px;
        border-right: 5px solid #1f77b4;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    h1, h2, h3 { color: #2c3e50; font-family: 'Arial', sans-serif; }
    hr { border-top: 2px solid #e0e0e0; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def fetch_and_process_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRmiO4XN9kssEddDdU8TuKtXOypsisNKiKejQ-DCDqcgmox6s7DV0zRJ6mxpLqpBA5XQr4JMgFE11_o/pub?gid=826428120&single=true&output=csv"
    
    # قراءة البيانات الخام
    raw_df = pd.read_csv(url, header=None)
    
    # تحديد صف العنوان
    start_row = raw_df[raw_df.apply(lambda row: "التاريخ" in str(row.values), axis=1)].index[0]
    df = raw_df.iloc[start_row:].reset_index(drop=True)
    df.columns = df.iloc[0]
    df = df.iloc[1:].reset_index(drop=True)
    
    # تنظيف أسماء الأعمدة من المسافات الزائدة لتسهيل الاستدعاء
    df.columns = df.columns.str.strip()

    # خريطة لربط الأسماء العربية بأسماء متغيرة قصيرة لسهولة الكود
    # استخدمنا الأسماء الدقيقة التي أرسلتها في رسالة سابقة
    col_mapping = {
        "التاريخ": "Date",
        "إجمالي المسجلين الجدد (أنشأ حسابًا على الموقع)": "Total_New",
        "مسجلين اليوم (أنشأ حسابًا على الموقع)": "Today_New",
        "المسجلين الجدد من قدامى البهوتي (لم يدرس ولم يدفع)": "Buhuti_Old",
        "المسجلين الجدد من طلاب البهوتي (طالب حالي يدرس البهوتي )": "Buhuti_Current",
        "المسجلين الجدد من طلاب البهوتي المتوقفين (درس ولم يكمل)": "Buhuti_Stopped",
        "المسجلين الجدد غير المسجلين في البهوتي": "Non_Buhuti"
    }

    # التحقق من وجود الأعمدة المطلوبة وتغيير أسمائها
    available_cols = {}
    for ar_col, en_col in col_mapping.items():
        # البحث عن عمود يطابق أو يحتوي على النص العربي
        matching_col = next((c for c in df.columns if ar_col in str(c)), None)
        if matching_col:
            available_cols[matching_col] = en_col
    
    df = df.rename(columns=available_cols)
    
    # الاحتفاظ فقط بالأعمدة التي تم التعرف عليها
    df = df[list(available_cols.values())]

    # تحويل التواريخ والفلترة
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
    df = df[df['Date'] <= pd.to_datetime(datetime.now().date())]

    # تحويل الأرقام بصرامة
    numeric_cols = [c for c in df.columns if c != 'Date']
    for col in numeric_cols:
        df[col] = df[col].astype(str).str.replace(r'[^\d.]', '', regex=True)
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    return df

try:
    df = fetch_and_process_data()

    if df.empty:
        st.warning("⚠️ لم يتم العثور على بيانات صالحة للعرض بعد التنظيف.")
    else:
        st.markdown("<h1 style='text-align: center; color: #1a237e; margin-bottom: 10px;'>📊 لوحة المؤشرات الاستراتيجية - التأهيل الفقهي</h1>", unsafe_allow_html=True)
        
        latest = df.iloc[-1]
        
        # التأكد من وجود الأعمدة قبل عرض KPIs
        col1, col2, col3, col4 = st.columns(4)
        if 'Total_New' in df.columns:
            col1.metric("إجمالي المسجلين (تراكمي)", f"{int(latest['Total_New']):,}")
        if 'Today_New' in df.columns:
            col2.metric("مسجلي اليوم الفعلي", f"{int(latest['Today_New']):,}")
        
        buhuti_total = 0
        if all(c in df.columns for c in ['Buhuti_Old', 'Buhuti_Current', 'Buhuti_Stopped']):
             buhuti_total = latest['Buhuti_Old'] + latest['Buhuti_Current'] + latest['Buhuti_Stopped']
             col3.metric("إجمالي المرتبطين بالبهوتي", f"{int(buhuti_total):,}")
        
        if 'Non_Buhuti' in df.columns:
             col4.metric("متقدمين من خارج البهوتي", f"{int(latest['Non_Buhuti']):,}")

        st.markdown("<br><hr><br>", unsafe_allow_html=True)

        col_chart1, col_chart2 = st.columns([2.5, 1.5])

        with col_chart1:
            st.markdown("### 📈 نمو التسجيل التراكمي وتصنيف المتقدمين")
            fig_area = go.Figure()
            # إضافة الـ Traces فقط إذا كان العمود موجوداً لتجنب الأخطاء
            if 'Non_Buhuti' in df.columns: fig_area.add_trace(go.Scatter(x=df['Date'], y=df['Non_Buhuti'], mode='lines', stackgroup='one', name='من خارج البهوتي', line=dict(color='#2ca02c')))
            if 'Buhuti_Old' in df.columns: fig_area.add_trace(go.Scatter(x=df['Date'], y=df['Buhuti_Old'], mode='lines', stackgroup='one', name='قدامى البهوتي', line=dict(color='#ff7f0e')))
            if 'Buhuti_Current' in df.columns: fig_area.add_trace(go.Scatter(x=df['Date'], y=df['Buhuti_Current'], mode='lines', stackgroup='one', name='طلاب البهوتي الحاليين', line=dict(color='#1f77b4')))
            if 'Buhuti_Stopped' in df.columns: fig_area.add_trace(go.Scatter(x=df['Date'], y=df['Buhuti_Stopped'], mode='lines', stackgroup='one', name='طلاب البهوتي المتوقفين', line=dict(color='#d62728')))

            fig_area.update_layout(hovermode='x unified', margin=dict(l=0, r=0, t=20, b=0), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig_area, use_container_width=True)

        with col_chart2:
            st.markdown("### 🎯 التوزيع النهائي للمسجلين الجدد")
            labels, values = [], []
            if 'Non_Buhuti' in df.columns: labels.append('من خارج البهوتي'); values.append(latest['Non_Buhuti'])
            if 'Buhuti_Old' in df.columns: labels.append('قدامى البهوتي'); values.append(latest['Buhuti_Old'])
            if 'Buhuti_Current' in df.columns: labels.append('حاليين بالبهوتي'); values.append(latest['Buhuti_Current'])
            if 'Buhuti_Stopped' in df.columns: labels.append('متوقفين بالبهوتي'); values.append(latest['Buhuti_Stopped'])
            
            if values:
                fig_pie = px.pie(values=values, names=labels, hole=0.45, color_discrete_sequence=['#2ca02c', '#ff7f0e', '#1f77b4', '#d62728'])
                fig_pie.update_traces(textposition='inside', textinfo='percent+value')
                fig_pie.update_layout(margin=dict(l=0, r=0, t=20, b=0), showlegend=True)
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("لا توجد بيانات كافية للرسم الدائري.")

        st.markdown("<br><hr><br>", unsafe_allow_html=True)

        if 'Today_New' in df.columns:
            st.markdown("### 📊 الأعداد اليومية للمسجلين الجدد")
            fig_bar = px.bar(df, x='Date', y='Today_New', text_auto=True)
            fig_bar.update_traces(marker_color='#1a237e', textposition='outside')
            fig_bar.update_layout(xaxis_title="التاريخ", yaxis_title="عدد المسجلين في اليوم", margin=dict(l=0, r=0, t=20, b=0), xaxis=dict(tickformat="%Y-%m-%d"))
            st.plotly_chart(fig_bar, use_container_width=True)

        with st.expander("📄 استعراض جدول البيانات التفصيلي"):
            st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"⚠️ نعتذر، حدث خطأ أثناء معالجة البيانات: {e}")
