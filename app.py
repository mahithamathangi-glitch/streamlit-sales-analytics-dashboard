import streamlit as st
import pandas as pd
import plotly.express as px


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Superstore Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------



# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>

/* Main page */
.main {
    background-color: #f7f9fc;
}

/* Sidebar background */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #172554 0%, #1e3a8a 100%);
}

/* Sidebar heading */
[data-testid="stSidebar"] h2 {
    color: white !important;
    font-size: 1.35rem;
    font-weight: 700;
}

/* Sidebar labels */
[data-testid="stSidebar"] label {
    color: white !important;
    font-weight: 600;
}

/* Multiselect box */
[data-testid="stSidebar"] [data-baseweb="select"] {
    background-color: rgba(255, 255, 255, 0.15);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 10px;
}

/* Date input box */
[data-testid="stSidebar"] [data-testid="stDateInput"] {
    background-color: rgba(255, 255, 255, 0.15);
    border-radius: 10px;
    padding: 5px;
}

/* Keep date text dark and readable */
[data-testid="stSidebar"] [data-testid="stDateInput"] input {
    color: #222222 !important;
    background-color: white !important;
}

/* Date placeholder */
[data-testid="stSidebar"] [data-testid="stDateInput"] input::placeholder {
    color: #666666 !important;
}

/* KPI cards */
.metric-card {
    background-color: white;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
}

