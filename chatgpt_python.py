import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(
    page_title="Growth OS Dashboard",
    layout="wide"
)

# ======================================================
# LOAD DATA
# ======================================================

@st.cache_data(ttl=300)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRmiO4XN9kssEddDdU8TuKtXOypsisNKiKejQ-DCDqcgmox6s7DV0zRJ6mxpLqpBA5XQr4JMgFE11_o/pub?output=tsv"
    df = pd.read_csv(url, sep="\t")
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# ======================================================
# SAFE CHECKS
# ======================================================

def safe_col(col):
    return col in df.columns

def vc(data, col, n=10):
    if col not in data.columns:
        return pd.DataFrame()
    return data[col].value_counts().head(n).reset_index()

# ======================================================
# SIDEBAR FILTERS
# ======================================================

st.sidebar.title("🎛 Filters")

if safe_col("الدولة"):
    country_filter = st.sidebar.multiselect(
        "الدولة",
        df["الدولة"].dropna().unique()
    )
else:
    country_filter = []

if safe_col("من أين عرفت المعهد؟"):
    source_filter = st.sidebar.multiselect(
        "مصدر التسجيل",
        df["من أين عرفت المعهد؟"].dropna().unique()
    )
else:
    source_filter = []

filtered = df.copy()

if country_filter:
    filtered = filtered[filtered["الدولة"].isin(country_filter)]

if source_filter:
    filtered = filtered[filtered["من أين عرفت المعهد؟"].isin(source_filter)]

# ======================================================
# TITLE
# ======================================================

st.title("🚀 Growth OS Dashboard - Command Center")
st.markdown("تحليل إداري + تسويقي + نمو + ذكاء تنبؤ + قرارات تشغيلية")

st.markdown("---")

# ======================================================
# KPI LAYER (SMART KPIs)
# ======================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric("إجمالي المسجلين", len(filtered))

col2.metric(
    "الدول",
    filtered["الدولة"].nunique() if safe_col("الدولة") else 0
)

col3.metric(
    "المصادر",
    filtered["من أين عرفت المعهد؟"].nunique() if safe_col("من أين عرفت المعهد؟") else 0
)

col4.metric(
    "متوسط العمر",
    round(filtered["العمر"].dropna().mean(), 1) if safe_col("العمر") else 0
)

st.markdown("---")

# ======================================================
# TABS
# ======================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Executive",
    "📣 Marketing",
    "🚀 Growth",
    "🧠 Intelligence"
])

# ======================================================
# TAB 1 - EXECUTIVE
# ======================================================

with tab1:

    st.subheader("📊 لوحة الإدارة")

    c1, c2 = st.columns(2)

    if safe_col("الدولة"):
        with c1:
            fig = px.bar(
                vc(filtered, "الدولة"),
                x="index",
                y="الدولة",
                title="أكثر الدول تسجيلًا"
            )
            st.plotly_chart(fig, use_container_width=True)

    if safe_col("المستوى التعليمي"):
        with c2:
            fig = px.bar(
                vc(filtered, "المستوى التعليمي"),
                x="index",
                y="المستوى التعليمي",
                title="المستوى التعليمي"
            )
            st.plotly_chart(fig, use_container_width=True)

# ======================================================
# TAB 2 - MARKETING
# ======================================================

with tab2:

    st.subheader("📣 Marketing Intelligence")

    if safe_col("من أين عرفت المعهد؟"):

        source = filtered["من أين عرفت المعهد؟"].value_counts().reset_index()
        source.columns = ["source", "count"]

        fig = px.pie(
            source,
            names="source",
            values="count",
            title="مصادر التسجيل"
        )
        st.plotly_chart(fig, use_container_width=True)

    if safe_col("الدولة") and safe_col("من أين عرفت المعهد؟"):

        st.markdown("### 🌍 الدولة × المصدر")

        cross = pd.crosstab(
            filtered["الدولة"],
            filtered["من أين عرفت المعهد؟"]
        )

        st.dataframe(cross, use_container_width=True)

# ======================================================
# TAB 3 - GROWTH ENGINE
# ======================================================

with tab3:

    st.subheader("🚀 Growth Engine")

    if safe_col("زمن التسجيل"):

        filtered["زمن التسجيل"] = pd.to_datetime(
            filtered["زمن التسجيل"],
            errors="coerce"
        )

        daily = filtered.groupby(
            filtered["زمن التسجيل"].dt.date
        ).size().reset_index()

        daily.columns = ["date", "count"]

        # ---- Growth Line ----
        fig = px.line(
            daily,
            x="date",
            y="count",
            markers=True,
            title="التسجيلات اليومية"
        )
        st.plotly_chart(fig, use_container_width=True)

        # ---- Growth Rate ----
        daily["growth"] = daily["count"].pct_change() * 100

        fig2 = px.bar(
            daily,
            x="date",
            y="growth",
            title="معدل النمو اليومي %"
        )
        st.plotly_chart(fig2, use_container_width=True)

        # ---- SIMPLE FORECAST (Moving Average) ----
        daily["MA7"] = daily["count"].rolling(7).mean()

        fig3 = px.line(
            daily,
            x="date",
            y=["count", "MA7"],
            title="Forecast (Moving Average 7 days)"
        )
        st.plotly_chart(fig3, use_container_width=True)

    # ---- BEHOOTY SEGMENTS ----
    if safe_col("الموقف من البهوتي"):

        seg = filtered["الموقف من البهوتي"].value_counts().reset_index()
        seg.columns = ["segment", "count"]

        fig = px.bar(
            seg,
            x="segment",
            y="count",
            title="Segmentation - البهوتي"
        )

        st.plotly_chart(fig, use_container_width=True)

# ======================================================
# TAB 4 - INTELLIGENCE LAYER
# ======================================================

with tab4:

    st.subheader("🧠 Intelligence Layer (Lead Scoring + Alerts)")

    temp = filtered.copy()

    # ==================================================
    # LEAD SCORING (simple but powerful)
    # ==================================================

    score = np.zeros(len(temp))

    if safe_col("كم ساعة يمكن أن توفرها للمعهد يوميًا؟"):
        score += temp["كم ساعة يمكن أن توفرها للمعهد يوميًا؟"].fillna(0).astype(float)

    if safe_col("الفئة العمرية للطالب"):
        score += temp["الفئة العمرية للطالب"].notna().astype(int)

    if safe_col("هل تعمل بدوام؟"):
        score += temp["هل تعمل بدوام؟"].notna().astype(int)

    temp["lead_score"] = score

    st.markdown("### 🎯 أعلى الطلاب جودة (Lead Score)")

    st.dataframe(
        temp.sort_values("lead_score", ascending=False).head(20),
        use_container_width=True
    )

    # ==================================================
    # ALERTS SYSTEM
    # ==================================================

    st.markdown("### 🚨 Alerts")

    alerts = []

    if safe_col("زمن التسجيل"):
        if len(filtered) > 0:
            last_day = filtered["زمن التسجيل"].dropna().max()
            alerts.append(f"آخر تسجيل: {last_day}")

    if len(filtered) < len(df) * 0.7:
        alerts.append("⚠️ انخفاض كبير في التسجيلات بعد الفلترة")

    if alerts:
        for a in alerts:
            st.warning(a)
    else:
        st.success("كل المؤشرات مستقرة")
