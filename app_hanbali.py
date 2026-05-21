import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    layout="wide",
    page_title="داشبورد التأهيل الفقهي الحنبلي - الدفعة 16",
    page_icon="📜"
)

# ─── ثيم معهد البهوتي ────────────────────────────────────────────────────────
NAVY   = "#0f2c59"
GOLD   = "#c9a227"
CREAM  = "#faf8f3"
LIGHT  = "#f0ece0"
WHITE  = "#ffffff"
GRAY   = "#6b7280"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@400;600;700&family=Cairo:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Cairo', 'Noto Naskh Arabic', sans-serif !important;
        direction: rtl;
    }}
    .main {{ background-color: {CREAM}; }}
    .block-container {{ padding-top: 1.5rem; padding-bottom: 2rem; }}

    /* بطاقات المؤشرات */
    [data-testid="stMetric"] {{
        background: {WHITE};
        border-radius: 12px;
        padding: 18px 20px;
        border-right: 4px solid {GOLD};
        box-shadow: 0 2px 8px rgba(15,44,89,0.08);
    }}
    [data-testid="stMetricValue"] {{
        font-size: 2rem !important;
        font-weight: 800 !important;
        color: {NAVY} !important;
    }}
    [data-testid="stMetricLabel"] {{
        font-size: 0.85rem !important;
        color: {GRAY} !important;
        font-weight: 600 !important;
    }}
    [data-testid="stMetricDelta"] {{
        font-size: 0.8rem !important;
    }}

    /* تبويبات */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 6px;
        background: {LIGHT};
        padding: 6px;
        border-radius: 10px;
    }}
    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        border-radius: 8px;
        padding: 10px 22px;
        color: {NAVY};
        font-weight: 700;
        font-size: 0.9rem;
    }}
    .stTabs [aria-selected="true"] {{
        background: {NAVY} !important;
        color: {WHITE} !important;
    }}

    /* جداول البيانات */
    [data-testid="stDataFrame"] {{ border-radius: 10px; overflow: hidden; }}

    /* تنبيهات */
    .stAlert {{ border-radius: 10px; }}

    /* الهيدر */
    .dash-header {{
        background: linear-gradient(135deg, {NAVY} 0%, #1a3f7a 100%);
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 20px;
        box-shadow: 0 4px 20px rgba(15,44,89,0.2);
    }}
    .dash-header h1 {{
        color: {WHITE};
        margin: 0;
        font-size: 1.6rem;
        font-weight: 800;
    }}
    .dash-header p {{
        color: {GOLD};
        margin: 4px 0 0;
        font-size: 0.9rem;
    }}

    /* فاصل ذهبي */
    .gold-divider {{
        height: 2px;
        background: linear-gradient(90deg, {GOLD}, transparent);
        border: none;
        margin: 20px 0;
    }}

    /* بطاقة التوصية */
    .rec-card {{
        background: {WHITE};
        border-radius: 12px;
        padding: 20px;
        border-top: 3px solid {GOLD};
        box-shadow: 0 2px 8px rgba(15,44,89,0.06);
        height: 100%;
    }}
    .rec-card h4 {{
        color: {NAVY};
        font-size: 1rem;
        margin: 0 0 12px;
        font-weight: 700;
    }}

    h2, h3 {{ color: {NAVY} !important; font-weight: 700 !important; }}
    </style>
""", unsafe_allow_html=True)

# ─── الهيدر ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="dash-header">
    <img src="https://new.albuhutifiqh.online/_next/image?url=https%3A%2F%2Fcdn.albuhutifiqh.online%2Fstatic_pages%2F5%2Fhero_image_1777986406617&w=750&q=90"
         style="width:80px; height:80px; object-fit:cover; border-radius:12px; border:2px solid {GOLD};">
    <div>
        <h1>📜 لوحة المؤشرات الذكية | برنامج التأهيل الفقهي الحنبلي</h1>
        <p>متابعة حية وتحليل إحصائي متقدم لأداء التسجيل بالدفعة السادسة عشرة وعلاقتها بطلاب معهد البهوتي</p>
    </div>
</div>
""", unsafe_allow_html=True)


