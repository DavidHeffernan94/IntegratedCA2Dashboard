import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="Online Retail Store",
    page_icon="📊️",
    layout="wide"
)

GOOGLE_BLUE = "#4285F4"
GOOGLE_RED = "#EA4335"
GOOGLE_YELLOW = "#FBBC05"
GOOGLE_GREEN = "#34A853"
GOOGLE_COLORS = [GOOGLE_BLUE, GOOGLE_RED, GOOGLE_YELLOW, GOOGLE_GREEN]

st.markdown("""
    <style>
        /* Global font size for 65+ readability */
        html, body, [class*="css"] {
            font-size: 18px;
        }
        /* Metric labels */
        [data-testid="stMetricLabel"] {
            font-size: 16px !important;
            font-weight: 600;
            color: #444444;
        }
        /* Metric values */
        [data-testid="stMetricValue"] {
            font-size: 28px !important;
            font-weight: 700;
            color: #4285F4;
        }
        /* Tab font size */
        .stTabs [data-baseweb="tab"] {
            font-size: 16px;
            font-weight: 600;
            padding: 10px 20px;
        }
        /* Sidebar */
        .css-1d391kg {
            font-size: 16px;
        }
        /* Subheaders */
        h2, h3 {
            color: #4285F4;
        }
    </style>
""", unsafe_allow_html=True)

@st.cache_data  
def load_data():
    data = pd.read_csv("OnlineRetail_Cleaned.csv")  
    data["Date"] = pd.to_datetime(data["Date"])      
    return data 
    
df = load_data()

st.sidebar.title("Filters")

min_date = df["Date"].min()
max_date = df["Date"].max()
date_range = st.sidebar.date_input("Date Range", value=(min_date, max_date),
    min_value=min_date, max_value=max_date)
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

st.title("Google Merchandise Store Dashboard")
st.markdown("---")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview",
    "Sales Analysis",
    "Customer Analysis",
    "Basket Analysis",
    "ML Insights"
])

with tab1:
    st.subheader("Overview")
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(label="Total Revenue", value=f"${filtered_df['TotalPrice'].sum():,.2f}")
    col2.metric(label="Total Customers", value=f"{filtered_df['CustomerID'].nunique():,}")
    col3.metric(label="Total Transactions", value=f"{filtered_df['TransactionID'].nunique():,}")
    col4.metric(label="Avg Order Value", value=f"${filtered_df.groupby('TransactionID')['TotalPrice'].sum().mean():,.2f}")

    st.markdown("---")

    st.subheader("Monthly Revenue")
    monthly_revenue = filtered_df.groupby(filtered_df["Date"].dt.month)["TotalPrice"].sum().reset_index()
    monthly_revenue.columns = ["Month", "Revenue"]
    monthly_revenue["Month"] = pd.to_datetime(monthly_revenue["Month"], format="%m").dt.strftime("%B")

    fig = px.line(monthly_revenue, x="Month", y="Revenue",
                  title="Monthly Revenue (2019)",
                  markers=True,
                  color_discrete_sequence=[GOOGLE_BLUE])
    fig.update_layout(font=dict(size=16), plot_bgcolor="white",
                      yaxis=dict(gridcolor="#f0f0f0"),
                      xaxis=dict(gridcolor="#f0f0f0"))
    fig.update_traces(line=dict(width=3), marker=dict(size=10))
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)

    with col1:
        top_products = filtered_df.groupby("Description")["TotalPrice"].sum().reset_index()
        top_products = top_products.sort_values("TotalPrice", ascending=True).tail(10)

        fig2 = px.bar(top_products, x="TotalPrice", y="Description",
                      orientation="h",
                      title="Top 10 Products by Revenue",
                      labels={"TotalPrice": "Revenue ($)", "Description": ""},
                      color_discrete_sequence=[GOOGLE_BLUE])
        fig2.update_layout(font=dict(size=14), plot_bgcolor="white",
                           xaxis=dict(gridcolor="#f0f0f0"))
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        category_revenue = filtered_df.groupby("Category")["TotalPrice"].sum().reset_index()
        category_revenue = category_revenue.sort_values("TotalPrice", ascending=True)

        fig3 = px.bar(category_revenue, x="TotalPrice", y="Category",
                      orientation="h",
                      title="Revenue by Category",
                      labels={"TotalPrice": "Revenue ($)", "Category": ""},
                      color_discrete_sequence=[GOOGLE_GREEN])
        fig3.update_layout(font=dict(size=14), plot_bgcolor="white",
                           xaxis=dict(gridcolor="#f0f0f0"))
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")

    dow_revenue = filtered_df.groupby(filtered_df["Date"].dt.day_name())["TotalPrice"].sum().reset_index()
    dow_revenue.columns = ["Day", "Revenue"]
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow_revenue["Day"] = pd.Categorical(dow_revenue["Day"], categories=day_order, ordered=True)
    dow_revenue = dow_revenue.sort_values("Day")

    fig_dow = px.bar(dow_revenue, x="Day", y="Revenue",
                     title="Revenue by Day of Week",
                     labels={"Revenue": "Revenue ($)", "Day": ""},
                     color_discrete_sequence=[GOOGLE_YELLOW])
    fig_dow.update_layout(font=dict(size=14), plot_bgcolor="white",
                          yaxis=dict(gridcolor="#f0f0f0"))
    st.plotly_chart(fig_dow, use_container_width=True)

