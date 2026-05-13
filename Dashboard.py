import streamlit as st
import pandas as pd
import numpy as np

@st.cache_data  
def load_data():
    data = pd.read_csv("OnlineRetail_Cleaned.csv")  
    data["Date"] = pd.to_datetime(data["Date"])      
    return data 
    

df = load_data()

if st.checkbox("show raw data"):
    st.subheader("Raw Data")
    st.write(data)