# ─── دوال المساعدة ───────────────────────────────────────────────────────────
def clean_percentage(val):
    if pd.isna(val) or str(val).strip() in ('', '#DIV/0!', 'nan'):
        return 0.0
    val_str = str(val).strip().replace('%', '').replace(',', '')
    try:
        f = float(val_str)
        return f * 100 if f < 1 else f
    except ValueError:
        return 0.0


def clean_number(val):
    if pd.isna(val) or str(val).strip() in ('', 'nan'):
        return 0
    try:
        return int(float(str(val).replace(',', '')))
    except (ValueError, TypeError):
        return 0


# ─── تحميل البيانات ──────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_data():
    url = (
        "https://docs.google.com/spreadsheets/d/e/"
        "2PACX-1vRmiO4XN9kssEddDdU8TuKtXOypsisNKiKejQ-DCDqcgmox6s7DV0zRJ6mxpLqpBA5XQr4JMgFE11_o"
        "/pub?gid=826428120&single=true&output=csv"
    )

    raw = pd.read_csv(url, header=None, dtype=str)

    # ── 1. جدول الحركة اليومية ─────────────────────────────────────────────
    # العناوين في الصف 2 (index 1)، البيانات من الصف 4 (index 3)
    # الأعمدة: A-L  (0-11)  → 12 عمود
    COL_NAMES = [
        'Date',
        'Old',           # مهمل
        'Total_New',     # إجمالي مسجلين جدد (تراكمي)
        'Today_New',     # مسجلين اليوم
        'Behuti_Old',    # قدامى البهوتي (لم يدرس/يدفع)
        'Perc_Behuti_Old',
        'Behuti_Curr',   # طلاب بهوتي حاليين
        'Perc_Behuti_Curr',
        'Behuti_Stop',   # طلاب بهوتي متوقفين
        'Perc_Behuti_Stop',
        'Non_Behuti',    # غير مسجلين بالبهوتي
        'Perc_Non_Behuti',
    ]

    timeline_raw = raw.iloc[3:, :12].copy().reset_index(drop=True)
    timeline_raw.columns = COL_NAMES

    # تصفية الصفوف التي تحتوي على تاريخ صالح فقط
    timeline_raw['Date'] = pd.to_datetime(timeline_raw['Date'], errors='coerce')
    df = timeline_raw.dropna(subset=['Date']).copy().reset_index(drop=True)

    if df.empty:
        return df, *[pd.DataFrame(columns=['الفئة', 'العدد'])] * 5

    # تنظيف الأرقام والنسب
    for col in COL_NAMES[1:]:
        if 'Perc' in col:
            df[col] = df[col].apply(clean_percentage)
        else:
            df[col] = df[col].apply(clean_number)

    # ── 2. جداول التوزيع (pivot tables) من عمود N فصاعداً ─────────────────
    # البحث في كامل الجدول الخام ابتداءً من العمود 13 (index 13 = عمود N)
    side_raw = raw.iloc[:, 13:].copy().reset_index(drop=True)

    def extract_pivot(header_text):
        """يبحث عن header_text في side_raw ويستخرج الجدول أسفله."""
        for c in range(side_raw.shape[1]):
            col_series = side_raw.iloc[:, c].astype(str).str.strip()
            matches = col_series[col_series == header_text]
            if matches.empty:
                continue
            start_idx = matches.index[0]
            items, counts = [], []
            for i in range(start_idx + 1, len(side_raw)):
                name = str(side_raw.iloc[i, c]).strip()
                # توقف عند الخلايا الفارغة أو الإجماليات
                if name in ('', 'nan') or any(
                    x in name for x in ['Grand Total', 'الإجمالي', 'إجمالي']
                ):
                    break
                try:
                    count = float(str(side_raw.iloc[i, c + 1]).replace(',', ''))
                    items.append(name)
                    counts.append(count)
                except (ValueError, IndexError):
                    break
            if items:
                return pd.DataFrame({'الفئة': items, 'العدد': counts})
        return pd.DataFrame(columns=['الفئة', 'العدد'])

    p_gender   = extract_pivot("الجنس")
    p_geo      = extract_pivot("الدولة")
    p_relation = extract_pivot("العلاقة بالبهوتي")
    p_age      = extract_pivot("العمر")
    p_edu      = extract_pivot("المستوى التعليمي")

    return df, p_gender, p_geo, p_relation, p_age, p_edu


