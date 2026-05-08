import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Portfolio Dashboard", layout="wide")

data = [
    {"Symbol": "PRPH", "Profit %": -82, "Value": 320},
    {"Symbol": "CMND", "Profit %": -75, "Value": 410},
    {"Symbol": "OCG", "Profit %": -66, "Value": 530},
    {"Symbol": "EZRA", "Profit %": -85, "Value": 250},
    {"Symbol": "PASW", "Profit %": -48, "Value": 120},
    {"Symbol": "TNON", "Profit %": -12, "Value": 600},
]

df = pd.DataFrame(data)

st.title("📊 AI Portfolio Dashboard")

total_value = df["Value"].sum()

st.metric("💰 Portfolio Value", f"${total_value}")

fig = px.pie(
    df,
    values="Value",
    names="Symbol",
    hole=0.5
)

st.plotly_chart(fig, use_container_width=True)

fig2 = px.bar(
    df,
    x="Symbol",
    y="Profit %",
    color="Profit %"
)

st.plotly_chart(fig2, use_container_width=True)

st.dataframe(df, use_container_width=True)
