import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. إعداد الصفحة وتطبيق الهوية البصرية لمعهد البهوتي والتأهيل الفقهي الحنبلي
st.set_page_config(layout="wide", page_title="داشبورد التأهيل الفقهي الحنبلي - الدفعة 16", page_icon="📜")

# هندسة التصميم بالألوان المستوحاة من الموقع (Deep Royal Blue & Soft Beige)
st.markdown("""
    <style>
    .main { background-color: #fcfbfa; } /* خلفية بيج ناعمة جداً ومريحة للعين */
    h1, h2, h3 { color: #0f2c59; font-family: 'Arial', sans-serif; font-weight: 700; } /* الأزرق الداكن السندسي */
    div[data-testid="stMetricValue"] { font-size: 32px; font-weight: bold; color: #d4af37; } /* اللون الذهبي للأرقام */
    div[data-testid="stMetricLabel"] { font-size: 15px; color: #0f2c59; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { background-color: #f0f4f8; border-radius: 6px; padding: 12px 24px; color: #0f2c59; font-weight: bold; }
    .stTabs [aria-selected="true"] { background-color: #0f2c59; color: white; }
    hr { border-top: 2px solid #d4af37; }
    </style>
""", unsafe_allow_html=True)

# الهيدر الاحترافي مع الشعار والعنوان
col_logo, col_title = st.columns([1, 7])
with col_logo:
    # استخدام الصورة الرسمية من موقعكم كأيقونة علوية للداشبورد
    st.image("https://new.albuhutifiqh.online/_next/image?url=https%3A%2F%2Fcdn.albuhutifiqh.online%2Fstatic_pages%2F5%2Fhero_image_1777986406617&w=750&q=90", width=110)
with col_title:
    st.markdown("<h1 style='margin-top: 10px;'>📜 لوحة المؤشرات الذكية | برنامج التأهيل الفقهي الحنبلي</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#555;'>متابعة حية وتحليل إحصائي متقدم لأداء التسجيل بالدفعة السادسة عشرة وعلاقتها بطلاب معهد البهوتي</p>", unsafe_allow_html=True)
st.markdown("---")

def clean_percentage(val):
    if pd.isna(val) or val == '' or str(val).strip() == '#DIV/0!':
        return 0.0
    val_str = str(val).strip().replace('%', '').replace(',', '')
    try:
        f_val = float(val_str)
        return f_val * 100 if f_val < 1 else f_val
    except ValueError:
        return 0.0

