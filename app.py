import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(page_title="AI Portfolio Dashboard", layout="wide")

st.title("🚀 AI Portfolio Dashboard")
st.markdown("لوحة تحليل حقيقية لمحفظتك")

portfolio = [
    {"Symbol": "PRPH", "Quantity": 2107, "Buy": 2.50},
    {"Symbol": "CMND", "Quantity": 321, "Buy": 8.28},
    {"Symbol": "OCG", "Quantity": 653, "Buy": 5.58},
    {"Symbol": "KUST", "Quantity": 184, "Buy": 14.91},
    {"Symbol": "EZRA", "Quantity": 1000, "Buy": 0.5528},
    {"Symbol": "PASW", "Quantity": 234, "Buy": 0.2964},
    {"Symbol": "TNON", "Quantity": 167, "Buy": 0.8688},
    {"Symbol": "SMX", "Quantity": 3, "Buy": 1.37},
    {"Symbol": "TRIXF", "Quantity": 2000, "Buy": 1.10},
]

import yfinance as yf

def get_price(symbol, market="US"):

    try:
        if market == "SA":
            symbol = f"{symbol}.SR"

        stock = yf.Ticker(symbol)
        hist = stock.history(period="1d")

        if hist.empty:
            return None

        return float(hist["Close"].iloc[-1])

    except:
        return None
rows = []
rows = []

for stock in portfolio:

    symbol = stock["Symbol"]
    market = stock.get("Market", "US")

    price = get_price(symbol, market)

    if price is None:

        rows.append({
            "Symbol": symbol,
            "Quantity": stock["Quantity"],
            "Buy": stock["Buy"],
            "Current": None,
            "Cost": stock["Quantity"] * stock["Buy"],
            "Value": 0,
            "Profit": 0,
            "Profit %": 0,
            "Status": "لم يتم جلب السعر"
        })

        continue

    cost = stock["Quantity"] * stock["Buy"]

    value = stock["Quantity"] * price

    profit = value - cost

    profit_pct = (profit / cost) * 100

    rows.append({
        "Symbol": symbol,
        "Quantity": stock["Quantity"],
        "Buy": stock["Buy"],
        "Current": price,
        "Cost": cost,
        "Value": value,
        "Profit": profit,
        "Profit %": profit_pct,
        "Status": "تم"
    })


df = pd.DataFrame(rows)

total_cost = df["Cost"].sum()
total_value = df["Value"].sum()
total_profit = total_value - total_cost
total_pct = (total_profit / total_cost) * 100 if total_cost else 0

col1, col2, col3 = st.columns(3)
col1.metric("💰 قيمة المحفظة", f"${total_value:,.2f}")
col2.metric("📉 الربح / الخسارة", f"${total_profit:,.2f}", f"{total_pct:.2f}%")
col3.metric("💵 إجمالي التكلفة", f"${total_cost:,.2f}")

st.subheader("📈 توزيع المحفظة")

fig = px.pie(
    df[df["Value"] > 0],
    values="Value",
    names="Symbol",
    hole=0.5
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("📊 أداء الأسهم")

fig2 = px.bar(
    df,
    x="Symbol",
    y="Profit %",
    color="Profit %",
    text=df["Profit %"].round(2)
)
st.plotly_chart(fig2, use_container_width=True)

st.subheader("🧠 التحليل الذكي")

worst = df.sort_values("Profit %").head(3)
best = df.sort_values("Profit %", ascending=False).head(3)

st.error("أعلى الأسهم خطورة:")
st.dataframe(worst[["Symbol", "Profit %", "Profit", "Status"]], use_container_width=True)

st.success("أفضل الأسهم أداء:")
st.dataframe(best[["Symbol", "Profit %", "Profit", "Status"]], use_container_width=True)

st.subheader("📋 تفاصيل المحفظة")
st.dataframe(df, use_container_width=True)

if total_pct < -50:
    st.warning("⚠️ المحفظة عالية الخطورة وتحتاج مراجعة قوية.")
elif total_pct < -20:
    st.info("📊 المحفظة تحت ضغط وتحتاج متابعة.")
else:
    st.success("✅ الوضع العام أفضل نسبياً.")

st.caption("تحليل آلي تعليمي وليس توصية مالية.")
