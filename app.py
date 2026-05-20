import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime
import re

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

def clean_percentage(val):
    """دالة مخصصة لتنظيف القيم سواء كانت نصوصاً بها % أو أرقاماً عشرية"""
    if pd.isna(val) or val == '' or val == '#DIV/0!':
        return 0.0
    if isinstance(val, str):
        val = val.replace(',', '')
        if '%' in val:
            # إذا كانت نصاً ويحتوي على %، نزيل الـ % ونحولها لرقم
            return float(val.replace('%', '').strip())
        else:
            try:
                # محاولة تحويل النص لرقم
                return float(val) * 100 if float(val) < 1 else float(val)
            except ValueError:
                return 0.0
    elif isinstance(val, (int, float)):
         # إذا كانت رقماً عشرياً (مثل 0.20)، نضرب في 100 لتصبح 20%
         return float(val) * 100 if val < 1 else float(val)
    return 0.0

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
        if 'نسبة' in col or 'نسية' in col:
            # استخدام الدالة المخصصة لتنظيف النسب المئوية
            df[col] = df[col].apply(clean_percentage)
        else:
            # تنظيف الأرقام العادية
            if df[col].dtype == 'object':
                 df[col] = df[col].astype(str).str.replace(',', '', regex=True)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    df = df[df['المتقدمين الجدد (إجمالي)'] > 0]
    return df