@st.cache_data
def load_hanbali_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRmiO4XN9kssEddDdU8TuKtXOypsisNKiKejQ-DCDqcgmox6s7DV0zRJ6mxpLqpBA5XQr4JMgFE11_o/pub?gid=826428120&single=true&output=csv"
    
    # قراءة البيانات الخام بالكامل
    raw_df = pd.read_csv(url, header=None)
    
    # تنظيف العناوين بالصف الثاني (Index 1)
    headers = raw_df.iloc[1].astype(str).str.replace('\n', ' ', regex=True).str.strip()
    raw_df.columns = headers
    
    # استخلاص الخط الزمني الرئيسي (الأعمدة من A إلى M) وبدء البيانات من الصف الرابع (Index 3)
    timeline_df = raw_df.iloc[3:].copy().reset_index(drop=True)
    timeline_df['التاريخ'] = pd.to_datetime(timeline_df['التاريخ'], errors='coerce')
    timeline_df = timeline_df.dropna(subset=['التاريخ'])
    
    # تحويل وتنظيف البيانات الرقمية للخط الزمني
    for col in timeline_df.columns.drop('التاريخ'):
        if 'نسبة' in col:
            timeline_df[col] = timeline_df[col].apply(clean_percentage)
        else:
            if timeline_df[col].dtype == 'object':
                timeline_df[col] = timeline_df[col].astype(str).str.replace(',', '', regex=True)
            timeline_df[col] = pd.to_numeric(timeline_df[col], errors='coerce').fillna(0)
            
    # تصفية الأيام التي لم تبدأ أو الفارغة
    timeline_df = timeline_df[timeline_df['إجمالي المسجلين الجدد (أنشأ حسابًا على الموقع)'] > 0]
    
    # --- قراءة جداول الـ Pivot Tables ديناميكياً من العمود N وما بعده ---
    # نأخذ كامل الشيت ونبحث في الأعمدة الجانبية لاستخراج كتل الجداول
    side_data = raw_df.iloc[1:].copy() # تشمل العناوين والبيانات
    
    def extract_pivot(search_header, data_frame):
        # البحث عن العمود الذي يحتوي على اسم الجدول
        for col in data_frame.columns:
            if data_frame[col].astype(str).str.contains(search_header).any():
                idx = data_frame[data_frame[col].astype(str) == search_header].index[0]
                # استخراج الجدول الصغير حتى نصل لسطر فارغ أو كلمة "إجمالي"
                sub_df = data_frame.loc[idx:].copy()
                items = []
                counts = []
                for _, row in sub_df.iterrows():
                    val_name = str(row[col]).strip()
                    # التوقف عند نهاية الجدول أو السطور الفارغة
                    if val_name == 'nan' or 'Grand Total' in val_name or 'الإجمالي' in val_name or val_name == search_header:
                        if val_name == search_header: continue
                        break
                    
                    # القيمة الرقمية تكون في العمود التالي مباشرة
                    next_col_idx = list(data_frame.columns).index(col) + 1
                    try:
                        count_val = float(str(row.iloc[next_col_idx]).replace(',', ''))
                        items.append(val_name)
                        counts.append(count_val)
                    except:
                        continue
                return pd.DataFrame({'الفئة': items, 'العدد': counts})
        return pd.DataFrame({'الفئة': [], 'العدد': []})

    # استخراج الجداول الخمسة بناءً على المسميات المتوقعة في خلايا الـ Pivot المحددة بالشيت
    pivot_gender = extract_pivot("الجنس", side_data)
    pivot_geo = extract_pivot("الدولة", side_data)
    pivot_relation = extract_pivot("العلاقة بالبهوتي", side_data)
    pivot_age = extract_pivot("العمر", side_data)
    pivot_edu = extract_pivot("المستوى التعليمي", side_data)
    
    return timeline_df, pivot_gender, pivot_geo, pivot_relation, pivot_age, pivot_edu

