import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

# إعداد الصفحة بثيم أوسع وألوان مخصصة
st.set_page_config(layout="wide", page_title="داشبورد معهد خليل", page_icon="🟢")

# تخصيص الثيم باستخدام ألوان معهد خليل (أخضر داكن وذهبي)
st.markdown("""
    <style>
    .main { background-color: #f4f7f6; } /* لون خلفية مريح */
    h1, h2, h3 { color: #1e4620; font-family: 'Arial', sans-serif; } /* أخضر داكن للعناوين */
    div[data-testid="stMetricValue"] { font-size: 30px; font-weight: bold; color: #b8860b; } /* ذهبي داكن للأرقام */
    div[data-testid="stMetricLabel"] { font-size: 16px; color: #1e4620; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #e8eceb; border-radius: 5px; padding: 10px 20px; }
    .stTabs [aria-selected="true"] { background-color: #1e4620; color: white; }
    hr { border-top: 2px solid #b8860b; }
    </style>
""", unsafe_allow_html=True)

# إضافة الشعار كصورة مصغرة بجانب العنوان (يمكنك استبدال الرابط برابط شعاركم الحقيقي)
col_logo, col_title = st.columns([1, 8])
with col_logo:
    # ضع رابط الشعار الحقيقي هنا إن وجد
    st.image("https://via.placeholder.com/150/1e4620/FFFFFF?text=Khalil", width=80) 
with col_title:
    st.title("📊 لوحة التحكم التفاعلية - الدفعة الجديدة (معهد خليل)")
st.markdown("---")

