import streamlit as st
import pandas as pd
import datetime
import altair as alt

# 初始化 Session State
if 'records' not in st.session_state:
    st.session_state.records = []

# Sidebar設定
st.sidebar.title("設定 Settings")

# 語言選擇
lang = st.sidebar.selectbox("Language 語言", ["中文", "English"])

# 自訂匯率
usd_to_twd_rate = st.sidebar.number_input("美金轉台幣匯率 (USD ➔ TWD)", min_value=1.0, max_value=100.0, value=32.0, step=0.1)

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
        "categories": ["餐飲", "交通", "娛樂", "購物", "其他"],
        "delete": "刪除",
        "statistics": "📊 每月統計"
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
        "categories": ["Food", "Transport", "Entertainment", "Shopping", "Others"],
        "delete": "Delete",
        "statistics": "📊 Monthly Statistics"
    }
}

t = texts[lang]

# 畫面標題
st.title(t["title"])

# 新增支出
st.header(t["new_record"])
amount = st.number_input(t["amount"], min_value=0.0, step=0.01)
currency = st.selectbox(t["currency"], t["currency_options"])
category = st.selectbox(t["category"], t["categories"])
note = st.text_input(t["note"])
date = st.date_input("日期 Date", value=datetime.date.today())

if st.button(t["add_record"]):
    # 貨幣轉換
    if "USD" in currency:
        amount_twd = amount * usd_to_twd_rate
    else:
        amount_twd = amount

    # 加入紀錄
    st.session_state.records.append({
        "日期 (Date)": date,
        f"{t['amount']} ({t['currency']})": f"{amount} {currency}",
        "折合台幣 (TWD Equivalent)": amount_twd,
        t["category"]: category,
        t["note"]: note
    })
    st.success(t["record_success"])

# 顯示紀錄
st.header(t["records"])
if st.session_state.records:
    df = pd.DataFrame(st.session_state.records)

    # 刪除單筆紀錄功能
    for idx in range(len(df)):
        col1, col2 = st.columns([8, 1])
        with col1:
            st.write(df.iloc[idx].to_dict())
        with col2:
            if st.button(f"{t['delete']} {idx}", key=f"delete_{idx}"):
                st.session_state.records.pop(idx)
                st.experimental_rerun()

    # 總支出
    total_spent = df["折合台幣 (TWD Equivalent)"].sum()
    st.subheader(f"{t['total_spent']}：NT$ {total_spent:,.2f}")
else:
    st.info(t["no_records"])

# 每月統計
st.header(t["statistics"])
if st.session_state.records:
    df['Month'] = pd.to_datetime(df["日期 (Date)"]).dt.to_period('M')
    month_summary = df.groupby('Month')["折合台幣 (TWD Equivalent)"].sum().reset_index()

    chart = alt.Chart(month_summary).mark_bar().encode(
        x='Month:N',
        y='折合台幣 (TWD Equivalent):Q',
        tooltip=['Month', '折合台幣 (TWD Equivalent)']
    ).properties(width=600, height=400)

    st.altair_chart(chart, use_container_width=True)