# ─── تنسيق الرسوم البيانية ──────────────────────────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Cairo, sans-serif", color=NAVY),
    title_font=dict(size=14, color=NAVY, family="Cairo, sans-serif"),
    margin=dict(l=10, r=10, t=50, b=10),
)


def style_fig(fig):
    fig.update_layout(**CHART_LAYOUT)
    fig.update_xaxes(gridcolor="#e8e4d9", tickfont_family="Cairo, sans-serif")
    fig.update_yaxes(gridcolor="#e8e4d9", tickfont_family="Cairo, sans-serif")
    return fig


# ─── التحميل ─────────────────────────────────────────────────────────────────
with st.spinner("⏳ جاري تحميل البيانات…"):
    try:
        df, p_gender, p_geo, p_relation, p_age, p_edu = load_data()
    except Exception as ex:
        st.error(f"⚠️ فشل تحميل البيانات: {ex}")
        st.stop()

if df.empty:
    st.warning("⚠️ لم يتم العثور على بيانات تحتوي على تواريخ صالحة. تحقق من أن الشيت مفتوح للعموم (Publish to web).")
    st.stop()

last = df.iloc[-1]

# ─── التبويبات ───────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "📈 حركية التسجيل اليومي",
    "📊 الخصائص الديموغرافية والتعليمية",
    "🎯 تحليل العلاقة مع معهد البهوتي",
])


