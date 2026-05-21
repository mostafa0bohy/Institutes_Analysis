import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# إعداد الصفحة وتطبيق المظهر الاحترافي الموحد
st.set_page_config(layout="wide", page_title="داشبورد التأهيل الفقهي", page_icon="📜")

# الألوان المعتمدة للواجهة #006e7f (الأساسي) و #cce2e5 (الخلفيات الخفيفة)
st.markdown("""
    <style>
    .main { background-color: #fafafa; }
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
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
def load_perfect_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRmiO4XN9kssEddDdU8TuKtXOypsisNKiKejQ-DCDqcgmox6s7DV0zRJ6mxpLqpBA5XQr4JMgFE11_o/pub?gid=826428120&single=true&output=csv"
    
    # قراءة البيانات بالكامل كنصوص لمنع تفسيرها الخاطئ أثناء التحميل
    raw_df = pd.read_csv(url, header=None, dtype=str)
    
    # البحث عن السطر الذي يبدأ بـ "التاريخ"
    start_row = None
    for i in range(len(raw_df)):
        if raw_df.iloc[i].astype(str).str.contains("التاريخ").any():
            start_row = i
            break
            
    if start_row is None:
        return pd.DataFrame()

    # تحديد موقع عمود التاريخ بالضبط داخل هذا السطر
    row_cells = raw_df.iloc[start_row].astype(str).tolist()
    date_col_idx = next(idx for idx, val in enumerate(row_cells) if "التاريخ" in val)

    # قطع الـ 11 عمود المتتالية فقط بناءً على موقع عمود التاريخ الثابت
    df = raw_df.iloc[start_row+1:, date_col_idx:date_col_idx+11].copy()
    
    # تسمية الأعمدة برمجياً بالترتيب العددي الصارم لحل مشكلة الأسماء نهائياً
    df.columns = [
        "التاريخ", "إجمالي المسجلين", "تسجيل اليوم",
        "قدامى البهوتي", "نسبة القدامى",
        "طلاب حاليين", "نسبة الحاليين",
        "طلاب متوقفين", "نسبة المتوقفيين",
        "من خارج البهوتي", "نسبة الخارج"
    ]
    
    # تنظيف وتجهيز عمود التاريخ
    df["التاريخ"] = df["التاريخ"].astype(str).str.strip()
    df["التاريخ"] = pd.to_datetime(df["التاريخ"], errors='coerce')
    df = df.dropna(subset=["التاريخ"])
    
    # فلترة التواريخ المستقبلية (حتى تاريخ اليوم فقط)
    today_date = pd.to_datetime(datetime.now().date())
    df = df[df["التاريخ"] <= today_date]
    
    # تحويل كافة الأعمدة الأخرى إلى أرقام حقيقية بعد تنظيف الفواصل والرموز والمسافات
    for col in df.columns:
        if col != "التاريخ":
            df[col] = df[col].astype(str).str.replace(r'[^\d.]', '', regex=True)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    # ترتيب البيانات تصاعدياً حسب التاريخ لضمان سلامة الرسم البياني التراكمي
    df = df.sort_values("التاريخ").reset_index(drop=True)
    return df

try:
    df = load_perfect_data()
    
    if df.empty:
        st.error("❌ فشل الكود في تحديد مكان جدول البيانات داخل ملف الشيت. يرجى مراجعة صف الرأس.")
    else:
        # واجهة الداشبورد الاحترافية
        st.markdown("<h1 style='text-align: center; margin-bottom: 5px;'>📊 لوحة متابعة تسجيل الدفعة 16</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666; margin-bottom: 30px;'>تحليل إحصائي واستراتيجي لربط المتقدمين بمعهد البهوتي</p>", unsafe_allow_html=True)
        
        # جلب أحدث صف يحتوي على بيانات فعلية
        latest = df.iloc[-1]
        
        # صف المؤشرات الرئيسية (KPIs)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("إجمالي الحسابات المنشأة", f"{int(latest['إجمالي المسجلين']):,}")
        col2.metric("مسجلي اليوم", f"{int(latest['تسجيل اليوم']):,}")
        
        buhuti_total = latest['قدامى البهوتي'] + latest['طلاب حاليين'] + latest['طلاب متوقفين']
        col3.metric("إجمالي منتسبي البهوتي", f"{int(buhuti_total):,}")
        col4.metric("متقدمين مستقلين (خارج البهوتي)", f"{int(latest['من خارج البهوتي']):,}")
        
        st.markdown("<br><hr><br>", unsafe_allow_html=True)
        
        # الصف الثاني: الرسوم البيانية الاستراتيجية
        chart_col1, chart_col2 = st.columns([2.5, 1.5])
        
        with chart_col1:
            st.markdown("### 📈 النمو التراكمي وتصنيفات معهد البهوتي")
            fig_area = go.Figure()
            # رسم بياني مساحي متراكم يعتمد على الأعداد التراكمية الحقيقية لكل تصنيف
            fig_area.add_trace(go.Scatter(x=df['التاريخ'], y=df['من خارج البهوتي'], mode='lines', stackgroup='one', name='من خارج البهوتي', line=dict(color='#006e7f')))
            fig_area.add_trace(go.Scatter(x=df['التاريخ'], y=df['قدامى البهوتي'], mode='lines', stackgroup='one', name='قدامى البهوتي', line=dict(color='#ff9f43')))
            fig_area.add_trace(go.Scatter(x=df['التاريخ'], y=df['طلاب حاليين'], mode='lines', stackgroup='one', name='طلاب حاليين يدرسون بالبهوتي', line=dict(color='#10ac84')))
            fig_area.add_trace(go.Scatter(x=df['التاريخ'], y=df['طلاب متوقفين'], mode='lines', stackgroup='one', name='طلاب متوقفين بالبهوتي', line=dict(color='#ee5253')))
            
            fig_area.update_layout(
                hovermode='x unified',
                margin=dict(l=10, r=10, t=10, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_area, use_container_width=True)
            
        with chart_col2:
            st.markdown("### 🎯 التوزيع النسبي لإجمالي الدفعة")
            labels = ['خارج البهوتي', 'قدامى البهوتي', 'طلاب حاليين', 'طلاب متوقفين']
            values = [latest['من خارج البهوتي'], latest['قدامى البهوتي'], latest['طلاب حاليين'], latest['طلاب متوقفين']]
            colors = ['#006e7f', '#ff9f43', '#10ac84', '#ee5253']
            
            fig_pie = px.pie(values=values, names=labels, hole=0.5, color_discrete_sequence=colors)
            fig_pie.update_traces(textposition='inside', textinfo='percent+value', labels=labels)
            fig_pie.update_layout(margin=dict(l=10, r=10, t=10, b=10), showlegend=True)
            st.plotly_chart(fig_pie, use_container_width=True)
            
        st.markdown("<br><hr><br>", unsafe_allow_html=True)
        
        # قسم رسم الأعداد اليومية (منفصل)
        st.markdown("### 📊 حركية التسجيل اليومية الفعالة")
        # استثناء الأيام التي يكون فيها تسجيل اليوم صفر لتنظيف الجراف وتوضيح الأيام النشطة فقط
        df_daily = df[df["تسجيل اليوم"] > 0]
        
        fig_bar = px.bar(df_daily, x='التاريخ', y='تسجيل اليوم', text_auto=True)
        fig_bar.update_traces(marker_color='#006e7f', textposition='outside')
        fig_bar.update_layout(
            xaxis_title="التاريخ الفعلي",
            yaxis_title="عدد المسجلين الجدد",
            margin=dict(l=10, r=10, t=20, b=10),
            xaxis=dict(tickformat="%Y-%m-%d"),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # جدول مراجعة البيانات باللغة العربية
        with st.expander("📋 استعراض السجل الرقمي المنظّم"):
            formatted_df = df.copy()
            # تنسيق التاريخ للعرض بوضوح
            formatted_df["التاريخ"] = formatted_df["التاريخ"].dt.strftime('%Y-%m-%d')
            st.dataframe(formatted_df.style.background_gradient(cmap='GnBu', subset=["تسجيل اليوم", "إجمالي المسجلين"]), use_container_width=True)

except Exception as e:
    st.error(f"⚠️ خطأ فني أثناء التشغيل: {e}")