with tab3:
    col1, col2 = st.columns(2)

    with col1:
        spend_gender = filtered_df.groupby("Gender")[["OnlineSpend", "OfflineSpend"]].mean().reset_index()
        spend_gender = spend_gender.melt(id_vars="Gender", var_name="Channel", value_name="Avg Spend")

        fig4 = px.bar(spend_gender, x="Gender", y="Avg Spend", color="Channel",
                      barmode="group",
                      title="Average Online vs Offline Spend by Gender",
                      labels={"Avg Spend": "Average Spend ($)"},
                      color_discrete_sequence=[GOOGLE_BLUE, GOOGLE_RED])
        fig4.update_layout(font=dict(size=14), plot_bgcolor="white",
                           yaxis=dict(gridcolor="#f0f0f0"))
        st.plotly_chart(fig4, use_container_width=True)

    with col2:
        spend_location = filtered_df.groupby("Location")["TotalPrice"].sum().reset_index()
        spend_location = spend_location.sort_values("TotalPrice", ascending=True)

        fig5 = px.bar(spend_location, x="TotalPrice", y="Location",
                      orientation="h",
                      title="Total Revenue by Location",
                      labels={"TotalPrice": "Revenue ($)", "Location": ""},
                      color_discrete_sequence=[GOOGLE_GREEN])
        fig5.update_layout(font=dict(size=14), plot_bgcolor="white",
                           xaxis=dict(gridcolor="#f0f0f0"))
        st.plotly_chart(fig5, use_container_width=True)

    st.markdown("---")

    col3, col4 = st.columns(2)

    with col3:
        tenure_counts = filtered_df.groupby("Tenure")["CustomerID"].nunique().reset_index()
        tenure_counts.columns = ["Tenure", "Customers"]

        fig6 = px.bar(tenure_counts, x="Tenure", y="Customers",
                      title="Number of Customers by Tenure Segment",
                      labels={"Customers": "Number of Customers", "Tenure": ""},
                      color_discrete_sequence=[GOOGLE_BLUE])
        fig6.update_layout(font=dict(size=14), plot_bgcolor="white",
                           yaxis=dict(gridcolor="#f0f0f0"), xaxis_tickangle=0)
        st.plotly_chart(fig6, use_container_width=True)

    with col4:
        coupon_counts = filtered_df["CouponStatus"].value_counts().reset_index()
        coupon_counts.columns = ["CouponStatus", "Count"]

        fig7 = px.pie(coupon_counts, values="Count", names="CouponStatus",
                      title="Coupon Usage Breakdown",
                      hole=0.4,
                      color_discrete_sequence=GOOGLE_COLORS)
        fig7.update_layout(font=dict(size=14))
        fig7.update_traces(textfont_size=14)
        st.plotly_chart(fig7, use_container_width=True)

