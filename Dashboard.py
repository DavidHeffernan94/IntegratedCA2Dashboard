import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="Google Merchandise Store",
    page_icon="📊️",
    layout="wide"
)

GOOGLE_BLUE = "#4285F4"
GOOGLE_RED = "#EA4335"
GOOGLE_YELLOW = "#FBBC05"
GOOGLE_GREEN = "#34A853"
GOOGLE_COLORS = [GOOGLE_BLUE, GOOGLE_RED, GOOGLE_YELLOW, GOOGLE_GREEN]
PLOT_BG = "#F8F9FA"

st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-size: 18px;
        }
        [data-testid="stMetricLabel"] {
            font-size: 16px !important;
            font-weight: 600;
            color: #444444;
        }
        [data-testid="stMetricValue"] {
            font-size: 28px !important;
            font-weight: 700;
            color: #4285F4;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 16px;
            font-weight: 600;
            padding: 10px 20px;
        }
        .css-1d391kg {
            font-size: 16px;
        }
        h2, h3 {
            color: #4285F4;
        }
        .stApp {
            background-color: #F8F9FA;
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
    st.caption("A high-level summary of store performance. Use the filters on the left to explore specific time periods, categories, locations or customer groups.")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="Total Revenue", value=f"${filtered_df['TotalPrice'].sum():,.2f}")
    col2.metric(label="Total Customers", value=f"{filtered_df['CustomerID'].nunique():,}")
    col3.metric(label="Total Transactions", value=f"{filtered_df['TransactionID'].nunique():,}")
    col4.metric(label="Avg Order Value", value=f"${filtered_df.groupby('TransactionID')['TotalPrice'].sum().mean():,.2f}")

    st.markdown("---")

    col_rev, col_gender = st.columns(2)

    with col_rev:
        st.subheader("Monthly Revenue")
        monthly_revenue = filtered_df.groupby(filtered_df["Date"].dt.month)["TotalPrice"].sum().reset_index()
        monthly_revenue.columns = ["Month", "Revenue"]
        monthly_revenue["Month"] = pd.to_datetime(monthly_revenue["Month"], format="%m").dt.strftime("%B")

        fig = px.line(monthly_revenue, x="Month", y="Revenue",
                      title="Monthly Revenue (2019)",
                      markers=True,
                      color_discrete_sequence=[GOOGLE_BLUE])
        fig.update_layout(font=dict(size=16), plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG,
                          yaxis=dict(gridcolor="#E0E0E0"),
                          xaxis=dict(gridcolor="#E0E0E0"))
        fig.update_traces(line=dict(width=3), marker=dict(size=10))
        st.plotly_chart(fig, use_container_width=True)

    with col_gender:
        st.subheader("Revenue by Gender")
        gender_revenue = filtered_df.groupby("Gender")["TotalPrice"].sum().reset_index()
        gender_revenue.columns = ["Gender", "Revenue"]

        fig_gender = px.bar(gender_revenue, x="Gender", y="Revenue",
                            title="Total Revenue by Gender",
                            labels={"Revenue": "Revenue ($)", "Gender": ""},
                            color_discrete_sequence=[GOOGLE_BLUE, GOOGLE_RED])
        fig_gender.update_layout(font=dict(size=14), plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG,
                                  yaxis=dict(gridcolor="#E0E0E0"))
        st.plotly_chart(fig_gender, use_container_width=True)

with tab2:
    st.subheader("Sales Analysis")
    st.caption("Explore product and category performance, and identify which days of the week generate the most revenue.")

    col1, col2 = st.columns(2)

    with col1:
        top_products = filtered_df.groupby("Description")["TotalPrice"].sum().reset_index()
        top_products = top_products.sort_values("TotalPrice", ascending=True).tail(10)

        fig2 = px.bar(top_products, x="TotalPrice", y="Description",
                      orientation="h",
                      title="Top 10 Products by Revenue",
                      labels={"TotalPrice": "Revenue ($)", "Description": ""},
                      color_discrete_sequence=[GOOGLE_BLUE])
        fig2.update_layout(font=dict(size=14), plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG,
                           xaxis=dict(gridcolor="#E0E0E0"))
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        category_revenue = filtered_df.groupby("Category")["TotalPrice"].sum().reset_index()
        category_revenue = category_revenue.sort_values("TotalPrice", ascending=True)

        fig3 = px.bar(category_revenue, x="TotalPrice", y="Category",
                      orientation="h",
                      title="Revenue by Category",
                      labels={"TotalPrice": "Revenue ($)", "Category": ""},
                      color_discrete_sequence=[GOOGLE_GREEN])
        fig3.update_layout(font=dict(size=14), plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG,
                           xaxis=dict(gridcolor="#E0E0E0"))
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
    fig_dow.update_layout(font=dict(size=14), plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG,
                          yaxis=dict(gridcolor="#E0E0E0"))
    fig_dow.add_annotation(
        text="Sales peak Wednesday to Friday",
        xref="paper", yref="paper",
        x=0.5, y=1.05,
        showarrow=False,
        font=dict(size=13, color="#444444"),
        align="center"
    )
    st.plotly_chart(fig_dow, use_container_width=True)

