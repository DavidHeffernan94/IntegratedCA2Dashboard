import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="Online Retail Store",
    page_icon="📊️",
    layout="wide"
)

@st.cache_data  
def load_data():
    data = pd.read_csv("OnlineRetail_Cleaned.csv")  
    data["Date"] = pd.to_datetime(data["Date"])      
    return data 
    
df = load_data()


st.sidebar.title("Filters")

min_date = df["Date"].min()
max_date = df["Date"].max()
date_range = st.sidebar.date_input("Date Range",value=(min_date, max_date),
    min_value=min_date,max_value=max_date)
selected_category = st.sidebar.multiselect("Category", sorted(df["Category"].unique()))
selected_location = st.sidebar.multiselect("Location", sorted(df["Location"].unique()))
selected_gender = st.sidebar.multiselect("Gender", sorted(df["Gender"].unique()))


filtered_df = df.copy()
if len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df["Date"] >= pd.Timestamp(date_range[0])) &
        (filtered_df["Date"] <= pd.Timestamp(date_range[1]))
    ]
if selected_category:
    filtered_df = filtered_df[filtered_df["Category"].isin(selected_category)]
if selected_location:
    filtered_df = filtered_df[filtered_df["Location"].isin(selected_location)]
if selected_gender:
    filtered_df = filtered_df[filtered_df["Gender"].isin(selected_gender)]
    

st.title("Online Retail Store Dashboard")
st.markdown("---")


st.subheader("Overview")
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    label="Total Revenue",
    value=f"${filtered_df['TotalPrice'].sum():,.2f}"
)
col2.metric(
    label="Total Customers",
    value=f"{filtered_df['CustomerID'].nunique():,}"
)
col3.metric(
    label="Total Transactions",
    value=f"{filtered_df['TransactionID'].nunique():,}"
)
col4.metric(
    label="Avg Order Value",
    value=f"${filtered_df.groupby('TransactionID')['TotalPrice'].sum().mean():,.2f}"
)

st.markdown("---")


st.subheader("Monthly Revenue")
monthly_revenue = filtered_df.groupby(filtered_df["Date"].dt.month)["TotalPrice"].sum().reset_index()
monthly_revenue.columns = ["Month", "Revenue"]
monthly_revenue["Month"] = pd.to_datetime(monthly_revenue["Month"], format="%m").dt.strftime("%B")

fig = px.line(monthly_revenue, x="Month", y="Revenue",
              title="Monthly Revenue (2019)",
              markers=True)
fig.update_layout(font=dict(size=16))
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Top 10 Products by Revenue")
    top_products = filtered_df.groupby("Description")["TotalPrice"].sum().reset_index()
    top_products = top_products.sort_values("TotalPrice", ascending=True).tail(10)
    
    fig2 = px.bar(top_products, x="TotalPrice", y="Description",
                  orientation="h",
                  title="Top 10 Products by Revenue",
                  labels={"TotalPrice": "Revenue ($)", "Description": ""})
    fig2.update_layout(font=dict(size=14))
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.subheader("📦 Revenue by Category")
    category_revenue = filtered_df.groupby("Category")["TotalPrice"].sum().reset_index()
    category_revenue = category_revenue.sort_values("TotalPrice", ascending=True)
    
    fig3 = px.bar(category_revenue, x="TotalPrice", y="Category",
                  orientation="h",
                  title="Revenue by Category",
                  labels={"TotalPrice": "Revenue ($)", "Category": ""})
    fig3.update_layout(font=dict(size=14))
    st.plotly_chart(fig3, use_container_width=True)