</style>
""", unsafe_allow_html=True)
# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data():

    df = pd.read_csv(
        "data/Superstore.csv",
        encoding="latin1"
    )

    df["Order Date"] = pd.to_datetime(
        df["Order Date"],
        errors="coerce"
    )

    df["Sales"] = pd.to_numeric(
        df["Sales"],
        errors="coerce"
    )

    df["Profit"] = pd.to_numeric(
        df["Profit"],
        errors="coerce"
    )

    df["Quantity"] = pd.to_numeric(
        df["Quantity"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["Order Date", "Sales", "Profit"]
    )

    return df


df = load_data()


# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("📊 Superstore Sales Analytics")

st.markdown(
    """
    ### Interactive Business Intelligence Dashboard

    Explore sales, profitability, categories and regional performance
    using interactive filters.
    """
)


# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("🔎 Dashboard Filters")


# Region filter
regions = sorted(df["Region"].dropna().unique())

selected_regions = st.sidebar.multiselect(
    "Select Region",
    regions,
    default=regions
)


# Category filter
categories = sorted(df["Category"].dropna().unique())

selected_categories = st.sidebar.multiselect(
    "Select Category",
    categories,
    default=categories
)


# Date filter
min_date = df["Order Date"].min().date()
max_date = df["Order Date"].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    format="DD/MM/YYYY"
)


# --------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------

filtered_df = df[
    df["Region"].isin(selected_regions)
    &
    df["Category"].isin(selected_categories)
]


if len(date_range) == 2:

    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])

    filtered_df = filtered_df[
        (filtered_df["Order Date"] >= start_date)
        &
        (filtered_df["Order Date"] <= end_date)
    ]


# --------------------------------------------------
# EMPTY DATA HANDLING
# --------------------------------------------------

if filtered_df.empty:

    st.warning(
        "⚠️ No data matches the selected filters. "
        "Please change your filters."
    )

    st.stop()


# --------------------------------------------------
# KPI SECTION
# --------------------------------------------------

st.subheader("📌 Executive Overview")

total_sales = filtered_df["Sales"].sum()

total_profit = filtered_df["Profit"].sum()

total_orders = filtered_df["Order ID"].nunique()

avg_order_value = (
    total_sales / total_orders
    if total_orders > 0
    else 0
)

profit_margin = (
    (total_profit / total_sales) * 100
    if total_sales != 0
    else 0
)


col1, col2, col3, col4, col5 = st.columns(5)


col1.metric(
    "💰 Total Sales",
    f"${total_sales:,.0f}"
)

col2.metric(
    "📈 Total Profit",
    f"${total_profit:,.0f}"
)

col3.metric(
    "🛒 Orders",
    f"{total_orders:,}"
)

col4.metric(
    "🧾 Avg Order Value",
    f"${avg_order_value:,.2f}"
)

col5.metric(
    "📊 Profit Margin",
    f"{profit_margin:.2f}%"
)


st.divider()


# --------------------------------------------------
# CHART 1 — SALES TREND
# --------------------------------------------------

st.subheader("📈 Sales Trend Over Time")

monthly_sales = (
    filtered_df
    .set_index("Order Date")
    .resample("ME")["Sales"]
    .sum()
    .reset_index()
)

fig_sales = px.line(
    monthly_sales,
    x="Order Date",
    y="Sales",
    markers=True,
    title="Monthly Sales Trend"
)

fig_sales.update_layout(
    xaxis_title="Month",
    yaxis_title="Sales"
)

st.plotly_chart(
    fig_sales,
    use_container_width=True
)


# --------------------------------------------------
# CHART 2 — SALES BY CATEGORY
# --------------------------------------------------

col1, col2 = st.columns(2)


with col1:

    category_sales = (
        filtered_df
        .groupby("Category")["Sales"]
        .sum()
        .reset_index()
        .sort_values("Sales", ascending=False)
    )

    fig_category = px.bar(
        category_sales,
        x="Category",
        y="Sales",
        title="Sales by Category",
        text_auto=".2s"
    )

    st.plotly_chart(
        fig_category,
        use_container_width=True
    )


# --------------------------------------------------
# CHART 3 — PROFIT BY REGION
# --------------------------------------------------

with col2:

    region_profit = (
        filtered_df
        .groupby("Region")["Profit"]
        .sum()
        .reset_index()
        .sort_values("Profit")
    )

    fig_region = px.bar(
        region_profit,
        x="Profit",
        y="Region",
        orientation="h",
        title="Profit by Region",
        text_auto=".2s"
    )

    st.plotly_chart(
        fig_region,
        use_container_width=True
    )


# --------------------------------------------------
# CHART 4 — CATEGORY PROFITABILITY
# --------------------------------------------------

st.subheader("🎯 Category Profitability")

category_profit = (
    filtered_df
    .groupby("Category")
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum")
    )
    .reset_index()
)

fig_profit = px.scatter(
    category_profit,
    x="Sales",
    y="Profit",
    size="Sales",
    color="Category",
    hover_name="Category",
    title="Sales vs Profit by Category"
)

st.plotly_chart(
    fig_profit,
    use_container_width=True
)


# --------------------------------------------------
# ANALYTICAL SUMMARY
# --------------------------------------------------

st.subheader("🧠 Analytical Summary")


best_category = (
    filtered_df
    .groupby("Category")["Sales"]
    .sum()
    .idxmax()
)

best_region = (
    filtered_df
    .groupby("Region")["Profit"]
    .sum()
    .idxmax()
)

best_subcategory = (
    filtered_df
    .groupby("Sub-Category")["Profit"]
    .sum()
    .idxmax()
)


st.success(
    f"""
    **Business Insights**

    • Highest-sales category: **{best_category}**

    • Most profitable region: **{best_region}**

    • Most profitable sub-category: **{best_subcategory}**

    • Overall profit margin: **{profit_margin:.2f}%**

    These insights can help business stakeholders identify
    high-performing categories and regions.
    """
)


# --------------------------------------------------
# RAW DATA
# --------------------------------------------------

with st.expander("📋 View Filtered Data"):

    st.dataframe(
        filtered_df,
        use_container_width=True
    )


# --------------------------------------------------
# DOWNLOAD DATA
# --------------------------------------------------

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Download Filtered Data",
    data=csv,
    file_name="filtered_superstore_data.csv",
    mime="text/csv"
)


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Built with Python • Pandas • Plotly • Streamlit"
)