import streamlit as st
import gspread
import pandas as pd
import datetime
import altair as alt

from google.oauth2.service_account import Credentials

# --- Google Sheets Setup ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["google_auth"], scopes=scope)
client = gspread.authorize(creds)
sheet = client.open("Expense-Tracker").sheet1

# Initialize Session State
if 'records' not in st.session_state:
    st.session_state.records = []

# Sidebar Settings
st.sidebar.title("設定 Settings")
lang = st.sidebar.selectbox("Language 語言", ["中文", "English"])
usd_to_twd_rate = st.sidebar.number_input("美金轉台幣匯率 (USD ➔ TWD)", min_value=1.0, max_value=100.0, value=32.0, step=0.1)

# Language Dictionary
texts = {
    "中文": {
        "title": "💰 簡易記帳 App",
        "new_record": "新增紀錄",
        "type": "類型",
        "income": "收入",
        "expense": "支出",
        "amount": "金額",
        "currency": "貨幣",
        "category": "分類",
        "note": "備註",
        "add_record": "新增紀錄",
        "record_success": "紀錄新增成功！",
        "records": "📋 金流紀錄",
        "no_records": "目前沒有任何紀錄喔～",
        "total_income": "總收入（台幣）",
        "total_expense": "總支出（台幣）",
        "balance": "目前餘額（台幣）",
        "currency_options": ["台幣 (TWD)", "美金 (USD)"],
        "categories": ["餐飲", "交通", "娛樂", "購物", "薪資", "投資", "其他"],
        "delete": "刪除",
        "statistics": "📊 每月統計"
    },
    "English": {
        "title": "💰 Simple Expense Tracker",
        "new_record": "New Record",
        "type": "Type",
        "income": "Income",
        "expense": "Expense",
        "amount": "Amount",
        "currency": "Currency",
        "category": "Category",
        "note": "Note",
        "add_record": "Add Record",
        "record_success": "Record added successfully!",
        "records": "📋 Transactions",
        "no_records": "No records yet.",
        "total_income": "Total Income (TWD)",
        "total_expense": "Total Expense (TWD)",
        "balance": "Current Balance (TWD)",
        "currency_options": ["TWD", "USD"],
        "categories": ["Food", "Transport", "Entertainment", "Shopping", "Salary", "Investment", "Others"],
        "delete": "Delete",
        "statistics": "📊 Monthly Statistics"
    }
}

# Select language
t = texts[lang]

# --- Main App ---
st.title(t["title"])

# New Record Entry
st.header(t["new_record"])
record_type = st.selectbox(t["type"], [t["income"], t["expense"]])
amount = st.number_input(t["amount"], min_value=0.0, step=0.01)
currency = st.selectbox(t["currency"], t["currency_options"])
category = st.selectbox(t["category"], t["categories"])
note = st.text_input(t["note"])
date = st.date_input("日期 Date", value=datetime.date.today())

if st.button(t["add_record"]):
    if "USD" in currency:
        amount_twd = amount * usd_to_twd_rate
    else:
        amount_twd = amount

    if record_type == t["expense"]:
        amount_twd = -amount_twd  # expenses are negative

    st.session_state.records.append({
        "日期 (Date)": date,
        f"{t['amount']} ({t['currency']})": f"{amount} {currency}",
        "台幣金額 (TWD)": amount_twd,
        t["type"]: record_type,
        t["category"]: category,
        t["note"]: note
    })
    st.success(t["record_success"])

# Display Records
st.header(t["records"])
if st.session_state.records:
    df = pd.DataFrame(st.session_state.records)

    for idx in range(len(df)):
        col1, col2 = st.columns([8, 1])
        with col1:
            st.write(df.iloc[idx].to_dict())
        with col2:
            if st.button(f"{t['delete']} {idx}", key=f"delete_{idx}"):
                st.session_state.records.pop(idx)
                st.experimental_rerun()

    # Calculate Summary
    total_income = df[df[t["type"]] == t["income"]]["台幣金額 (TWD)"].sum()
    total_expense = -df[df[t["type"]] == t["expense"]]["台幣金額 (TWD)"].sum()
    balance = total_income - total_expense

    st.subheader(f"{t['total_income']}：NT$ {total_income:,.2f}")
    st.subheader(f"{t['total_expense']}：NT$ {total_expense:,.2f}")
    st.subheader(f"{t['balance']}：NT$ {balance:,.2f}")
else:
    st.info(t["no_records"])

# Monthly Statistics
st.header(t["statistics"])
if st.session_state.records:
    df['Month'] = pd.to_datetime(df["日期 (Date)"]).dt.to_period('M')
    month_summary = df.groupby(['Month', t["type"]])["台幣金額 (TWD)"].sum().reset_index()

    chart = alt.Chart(month_summary).mark_bar().encode(
        x='Month:N',
        y='台幣金額 (TWD):Q',
        color=t["type"] + ':N',
        tooltip=['Month', t["type"], '台幣金額 (TWD)']
    ).properties(width=600, height=400)

    st.altair_chart(chart, use_container_width=True)