try:
    df = load_data()
    last_row = df.iloc[-1]
    
    tab1, tab2, tab3 = st.tabs(["🏛️ الإدارة العليا والتشغيل", "📈 المبيعات والتدفق النقدي", "🎯 قطاع التسويق والبرامج"])
    
    with tab1:
        st.subheader("📌 أحدث المؤشرات القياسية لأداء الدفعة")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("إجمالي المتقدمين الجدد", f"{int(last_row['المتقدمين الجدد (إجمالي)']):,}")
        
        total_payers = int(last_row['إجمالي عدد الكاش'] + last_row['إجمالي المقسطين'])
        exemptions = int(last_row['إعفاء مفعل (تم استخدام كوبون الإعفاء)'])
        total_actual_students = total_payers + exemptions
        
        col2.metric("إجمالي الدافعين", f"{total_payers:,}")
        col3.metric("إجمالي الطلاب (دافعين + إعفاء)", f"{total_actual_students:,}")
        col4.metric("الإعفاءات المفعلة", f"{exemptions:,}")
        col5.metric("نسبة الدفع من المستهدف", f"{last_row['نسبة الدفع من إجمالي المستهدفين']:.1f}%")
        
        st.markdown("---")
        
        st.subheader("📊 معدلات التحويل (نسبة الدفع) حسب فئة المتقدمين")
        col_rates1, col_rates2, col_rates3, col_rates4 = st.columns(4)
        col_rates1.metric("نسبة الدفع من الجدد", f"{last_row['نسبة الدفع من الجدد']:.1f}%")
        col_rates2.metric("نسبة الدفع من القدامى", f"{last_row['نسبة الدفع من المسجلين القدامى']:.1f}%")
        col_rates3.metric("نسبة الدفع من الراسبين", f"{last_row['نسبة الدفع من الراسبين']:.1f}%")
        col_rates4.metric("نسبة الدفع من المتوقفين", f"{last_row['نسبة الدفع من المتوقفين']:.1f}%")
        
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
        fig_seg = px.bar(segment_data, x='الفئة', y='العدد', color='الفئة', text_auto=True, title="توزيع المتقدمين")
        st.plotly_chart(fig_seg, use_container_width=True)

    with tab2:
        st.subheader("💰 تحليل طرق الدفع والسيولة")
        col_pay1, col_pay2 = st.columns([1, 2])
        
        with col_pay1:
            payment_data = pd.DataFrame({
                'طريقة الدفع': ['كاش', 'أقساط', 'باقات متعددة'],
                'العدد': [last_row['إجمالي عدد الكاش'], last_row['إجمالي المقسطين'], last_row['إجمالي الباقات (اشتراك متعدد السنوات)']]
            })
            fig_pay = px.pie(payment_data, values='العدد', names='طريقة الدفع', hole=0.4, title="توزيع طرق الدفع")
            st.plotly_chart(fig_pay, use_container_width=True)
            
        with col_pay2:
            st.write("**📈 المنحنى الزمني للتسجيل اليومي الفعلي**")
            fig_line = px.line(df, x='التاريخ', y=['المتقدمين الجدد (يومي)', 'عدد الطلاب (اليومي)'], markers=True)
            st.plotly_chart(fig_line, use_container_width=True)

    with tab3:
        st.subheader("🎯 أثر المعاهد على معهد خليل (معدلات التحويل)")
        programs = ["التأهيل الفقهي", "ابن مالك", "بداية اللغوي"]
        
        prog_matrix = pd.DataFrame({
            "المعهد": programs,
            "إجمالي الطلاب من المتقدمين لخليل": [
                last_row["عدد طلاب التأهيل الفقهي من متقدمي خليل الجدد (إجمالي)"],
                last_row["عدد طلاب ابن مالك من متقدمي خليل الجدد (إجمالي)"],
                last_row["عدد طلاب بداية اللغوي من متقدمي خليل الجدد (إجمالي)"]
            ],
            "نسبة الطلاب من إجمالي المتقدمين": [
                f"{last_row['نسية طلاب التأهيل الفقهي من متقدمي خليل']:.1f}%",
                f"{last_row['نسبة طلاب ابن مالك من متقدمي خليل']:.1f}%",
                f"{last_row['نسية طلاب بداية اللغوي من متقدمي خليل']:.1f}%"
            ],
            "عدد الدافعين الفعليين": [
                last_row["عدد الدافعين من طلبة التأهيل الفقهي"],
                last_row["عدد الدافعين من طلبة ابن مالك"],
                last_row["عدد الدافعين من طلبة بداية اللغوي"]
            ],
            "معدل التحويل (نسبة الدفع)": [
                f"{last_row['نسبة الدفع من طلاب التأهيل الفقهي']:.1f}%",
                f"{last_row['نسبة الدفع من طلاب ابن مالك']:.1f}%",
                f"{last_row['نسبة الدفع من طلاب بداية اللغوي']:.1f}%"
            ]
        })
        st.dataframe(prog_matrix, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("💡 التقرير الاستراتيجي والتوصيات الذكية (ديناميكية)")
        
        col_rec1, col_rec2, col_rec3 = st.columns(3)
        
        with col_rec1:
            st.markdown("🎯 **الإدارة العليا**")
            target_rate = last_row['نسبة الدفع من إجمالي المستهدفين']
            if target_rate < 30:
                 st.error(f"⚠️ تحذير: نسبة الإنجاز من المستهدف متدنية ({target_rate:.1f}%). يجب مراجعة خطة التسعير أو تكثيف الجهود الإعلانية فوراً.")
            elif target_rate < 70:
                 st.warning(f"🟡 نسبة الإنجاز متوسطة ({target_rate:.1f}%). مسار التسجيل مستقر ولكن يحتاج لدفعة إضافية قبل إغلاق باب التسجيل.")
            else:
                 st.success(f"✅ أداء ممتاز! نسبة الإنجاز ({target_rate:.1f}%) ممتازة. الاستمرار على نفس الاستراتيجية.")
                 
            if exemptions > (total_actual_students * 0.15):
                 st.warning(f"⚠️ تنبيه: نسبة الإعفاءات تتجاوز 15% من إجمالي الطلاب ({exemptions} طالب). راجع سياسة الكوبونات لتأثيرها على التدفق النقدي.")

        with col_rec2:
            st.markdown("💼 **المبيعات والتشغيل**")
            new_rate = last_row['نسبة الدفع من الجدد']
            old_rate = last_row['نسبة الدفع من المسجلين القدامى']
            
            if new_rate < 15:
                st.warning(f"⚠️ معدل تحويل المتقدمين الجدد ضعيف ({new_rate:.1f}%). نوصي بتفعيل حملات (Follow-up) مكثفة عبر الواتساب.")
            else:
                st.success(f"✅ معدل تحويل الجدد جيد ({new_rate:.1f}%).")
                
            if old_rate > new_rate:
                st.info("💡 المسجلون القدامى أكثر استجابة للدفع من الجدد. خصصوا عروض ولاء (Loyalty Offers) لهم لزيادة هذه النسبة.")
            else:
                st.info("💡 التركيز الحالي يحقق نتائج جيدة مع المتقدمين الجدد.")

        with col_rec3:
            st.markdown("📣 **التسويق**")
            # استخراج أقل معهد من حيث معدل التحويل
            min_prog_rate = prog_matrix['معدل التحويل (نسبة الدفع)'].str.replace('%','').astype(float).min()
            min_prog_name = prog_matrix.loc[prog_matrix['معدل التحويل (نسبة الدفع)'].str.replace('%','').astype(float) == min_prog_rate, 'المعهد'].iloc[0]
            
            st.warning(f"📉 **{min_prog_name}** هو الأقل في معدل التحويل ({min_prog_rate:.1f}%). نوصي بإنشاء حملات إعادة استهداف (Retargeting) مخصصة لطلاب هذا المعهد وتوضيح الفوائد المشتركة مع معهد خليل.")
            st.info("💡 تأكد من تنويع المحتوى الإعلاني لتعزيز 'الباقات المتعددة' حيث أنها توفر سيولة نقدية طويلة الأجل.")

except Exception as e:
    st.error(f"⚠️ خطأ أثناء معالجة البيانات: {e}")
