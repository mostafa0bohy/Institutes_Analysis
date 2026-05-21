import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# إعداد الصفحة لتكون واسعة وتغيير العنوان
st.set_page_config(layout="wide", page_title="الداشبورد التفاعلي | التأهيل الفقهي", page_icon="📈")

# إضافة CSS لتحسين المظهر العام (UI Upgrade)
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
    raw_df = pd.read_csv(url, header=None)

    # 1. البحث الدقيق عن صف "التاريخ" والعمود الخاص به (حل ذكي لمنع الأخطاء)
    mask = raw_df.apply(lambda row: row.astype(str).str.contains("التاريخ").any(), axis=1)
    header_idx = raw_df[mask].index[0]
    
    row_data = raw_df.iloc[header_idx].astype(str).tolist()
    date_col_idx = next(i for i, val in enumerate(row_data) if "التاريخ" in val)

    # 2. استخراج الـ 11 عمود المطلوبة فقط بدءاً من عمود التاريخ
    df = raw_df.iloc[header_idx+1:, date_col_idx:date_col_idx+11].copy()

    # 3. توحيد أسماء الأعمدة داخلياً برمجياً لضمان عدم وجود أخطاء في العرض
    cols = [
        "Date", "Total_New", "Today_New", 
        "Buhuti_Old", "Buhuti_Old_Perc", 
        "Buhuti_Current", "Buhuti_Current_Perc", 
        "Buhuti_Stopped", "Buhuti_Stopped_Perc", 
        "Non_Buhuti", "Non_Buhuti_Perc"
    ]
    df.columns = cols

    # 4. تنظيف التواريخ وإزالة التواريخ المستقبلية
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
    df = df[df['Date'] <= pd.to_datetime(datetime.now().date())]

    # 5. تنظيف الأرقام بصرامة (إزالة أي فواصل، أو %، أو مسافات خفية)
    for col in cols[1:]:
        df[col] = df[col].astype(str).str.replace(r'[%,\s]', '', regex=True)
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    return df

try:
    df = fetch_and_process_data()

    # العنوان الرئيسي
    st.markdown("<h1 style='text-align: center; color: #1a237e; margin-bottom: 10px;'>📊 لوحة المؤشرات الاستراتيجية - التأهيل الفقهي</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #7f8c8d; margin-bottom: 40px;'>متابعة حية وتحليل دقيق لبيانات التسجيل بالدفعة 16 وعلاقتها بمعهد البهوتي</p>", unsafe_allow_html=True)

    # ------------------- قسم المؤشرات السريعة (KPIs) -------------------
    latest = df.iloc[-1]
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("إجمالي المسجلين (تراكمي)", f"{int(latest['Total_New']):,}")
    col2.metric("مسجلي اليوم الفعلي", f"{int(latest['Today_New']):,}")
    col3.metric("إجمالي المرتبطين بالبهوتي", f"{int(latest['Buhuti_Old'] + latest['Buhuti_Current'] + latest['Buhuti_Stopped']):,}")
    col4.metric("متقدمين من خارج البهوتي", f"{int(latest['Non_Buhuti']):,}")

    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    # ------------------- قسم الرسوم البيانية التراكمية والنسب -------------------
    col_chart1, col_chart2 = st.columns([2.5, 1.5])

    with col_chart1:
        st.markdown("### 📈 نمو التسجيل التراكمي وتصنيف المتقدمين")
        # رسم بياني تراكمي متراكب (Stacked Area)
        fig_area = go.Figure()
        fig_area.add_trace(go.Scatter(x=df['Date'], y=df['Non_Buhuti'], mode='lines', stackgroup='one', name='من خارج البهوتي', line=dict(color='#2ca02c')))
        fig_area.add_trace(go.Scatter(x=df['Date'], y=df['Buhuti_Old'], mode='lines', stackgroup='one', name='قدامى البهوتي', line=dict(color='#ff7f0e')))
        fig_area.add_trace(go.Scatter(x=df['Date'], y=df['Buhuti_Current'], mode='lines', stackgroup='one', name='طلاب البهوتي الحاليين', line=dict(color='#1f77b4')))
        fig_area.add_trace(go.Scatter(x=df['Date'], y=df['Buhuti_Stopped'], mode='lines', stackgroup='one', name='طلاب البهوتي المتوقفين', line=dict(color='#d62728')))

        fig_area.update_layout(
            hovermode='x unified', 
            margin=dict(l=0, r=0, t=20, b=0), 
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis_title="التاريخ", yaxis_title="عدد المسجلين التراكمي"
        )
        st.plotly_chart(fig_area, use_container_width=True)

    with col_chart2:
        st.markdown("### 🎯 التوزيع النهائي للمسجلين الجدد")
        # رسم دائري مفرغ (Donut Chart)
        labels = ['من خارج البهوتي', 'قدامى البهوتي', 'حاليين بالبهوتي', 'متوقفين بالبهوتي']
        values = [latest['Non_Buhuti'], latest['Buhuti_Old'], latest['Buhuti_Current'], latest['Buhuti_Stopped']]
        colors = ['#2ca02c', '#ff7f0e', '#1f77b4', '#d62728']
        
        fig_pie = px.pie(values=values, names=labels, hole=0.45, color_discrete_sequence=colors)
        fig_pie.update_traces(textposition='inside', textinfo='percent+value')
        fig_pie.update_layout(margin=dict(l=0, r=0, t=20, b=0), showlegend=True)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    # ------------------- قسم رسم الأعداد اليومية -------------------
    st.markdown("### 📊 الأعداد اليومية للمسجلين الجدد")
    fig_bar = px.bar(df, x='Date', y='Today_New', text_auto=True)
    fig_bar.update_traces(marker_color='#1a237e', textposition='outside')
    fig_bar.update_layout(
        xaxis_title="التاريخ", 
        yaxis_title="عدد المسجلين في اليوم",
        margin=dict(l=0, r=0, t=20, b=0),
        xaxis=dict(tickformat="%Y-%m-%d")
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------- جدول البيانات التفصيلي -------------------
    with st.expander("📄 استعراض جدول البيانات التفصيلي (للتصدير أو المراجعة)"):
        display_df = df.copy()
        # إعادة تسمية الأعمدة للعربية لسهولة القراءة
        display_df.columns = [
            "التاريخ", "إجمالي المسجلين", "تسجيل اليوم", 
            "قدامى البهوتي (عدد)", "قدامى (%)", 
            "حاليين (عدد)", "حاليين (%)", 
            "متوقفين (عدد)", "متوقفين (%)", 
            "من الخارج (عدد)", "من الخارج (%)"
        ]
        # تلوين الخلفية بشكل خفيف
        st.dataframe(display_df.style.background_gradient(cmap='Blues', subset=["تسجيل اليوم", "إجمالي المسجلين"]), use_container_width=True)

except Exception as e:
    st.error(f"⚠️ نعتذر، حدث خطأ أثناء معالجة البيانات: {e}")
