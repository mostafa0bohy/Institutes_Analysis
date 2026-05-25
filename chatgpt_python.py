import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Institute Registration Dashboard",
    layout="wide"
)

# ======================================================
# LOAD DATA
# ======================================================

@st.cache_data(ttl=300)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRmiO4XN9kssEddDdU8TuKtXOypsisNKiKejQ-DCDqcgmox6s7DV0zRJ6mxpLqpBA5XQr4JMgFE11_o/pub?output=tsv"
    return pd.read_csv(url, sep="\t")

df = load_data()
df.columns = df.columns.str.strip()

# ======================================================
# CLEANING HELPERS
# ======================================================

def top_value_counts(data, col, n=10):
    if col not in data.columns:
        return pd.DataFrame()
    return (
        data[col]
        .value_counts()
        .head(n)
        .reset_index()
        .rename(columns={"index": col, col: "count"})
    )

# ======================================================
# TITLE
# ======================================================

st.title("📊 لوحة متابعة التسجيل - برنامج التأهيل الفقهي الحنبلي")
st.markdown("---")

# ======================================================
# TABS
# ======================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📌 Overview",
    "📣 Marketing Sources",
    "👥 Demographics",
    "📈 Registration Trends"
])

# ======================================================
# TAB 1 - OVERVIEW
# ======================================================

with tab1:

    st.subheader("الإحصائيات العامة")

    col1, col2, col3 = st.columns(3)

    col1.metric("إجمالي المسجلين", len(df))
    col2.metric("عدد الدول", df["الدولة"].nunique() if "الدولة" in df.columns else 0)
    col3.metric("عدد مصادر التسجيل", df["من أين عرفت المعهد؟"].nunique() if "من أين عرفت المعهد؟" in df.columns else 0)

    st.markdown("### أهم التوزيعات")

    c1, c2 = st.columns(2)

    with c1:
        fig = px.bar(
            top_value_counts(df, "الدولة", 10),
            x="الدولة",
            y="count",
            title="أكثر الدول تسجيلًا"
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.bar(
            top_value_counts(df, "من أين عرفت المعهد؟", 10),
            x="من أين عرفت المعهد؟",
            y="count",
            title="مصادر التعرف على المعهد"
        )
        st.plotly_chart(fig, use_container_width=True)


# ======================================================
# TAB 2 - MARKETING SOURCES
# ======================================================

with tab2:

    st.subheader("📣 تحليل القنوات التسويقية")

    if "من أين عرفت المعهد؟" in df.columns:

        source_df = top_value_counts(df, "من أين عرفت المعهد؟", 15)

        fig = px.pie(
            source_df,
            names="من أين عرفت المعهد؟",
            values="count",
            title="توزيع مصادر التسجيل"
        )

        st.plotly_chart(fig, use_container_width=True)

    if "الدولة" in df.columns:

        st.markdown("### الدول حسب القنوات (Insight)")
        cross = pd.crosstab(df["الدولة"], df["من أين عرفت المعهد؟"])
        st.dataframe(cross, use_container_width=True)


# ======================================================
# TAB 3 - DEMOGRAPHICS
# ======================================================

with tab3:

    st.subheader("👥 تحليل الطلاب")

    c1, c2 = st.columns(2)

    if "الجنس (ذكر,أنثى)" in df.columns:
        with c1:
            fig = px.pie(
                df,
                names="الجنس (ذكر,أنثى)",
                title="توزيع الجنس"
            )
            st.plotly_chart(fig, use_container_width=True)

    if "الفئة العمرية للطالب" in df.columns:
        with c2:
            fig = px.bar(
                top_value_counts(df, "الفئة العمرية للطالب", 10),
                x="الفئة العمرية للطالب",
                y="count",
                title="الفئات العمرية"
            )
            st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)

    if "المستوى التعليمي" in df.columns:
        with c3:
            fig = px.bar(
                top_value_counts(df, "المستوى التعليمي", 10),
                x="المستوى التعليمي",
                y="count",
                title="المستوى التعليمي"
            )
            st.plotly_chart(fig, use_container_width=True)

    if "هل تعمل بدوام؟" in df.columns:
        with c4:
            fig = px.pie(
                df,
                names="هل تعمل بدوام؟",
                title="حالة العمل"
            )
            st.plotly_chart(fig, use_container_width=True)


# ======================================================
# TAB 4 - REGISTRATION TRENDS (Sheet 16 concept)
# ======================================================

with tab4:

    st.subheader("📈 تطور التسجيلات")

    if "زمن التسجيل" in df.columns:

        df["زمن التسجيل"] = pd.to_datetime(df["زمن التسجيل"], errors="coerce")

        trend = (
            df.groupby(df["زمن التسجيل"].dt.date)
            .size()
            .reset_index(name="count")
        )

        fig = px.line(
            trend,
            x="زمن التسجيل",
            y="count",
            markers=True,
            title="التسجيلات اليومية"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### تحليل سريع")

    st.info("لو عايز تحليل أعمق للدفعة 16 (التفصيل اليومي + نسب البهوتي)، نربطه بشيت منفصل مباشرة.")
