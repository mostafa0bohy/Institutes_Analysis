import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="داشبورد التأهيل الفقهي الحنبلي - الدفعة 16", page_icon="📜")

# تطبيق التنسيق البصري الهوية البصرية لمعهد البهوتي
st.markdown("""
    <style>
    .main { background-color: #fcfbfa; } 
    h1, h2, h3 { color: #0f2c59; font-family: 'Arial', sans-serif; font-weight: 700; } 
    div[data-testid="stMetricValue"] { font-size: 32px; font-weight: bold; color: #d4af37; } 
    div[data-testid="stMetricLabel"] { font-size: 15px; color: #0f2c59; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { background-color: #f0f4f8; border-radius: 6px; padding: 12px 24px; color: #0f2c59; font-weight: bold; }
    .stTabs [aria-selected="true"] { background-color: #0f2c59; color: white; }
    hr { border-top: 2px solid #d4af37; }
    </style>
""", unsafe_allow_html=True)

# الهيدر والشعار
col_logo, col_title = st.columns([1, 7])
with col_logo:
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
def load_hanbali_data_final():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRmiO4XN9kssEddDdU8TuKtXOypsisNKiKejQ-DCDqcgmox6s7DV0zRJ6mxpLqpBA5XQr4JMgFE11_o/pub?gid=826428120&single=true&output=csv"
    
    # قراءة الشيت كـ مصفوفة نصوص خام بالكامل لتفادي أي تعارض في الأنواع
    raw_df = pd.read_csv(url, header=None).astype(str)
    
    # 1. استخراج الخط الزمني (أول 12 عموداً من الصف الرابع فما دون)
    timeline_df = raw_df.iloc[3:, :12].copy().reset_index(drop=True)
    col_names = [
        'Date', 'Old', 'Total_New', 'Today_New', 
        'Behuti_Old', 'Perc_Behuti_Old', 'Behuti_Curr', 'Perc_Behuti_Curr', 
        'Behuti_Stop', 'Perc_Behuti_Stop', 'Non_Behuti', 'Perc_Non_Behuti'
    ]
    timeline_df.columns = col_names
    
    # تحويل التواريخ وتصفية الأسطر الفارغة أو أسطر الإجماليات النصية
    timeline_df['Date'] = pd.to_datetime(timeline_df['Date'], errors='coerce')
    timeline_df = timeline_df.dropna(subset=['Date'])
    
    # تنظيف الأرقام والنسب للخط الزمني
    for col in col_names:
        if col == 'Date': continue
        if 'Perc' in col:
            timeline_df[col] = timeline_df[col].apply(clean_percentage)
        else:
            timeline_df[col] = timeline_df[col].str.replace(',', '', regex=True)
            timeline_df[col] = pd.to_numeric(timeline_df[col], errors='coerce').fillna(0)
            
    # 2. حل جذري لاستخراج الـ Pivot Tables بدون استخدام .str.contains على الـ DataFrame
    def safe_extract_pivot(search_text, full_matrix):
        # البحث عن رقم السطر ورقم العمود الذي يحتوي على الكلمة المفتاحية بشكل يدوي وآمن 100%
        found_row, found_col = None, None
        for r_idx in range(full_matrix.shape[0]):
            for c_idx in range(full_matrix.shape[1]):
                cell_value = str(full_matrix.iloc[r_idx, c_idx]).strip()
                if search_text == cell_value:
                    found_row, found_col = r_idx, c_idx
                    break
            if found_row is not None: break
            
        if found_row is借 None:
            return pd.DataFrame({'الفئة': [], 'العدد': []})
            
        # النزول لأسفل لقراءة عناصر الجدول الجانبي والعمود المجاور له
        items, counts = [], []
        for r_sub in range(found_row + 1, full_matrix.shape[0]):
            val_name = str(full_matrix.iloc[r_sub, found_col]).strip()
            
            # التوقف عند نهاية الجدول المصغر (خلايا فارغة أو إجماليات)
            if val_name == 'nan' or 'Total' in val_name or 'الإجمالي' in val_name or val_name == '':
                break
                
            # قراءة الرقم من العمود المجاور مباشرة
            try:
                count_val = str(full_matrix.iloc[r_sub, found_col + 1]).replace(',', '').strip()
                items.append(val_name)
                counts.append(float(count_val))
            except:
                continue
                
        return pd.DataFrame({'الفئة': items, 'العدد': counts})

    # استخراج الجداول الفرعية بأمان تام
    pivot_gender = safe_extract_pivot("الجنس", raw_df)
    pivot_geo = safe_extract_pivot("الدولة", raw_df)
    pivot_relation = safe_extract_pivot("العلاقة بالبهوتي", raw_df)
    pivot_age = safe_extract_pivot("العمر", raw_df)
    pivot_edu = safe_extract_pivot("المستوى التعليمي", raw_df)
    
    return timeline_df, pivot_gender, pivot_geo, pivot_relation, pivot_age, pivot_edu

