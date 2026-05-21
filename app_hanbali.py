import streamlit as st
import pandas as pd
import plotly.express as px

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
def load_hanbali_data_by_index():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRmiO4XN9kssEddDdU8TuKtXOypsisNKiKejQ-DCDqcgmox6s7DV0zRJ6mxpLqpBA5XQr4JMgFE11_o/pub?gid=826428120&single=true&output=csv"
    
    raw_df = pd.read_csv(url, header=None)
    side_data = raw_df.iloc[1:].copy()
    
    # استخلاص الخط الزمني من الصف الرابع (index 3) واختيار أول 12 عموداً
    timeline_df = raw_df.iloc[3:, :12].copy().reset_index(drop=True)
    
    # إعطاء أسماء أعمدة بسيطة وموحدة للعمل عليها
    col_names = [
        'Date',             # 0
        'Old',              # 1
        'Total_New',        # 2
        'Today_New',        # 3
        'Behuti_Old',       # 4
        'Perc_Behuti_Old',  # 5
        'Behuti_Curr',      # 6
        'Perc_Behuti_Curr', # 7
        'Behuti_Stop',      # 8
        'Perc_Behuti_Stop', # 9
        'Non_Behuti',       # 10
        'Perc_Non_Behuti'   # 11
    ]
    timeline_df.columns = col_names
    
    # تنظيف التاريخ
    timeline_df['Date'] = pd.to_datetime(timeline_df['Date'], errors='coerce')
    timeline_df = timeline_df.dropna(subset=['Date'])
    
    # تنظيف الأرقام والنسب
    for i, col in enumerate(col_names):
        if col == 'Date': continue
        if 'Perc' in col:
            timeline_df[col] = timeline_df[col].apply(clean_percentage)
        else:
            if timeline_df[col].dtype == 'object':
                timeline_df[col] = timeline_df[col].astype(str).str.replace(',', '', regex=True)
            timeline_df[col] = pd.to_numeric(timeline_df[col], errors='coerce').fillna(0)
            
    # تصفية السطور بناءً على عمود Total_New
    timeline_df = timeline_df[timeline_df['Total_New'] > 0]
    
    # استخراج الجداول الجانبية
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
    df, p_gender, p_geo, p_relation, p_age, p_edu = load_hanbali_data_by_index()
    
    if df.empty:
        st.warning("⚠️ لم يتم العثور على بيانات نشطة لتاريخ اليوم في الشيت، يرجى التحقق من إدخال البيانات.")
    else:
        last_row = df.iloc[-1]
        
        tab1, tab2, tab3 = st.tabs(["📈 حركية التسجيل اليومي", "📊 الخصائص الديموغرافية والتعليمية", "🎯 تحليل العلاقة مع معهد البهوتي"])
        
        with tab1:
            st.subheader("📌 أداء ووتيرة التدفق الحالية للمتقدمين")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("إجمالي المسجلين الجدد (تراكمي)", f"{int(last_row['Total_New']):,}")
            col2.metric("مسجلي اليوم الفعلي", f"{int(last_row['Today_New']):,}")
            
            avg_daily = df['Today_New'].mean()
            col3.metric("متوسط التسجيل اليومي", f"{avg_daily:.1f} طالب / يوم")
            
            max_daily = df['Today_New'].max()
            max_date = df.loc[df['Today_New'] == max_daily, 'Date'].iloc[0].strftime('%Y-%m-%d')
            col4.metric("أعلى ذروة تسجيل يومية", f"{int(max_daily)} طالب", f"تاريخ: {max_date}", delta_color="off")
            
            st.markdown("---")
            st.subheader("📉 المنحنى الزمني لتطور عمليات إنشاء الحسابات للدفعة 16")
            
            # تغيير أسماء الأعمدة للعرض في الرسم البياني
            df_plot = df.rename(columns={'Total_New': 'إجمالي المسجلين الجدد', 'Today_New': 'مسجلين اليوم'})
            fig_line = px.line(df_plot, x='Date', y=['إجمالي المسجلين الجدد', 'مسجلين اليوم'],
                               labels={'value': 'عدد الطلاب', 'variable': 'مؤشر القياس', 'Date': 'التاريخ'},
                               color_discrete_sequence=['#0f2c59', '#d4af37'], markers=True)
            fig_line.update_layout(hovermode="x unified")
            st.plotly_chart(fig_line, use_container_width=True)

        with tab2:
            st.subheader("👥 البنية الإحصائية والديموغرافية للطلاب الجدد")
            
            col_demo1, col_demo2 = st.columns(2)
            
            with col_demo1:
                if not p_gender.empty:
                    fig_g = px.pie(p_gender, values='العدد', names='الفئة', hole=0.4,
                                   color_discrete_sequence=['#0f2c59', '#d4af37'],
                                   title="🧬 التوزيع الجندري بين الجنسين")
                    st.plotly_chart(fig_g, use_container_width=True)
                else:
                    st.info("ℹ️ لم يتم العثور على جدول 'الجنس' في البيانات الجانبية بعد.")
                    
                if not p_age.empty:
                    fig_a = px.bar(p_age, x='الفئة', y='العدد', text_auto=True,
                                   color_discrete_sequence=['#0f2c59'],
                                   title="⏳ التوزيع العددي للفئات العمرية للمتقدمين")
                    st.plotly_chart(fig_a, use_container_width=True)
                else:
                    st.info("ℹ️ لم يتم العثور على جدول 'العمر' في البيانات الجانبية بعد.")

            with col_demo2:
                if not p_edu.empty:
                    fig_e = px.bar(p_edu, y='الفئة', x='العدد', orientation='h', text_auto=True,
                                   color_discrete_sequence=['#2c5282'],
                                   title="🎓 توزيع المستويات التعليمية والأكاديمية للطلاب")
                    st.plotly_chart(fig_e, use_container_width=True)
                else:
                    st.info("ℹ️ لم يتم العثور على جدول 'المستوى التعليمي' في البيانات الجانبية بعد.")
                    
                if not p_geo.empty:
                    p_geo_top = p_geo.sort_values(by='العدد', ascending=False).head(10)
                    fig_geo = px.bar(p_geo_top, x='الفئة', y='العدد', text_auto=True,
                                     color_discrete_sequence=['#b8860b'],
                                     title="🌍 التوزيع الجغرافي (أعلى 10 دول من حيث الإقبال)")
                    st.plotly_chart(fig_geo, use_container_width=True)
                else:
                    st.info("ℹ️ لم يتم العثور على جدول 'الدولة' في البيانات الجانبية بعد.")

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
                    last_row['Non_Behuti'],
                    last_row['Behuti_Old'],
                    last_row['Behuti_Curr'],
                    last_row['Behuti_Stop']
                ],
                "النسبة من إجمالي الدفعة": [
                    f"{last_row['Perc_Non_Behuti']:.1f}%",
                    f"{last_row['Perc_Behuti_Old']:.1f}%",
                    f"{last_row['Perc_Behuti_Curr']:.1f}%",
                    f"{last_row['Perc_Behuti_Stop']:.1f}%"
                ]
            })
            
            st.dataframe(behuti_segments.style.set_properties(**{
                'background-color': '#fafbfc', 
                'color': '#0f2c59', 
                'border': '1px solid #d4af37'
            }), use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.subheader("💡 التقرير الاستراتيجي والتوصيات العملية (تحديث التريند الحالي)")
            
            col_rec1, col_rec2, col_rec3 = st.columns(3)
            
            with col_rec1:
                st.markdown("📣 **استراتيجية الجذب الخارجي**")
                new_non_behuti_rate = last_row['Perc_Non_Behuti']
                if new_non_behuti_rate > 50:
                    st.success(f"✅ الجذب الخارجي ممتاز! النسبة تسجل ({new_non_behuti_rate:.1f}%) من الطلاب الجدد تماماً خارج نظام البهوتي. هذا يعني نجاح انتشار الهوية التسويقية المستقلة للتأهيل الفقهي.")
                else:
                    st.warning(f"⚠️ الامتداد الخارجي يمثل ({new_non_behuti_rate:.1f}%). البرنامج يعتمد بشكل ثقيل على القنوات الداخلية؛ يُنصح بإطلاق حملات ممولة موجهة لشرائح جديدة كلياً لرفع الوعي بالبرنامج خارج نطاق المعهد الداخلي.")
                    
            with col_rec2:
                st.markdown("💼 **توصيات فريق المبيعات واستغلال الـ Leads**")
                behuti_old = last_row['Behuti_Old']
                behuti_stopped = last_row['Behuti_Stop']
                
                st.info(f"💡 هناك **{int(behuti_old)}** طالب مسجل من 'قدامى البهوتي' (سجلوا فقط ولم يدرسوا). هؤلاء يمثلون فرصة إعادة تنشيط (Re-engagement) قوية عبر إرسال محتوى تعريفي تخصصي خفيف يربط الفقه بالواقع.")
                if behuti_stopped > 0:
                    st.success(f"🔥 فئة المتوقفين تضم **{int(behuti_stopped)}** طالب قاموا بالتسجيل مجدداً. هؤلاء لديهم رغبة حقيقية في العودة؛ مكالمة هاتفية أو رسالة دعم مخصصة من فريق المبيعات كفيلة بتحويلهم لملتزمين بالدراسة فوراً.")

            with col_rec3:
                st.markdown("🏛️ **تكامل المناهج والولاء**")
                behuti_current_rate = last_row['Perc_Behuti_Curr']
                st.info(f"💡 نسبة الطلاب الحاليين بالبهوتي والذين قاموا بالتسجيل هنا بلغت ({behuti_current_rate:.1f}%). هذا التريند يعكس رغبة صادقة من طلاب المعهد الحاليين لتعميق دراستهم التخصصية بالمتون الحنبلية.")

except Exception as e:
    st.error(f"⚠️ فشل تحليل الشيت الفعلي: {e}")
