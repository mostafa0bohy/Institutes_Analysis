import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

st.set_page_config(layout="wide", page_title="داشبورد معهد خليل", page_icon="📊")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="stMetricValue"] { font-size: 28px; font-weight: bold; color: #1E3A8A; }
    div[data-testid="stMetricLabel"] { font-size: 16px; color: #4B5563; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 لوحة التحكم الذكية لفتح الدفعة الجديدة - معهد خليل")
st.markdown("---")

@st.cache_data
def load_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRTJXOApbP389e07-RnHJtOlC9iMwKdWo4xID1BfwPhoHisk1wl4aS1Gge5P0_2tkoI_IMuAfvaRMdR/pub?gid=1631853462&single=true&output=csv"
    
    raw_df = pd.read_csv(url, header=None)
    headers = raw_df.iloc[1].astype(str).str.replace('\n', ' ', regex=True).str.strip()
    raw_df.columns = headers
    df = raw_df.iloc[3:].reset_index(drop=True)
    
    df['التاريخ'] = pd.to_datetime(df['التاريخ'], errors='coerce')
    df = df.dropna(subset=['التاريخ'])
    
    for col in df.columns.drop('التاريخ'):
        if df[col].dtype == 'object':
            # تنظيف النسب المئوية والفواصل
            df[col] = df[col].astype(str).str.replace('%', '', regex=True).str.replace(',', '', regex=True).str.strip()
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    df = df[df['المتقدمين الجدد (إجمالي)'] > 0]
    
    return df

try:
    df = load_data()
    last_row = df.iloc[-1]
    
    tab1, tab2, tab3 = st.tabs(["🏛️ الإدارة العليا والتشغيل", "📈 المبيعات والتدفق النقدي", "🎯 قطاع التسويق والبرامج"])
    
    # -------------------------------------------------------------------------
    # التبويب الأول: الإدارة العليا والتشغيل
    # -------------------------------------------------------------------------
    with tab1:
        st.subheader("📌 أحدث المؤشرات القياسية لأداء الدفعة")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("إجمالي المتقدمين الجدد", f"{int(last_row['المتقدمين الجدد (إجمالي)']):,}")
        
        # التعديل 1: الفصل بين الدافعين وإجمالي الطلاب (بما في ذلك الإعفاءات)
        total_payers = int(last_row['إجمالي عدد الكاش'] + last_row['إجمالي المقسطين'])
        exemptions = int(last_row['إعفاء مفعل (تم استخدام كوبون الإعفاء)'])
        total_actual_students = total_payers + exemptions
        
        col2.metric("إجمالي الدافعين", f"{total_payers:,}")
        col3.metric("إجمالي الطلاب (دافعين + إعفاء)", f"{total_actual_students:,}")
        col4.metric("الإعفاءات المفعلة", f"{exemptions:,}")
        col5.metric("نسبة الدفع من المستهدف", f"{last_row['نسبة الدفع من إجمالي المستهدفين']:.2f}%")
        
        st.markdown("---")
        
        # التعديل 2: عرض نسب الدفع من كل فئة
        st.subheader("📊 معدلات التحويل (نسبة الدفع) حسب فئة المتقدمين")
        col_rates1, col_rates2, col_rates3, col_rates4 = st.columns(4)
        col_rates1.metric("نسبة الدفع من الجدد", f"{last_row['نسبة الدفع من الجدد']:.2f}%")
        col_rates2.metric("نسبة الدفع من القدامى", f"{last_row['نسبة الدفع من المسجلين القدامى']:.2f}%")
        col_rates3.metric("نسبة الدفع من الراسبين", f"{last_row['نسبة الدفع من الراسبين']:.2f}%")
        col_rates4.metric("نسبة الدفع من المتوقفين", f"{last_row['نسبة الدفع من المتوقفين']:.2f}%")
        
        st.markdown("---")
        
        st.subheader("👥 تحليل نوعية وفئات الطلاب المتقدمين")
        segment_data = pd.DataFrame({
            'الفئة': ['متقدمين جدد', 'متقدمين قدامى', 'متوقفين سابقاً (راسب)', 'باقين للإعادة'],
            'العدد': [
                last_row['المتقدمين الجدد (إجمالي)'],
                last_row['متقدمين قدامى (لم يدرسوا من قبل)'],
                last_row['متوقفين من الدفعات السابقة (راسب)'],
                last_row['الباقين للإعادة (راسبين د4 س1)']
            ]
        })
        fig_seg = px.bar(segment_data, x='الفئة', y='العدد', color='الفئة', text_auto=True,
                         title="توزيع المتقدمين حسب حالتهم الأكاديمية السابقة")
        st.plotly_chart(fig_seg, use_container_width=True)

    # -------------------------------------------------------------------------
    # التبويب الثاني: المبيعات والتدفق النقدي
    # -------------------------------------------------------------------------
    with tab2:
        st.subheader("💰 تحليل طرق الدفع والسيولة")
        
        col_pay1, col_pay2 = st.columns([1, 2])
        
        with col_pay1:
            payment_data = pd.DataFrame({
                'طريقة الدفع': ['كاش', 'أقساط', 'باقات متعددة السنوات'],
                'العدد': [last_row['إجمالي عدد الكاش'], last_row['إجمالي المقسطين'], last_row['إجمالي الباقات (اشتراك متعدد السنوات)']]
            })
            fig_pay = px.pie(payment_data, values='العدد', names='طريقة الدفع', hole=0.4,
                             title="نسبة توزيع طرق الدفع بين الطلاب")
            st.plotly_chart(fig_pay, use_container_width=True)
            
        with col_pay2:
            st.write("**📈 المنحنى الزمني للتسجيل اليومي الفعلي**")
            fig_line = px.line(df, x='التاريخ', y=['المتقدمين الجدد (يومي)', 'عدد الطلاب (اليومي)'], 
                               labels={'value': 'العدد', 'variable': 'الفئة'}, markers=True)
            st.plotly_chart(fig_line, use_container_width=True)

    # -------------------------------------------------------------------------
    # التبويب الثالث: قطاع التسويق والبرامج
    # -------------------------------------------------------------------------
    with tab3:
        st.subheader("🎯 أثر المعاهد على معهد خليل (معدلات التحويل)")
        
        # التعديل 3: التركيز على الثلاث معاهد المطلوبة فقط
        programs = ["التأهيل الفقهي", "ابن مالك", "بداية اللغوي"]
        
        prog_matrix = pd.DataFrame({
            "المعهد": programs,
            "إجمالي الطلاب من المتقدمين لخليل": [
                last_row["عدد طلاب التأهيل الفقهي من متقدمي خليل الجدد (إجمالي)"],
                last_row["عدد طلاب ابن مالك من متقدمي خليل الجدد (إجمالي)"],
                last_row["عدد طلاب بداية اللغوي من متقدمي خليل الجدد (إجمالي)"]
            ],
            "نسبة الطلاب من إجمالي المتقدمين": [
                f"{last_row['نسية طلاب التأهيل الفقهي من متقدمي خليل']:.2f}%",
                f"{last_row['نسبة طلاب ابن مالك من متقدمي خليل']:.2f}%",
                f"{last_row['نسية طلاب بداية اللغوي من متقدمي خليل']:.2f}%"
            ],
            "عدد الدافعين الفعليين": [
                last_row["عدد الدافعين من طلبة التأهيل الفقهي"],
                last_row["عدد الدافعين من طلبة ابن مالك"],
                last_row["عدد الدافعين من طلبة بداية اللغوي"]
            ],
            "معدل التحويل (نسبة الدفع)": [
                f"{last_row['نسبة الدفع من طلاب التأهيل الفقهي']:.2f}%",
                f"{last_row['نسبة الدفع من طلاب ابن مالك']:.2f}%",
                f"{last_row['نسبة الدفع من طلاب بداية اللغوي']:.2f}%"
            ]
        })
        
        st.dataframe(prog_matrix, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("💡 التقرير الاستراتيجي والتوصيات الذكية")
        
        col_rec1, col_rec2, col_rec3 = st.columns(3)
        
        with col_rec1:
            st.info("🎯 **توصيات الإدارة العليا**\n\n"
                    f"• نسبة الإنجاز الحالية من المستهدف العام هي **{last_row['نسبة الدفع من إجمالي المستهدفين']:.1f}%**.\n"
                    f"• يشكل الحاصلون على إعفاءات نسبة ملحوظة من إجمالي الطلاب ({exemptions} طالب).")
            
        with col_rec2:
            st.success("💼 **توصيات رؤساء أقسام المبيعات والتشغيل**\n\n"
                       f"• معدل تحويل المتقدمين الجدد هو **{last_row['نسبة الدفع من الجدد']:.1f}%**.\n"
                       f"• يرجى مراجعة فئات القدامى والراسبين حيث أن معدلات دفعهم قد تحتاج لتنشيط أو رسائل تذكيرية.")
            
        with col_rec3:
            st.warning("📣 **توصيات قسم التسويق**\n\n"
                       "• راقب معدلات تحويل المعاهد الثلاثة المرتبطة بمعهد خليل (التأهيل الفقهي، ابن مالك، بداية اللغوي).\n"
                       "• يمكن توجيه حملات محددة لطلاب هذه المعاهد الذين لم يكملوا الدفع لزيادة معدل التحويل.")

except Exception as e:
    st.error(f"⚠️ واجهت المنصة مشكلة في معالجة بعض حقول البيانات: {e}")