try:
    df, p_gender, p_geo, p_relation, p_age, p_edu = load_hanbali_data_final()
    
    if df.empty:
        st.warning("⚠️ الشيت لا يحتوي على تواريخ نشطة حالياً.")
    else:
        last_row = df.iloc[-1]
        
        tab1, tab2, tab3 = st.tabs(["📈 حركية التسجيل اليومي", "📊 الخصائص الديموغرافية والتعليمية", "🎯 تحليل العلاقة مع معهد البهوتي"])
        
        with tab1:
            st.subheader("📌 أداء ووتيرة التدفق الحالية للمتقدمين")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("إجمالي المسجلين الجدد", f"{int(last_row['Total_New']):,}")
            col2.metric("مسجلي اليوم الفعلي", f"{int(last_row['Today_New']):,}")
            
            avg_daily = df['Today_New'].mean()
            col3.metric("متوسط التسجيل اليومي", f"{avg_daily:.1f} طالب / يوم")
            
            max_daily = df['Today_New'].max()
            max_date = df.loc[df['Today_New'] == max_daily, 'Date'].iloc[0].strftime('%Y-%m-%d')
            col4.metric("أعلى ذروة تسجيل", f"{int(max_daily)} طالب", f"تاريخ: {max_date}", delta_color="off")
            
            st.markdown("---")
            st.subheader("📉 المنحنى الزمني لتطور عمليات إنشاء الحسابات")
            df_plot = df.rename(columns={'Total_New': 'إجمالي المسجلين الجدد', 'Today_New': 'مسجلين اليوم'})
            fig_line = px.line(df_plot, x='Date', y=['إجمالي المسجلين الجدد', 'مسجلين اليوم'],
                               labels={'value': 'عدد الطلاب', 'variable': 'مؤشر القياس', 'Date': 'التاريخ'},
                               color_discrete_sequence=['#0f2c59', '#d4af37'], markers=True)
            st.plotly_chart(fig_line, use_container_width=True)

        with tab2:
            st.subheader("👥 البنية الإحصائية والديموغرافية للطلاب الجدد")
            col_demo1, col_demo2 = st.columns(2)
            
            with col_demo1:
                if not p_gender.empty:
                    fig_g = px.pie(p_gender, values='العدد', names='الفئة', hole=0.4,
                                   color_discrete_sequence=['#0f2c59', '#d4af37'], title="🧬 التوزيع الجندري")
                    st.plotly_chart(fig_g, use_container_width=True)
                else: st.info("ℹ️ جدول 'الجنس' غير متوفر حالياً.")
                    
                if not p_age.empty:
                    fig_a = px.bar(p_age, x='الفئة', y='العدد', text_auto=True, color_discrete_sequence=['#0f2c59'], title="⏳ التوزيع العمري")
                    st.plotly_chart(fig_a, use_container_width=True)
                else: st.info("ℹ️ جدول 'العمر' غير متوفر حالياً.")

            with col_demo2:
                if not p_edu.empty:
                    fig_e = px.bar(p_edu, y='الفئة', x='العدد', orientation='h', text_auto=True, color_discrete_sequence=['#2c5282'], title="🎓 المستوى التعليمي")
                    st.plotly_chart(fig_e, use_container_width=True)
                else: st.info("ℹ️ جدول 'المستوى التعليمي' غير متوفر حالياً.")
                    
                if not p_geo.empty:
                    p_geo_top = p_geo.sort_values(by='العدد', ascending=False).head(10)
                    fig_geo = px.bar(p_geo_top, x='الفئة', y='العدد', text_auto=True, color_discrete_sequence=['#b8860b'], title="🌍 أعلى 10 دول إقبالاً")
                    st.plotly_chart(fig_geo, use_container_width=True)
                else: st.info("ℹ️ جدول 'الدولة' غير متوفر حالياً.")

        with tab3:
            st.subheader("🎯 رصد وتحليل روافد المتقدمين وعلاقتهم التاريخية بمعهد البهوتي")
            behuti_segments = pd.DataFrame({
                "تصنيف الفئة وسلوكها": [
                    "متقدمين جدد (لا علاقة لهم بالبهوتي مطلقاً)",
                    "قدامى البهوتي (سجل قديماً بالبهوتي.. لم يدرس ولم يدفع)",
                    "طلاب البهوتي الحاليين (طالب مستمر يدرس الآن هناك)",
                    "طلاب البهوتي المتوقفين (درس بالبهوتي سابقاً ولم يكمل)"
                ],
                "عدد الحسابات المنشأة": [
                    last_row['Non_Behuti'], last_row['Behuti_Old'], last_row['Behuti_Curr'], last_row['Behuti_Stop']
                ],
                "النسبة من إجمالي الدفعة": [
                    f"{last_row['Perc_Non_Behuti']:.1f}%", f"{last_row['Perc_Behuti_Old']:.1f}%", f"{last_row['Perc_Behuti_Curr']:.1f}%", f"{last_row['Perc_Behuti_Stop']:.1f}%"
                ]
            })
            st.dataframe(behuti_segments, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"⚠️ خطأ غير متوقع: {e}")