with tab3:
    st.subheader("Customer Analysis")
    st.caption("Understand who your customers are, where they are based, how long they have been shopping with you, and how they respond to promotions.")

    col1, col2 = st.columns(2)

    with col1:
        spend_gender = filtered_df.groupby("Gender")[["OnlineSpend", "OfflineSpend"]].mean().reset_index()
        spend_gender = spend_gender.melt(id_vars="Gender", var_name="Channel", value_name="Avg Spend")

        fig4 = px.bar(spend_gender, x="Gender", y="Avg Spend", color="Channel",
                      barmode="group",
                      title="Average Online vs Offline Spend by Gender",
                      labels={"Avg Spend": "Average Spend ($)"},
                      color_discrete_sequence=[GOOGLE_BLUE, GOOGLE_RED])
        fig4.update_layout(font=dict(size=14), plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG,
                           yaxis=dict(gridcolor="#E0E0E0"))
        st.plotly_chart(fig4, use_container_width=True)

    with col2:
        avg_spend_location = filtered_df.groupby("Location")["TotalPrice"].mean().reset_index()
        avg_spend_location.columns = ["Location", "Avg Revenue per Transaction"]
        avg_spend_location = avg_spend_location.sort_values("Avg Revenue per Transaction", ascending=True)

        fig5 = px.bar(avg_spend_location, x="Avg Revenue per Transaction", y="Location",
                      orientation="h",
                      title="Average Spend per Transaction by Location",
                      labels={"Avg Revenue per Transaction": "Avg Spend ($)", "Location": ""},
                      color_discrete_sequence=[GOOGLE_GREEN])
        fig5.update_layout(font=dict(size=14), plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG,
                           xaxis=dict(gridcolor="#E0E0E0"))
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
        fig6.update_layout(font=dict(size=14), plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG,
                           yaxis=dict(gridcolor="#E0E0E0"))
        st.plotly_chart(fig6, use_container_width=True)

    with col4:
        coupon_counts = filtered_df["CouponStatus"].value_counts().reset_index()
        coupon_counts.columns = ["CouponStatus", "Count"]

        fig7 = px.pie(coupon_counts, values="Count", names="CouponStatus",
                      title="Coupon Usage Breakdown",
                      hole=0.4,
                      color_discrete_sequence=GOOGLE_COLORS)
        fig7.update_layout(font=dict(size=14), paper_bgcolor=PLOT_BG)
        fig7.update_traces(textfont_size=14)
        st.plotly_chart(fig7, use_container_width=True)

    clicked_pct = round(coupon_counts[coupon_counts["CouponStatus"] == "Clicked"]["Count"].values[0] / coupon_counts["Count"].sum() * 100, 1)
    st.info(f"**Coupon Insight:** {clicked_pct}% of customers clicked a coupon but did not use it, suggesting the current coupon strategy may need refinement to convert interest into redemption.")

with tab4:
    st.subheader("Basket Analysis")
    st.caption("Discover which products are frequently bought together and which combinations are the strongest predictors of co-purchase behaviour.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Top Item Pairs by Support")
        st.caption("Support shows how often two items appear together across all transactions.")
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
        fig8.update_layout(font=dict(size=13), plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG,
                           xaxis=dict(gridcolor="#E0E0E0"))
        fig8.update_yaxes(autorange="reversed")
        st.plotly_chart(fig8, use_container_width=True)

    with col2:
        st.markdown("#### Top Association Rules by Lift")
        st.caption("Lift measures how much more likely two items are bought together compared to by chance. A lift of 60 means customers are 60 times more likely to buy both items together.")
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
        fig9.update_layout(font=dict(size=13), plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG,
                           xaxis=dict(gridcolor="#E0E0E0"))
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
    fig10.update_layout(font=dict(size=14), plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG,
                        yaxis=dict(gridcolor="#E0E0E0"))
    st.plotly_chart(fig10, use_container_width=True)

with tab5:
    st.subheader("ML Insights")
    st.caption("A summary of the machine learning models applied to this dataset, including recommendation systems and market basket analysis algorithms.")

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
                "Jan 2019 - Dec 2019"
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

        st.markdown("""
        The high matrix sparsity of 97.76% is a common challenge in retail recommendation systems.
        It was addressed by applying a minimum similarity threshold and lowering the support threshold
        for market basket analysis to ensure meaningful patterns could still be identified.
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

        st.markdown("""
        A hybrid approach combining all three methods would be optimal in production.
        Content-based filtering handles new customers, while collaborative filtering
        improves as purchase history grows.
        """)

        st.markdown("#### Algorithm Comparison")
        algo_data = {
            "Metric": ["Rules Generated", "Frequent Itemsets", "Avg Runtime"],
            "Apriori": ["106", "Identical", "4.81s"],
            "FP Growth": ["106", "Identical", "7.04s"]
        }
        algo_df = pd.DataFrame(algo_data)
        st.table(algo_df)

        st.markdown("""
        Both algorithms produced identical results. Apriori was faster on this dataset
        due to high sparsity, which limits the effectiveness of FP Growth's tree compression.
        This highlights the importance of matching algorithm choice to dataset characteristics.
        """)

st.markdown("---")