import streamlit as st
import pandas as pd

# 初始化 Session State
if 'records' not in st.session_state:
    st.session_state.records = []

# 匯率設定
usd_to_twd_rate = 32.0

# 語言設定
lang = st.sidebar.selectbox("Language 語言", ["中文", "English"])

# 語言字典
texts = {
    "中文": {
        "title": "💰 簡易記帳 App",
        "new_record": "新增支出",
        "amount": "金額",
        "currency": "貨幣",
        "category": "分類",
        "note": "備註",
        "add_record": "新增紀錄",
        "record_success": "紀錄新增成功！",
        "records": "📋 支出紀錄",
        "no_records": "目前沒有任何紀錄喔～",
        "total_spent": "總支出（台幣）",
        "currency_options": ["台幣 (TWD)", "美金 (USD)"],
        "categories": ["餐飲", "交通", "娛樂", "購物", "其他"]
    },
    "English": {
        "title": "💰 Simple Expense Tracker",
        "new_record": "New Expense",
        "amount": "Amount",
        "currency": "Currency",
        "category": "Category",
        "note": "Note",
        "add_record": "Add Record",
        "record_success": "Record added successfully!",
        "records": "📋 Expense Records",
        "no_records": "No records yet.",
        "total_spent": "Total Spent (TWD)",
        "currency_options": ["TWD", "USD"],
        "categories": ["Food", "Transport", "Entertainment", "Shopping", "Others"]
    }
}

t = texts[lang]

# 畫面顯示
st.title(t["title"])

st.header(t["new_record"])
amount = st.number_input(t["amount"], min_value=0.0, step=0.01)
currency = st.selectbox(t["currency"], t["currency_options"])
category = st.selectbox(t["category"], t["categories"])
note = st.text_input(t["note"])

if st.button(t["add_record"]):
    # 貨幣轉換
    if "USD" in currency:
        amount_twd = amount * usd_to_twd_rate
    else:
        amount_twd = amount
    
    st.session_state.records.append({
        f"{t['amount']} ({t['currency']})": f"{amount} {currency}",
        "折合台幣 (TWD Equivalent)": amount_twd,
        t["category"]: category,
        t["note"]: note
    })
    st.success(t["record_success"])

st.header(t["records"])
if st.session_state.records:
    df = pd.DataFrame(st.session_state.records)
    st.dataframe(df, use_container_width=True)
    
    total_spent = df["折合台幣 (TWD Equivalent)"].sum()
    st.subheader(f"{t['total_spent']}：NT$ {total_spent:,.2f}")
else:
    st.info(t["no_records"])
