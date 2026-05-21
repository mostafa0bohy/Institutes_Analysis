import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# إعداد الصفحة وتطبيق المظهر الاحترافي
st.set_page_config(layout="wide", page_title="داشبورد التأهيل الفقهي", page_icon="📜")

# الألوان المعتمدة للواجهة #006e7f (الأساسي) و #cce2e5 (الخلفيات الخفيفة)
st.markdown("""
    <style>
    .main { background-color: #fafafa; }
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #cce2e5;
        padding: 15px;
        border-radius: 8px;
        border-right: 5px solid #006e7f;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    div[data-testid="metric-container"] label {
        color: #555555 !important;
        font-weight: bold !important;
        font-size: 14px !important;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #006e7f !important;
        font-size: 28px !important;
    }
    h1, h2, h3 { color: #006e7f; font-family: 'Arial', sans-serif; }
    hr { border-top: 1px solid #cce2e5; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_clean_data():
    # الرابط الجديد الذي يحتوي على البيانات المنظمة
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRmiO4XN9kssEddDdU8TuKtXOypsisNKiKejQ-DCDqcgmox6s7DV0zRJ6mxpLqpBA5XQr4JMgFE11_o/pub?gid=593259252&single=true&output=csv"
    
    raw_df = pd.read_csv(url, header=None, dtype=str)
    
    start_row = None
    for i in range(len(raw_df)):
        if raw_df.iloc[i].astype(str).str.contains("التاريخ").any():
            start_row = i
            break
            
    if start_row is None:
        return pd.DataFrame() 
        
    row_cells = raw_df.iloc[start_row].astype(str).tolist()
    date_col_idx = next((idx for idx, val in enumerate(row_cells) if "التاريخ" in val), 0)
    
    df = raw_df.iloc[start_row+1:, date_col_idx:date_col_idx+11].copy()
    
    df.columns = [
        "Date", "Total_New", "Today_New", 
        "Buhuti_Old", "Buhuti_Old_Perc", 
        "Buhuti_Current", "Buhuti_Current_Perc", 
        "Buhuti_Stopped", "Buhuti_Stopped_Perc", 
        "Non_Buhuti", "Non_Buhuti_Perc"
    ]
    
    df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
    df = df.dropna(subset=["Date"])
    
    # فلترة التواريخ التي لم تأتِ بعد
    today = pd.to_datetime(datetime.now().date())
    df = df[df["Date"] <= today]
    
    for col in df.columns:
        if col != "Date":
            df[col] = df[col].astype(str).str.replace(r'[^\d.]', '', regex=True)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    df = df.sort_values("Date").reset_index(drop=True)
    return df

try:
    df = load_clean_data()
    
    if df.empty:
        st.error("❌ لم يتم العثور على بيانات صالحة. تأكد أن الشيت الجديد يحتوي على عمود باسم 'التاريخ'.")
    else:
        latest = df.iloc[-1]
        
        st.markdown("<h1 style='text-align: center; margin-bottom: 5px;'>📊 داشبورد برنامج التأهيل الفقهي الحنبلي</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666; margin-bottom: 30px;'>قراءة حية للبيانات ومؤشرات الأداء من الشيت المحدث</p>", unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("إجمالي الحسابات المنشأة", f"{int(latest['Total_New']):,}")
        col2.metric("مسجلي اليوم", f"{int(latest['Today_New']):,}")
        
        buhuti_total = latest['Buhuti_Old'] + latest['Buhuti_Current'] + latest['Buhuti_Stopped']
        col3.metric("إجمالي منتسبي البهوتي", f"{int(buhuti_total):,}")
        col4.metric("من خارج البهوتي", f"{int(latest['Non_Buhuti']):,}")
        
        st.markdown("<br><hr><br>", unsafe_allow_html=True)
        
        chart_col1, chart_col2 = st.columns([2.5, 1.5])
        
        with chart_col1:
            st.markdown("### 📈 النمو التراكمي وتصنيفات المتقدمين")
            fig_area = go.Figure()
            fig_area.add_trace(go.Scatter(x=df['Date'], y=df['Non_Buhuti'], mode='lines', stackgroup='one', name='من خارج البهوتي', line=dict(color='#006e7f')))
            fig_area.add_trace(go.Scatter(x=df['Date'], y=df['Buhuti_Old'], mode='lines', stackgroup='one', name='قدامى البهوتي', line=dict(color='#f39c12')))
            fig_area.add_trace(go.Scatter(x=df['Date'], y=df['Buhuti_Current'], mode='lines', stackgroup='one', name='طلاب حاليين', line=dict(color='#cce2e5')))
            fig_area.add_trace(go.Scatter(x=df['Date'], y=df['Buhuti_Stopped'], mode='lines', stackgroup='one', name='طلاب متوقفين', line=dict(color='#e74c3c')))
            
            fig_area.update_layout(
                hovermode='x unified',
                margin=dict(l=10, r=10, t=10, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_area, use_container_width=True)
            
        with chart_col2:
            st.markdown("### 🎯 التوزيع النسبي للدفعة")
            labels = ['خارج البهوتي', 'قدامى البهوتي', 'طلاب حاليين', 'طلاب متوقفين']
            values = [latest['Non_Buhuti'], latest['Buhuti_Old'], latest['Buhuti_Current'], latest['Buhuti_Stopped']]
            colors = ['#006e7f', '#f39c12', '#cce2e5', '#e74c3c']
            
            fig_pie = px.pie(values=values, names=labels, hole=0.5, color_discrete_sequence=colors)
            fig_pie.update_traces(textposition='inside', textinfo='percent+value', labels=labels)
            fig_pie.update_layout(margin=dict(l=10, r=10, t=10, b=10), showlegend=True)
            st.plotly_chart(fig_pie, use_container_width=True)
            
        st.markdown("<br><hr><br>", unsafe_allow_html=True)
        
        st.markdown("### 📊 حركية التسجيل اليومية (الأيام النشطة فقط)")
        df_daily = df[df["Today_New"] > 0] 
        
        fig_bar = px.bar(df_daily, x='Date', y='Today_New', text_auto=True)
        fig_bar.update_traces(marker_color='#006e7f', textposition='outside')
        fig_bar.update_layout(
            xaxis_title="التاريخ",
            yaxis_title="عدد المسجلين الجدد",
            margin=dict(l=10, r=10, t=20, b=10),
            xaxis=dict(tickformat="%Y-%m-%d"),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
        with st.expander("📋 استعراض السجل الرقمي المنظّم"):
            display_df = df.copy()
            display_df["Date"] = display_df["Date"].dt.strftime('%Y-%m-%d')
            display_df.columns = [
                "التاريخ", "إجمالي المسجلين", "مسجلين اليوم",
                "قدامى البهوتي", "نسبة القدامى",
                "طلاب حاليين", "نسبة الحاليين",
                "طلاب متوقفين", "نسبة المتوقفين",
                "من خارج البهوتي", "نسبة خارج البهوتي"
            ]
            st.dataframe(display_df.style.background_gradient(cmap='GnBu', subset=["إجمالي المسجلين", "مسجلين اليوم"]), use_container_width=True)

except Exception as e:
    st.error(f"⚠️ خطأ فني أثناء التشغيل: {e}")