# ══════════════════════════════════════════════════════════════════════════════
# تبويب 1 — حركية التسجيل
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("📌 مؤشرات الأداء اللحظية")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("إجمالي المسجلين الجدد", f"{int(last['Total_New']):,}")
    c2.metric("مسجلو اليوم", f"{int(last['Today_New']):,}")

    avg = df['Today_New'].mean()
    c3.metric("متوسط التسجيل اليومي", f"{avg:.1f} طالب/يوم")

    max_v = df['Today_New'].max()
    max_d = df.loc[df['Today_New'] == max_v, 'Date'].iloc[0].strftime('%Y-%m-%d')
    c4.metric("أعلى ذروة يومية", f"{int(max_v):,} طالب", f"بتاريخ {max_d}", delta_color="off")

    st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)
    st.subheader("📉 المنحنى الزمني لتطور عمليات التسجيل")

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=df['Date'], y=df['Total_New'],
        name="إجمالي المسجلين (تراكمي)",
        line=dict(color=NAVY, width=2.5),
        fill='tozeroy', fillcolor=f"rgba(15,44,89,0.08)",
        mode='lines+markers', marker=dict(size=5),
    ))
    fig1.add_trace(go.Bar(
        x=df['Date'], y=df['Today_New'],
        name="مسجلو اليوم",
        marker_color=GOLD, opacity=0.7,
        yaxis='y2',
    ))
    fig1.update_layout(
        **CHART_LAYOUT,
        hovermode="x unified",
        legend=dict(orientation="h", y=1.1),
        yaxis=dict(title="تراكمي", gridcolor="#e8e4d9"),
        yaxis2=dict(title="يومي", overlaying='y', side='left', gridcolor="#e8e4d9"),
    )
    st.plotly_chart(fig1, use_container_width=True)

    # جدول آخر 10 أيام
    st.subheader("🗓️ آخر 10 أيام")
    recent = df[['Date', 'Total_New', 'Today_New']].tail(10).copy()
    recent['Date'] = recent['Date'].dt.strftime('%Y-%m-%d')
    recent.columns = ['التاريخ', 'الإجمالي التراكمي', 'مسجلو اليوم']
    st.dataframe(recent[::-1].reset_index(drop=True), use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# تبويب 2 — الديموغرافيا
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("👥 البنية الإحصائية والديموغرافية للطلاب الجدد")

    col_a, col_b = st.columns(2)

    # التوزيع الجندري
    with col_a:
        if not p_gender.empty:
            fig_g = px.pie(
                p_gender, values='العدد', names='الفئة', hole=0.45,
                color_discrete_sequence=[NAVY, GOLD, "#2c6fad", "#e8c547"],
                title="🧬 التوزيع بين الجنسين",
            )
            fig_g.update_traces(textfont_family="Cairo, sans-serif", textfont_size=13)
            st.plotly_chart(style_fig(fig_g), use_container_width=True)
        else:
            st.info("ℹ️ لم يُعثر على جدول 'الجنس' في الشيت.")

        # العلاقة بالبهوتي (جدول التوزيع من الـ pivot)
        if not p_relation.empty:
            fig_r = px.pie(
                p_relation, values='العدد', names='الفئة', hole=0.45,
                color_discrete_sequence=[NAVY, GOLD, "#1a5276", "#f0c040", "#85929e"],
                title="🏛️ توزيع العلاقة بمعهد البهوتي",
            )
            fig_r.update_traces(textfont_family="Cairo, sans-serif", textfont_size=12)
            st.plotly_chart(style_fig(fig_r), use_container_width=True)
        else:
            st.info("ℹ️ لم يُعثر على جدول 'العلاقة بالبهوتي' في الشيت.")

    with col_b:
        # الفئات العمرية
        if not p_age.empty:
            fig_a = px.bar(
                p_age, x='الفئة', y='العدد', text_auto=True,
                color='العدد',
                color_continuous_scale=[[0, LIGHT], [0.5, GOLD], [1, NAVY]],
                title="⏳ التوزيع العمري للمتقدمين",
            )
            fig_a.update_traces(textfont_family="Cairo, sans-serif")
            fig_a.update_coloraxes(showscale=False)
            st.plotly_chart(style_fig(fig_a), use_container_width=True)
        else:
            st.info("ℹ️ لم يُعثر على جدول 'العمر' في الشيت.")

        # المستوى التعليمي
        if not p_edu.empty:
            p_edu_s = p_edu.sort_values('العدد')
            fig_e = px.bar(
                p_edu_s, y='الفئة', x='العدد', orientation='h', text_auto=True,
                color='العدد',
                color_continuous_scale=[[0, LIGHT], [0.5, "#2c6fad"], [1, NAVY]],
                title="🎓 توزيع المستويات التعليمية",
            )
            fig_e.update_traces(textfont_family="Cairo, sans-serif")
            fig_e.update_coloraxes(showscale=False)
            st.plotly_chart(style_fig(fig_e), use_container_width=True)
        else:
            st.info("ℹ️ لم يُعثر على جدول 'المستوى التعليمي' في الشيت.")

    # التوزيع الجغرافي — صف كامل
    if not p_geo.empty:
        st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)
        top_n = min(15, len(p_geo))
        p_geo_top = p_geo.sort_values('العدد', ascending=False).head(top_n)
        fig_geo = px.bar(
            p_geo_top, x='الفئة', y='العدد', text_auto=True,
            color='العدد',
            color_continuous_scale=[[0, "#e8c547"], [0.5, GOLD], [1, NAVY]],
            title=f"🌍 التوزيع الجغرافي — أعلى {top_n} دولة",
        )
        fig_geo.update_traces(textfont_family="Cairo, sans-serif")
        fig_geo.update_coloraxes(showscale=False)
        st.plotly_chart(style_fig(fig_geo), use_container_width=True)
    else:
        st.info("ℹ️ لم يُعثر على جدول 'الدولة' في الشيت.")