with tab4:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Top Item Pairs by Support")
        pair_data = {
            "Item Pair": [
                "Nest Outdoor Camera, Nest Indoor Camera",
                "Nest Thermostat (Steel), Nest Outdoor Camera",
                "Nest Thermostat (Steel), Nest Indoor Camera",
                "Nest Battery Alarm, Nest Thermostat (Steel)",
                "Nest Battery Alarm, Nest Outdoor Camera",
                "Nest Wired Alarm, Nest Thermostat (Steel)",
                "Nest Battery Alarm, Nest Indoor Camera",
                "Google Stickers, YouTube Decals",
                "Nest Wired Alarm, Nest Outdoor Camera",
                "Google Stickers, Google Doodle Decal"
            ],
            "Support (%)": [2.77, 1.20, 0.91, 0.90, 0.77, 0.72, 0.60, 0.54, 0.50, 0.49]
        }
        pair_df = pd.DataFrame(pair_data)

        fig8 = px.bar(pair_df, x="Support (%)", y="Item Pair",
                      orientation="h",
                      title="Top 10 Item Pairs by Support",
                      labels={"Support (%)": "Support (%)", "Item Pair": ""},
                      color_discrete_sequence=[GOOGLE_BLUE])
        fig8.update_layout(font=dict(size=13), plot_bgcolor="white",
                           xaxis=dict(gridcolor="#f0f0f0"))
        fig8.update_yaxes(autorange="reversed")
        st.plotly_chart(fig8, use_container_width=True)

    with col2:
        st.markdown("#### Top Association Rules by Lift")
        rules_data = {
            "Rule": [
                "Google Tee Blue → Google Tee Green",
                "Google Tee Green → Google Tee Blue",
                "Scoop Neck Tee White → Scoop Neck Tee Black",
                "Scoop Neck Tee Black → Scoop Neck Tee White",
                "Android Sticker Ultra → 8pc Android Sticker",
                "8pc Android Sticker → Android Sticker Ultra",
                "Vintage Badge Tee White → Vintage Badge Tee Sage",
                "22oz Android Bottle → Google 22oz Water Bottle",
                "8pc Android Sticker → Google Doodle Decal",
                "Android Sticker Ultra → Google Stickers"
            ],
            "Lift": [59.81, 59.81, 43.77, 43.77, 30.57, 30.57, 17.65, 17.09, 16.05, 14.61]
        }
        rules_df = pd.DataFrame(rules_data)

        fig9 = px.bar(rules_df, x="Lift", y="Rule",
                      orientation="h",
                      title="Top 10 Association Rules by Lift",
                      labels={"Lift": "Lift Score", "Rule": ""},
                      color_discrete_sequence=[GOOGLE_RED])
        fig9.update_layout(font=dict(size=13), plot_bgcolor="white",
                           xaxis=dict(gridcolor="#f0f0f0"))
        fig9.update_yaxes(autorange="reversed")
        st.plotly_chart(fig9, use_container_width=True)

    st.markdown("---")

    st.subheader("Basket Size Distribution")
    basket_sizes = filtered_df.groupby("TransactionID")["Description"].count().reset_index()
    basket_sizes.columns = ["TransactionID", "Basket Size"]
    basket_sizes = basket_sizes[basket_sizes["Basket Size"] <= 10]

    fig10 = px.histogram(basket_sizes, x="Basket Size",
                         title="Distribution of Basket Sizes",
                         labels={"Basket Size": "Number of Items", "count": "Number of Transactions"},
                         nbins=10,
                         color_discrete_sequence=[GOOGLE_GREEN])
    fig10.update_layout(font=dict(size=14), plot_bgcolor="white",
                        yaxis=dict(gridcolor="#f0f0f0"))
    st.plotly_chart(fig10, use_container_width=True)

with tab5:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Why This Dataset Suits Machine Learning")

        ml_stats = {
            "Metric": [
                "Total Transactions",
                "Unique Customers",
                "Unique Products",
                "Avg Basket Size",
                "Matrix Sparsity",
                "Date Range"
            ],
            "Value": [
                f"{filtered_df['TransactionID'].nunique():,}",
                f"{filtered_df['CustomerID'].nunique():,}",
                f"{filtered_df['Description'].nunique():,}",
                f"{filtered_df.groupby('TransactionID')['Description'].count().mean():.2f}",
                "97.76%",
                "Jan 2019 — Dec 2019"
            ]
        }
        ml_df = pd.DataFrame(ml_stats)
        st.table(ml_df)

        st.markdown("""
        **Key ML Suitability Factors:**
        - Sufficient customer and product volume for collaborative filtering
        - Rich product descriptions enable content-based filtering
        - Transaction history supports market basket analysis
        - Customer demographics enable segmentation
        """)

    with col2:
        st.markdown("#### Recommendation System Summary")

        rec_data = {
            "Method": ["Content-Based", "User-User", "Item-Item"],
            "Based On": ["Product attributes", "Customer behaviour", "Customer behaviour"],
            "Cold Start": ["Handles new users", "Struggles", "Struggles"],
            "Best For": ["New customers", "Established customers", "Cross-category discovery"]
        }
        rec_df = pd.DataFrame(rec_data)
        st.table(rec_df)

        st.markdown("#### Algorithm Comparison")
        algo_data = {
            "Metric": ["Rules Generated", "Frequent Itemsets", "Avg Runtime"],
            "Apriori": ["106", "Identical", "4.81s"],
            "FP Growth": ["106", "Identical", "7.04s"]
        }
        algo_df = pd.DataFrame(algo_data)
        st.table(algo_df)

st.markdown("---")
