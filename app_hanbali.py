import streamlit as st
import pandas as pd

# القائمة المطلوبة للأعمدة (كما حددتها أنت)
REQUIRED_COLUMNS = [
    "التاريخ",
    "إجمالي المسجلين الجدد (أنشأ حسابًا على الموقع)",
    "مسجلين اليوم (أنشأ حسابًا على الموقع)",
    "المسجلين الجدد من قدامى البهوتي (لم يدرس ولم يدفع)",
    "نسبة المسجلين الجدد من قدامى البهوتي ",
    "المسجلين الجدد من طلاب البهوتي (طالب حالي يدرس البهوتي )",
    "نسبة المسجلين الجدد من طلاب البهوتي ",
    "المسجلين الجدد من طلاب البهوتي المتوقفين (درس ولم يكمل)",
    "نسبة المسجلين الجدد من طلبة البهوتي المتوقفين",
    "المسجلين الجدد غير المسجلين في البهوتي ",
    "نسبة المسجلين الجدد غير المسجلين في البهوتي "
]

@st.cache_data
def load_and_fix_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRmiO4XN9kssEddDdU8TuKtXOypsisNKiKejQ-DCDqcgmox6s7DV0zRJ6mxpLqpBA5XQr4JMgFE11_o/pub?gid=826428120&single=true&output=csv"
    
    # قراءة كامل البيانات
    raw_df = pd.read_csv(url, header=None)
    
    # العثور على سطر البداية (الذي يحتوي كلمة "التاريخ")
    start_row = raw_df[raw_df.apply(lambda row: "التاريخ" in str(row.values), axis=1)].index[0]
    
    df = raw_df.iloc[start_row:].reset_index(drop=True)
    df.columns = df.iloc[0]
    df = df.iloc[1:].reset_index(drop=True)
    
    # اختيار الأعمدة التي حددتها فقط
    # نقوم بعمل "تطابق ذكي" لتجنب أخطاء المسافات الزائدة
    df = df.loc[:, df.columns.isin(REQUIRED_COLUMNS)]
    
    # حذف الصفوف التي لا تحتوي على تاريخ
    df = df.dropna(subset=["التاريخ"])
    
    return df

# العرض
df = load_and_fix_data()
st.write("### البيانات بعد التخصيص:")
st.dataframe(df)
