import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(layout="wide", page_title="داشبورد التأهيل الفقهي الحنبلي - الدفعة 16", page_icon="📜")

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
def load_hanbali_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRmiO4XN9kssEddDdU8TuKtXOypsisNKiKejQ-DCDqcgmox6s7DV0zRJ6mxpLqpBA5XQr4JMgFE11_o/pub?gid=826428120&single=true&output=csv"
    
    raw_df = pd.read_csv(url, header=None)
    
    headers = raw_df.iloc[1].astype(str).str.replace('\n', ' ', regex=True).str.strip()
    raw_df.columns = headers
    
    # الأسماء الدقيقة من الصورة المرفقة
    main_columns = [
        'التاريخ',
        'إجمالي المسجلين الجدد (أنشأ حسابا على الموقع)',
        'مسجلي اليوم (أنشأ حسابا على الموقع)',
        'المسجلين الجدد من قدامى البهوتي (لم يدرس ولم يدفع)',
        'نسبة المسجلين الجدد من قدامى البهوتي',
        'المسجلين الجدد من طلاب البهوتي (طالب حالي يدرس البهوتي )',
        'نسبة المسجلين الجدد من طلاب البهوتي',
        'المسجلين الجدد من طلاب البهوتي المتوقفين (درس ولم يكمل)',
        'نسبة المسجلين الجدد من طلبة البهوتي المتوقفين',
        'المسجلين الجدد غير المسجلين في البهوتي',
        'نسبة المسجلين الجدد غير المسجلين في البهوتي'
    ]
    
    available_cols = [col for col in main_columns if col in raw_df.columns]
    
    timeline_df = raw_df.iloc[3:][available_cols].copy().reset_index(drop=True)
    timeline_df['التاريخ'] = pd.to_datetime(timeline_df['التاريخ'], errors='coerce')
    timeline_df = timeline_df.dropna(subset=['التاريخ'])
    
    for col in timeline_df.columns:
        if col == 'التاريخ':
            continue
        if 'نسبة' in str(col):
            timeline_df[col] = timeline_df[col].apply(clean_percentage)
        else:
            if timeline_df[col].dtype == 'object':
                timeline_df[col] = timeline_df[col].astype(str).str.replace(',', '', regex=True)
            timeline_df[col] = pd.to_numeric(timeline_df[col], errors='coerce').fillna(0)
            
    # تغيير الشرط للبحث بالاسم الجديد
    if 'إجمالي المسجلين الجدد (أنشأ حسابا على الموقع)' in timeline_df.columns:
        timeline_df = timeline_df[timeline_df['إجمالي المسجلين الجدد (أنشأ حسابا على الموقع)'] > 0]
    
    side_data = raw_df.iloc[1:].copy()
    
    def extract_pivot(search_header, data_frame):
        for col in data_frame.columns:
            col_data_str = data_frame[col].astype(str)
            if col_data_str.str.contains(search_header, na=False, regex=False).any():
                idx = data_frame[col_data_str == search_header].index[0]
                sub_df = data_frame.loc[idx:].copy()
                items, counts = [], []
                
                for _, row in sub_df.iterrows():
                    val_name = str(row[col]).strip()
                    if val_name == 'nan' or 'Grand Total' in val_name or 'الإجمالي' in val_name or val_name == search_header:
                        if val_name == search_header: continue
                        break
                    
                    next_col_idx = list(data_frame.columns).index(col) + 1
                    try:
                        count_val = float(str(row.iloc[next_col_idx]).replace(',', ''))
                        items.append(val_name)
                        counts.append(count_val)
                    except:
                        continue
                return pd.DataFrame({'الفئة': items, 'العدد': counts})
        return pd.DataFrame({'الفئة': [], 'العدد': []})

    pivot_gender = extract_pivot("الجنس", side_data)
    pivot_geo = extract_pivot("الدولة", side_data)
    pivot_relation = extract_pivot("العلاقة بالبهوتي", side_data)
    pivot_age = extract_pivot("العمر", side_data)
    pivot_edu = extract_pivot("المستوى التعليمي", side_data)
    
    return timeline_df, pivot_gender, pivot_geo, pivot_relation, pivot_age, pivot_edu