# ══════════════════════════════════════════════════════════════════════════════
# تبويب 3 — العلاقة مع البهوتي
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("🎯 رصد وتحليل روافد المتقدمين وعلاقتهم بمعهد البهوتي")

    segments = pd.DataFrame({
        "تصنيف الفئة": [
            "متقدمون جدد (لا علاقة لهم بالبهوتي)",
            "قدامى البهوتي (سجل ولم يدرس/يدفع)",
            "طلاب البهوتي الحاليون (مستمر الآن)",
            "طلاب البهوتي المتوقفون (درس ولم يكمل)",
        ],
        "العدد": [
            int(last['Non_Behuti']),
            int(last['Behuti_Old']),
            int(last['Behuti_Curr']),
            int(last['Behuti_Stop']),
        ],
        "النسبة": [
            f"{last['Perc_Non_Behuti']:.1f}%",
            f"{last['Perc_Behuti_Old']:.1f}%",
            f"{last['Perc_Behuti_Curr']:.1f}%",
            f"{last['Perc_Behuti_Stop']:.1f}%",
        ],
    })

    col_tbl, col_donut = st.columns([1.2, 1])

    with col_tbl:
        st.dataframe(
            segments.style
                .set_properties(**{'color': NAVY, 'font-weight': '600'})
                .highlight_max(subset=['العدد'], color=f"rgba(201,162,39,0.15)"),
            use_container_width=True,
            hide_index=True,
        )

    with col_donut:
        fig_seg = px.pie(
            segments, values='العدد', names='تصنيف الفئة', hole=0.5,
            color_discrete_sequence=[NAVY, GOLD, "#2c6fad", "#e8c547"],
        )
        fig_seg.update_traces(
            textposition='outside',
            textfont_family="Cairo, sans-serif",
        )
        fig_seg.update_layout(
            **CHART_LAYOUT,
            showlegend=True,
            legend=dict(orientation="v", font=dict(family="Cairo, sans-serif", size=11)),
        )
        st.plotly_chart(fig_seg, use_container_width=True)

    # منحنى زمني لفئات البهوتي
    st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)
    st.subheader("📈 تطور أعداد فئات البهوتي عبر الزمن")

    fig_behuti = go.Figure()
    segments_map = {
        "قدامى البهوتي":    ('Behuti_Old',  GOLD),
        "طلاب حاليون":      ('Behuti_Curr', NAVY),
        "متوقفون":           ('Behuti_Stop', "#e8c547"),
        "خارج البهوتي":      ('Non_Behuti',  "#2c6fad"),
    }
    for label, (col, color) in segments_map.items():
        if col in df.columns:
            fig_behuti.add_trace(go.Scatter(
                x=df['Date'], y=df[col],
                name=label,
                line=dict(color=color, width=2),
                mode='lines+markers', marker=dict(size=5),
            ))
    fig_behuti.update_layout(**CHART_LAYOUT, hovermode="x unified",
                              legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig_behuti, use_container_width=True)

    # التوصيات
    st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)
    st.subheader("💡 التقرير الاستراتيجي والتوصيات")

    r1, r2, r3 = st.columns(3)

    with r1:
        st.markdown(f"""
        <div class="rec-card">
            <h4>📣 استراتيجية الجذب الخارجي</h4>
        """, unsafe_allow_html=True)
        rate = last['Perc_Non_Behuti']
        if rate > 50:
            st.success(f"✅ الجذب الخارجي ممتاز! {rate:.1f}% من المسجلين لا علاقة لهم بالبهوتي سابقاً.")
        else:
            st.warning(f"⚠️ الامتداد الخارجي {rate:.1f}%. يُنصح بإطلاق حملات ممولة لاستهداف شرائح جديدة.")
        st.markdown("</div>", unsafe_allow_html=True)

    with r2:
        st.markdown(f"""
        <div class="rec-card">
            <h4>💼 فرص فريق المبيعات</h4>
        """, unsafe_allow_html=True)
        st.info(f"💡 **{int(last['Behuti_Old']):,}** طالب من قدامى البهوتي سجّلوا دون أن يدرسوا.")
        if int(last['Behuti_Stop']) > 0:
            st.success(f"🔥 **{int(last['Behuti_Stop']):,}** من المتوقفين عادوا للتسجيل.")
        st.markdown("</div>", unsafe_allow_html=True)

    with r3:
        st.markdown(f"""
        <div class="rec-card">
            <h4>🏛️ تكامل المناهج والولاء</h4>
        """, unsafe_allow_html=True)
        st.info(f"💡 **{last['Perc_Behuti_Curr']:.1f}%** من الطلاب الحاليين في البهوتي سجّلوا أيضاً في برنامج التأهيل.")
        st.markdown("</div>", unsafe_allow_html=True)
