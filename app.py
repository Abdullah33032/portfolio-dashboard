import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="AI Portfolio Dashboard",
    layout="wide"
)

# =========================
# بيانات المحفظة
# =========================

data = [
    {"Symbol": "PRPH", "Profit %": -82, "Value": 320},
    {"Symbol": "CMND", "Profit %": -75, "Value": 410},
    {"Symbol": "OCG", "Profit %": -66, "Value": 530},
    {"Symbol": "EZRA", "Profit %": -85, "Value": 250},
    {"Symbol": "PASW", "Profit %": -48, "Value": 120},
    {"Symbol": "TNON", "Profit %": -12, "Value": 600},
]

df = pd.DataFrame(data)

# =========================
# العنوان
# =========================

st.title("🚀 AI Portfolio Dashboard")
st.markdown("### لوحة تحليل ذكية لمحفظة الأسهم")

# =========================
# الإحصائيات
# =========================

total_value = df["Value"].sum()
avg_profit = df["Profit %"].mean()

col1, col2, col3 = st.columns(3)

col1.metric("💰 قيمة المحفظة", f"${total_value}")
col2.metric("📉 متوسط الأداء", f"{avg_profit:.1f}%")
col3.metric("📊 عدد الأسهم", len(df))

# =========================
# الرسم الدائري
# =========================

pie = px.pie(
    df,
    names="Symbol",
    values="Value",
    hole=0.5,
    title="توزيع المحفظة"
)

st.plotly_chart(pie, use_container_width=True)

# =========================
# الرسم البياني للأداء
# =========================

bar = px.bar(
    df,
    x="Symbol",
    y="Profit %",
    color="Profit %",
    title="أداء الأسهم",
    text="Profit %"
)

st.plotly_chart(bar, use_container_width=True)

# =========================
# تحليل ذكي
# =========================

worst_stock = df.loc[df["Profit %"].idxmin()]
best_stock = df.loc[df["Profit %"].idxmax()]

st.subheader("🧠 التحليل الذكي")

st.error(
    f"أعلى سهم خطورة: {worst_stock['Symbol']} "
    f"({worst_stock['Profit %']}%)"
)

st.success(
    f"أفضل سهم بالمحفظة: {best_stock['Symbol']} "
    f"({best_stock['Profit %']}%)"
)

# =========================
# الجدول
# =========================

st.subheader("📋 تفاصيل المحفظة")

st.dataframe(df, use_container_width=True)

# =========================
# التقييم النهائي
# =========================

if avg_profit < -50:
    st.warning("⚠️ المحفظة تحتاج إعادة هيكلة وتقليل المخاطر")
elif avg_profit < -20:
    st.info("📊 المحفظة متوسطة الخطورة")
else:
    st.success("✅ أداء المحفظة جيد")

st.caption("تم إنشاء هذه اللوحة بواسطة الذكاء الاصطناعي")
