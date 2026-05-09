import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf

st.set_page_config(page_title="AI Portfolio Dashboard", layout="wide")

SHEET_ID = "1-mdVLqNWMMRrbz3mS18gB5MVx-b0-YlvNdPzojoPaaQ"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

st.title("🚀 AI Portfolio Dashboard")
st.markdown("لوحة احترافية تقرأ عملياتك من Google Sheets")
st.sidebar.header("➕ إضافة صفقة جديدة")

new_date = st.sidebar.date_input("التاريخ")
new_type = st.sidebar.selectbox("نوع العملية", ["BUY", "SELL"])
new_symbol = st.sidebar.text_input("رمز السهم", placeholder="PRPH أو 2222")
new_market = st.sidebar.selectbox("السوق", ["US", "SA"])
new_quantity = st.sidebar.number_input("الكمية", min_value=0.0, step=1.0)
new_price = st.sidebar.number_input("السعر", min_value=0.0, step=0.01)
new_fees = st.sidebar.number_input("الرسوم", min_value=0.0, step=0.01)

from google.oauth2.service_account import Credentials
import gspread

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(creds)

sheet = client.open_by_key(SHEET_ID).sheet1

if st.sidebar.button("إضافة الصفقة"):
    new_row = [
        str(new_date),
        new_type,
        new_symbol.upper(),
        new_market,
        float(new_quantity),
        float(new_price),
        float(new_fees)
    ]
    sheet.append_row(new_row)
st.sidebar.success("تمت إضافة الصفقة تلقائياً ✅")
st.experimental_rerun()
@st.cache_data(ttl=300)
def load_transactions():
    df = pd.read_csv(SHEET_URL)
    df["Symbol"] = df["Symbol"].astype(str).str.upper().str.strip()
    df["Type"] = df["Type"].astype(str).str.upper().str.strip()
    df["Market"] = df["Market"].astype(str).str.upper().str.strip()
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce").fillna(0)
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce").fillna(0)
    df["Fees"] = pd.to_numeric(df["Fees"], errors="coerce").fillna(0)
    return df

@st.cache_data(ttl=300)
def get_price(symbol, market):
    try:
        ticker = f"{symbol}.SR" if market == "SA" else symbol
        data = yf.Ticker(ticker).history(period="1d")
        if data.empty:
            return None
        return float(data["Close"].iloc[-1])
    except:
        return None

transactions = load_transactions()

positions = []

for symbol in transactions["Symbol"].unique():
    tx = transactions[transactions["Symbol"] == symbol]
    market = tx["Market"].iloc[-1]

    buy_qty = tx[tx["Type"] == "BUY"]["Quantity"].sum()
    sell_qty = tx[tx["Type"] == "SELL"]["Quantity"].sum()
    quantity = buy_qty - sell_qty

    if quantity <= 0:
        continue

    buy_cost = (
        tx[tx["Type"] == "BUY"]["Quantity"] * tx[tx["Type"] == "BUY"]["Price"]
    ).sum()

    buy_fees = tx[tx["Type"] == "BUY"]["Fees"].sum()
    avg_buy = (buy_cost + buy_fees) / buy_qty if buy_qty else 0

    current = get_price(symbol, market)

    if current is None:
        current = 0
        status = "لم يتم جلب السعر"
    else:
        status = "تم"

    cost = quantity * avg_buy
    value = quantity * current
    profit = value - cost
    profit_pct = (profit / cost) * 100 if cost else 0

    positions.append({
        "Symbol": symbol,
        "Market": market,
        "Quantity": quantity,
        "Avg Buy": avg_buy,
        "Current": current,
        "Cost": cost,
        "Value": value,
        "Profit": profit,
        "Profit %": profit_pct,
        "Status": status
    })

df = pd.DataFrame(positions)

if df.empty:
    st.warning("لا توجد مراكز مفتوحة في Google Sheet.")
    st.stop()

total_cost = df["Cost"].sum()
total_value = df["Value"].sum()
total_profit = total_value - total_cost
total_pct = (total_profit / total_cost) * 100 if total_cost else 0

col1, col2, col3 = st.columns(3)
col1.metric("💰 قيمة المحفظة", f"${total_value:,.2f}")
col2.metric("📉 الربح / الخسارة", f"${total_profit:,.2f}", f"{total_pct:.2f}%")
col3.metric("💵 إجمالي التكلفة", f"${total_cost:,.2f}")

st.subheader("📈 توزيع المحفظة")
fig = px.pie(df[df["Value"] > 0], values="Value", names="Symbol", hole=0.5)
st.plotly_chart(fig, use_container_width=True)

st.subheader("📊 أداء الأسهم")
fig2 = px.bar(df, x="Symbol", y="Profit %", color="Profit %", text=df["Profit %"].round(2))
st.plotly_chart(fig2, use_container_width=True)

st.subheader("🧠 التحليل الذكي")
worst = df.sort_values("Profit %").head(3)
best = df.sort_values("Profit %", ascending=False).head(3)

st.error("أعلى الأسهم خطورة")
st.dataframe(worst[["Symbol", "Profit %", "Profit", "Status"]], use_container_width=True)

st.success("أفضل الأسهم أداء")
st.dataframe(best[["Symbol", "Profit %", "Profit", "Status"]], use_container_width=True)

st.subheader("📋 تفاصيل المحفظة")
st.dataframe(df, use_container_width=True)

st.subheader("🧾 سجل العمليات")
st.dataframe(transactions, use_container_width=True)

if total_pct < -50:
    st.warning("⚠️ المحفظة عالية الخطورة وتحتاج مراجعة قوية.")
elif total_pct < -20:
    st.info("📊 المحفظة تحت ضغط وتحتاج متابعة.")
else:
    st.success("✅ الوضع العام أفضل نسبياً.")

st.caption("تحليل آلي تعليمي وليس توصية مالية.")