try:
    df, p_gender, p_geo, p_relation, p_age, p_edu = load_hanbali_data()
    last_row = df.iloc[-1]
    
    # إنشاء التبويبات الثلاثة للتحليل المتكامل
    tab1, tab2, tab3 = st.tabs(["📈 حركية التسجيل اليومي", "📊 الخصائص الديموغرافية والتعليمية", "🎯 تحليل العلاقة مع معهد البهوتي"])
    
    # -------------------------------------------------------------------------
    # التبويب الأول: حركية التسجيل اليومي
    # -------------------------------------------------------------------------
    with tab1:
        st.subheader("📌 نظرة عامة على وتيرة التدفق الحالية")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("إجمالي المسجلين الجدد تراكمي", f"{int(last_row['إجمالي المسجلين الجدد (أنشأ حسابًا على الموقع)']):,}")
        col2.metric("مسجلي اليوم الفعلي", f"{int(last_row['مسجلين اليوم (أنشأ حسابًا على الموقع)']):,}")
        
        # حساب متوسط التسجيل اليومي كـ Trend ذكي
        avg_daily = df['مسجلين اليوم (أنشأ حسابًا على الموقع)'].mean()
        col3.metric("متوسط التسجيل اليومي", f"{avg_daily:.1f} طالب / يوم")
        
        # رصد القمة التاريخية للتسجيل كمعيار أداء لقسم الميديا
        max_daily = df['مسجلين اليوم (أنشأ حسابًا على الموقع)'].max()
        max_date = df.loc[df['مسجلين اليوم (أنشأ حسابًا على الموقع)'] == max_daily, 'التاريخ'].iloc[0].strftime('%Y-%m-%d')
        col4.metric("أعلى ذروة تسجيل يومية", f"{int(max_daily)} طالب", f"في تاريخ {max_date}", delta_color="off")
        
        st.markdown("---")
        st.subheader("📉 المنحنى الزمني لتطور عمليات إنشاء الحسابات")
        
        fig_line = px.line(df, x='التاريخ', y=['إجمالي المسجلين الجدد (أنشأ حسابًا على الموقع)', 'مسجلين اليوم (أنشأ حسابًا على الموقع)'],
                           labels={'value': 'عدد الطلاب', 'variable': 'مؤشر القياس'},
                           color_discrete_sequence=['#0f2c59', '#d4af37'], markers=True)
        fig_line.update_layout(hovermode="x unified")
        st.plotly_chart(fig_line, use_container_width=True)

    # -------------------------------------------------------------------------
    # التبويب الثاني: الخصائص الديموغرافية والتعليمية (Pivot Tables)
    # -------------------------------------------------------------------------
    with tab2:
        st.subheader("👥 من هم طلاب الدفعة 16؟ (تحليل الـ Pivot Tables الجانبية)")
        
        col_demo1, col_demo2 = st.columns(2)
        
        with col_demo1:
            if not p_gender.empty:
                fig_g = px.pie(p_gender, values='العدد', names='الفئة', hole=0.4,
                               color_discrete_sequence=['#0f2c59', '#d4af37', '#2e8b57'],
                               title="🧬 التوزيع الجندري بين الجنسين")
                st.plotly_chart(fig_g, use_container_width=True)
            else:
                st.info("لم يتم العثور على Pivot تابل مخصص لـ 'الجنس' في الأعمدة الجانبية.")
                
            if not p_age.empty:
                fig_a = px.bar(p_age, x='الفئة', y='العدد', text_auto=True,
                               color_discrete_sequence=['#0f2c59'],
                               title="⏳ التوزيع المئوي للفئات العمرية للمتقدمين")
                st.plotly_chart(fig_a, use_container_width=True)
            else:
                st.info("لم يتم العثور على Pivot تابل مخصص لـ 'العمر' في الأعمدة الجانبية.")

        with col_demo2:
            if not p_edu.empty:
                fig_e = px.bar(p_edu, y='الفئة', x='العدد', orientation='h', text_auto=True,
                               color_discrete_sequence=['#2c5282'],
                               title="🎓 توزيع المستويات التعليمية والأكاديمية للطلاب")
                st.plotly_chart(fig_e, use_container_width=True)
            else:
                st.info("لم يتم العثور على Pivot تابل مخصص لـ 'المستوى التعليمي' في الأعمدة الجانبية.")
                
            if not p_geo.empty:
                # ترتيب تنازلي وعرض أعلى 10 دول قادمة للمعهد
                p_geo_top = p_geo.sort_values(by='العدد', ascending=False).head(10)
                fig_geo = px.bar(p_geo_top, x='الفئة', y='العدد', text_auto=True,
                                 color_discrete_sequence=['#b8860b'],
                                 title="🌍 التوزيع الجغرافي (أعلى 10 دول من حيث عدد الطلاب)")
                st.plotly_chart(fig_geo, use_container_width=True)
            else:
                st.info("لم يتم العثور على Pivot تابل مخصص لـ 'الدولة' في الأعمدة الجانبية.")

    # -------------------------------------------------------------------------
    # التبويب الثالث: تحليل العلاقة الحيوية مع معهد البهوتي
    # -------------------------------------------------------------------------
    with tab3:
        st.subheader("🎯 مصفوفة تفكيك المتقدمين وعلاقتهم التاريخية بمعهد البهوتي")
        
        # بناء البيانات بناءً على شرحك الدقيق للفئات الـ 4
        behuti_segments = pd.DataFrame({
            "تصنيف الفئة وسلوكها": [
                "متقدمين جدد (لا علاقة لهم بالبهوتي مطلقا)",
                "قدامى البهوتي (سجل قديماً بالبهوتي.. لم يدرس ولم يدفع)",
                "طلاب البهوتي الحاليين (طالب مستمر يدرس الآن هناك)",
                "طلاب البهوتي المتوقفين (درس بالبهوتي سابقاً ولم يكمل)"
            ],
            "عدد الحسابات المنشأة": [
                last_row["المسجلين الجدد غير المسجلين في البهوتي"],
                last_row["المسجلين الجدد من قدامى البهوتي (لم يدرس ولم يدفع)"],
                last_row["المسجلين الجدد من طلاب البهوتي (طالب حالي يدرس البهوتي )"],
                last_row["المسجلين الجدد من طلاب البهوتي المتوقفين (درس ولم يكمل)"]
            ],
            "النسبة من إجمالي الدفعة": [
                f"{last_row['نسبة المسجلين الجدد غير المسجلين في البهوتي']:.1f}%",
                f"{last_row['نسبة المسجلين الجدد من قدامى البهوتي']:.1f}%",
                f"{last_row['نسبة المسجلين الجدد من طلاب البهوتي']:.1f}%",
                f"{last_row['نسبة المسجلين الجدد من طلبة البهوتي المتوقفين']:.1f}%"
            ]
        })
        
        st.dataframe(behuti_segments.style.set_properties(**{
            'background-color': '#fafbfc', 
            'color': '#0f2c59', 
            'border': '1px solid #d4af37'
        }), use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("💡 التقرير الاستراتيجي والتوصيات العملية لقسم التسويق والمبيعات")
        
        col_rec1, col_rec2, col_rec3 = st.columns(3)
        
        with col_rec1:
            st.markdown("📣 **استراتيجية الجذب الخارجي (الطلاب الجدد)**")
            new_non_behuti_rate = last_row['نسبة المسجلين الجدد غير المسجلين في البهوتي']
            if new_non_behuti_rate > 50:
                st.success(f"✅ المعهد يحقق نجاحاً باهراً في الجذب الخارجي! الطلاب الذين ليس لهم علاقة بالبهوتي يمثلون الأغلبية بـ ({new_non_behuti_rate:.1f}%). استمروا في حملات الميديا العامة.")
            else:
                st.warning(f"⚠️ الامتداد الخارجي يمثل ({new_non_behuti_rate:.1f}%). البرنامح يعتمد بشكل ثقيل على روافد البهوتي الداخلية، نقترح زيادة الموازنة الإعلانية على منصات التواصل لجلب دماء جديدة تماماً للمعهد.")
                
        with col_rec2:
            st.markdown("💼 **فرص فريق المبيعات (القدامى والمتوقفين)**")
            behuti_old = last_row['المسجلين الجدد من قدامى البهوتي (لم يدرس ولم يدفع)']
            behuti_stopped = last_row['المسجلين الجدد من طلاب البهوتي المتوقفين (درس ولم يكمل)']
            
            st.info(f"💡 يوجد **{int(behuti_old)}** طالب مسجل من 'قدامى البهوتي' الذين لم يدرسوا أو يدفعوا قط. هؤلاء يمتلكون نية باردة (Cold Leads)؛ إرسال كتيب تعريفي مبسط أو فيديو تشويقي عن البرنامج سيعيد إحياء حماسهم.")
            if behuti_stopped > 0:
                st.success(f"🔥 فئة المتوقفين سابقاً تضم **{int(behuti_stopped)}** طالب مسجل. هؤلاء خاضوا التجربة من قبل وتوقفوا؛ تواصل فريق الدعم معهم لحل مشكلاتهم السابقة سيضمن تحويلهم إلى دافعين بسرعة.")

        with col_rec3:
            st.markdown("🏛️ **تكامل المناهج (الطلاب الحاليين)**")
            behuti_current_rate = last_row['نسبة المسجلين الجدد من طلاب البهوتي']
            st.info(f"💡 نسبة الطلاب الحاليين بالبهوتي والذين سجلوا هنا هي ({behuti_current_rate:.1f}%). هذا يوضح رغبتهم العالية في التخصص الفقهي الحنبلي بجانب دراستهم الحالية؛ ينصح بعمل لقاء زووم خاص ومفتوح يجمع شيخ البرنامج مع طلاب البهوتي لرفع معدل الاهتمام الحركي.")

except Exception as e:
    st.error(f"⚠️ فشلت عملية معالجة الشيت الحالي: {e}")
    st.info("تأكد أن مسميات الأعمدة والـ Pivot Tables في شيت البهوتي مطابقة للأسماء المدخلة في الكود.")