try:
    df, p_gender, p_geo, p_relation, p_age, p_edu = load_hanbali_data()
    
    if df.empty:
        st.warning("البيانات فارغة حالياً. يرجى التأكد من الشيت.")
    else:
        last_row = df.iloc[-1]
        
        tab1, tab2, tab3 = st.tabs(["📈 حركية التسجيل اليومي", "📊 الخصائص الديموغرافية والتعليمية", "🎯 تحليل العلاقة مع معهد البهوتي"])
        
        with tab1:
            st.subheader("📌 نظرة عامة على وتيرة التدفق الحالية")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("إجمالي المسجلين الجدد تراكمي", f"{int(last_row['إجمالي المسجلين الجدد (أنشأ حسابا على الموقع)']):,}")
            col2.metric("مسجلي اليوم الفعلي", f"{int(last_row['مسجلي اليوم (أنشأ حسابا على الموقع)']):,}")
            
            avg_daily = df['مسجلي اليوم (أنشأ حسابا على الموقع)'].mean()
            col3.metric("متوسط التسجيل اليومي", f"{avg_daily:.1f} طالب / يوم")
            
            max_daily = df['مسجلي اليوم (أنشأ حسابا على الموقع)'].max()
            max_date = df.loc[df['مسجلي اليوم (أنشأ حسابا على الموقع)'] == max_daily, 'التاريخ'].iloc[0].strftime('%Y-%m-%d')
            col4.metric("أعلى ذروة تسجيل يومية", f"{int(max_daily)} طالب", f"في تاريخ {max_date}", delta_color="off")
            
            st.markdown("---")
            st.subheader("📉 المنحنى الزمني لتطور عمليات إنشاء الحسابات")
            
            fig_line = px.line(df, x='التاريخ', y=['إجمالي المسجلين الجدد (أنشأ حسابا على الموقع)', 'مسجلي اليوم (أنشأ حسابا على الموقع)'],
                               labels={'value': 'عدد الطلاب', 'variable': 'مؤشر القياس'},
                               color_discrete_sequence=['#0f2c59', '#d4af37'], markers=True)
            fig_line.update_layout(hovermode="x unified")
            st.plotly_chart(fig_line, use_container_width=True)

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
                    st.info("لم يتم العثور على جدول 'الجنس'.")
                    
                if not p_age.empty:
                    fig_a = px.bar(p_age, x='الفئة', y='العدد', text_auto=True,
                                   color_discrete_sequence=['#0f2c59'],
                                   title="⏳ التوزيع المئوي للفئات العمرية للمتقدمين")
                    st.plotly_chart(fig_a, use_container_width=True)
                else:
                    st.info("لم يتم العثور على جدول 'العمر'.")

            with col_demo2:
                if not p_edu.empty:
                    fig_e = px.bar(p_edu, y='الفئة', x='العدد', orientation='h', text_auto=True,
                                   color_discrete_sequence=['#2c5282'],
                                   title="🎓 توزيع المستويات التعليمية والأكاديمية للطلاب")
                    st.plotly_chart(fig_e, use_container_width=True)
                else:
                    st.info("لم يتم العثور على جدول 'المستوى التعليمي'.")
                    
                if not p_geo.empty:
                    p_geo_top = p_geo.sort_values(by='العدد', ascending=False).head(10)
                    fig_geo = px.bar(p_geo_top, x='الفئة', y='العدد', text_auto=True,
                                     color_discrete_sequence=['#b8860b'],
                                     title="🌍 التوزيع الجغرافي (أعلى 10 دول)")
                    st.plotly_chart(fig_geo, use_container_width=True)
                else:
                    st.info("لم يتم العثور على جدول 'الدولة'.")

        with tab3:
            st.subheader("🎯 مصفوفة تفكيك المتقدمين وعلاقتهم التاريخية بمعهد البهوتي")
            
            behuti_segments = pd.DataFrame({
                "تصنيف الفئة وسلوكها": [
                    "متقدمين جدد (لا علاقة لهم بالبهوتي مطلقا)",
                    "قدامى البهوتي (سجل قديماً بالبهوتي.. لم يدرس ولم يدفع)",
                    "طلاب البهوتي الحاليين (طالب مستمر يدرس الآن هناك)",
                    "طلاب البهوتي المتوقفين (درس بالبهوتي سابقاً ولم يكمل)"
                ],
                "عدد الحسابات المنشأة": [
                    last_row.get("المسجلين الجدد غير المسجلين في البهوتي", 0),
                    last_row.get("المسجلين الجدد من قدامى البهوتي (لم يدرس ولم يدفع)", 0),
                    last_row.get("المسجلين الجدد من طلاب البهوتي (طالب حالي يدرس البهوتي )", 0),
                    last_row.get("المسجلين الجدد من طلاب البهوتي المتوقفين (درس ولم يكمل)", 0)
                ],
                "النسبة من إجمالي الدفعة": [
                    f"{last_row.get('نسبة المسجلين الجدد غير المسجلين في البهوتي', 0):.1f}%",
                    f"{last_row.get('نسبة المسجلين الجدد من قدامى البهوتي', 0):.1f}%",
                    f"{last_row.get('نسبة المسجلين الجدد من طلاب البهوتي', 0):.1f}%",
                    f"{last_row.get('نسبة المسجلين الجدد من طلبة البهوتي المتوقفين', 0):.1f}%"
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
                st.markdown("📣 **استراتيجية الجذب الخارجي**")
                new_non_behuti_rate = last_row.get('نسبة المسجلين الجدد غير المسجلين في البهوتي', 0)
                if new_non_behuti_rate > 50:
                    st.success(f"✅ الجذب الخارجي قوي! {new_non_behuti_rate:.1f}% من المسجلين لا علاقة لهم بالبهوتي.")
                else:
                    st.warning(f"⚠️ الاعتماد الأكبر على طلبة البهوتي. نقترح حملات تسويقية خارجية لاستقطاب المهتمين بالفقه الحنبلي من خارج دوائر المعهد.")
                    
            with col_rec2:
                st.markdown("💼 **فرص فريق المبيعات**")
                behuti_old = last_row.get('المسجلين الجدد من قدامى البهوتي (لم يدرس ولم يدفع)', 0)
                behuti_stopped = last_row.get('المسجلين الجدد من طلاب البهوتي المتوقفين (درس ولم يكمل)', 0)
                
                st.info(f"💡 {int(behuti_old)} طالب من 'قدامى البهوتي' يمتلكون نية باردة. يحتاجون رسائل تسويقية تشويقية.")
                if behuti_stopped > 0:
                    st.success(f"🔥 {int(behuti_stopped)} طالب من 'المتوقفين' سجلوا من جديد. فرصة ممتازة للتحويل بدعم بسيط.")

            with col_rec3:
                st.markdown("🏛️ **تكامل المناهج**")
                behuti_current_rate = last_row.get('نسبة المسجلين الجدد من طلاب البهوتي', 0)
                st.info(f"💡 {behuti_current_rate:.1f}% من مسجليكم هم طلاب مستمرون بالبهوتي. هذا مؤشر لولاء عالي وحرص على التخصص.")

except Exception as e:
    st.error(f"⚠️ حدث خطأ أثناء عرض البيانات: {e}")
