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