def clean_percentage(val):
    """دالة مخصصة لتنظيف النسب المئوية بدقة"""
    if pd.isna(val) or val == '' or str(val).strip() == '#DIV/0!':
        return 0.0
    val_str = str(val).strip().replace(',', '')
    if '%' in val_str:
        try:
            return float(val_str.replace('%', ''))
        except ValueError:
            return 0.0
    try:
        f_val = float(val_str)
        return f_val * 100 if f_val < 1 else f_val
    except ValueError:
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
    
    # تنظيف مخصص للنسب
    percent_columns = [
        'نسبة الدفع من إجمالي المستهدفين', 'نسبة الدفع من الجدد',
        'نسبة الدفع من المسجلين القدامى', 'نسبة الدفع من الراسبين', 'نسبة الدفع من المتوقفين',
        'نسبة الدفع من طلاب التأهيل الفقهي', 'نسبة الدفع من طلاب ابن مالك', 'نسبة الدفع من طلاب بداية اللغوي',
        'نسية طلاب التأهيل الفقهي من متقدمي خليل', 'نسبة طلاب ابن مالك من متقدمي خليل', 'نسية طلاب بداية اللغوي من متقدمي خليل'
    ]
    
    for col in df.columns.drop('التاريخ'):
        if col in percent_columns:
            df[col] = df[col].apply(clean_percentage)
        else:
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
        
        col2.metric("الدافعين الجدد (كاش+تقسيط)", f"{total_payers:,}")
        col3.metric("إجمالي الطلاب (دافعين + إعفاء)", f"{total_actual_students:,}")
        col4.metric("الإعفاءات المفعلة", f"{exemptions:,}")
        col5.metric("إجمالي المستهدفين (تقريبي)", f"{int(total_actual_students / (last_row['نسبة الدفع من إجمالي المستهدفين'] / 100)) if last_row['نسبة الدفع من إجمالي المستهدفين'] > 0 else 0:,}")

        st.markdown("---")
        
        st.subheader("📊 معدلات التحويل الفعلية حسب الفئة")
        col_rates1, col_rates2, col_rates3, col_rates4 = st.columns(4)
        # تصحيح عرض النسب من الفئات المختلفة
        col_rates1.metric("الجدد (معدل حقيقي)", f"{last_row['نسبة الدفع من الجدد']:.1f}%")
        col_rates2.metric("القدامى (سجلوا فقط)", f"{last_row['نسبة الدفع من المسجلين القدامى']:.1f}%")
        col_rates3.metric("الراسبين", f"{last_row['نسبة الدفع من الراسبين']:.1f}%")
        col_rates4.metric("المتوقفين (درسوا سابقاً)", f"{last_row['نسبة الدفع من المتوقفين']:.1f}%")
        
        st.markdown("---")
        
        st.subheader("👥 تحليل هيكل المتقدمين (النوايا)")
        segment_data = pd.DataFrame({
            'الفئة': ['متقدمين جدد تماماً', 'قدامى (تسجيل سابق)', 'متوقفين (درسوا سابقاً)', 'باقين للإعادة'],
            'العدد': [
                last_row['المتقدمين الجدد (إجمالي)'],
                last_row['متقدمين قدامى (لم يدرسوا من قبل)'],
                last_row['متوقفين من الدفعات السابقة (راسب)'],
                last_row['الباقين للإعادة (راسبين د4 س1)']
            ]
        })
        fig_seg = px.bar(segment_data, x='الفئة', y='العدد', color='الفئة', 
                         color_discrete_sequence=['#1e4620', '#2e8b57', '#b8860b', '#daa520'],
                         text_auto=True, title="توزيع المتقدمين حسب علاقتهم السابقة بالمعهد")
        st.plotly_chart(fig_seg, use_container_width=True)

    with tab2:
        st.subheader("💰 تحليل طرق الدفع والسيولة (نظام الباقات موقوف)")
        col_pay1, col_pay2 = st.columns([1, 2])
        
        with col_pay1:
            payment_data = pd.DataFrame({
                'طريقة الدفع': ['كاش', 'أقساط (سيولة مؤجلة)'],
                'العدد': [last_row['إجمالي عدد الكاش'], last_row['إجمالي المقسطين']]
            })
            fig_pay = px.pie(payment_data, values='العدد', names='طريقة الدفع', hole=0.5, 
                             color_discrete_sequence=['#1e4620', '#b8860b'],
                             title="توزيع طرق الدفع الحالية")
            st.plotly_chart(fig_pay, use_container_width=True)
            
        with col_pay2:
            st.write("**📈 اتجاهات التسجيل والتحصيل**")
            fig_line = px.line(df, x='التاريخ', y=['المتقدمين الجدد (يومي)', 'عدد الطلاب (اليومي)'], 
                               color_discrete_sequence=['#b8860b', '#1e4620'], markers=True)
            st.plotly_chart(fig_line, use_container_width=True)

    with tab3:
        st.subheader("🎯 تأثير المعاهد التأسيسية على معهد خليل")
        programs = ["التأهيل الفقهي", "ابن مالك", "بداية اللغوي"]
        
        prog_matrix = pd.DataFrame({
            "المعهد التأسيسي": programs,
            "الطلاب القادمون لخليل": [
                last_row["عدد طلاب التأهيل الفقهي من متقدمي خليل الجدد (إجمالي)"],
                last_row["عدد طلاب ابن مالك من متقدمي خليل الجدد (إجمالي)"],
                last_row["عدد طلاب بداية اللغوي من متقدمي خليل الجدد (إجمالي)"]
            ],
            "% من إجمالي المتقدمين لخليل": [
                f"{last_row['نسية طلاب التأهيل الفقهي من متقدمي خليل']:.1f}%",
                f"{last_row['نسبة طلاب ابن مالك من متقدمي خليل']:.1f}%",
                f"{last_row['نسية طلاب بداية اللغوي من متقدمي خليل']:.1f}%"
            ],
            "الدافعون فعلياً لخليل": [
                last_row["عدد الدافعين من طلبة التأهيل الفقهي"],
                last_row["عدد الدافعين من طلبة ابن مالك"],
                last_row["عدد الدافعين من طلبة بداية اللغوي"]
            ],
            "معدل التحويل الحقيقي لخليل": [
                f"{last_row['نسبة الدفع من طلاب التأهيل الفقهي']:.1f}%",
                f"{last_row['نسبة الدفع من طلاب ابن مالك']:.1f}%",
                f"{last_row['نسبة الدفع من طلاب بداية اللغوي']:.1f}%"
            ]
        })
        st.dataframe(prog_matrix.style.set_properties(**{'background-color': '#f4f7f6', 'color': '#1e4620', 'border': '1px solid #b8860b'}), use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("💡 التوصيات الاستراتيجية (مبنية على أرقام وسياق الدفعة الحالية)")
        
        col_rec1, col_rec2, col_rec3 = st.columns(3)
        
        with col_rec1:
            st.markdown("🎯 **التشغيل والسياسات**")
            # استنباط توصية من نسبة المقسطين للكاش
            if last_row['إجمالي المقسطين'] > last_row['إجمالي عدد الكاش']:
                 st.info("💡 الاعتماد الأكبر حالياً على الأقساط. يجب تجهيز فريق التحصيل بمتابعات دقيقة لضمان عدم تعثر التدفق النقدي في الأشهر القادمة.")
            else:
                 st.success("✅ نسبة الدفع الكاش ممتازة، مما يوفر سيولة نقدية جيدة للمعهد.")
                 
            # توصية بشأن الإعفاءات
            if exemptions > 0:
                 st.info(f"💡 تم تفعيل {exemptions} إعفاء. يُنصح بمراجعة العائد غير المباشر (مثل التسويق الشفهي) من هؤلاء الطلاب مقابل التكلفة المفقودة.")

        with col_rec2:
            st.markdown("💼 **المبيعات وإدارة العلاقات**")
            # تحليل سلوك المتوقفين والقدامى
            conv_stopped = last_row['نسبة الدفع من المتوقفين']
            conv_old = last_row['نسبة الدفع من المسجلين القدامى']
            
            if conv_stopped > 10:
                st.success(f"✅ معدل رجوع المتوقفين ({conv_stopped:.1f}%) يبشر بالخير. هؤلاء درسوا سابقاً ويعرفون قيمة المعهد. حملة 'عودة للمسار' قد تزيد هذا العدد.")
            else:
                st.warning(f"⚠️ المتوقفون (الذين درسوا سابقاً) معدل عودتهم ضعيف ({conv_stopped:.1f}%). يحتاجون تواصلاً شخصياً لمعرفة أسباب التوقف ومعالجتها.")
                
            st.info(f"💡 القدامى (معدل {conv_old:.1f}%) عبارة عن قاعدة بيانات ضخمة (Data) ولكنهم ليسوا مستهدفين حقيقيين. فلترة هذه القائمة وإرسال عروض خاصة للجادين فقط سيوفر وقت فريق المبيعات.")

        with col_rec3:
            st.markdown("📣 **التسويق والاستقطاب**")
            # استخراج أعلى وأقل معهد مصدر
            rates = {
                'التأهيل الفقهي': last_row['نسبة الدفع من طلاب التأهيل الفقهي'],
                'ابن مالك': last_row['نسبة الدفع من طلاب ابن مالك'],
                'بداية اللغوي': last_row['نسبة الدفع من طلاب بداية اللغوي']
            }
            top_prog = max(rates, key=rates.get)
            min_prog = min(rates, key=rates.get)
            
            st.success(f"📈 **{top_prog}** هو المورد الأقوى للطلاب الدافعين في خليل ({rates[top_prog]:.1f}%). يجب تعزيز الشراكة التسويقية الداخلية مع هذا المعهد وتوجيه رسائل مشتركة.")
            st.warning(f"📉 معدل تحويل طلاب **{min_prog}** ضعيف ({rates[min_prog]:.1f}%). ربما يحتاجون لفهم العلاقة المباشرة وتكامل المنهج بين معهدهم ومعهد خليل.")

except Exception as e:
    st.error(f"⚠️ خطأ أثناء معالجة البيانات: {e}")
