# ============================================================
# LOGIGUARD — SUPPLY CHAIN INTELLIGENCE DASHBOARD
# ============================================================

# ============================================================
# 1. IMPORTS
# ============================================================

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


# ============================================================
# 2. STREAMLIT CONFIG
# ============================================================

st.set_page_config(

    page_title="SupplySight | Supply Chain Intelligence",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="collapsed"
)
st.markdown(
    """
    <style>
    .bloack-container {
        padding-top: 1rem;
        padding-bottom: 1rem;  
        }
    </style>
    """,
    unsafe_allow_html=True 
)



# ============================================================
# 3. CUSTOM CSS
# ============================================================

st.markdown("""
<style>

    /* Main application */
  .stApp {
    background:
        radial-gradient(
            circle at top left,
            rgba(79, 70, 229, 0.25),
            transparent 35%
        ),
        radial-gradient(
            circle at top right,
            rgba(14, 165, 233, 0.20),
            transparent 35%
        ),
        linear-gradient(
            135deg,
            #cbd5e1 0%,
            #d5dce7 45%,
            #b8c5d6 100%
        );
    min-height: 100vh;
}

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1450px;
    }

    /* Hide Streamlit sidebar */
    section[data-testid="stSidebar"] {
        display: none;
    }

    /* Header */
    .main-title {
        font-size: 32px;
        font-weight: 700;
        color: #172033;
        margin-bottom: 0px;
    }

    .main-subtitle {
        color: #687386;
        font-size: 14px;
        margin-top: 2px;
        margin-bottom: 20px;
    }

    /* KPI Cards */
    .kpi-card {
        background: white;
        border: 1px solid #e4e8ee;
        border-radius: 12px;
        padding: 18px 20px;
        min-height: 125px;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.04);
    }

    .kpi-label {
        color: #687386;
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }

    .kpi-value {
        color: #172033;
        font-size: 29px;
        font-weight: 700;
        margin-top: 8px;
    }

    .kpi-description {
        color: #8a94a6;
        font-size: 12px;
        margin-top: 4px;
    }

    /* Section */
    .section-header {
        color: #172033;
        font-size: 19px;
        font-weight: 700;
        margin-top: 15px;
        margin-bottom: 10px;
    }

    /* Insight cards */
    .insight-card {
        background: white;
        border: 1px solid #e4e8ee;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
    }

    .insight-title {
        font-size: 13px;
        font-weight: 600;
        color: #687386;
    }

    .insight-value {
        font-size: 20px;
        font-weight: 700;
        color: #172033;
        margin-top: 5px;
    }

    /* Tabs */
    button[data-baseweb="tab"] {
        font-weight: 600;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
    }

</style>
""",
 unsafe_allow_html=True
)


# ============================================================
# 4. LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    file_path = "data/raw/Raw_data.csv"

    data = pd.read_csv(
        file_path,
        encoding="utf-8-sig"
    )

    return data


df = load_data()


# ============================================================
# 5. CLEAN COLUMN NAMES
# ============================================================

df.columns = (
    df.columns
    .str.replace("\ufeff", "", regex=False)
    .str.strip()
)


# ============================================================
# 6. FIX TEXT ENCODING
# ============================================================

def fix_encoding(value):

    if pd.isna(value):
        return value

    value = str(value)

    replacements = {
        "CÃ´te d'Ivoire": "Côte d'Ivoire",
        "CÃ´te dâ€™Ivoire": "Côte d'Ivoire",
        "CÃ´te d’Ivoire": "Côte d'Ivoire",
        "CÃ´te": "Côte",
        "Ã©": "é",
        "Ã¨": "è",
        "Ãª": "ê",
        "Ã ": "à",
        "Ã´": "ô",
        "Ã¼": "ü",
        "â€™": "'",
        "â€“": "-",
        "â€”": "-"
    }

    for wrong, correct in replacements.items():
        value = value.replace(wrong, correct)

    return value


text_columns = df.select_dtypes(include="object").columns

for col in text_columns:
    df[col] = df[col].apply(fix_encoding)
    df[col] = df[col].str.strip()


# ============================================================
# 7. STANDARDIZE ID COLUMN
# ============================================================

# Handle different possible ID names

possible_id_columns = [
    "ID",
    "id",
    "Id",
    "Ã¯Â»Â¿ID"
]

for col in possible_id_columns:

    if col in df.columns:

        df = df.rename(
            columns={col: "ID"}
        )

        break


# ============================================================
# 8. CONVERT DATE COLUMNS
# ============================================================

date_columns = [
    "Scheduled Delivery Date",
    "Delivered to Client Date",
    "Delivery Recorded Date"
]

for col in date_columns:

    if col in df.columns:

        df[col] = pd.to_datetime(
            df[col],
            errors="coerce"
        )


# ============================================================
# 9. CONVERT NUMERIC COLUMNS
# ============================================================

numeric_columns = [
    "Line Item Quantity",
    "Pack Price",
    "Unit Price",
    "Line Item Value",
    "Freight Cost (USD)",
    "Weight (Kilograms)",
    "Line Item Insurance (USD)"
]

for col in numeric_columns:

    if col in df.columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )


# ============================================================
# 10. REMOVE EMPTY / DUPLICATE RECORDS
# ============================================================

df = df.dropna(
    how="all"
)

df = df.drop_duplicates()


# ============================================================
# 11. FEATURE ENGINEERING
# ============================================================

# ------------------------------------------------------------
# Delivery Delay
# ------------------------------------------------------------

if (
    "Delivered to Client Date" in df.columns
    and
    "Scheduled Delivery Date" in df.columns
):

    df["Delivery Delay Days"] = (
        df["Delivered to Client Date"]
        -
        df["Scheduled Delivery Date"]
    ).dt.days

else:

    df["Delivery Delay Days"] = np.nan


# ------------------------------------------------------------
# Delivery Status
# ------------------------------------------------------------

df["Delivery Status"] = np.select(
    [
        df["Delivery Delay Days"] > 0,
        df["Delivery Delay Days"] <= 0
    ],
    [
        "Delayed",
        "On Time"
    ],
    default="Unknown"
)


# ------------------------------------------------------------
# Delay Flag
# ------------------------------------------------------------

df["Delay Flag"] = np.where(
    df["Delivery Status"] == "Delayed",
    1,
    0
)


# ------------------------------------------------------------
# Delivery Month
# ------------------------------------------------------------

if "Delivered to Client Date" in df.columns:

    df["Delivery Month"] = (
        df["Delivered to Client Date"]
        .dt.to_period("M")
        .astype(str)
    )

    df["Delivery Year"] = (
        df["Delivered to Client Date"]
        .dt.year
    )


# ------------------------------------------------------------
# Freight Cost per Unit
# ------------------------------------------------------------

if (
    "Freight Cost (USD)" in df.columns
    and
    "Line Item Quantity" in df.columns
):

    df["Freight Cost per Unit"] = np.where(
        df["Line Item Quantity"] > 0,
        df["Freight Cost (USD)"]
        /
        df["Line Item Quantity"],
        np.nan
    )


# ============================================================
# 12. APPLICATION HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🚚 SupplySight </div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="main-subtitle">'
    'Supply Chain Intelligence & Delivery Performance Analytics'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# 13. NAVIGATION
# ============================================================

page = st.radio(
    "",
    [
        "Home",
        "Shipment Performance",
        "Root Cause Analysis",
        "Data Quality",
        "Shipment Explorer"
    ],
    horizontal=True
)

st.divider()


# ============================================================
# 14. GLOBAL FILTERS
# ============================================================

if page == "Home":
    
    st.markdown(
        '<div class="section-header">Filters</div>',
        unsafe_allow_html=True
    )

    filter1, filter2, filter3, filter4 = st.columns(4)

    # Country filter
    with filter1:

        if "Country" in df.columns:

            countries = sorted(
                df["Country"]
                .dropna()
                .unique()
                .tolist()
            )

            selected_country = st.selectbox(
                "Country",
                ["All"] + countries
            )

        else:
            selected_country = "All"

    # Vendor filter
    with filter2:

        if "Vendor" in df.columns:

            vendors = sorted(
                df["Vendor"]
                .dropna()
                .unique()
                .tolist()
            )

            selected_vendor = st.selectbox(
                "Vendor",
                ["All"] + vendors
            )

        else:
            selected_vendor = "All"

    # Shipment mode
    with filter3:

        if "Shipment Mode" in df.columns:

            modes = sorted(
                df["Shipment Mode"]
                .dropna()
                .unique()
                .tolist()
            )

            selected_mode = st.selectbox(
                "Shipment Mode",
                ["All"] + modes
            )

        else:
            selected_mode = "All"

    # Delivery status
    with filter4:

        selected_status = st.selectbox(
            "Delivery Status",
            [
                "All",
                "On Time",
                "Delayed"
            ]
        )

else:

    # No filters on other pages
    selected_country = "All"
    selected_vendor = "All"
    selected_mode = "All"
    selected_status = "All"


# ============================================================
# 15. APPLY FILTERS
# ============================================================

filtered_df = df.copy()

if selected_country != "All":

    filtered_df = filtered_df[
        filtered_df["Country"] == selected_country
    ]

if selected_vendor != "All":

    filtered_df = filtered_df[
        filtered_df["Vendor"] == selected_vendor
    ]

if selected_mode != "All":

    filtered_df = filtered_df[
        filtered_df["Shipment Mode"] == selected_mode
    ]

if selected_status != "All":

    filtered_df = filtered_df[
        filtered_df["Delivery Status"] == selected_status
    ]


# ============================================================
# 16. DYNAMIC KPI CALCULATIONS
# ============================================================

total_shipments = len(filtered_df)

delayed_shipments = (
    filtered_df["Delivery Status"]
    .eq("Delayed")
    .sum()
)

on_time_shipments = (
    filtered_df["Delivery Status"]
    .eq("On Time")
    .sum()
)

valid_records = (
    filtered_df["Delivery Status"]
    .isin(
        [
            "On Time",
            "Delayed"
        ]
    )
    .sum()
)


if valid_records > 0:

    on_time_rate = (
        on_time_shipments
        /
        valid_records
        *
        100
    )

    delay_rate = (
        delayed_shipments
        /
        valid_records
        *
        100
    )

else:

    on_time_rate = 0
    delay_rate = 0


average_delay = (
    filtered_df.loc[
        filtered_df["Delivery Status"] == "Delayed",
        "Delivery Delay Days"
    ]
    .mean()
)


if pd.isna(average_delay):

    average_delay = 0


if "Freight Cost (USD)" in filtered_df.columns:

    freight_cost = filtered_df[
        "Freight Cost (USD)"
    ].sum()

else:

    freight_cost = 0


# ============================================================
# 17. KPI CARDS
# ============================================================

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)


with kpi1:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Total Shipments</div>
            <div class="kpi-value">{total_shipments:,}</div>
            <div class="kpi-description">
                Shipment records
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with kpi2:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">On-Time Delivery</div>
            <div class="kpi-value">{on_time_rate:.1f}%</div>
            <div class="kpi-description">
                {on_time_shipments:,} on-time
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with kpi3:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Delay Rate</div>
            <div class="kpi-value">{delay_rate:.1f}%</div>
            <div class="kpi-description">
                {delayed_shipments:,} delayed
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with kpi4:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Average Delay</div>
            <div class="kpi-value">{average_delay:.1f}</div>
            <div class="kpi-description">
                Days among delayed shipments
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with kpi5:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Freight Cost</div>
            <div class="kpi-value">${freight_cost:,.0f}</div>
            <div class="kpi-description">
                Total freight spend
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# PAGE 1 — HOME
# ============================================================

if page == "Home":

    st.markdown(
        '<div class="section-header">Executive Overview</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # Row 1 — Status + Monthly Trend
    # --------------------------------------------------------

    chart1, chart2 = st.columns(2)

    # Delivery Status
    with chart1:

        status_data = (
            filtered_df[
                filtered_df["Delivery Status"]
                != "Unknown"
            ]
            ["Delivery Status"]
            .value_counts()
            .reset_index()
        )

        status_data.columns = [
            "Status",
            "Shipments"
        ]

        fig_status = px.pie(
            status_data,
            names="Status",
            values="Shipments",
            hole=0.55,
            title="Delivery Status"
        )

        fig_status.update_layout(
            height=350,
            margin=dict(
                l=20,
                r=20,
                t=50,
                b=20
            ),
            legend_title=""
        )

        st.plotly_chart(
            fig_status,
            use_container_width=True
        )


    # Monthly shipment trend
    with chart2:

        if "Delivery Month" in filtered_df.columns:

            monthly = (
                filtered_df[
                    filtered_df["Delivery Month"]
                    != "NaT"
                ]
                .groupby("Delivery Month")
                .size()
                .reset_index(
                    name="Shipments"
                )
            )

            fig_month = px.line(
                monthly,
                x="Delivery Month",
                y="Shipments",
                markers=True,
                title="Monthly Shipment Volume"
            )

            fig_month.update_layout(
                height=350,
                margin=dict(
                    l=20,
                    r=20,
                    t=50,
                    b=20
                ),
                xaxis_title="",
                yaxis_title="Shipments"
            )

            st.plotly_chart(
                fig_month,
                use_container_width=True
            )


    # --------------------------------------------------------
    # Row 2 — Mode + Country
    # --------------------------------------------------------

    chart3, chart4 = st.columns(2)


    # Shipment mode
    with chart3:

        if "Shipment Mode" in filtered_df.columns:

            mode_data = (
                filtered_df
                .groupby("Shipment Mode")
                .agg(
                    Shipments=("Delivery Status", "count"),
                    Delayed=("Delay Flag", "sum")
                )
                .reset_index()
            )

            mode_data["Delay Rate %"] = (
                mode_data["Delayed"]
                /
                mode_data["Shipments"]
                *
                100
            )

            mode_data = mode_data.sort_values(
                "Delay Rate %",
                ascending=False
            )

            fig_mode = px.bar(
                mode_data,
                x="Shipment Mode",
                y="Delay Rate %",
                title="Delay Rate by Shipment Mode",
                text_auto=".1f"
            )

            fig_mode.update_layout(
                height=350,
                margin=dict(
                    l=20,
                    r=20,
                    t=50,
                    b=20
                ),
                xaxis_title="",
                yaxis_title="Delay Rate (%)"
            )

            st.plotly_chart(
                fig_mode,
                use_container_width=True
            )


    # Country
    with chart4:

        if "Country" in filtered_df.columns:

            country_data = (
                filtered_df
                .groupby("Country")
                .agg(
                    Shipments=("Delivery Status", "count"),
                    Delayed=("Delay Flag", "sum")
                )
                .reset_index()
            )

            country_data["Delay Rate %"] = (
                country_data["Delayed"]
                /
                country_data["Shipments"]
                *
                100
            )

            country_data = (
                country_data
                .sort_values(
                    "Delay Rate %",
                    ascending=False
                )
                .head(10)
            )

            fig_country = px.bar(
                country_data,
                x="Delay Rate %",
                y="Country",
                orientation="h",
                title="Top 10 Countries by Delay Rate",
                text_auto=".1f"
            )

            fig_country.update_layout(
                height=350,
                margin=dict(
                    l=20,
                    r=20,
                    t=50,
                    b=20
                ),
                xaxis_title="Delay Rate (%)",
                yaxis_title=""
            )

            st.plotly_chart(
                fig_country,
                use_container_width=True
            )


    # --------------------------------------------------------
    # Business Insights
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-header">Business Insights</div>',
        unsafe_allow_html=True
    )

    insight1, insight2, insight3 = st.columns(3)


    # Worst country
    with insight1:

        if "Country" in filtered_df.columns:

            country_insight = (
                filtered_df
                .groupby("Country")["Delay Flag"]
                .mean()
                .sort_values(
                    ascending=False
                )
            )

            if len(country_insight) > 0:

                worst_country = (
                    country_insight.index[0]
                )

                worst_country_rate = (
                    country_insight.iloc[0]
                    * 100
                )

                st.markdown(
                    f"""
                    <div class="insight-card">
                        <div class="insight-title">
                            Highest Delay Country
                        </div>
                        <div class="insight-value">
                            {worst_country}
                        </div>
                        <div class="kpi-description">
                            Delay rate: {worst_country_rate:.1f}%
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


    # Worst vendor
    with insight2:

        if "Vendor" in filtered_df.columns:

            vendor_insight = (
                filtered_df
                .groupby("Vendor")["Delay Flag"]
                .mean()
                .sort_values(
                    ascending=False
                )
            )

            if len(vendor_insight) > 0:

                worst_vendor = (
                    vendor_insight.index[0]
                )

                worst_vendor_rate = (
                    vendor_insight.iloc[0]
                    * 100
                )

                st.markdown(
                    f"""
                    <div class="insight-card">
                        <div class="insight-title">
                            Highest Delay Vendor
                        </div>
                        <div class="insight-value">
                            {worst_vendor}
                        </div>
                        <div class="kpi-description">
                            Delay rate: {worst_vendor_rate:.1f}%
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


    # Most used mode
    with insight3:

        if "Shipment Mode" in filtered_df.columns:

            mode_insight = (
                filtered_df[
                    "Shipment Mode"
                ]
                .value_counts()
            )

            if len(mode_insight) > 0:

                top_mode = mode_insight.index[0]

                st.markdown(
                    f"""
                    <div class="insight-card">
                        <div class="insight-title">
                            Most Used Shipment Mode
                        </div>
                        <div class="insight-value">
                            {top_mode}
                        </div>
                        <div class="kpi-description">
                            {mode_insight.iloc[0]:,} shipments
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


# ============================================================
# PAGE 2 — SHIPMENT PERFORMANCE
# ============================================================

elif page == "Shipment Performance":

    st.markdown(
        '<div class="section-header">'
        'Shipment Performance Analysis'
        '</div>',
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # Vendor Performance
    # --------------------------------------------------------

    col1, col2 = st.columns(2)


    with col1:

        vendor_data = (
            filtered_df
            .groupby("Vendor")
            .agg(
                Shipments=("Delivery Status", "count"),
                Delayed=("Delay Flag", "sum"),
                Average_Delay=("Delivery Delay Days", "mean")
            )
            .reset_index()
        )

        vendor_data["Delay Rate %"] = (
            vendor_data["Delayed"]
            /
            vendor_data["Shipments"]
            *
            100
        )

        vendor_data = vendor_data.sort_values(
            "Delay Rate %",
            ascending=False
        )

        st.subheader("Vendor Performance")

        st.dataframe(
            vendor_data.head(15),
            use_container_width=True,
            hide_index=True
        )


    with col2:

        top_vendor = vendor_data.head(10)

        fig_vendor = px.bar(
            top_vendor,
            x="Delay Rate %",
            y="Vendor",
            orientation="h",
            title="Top Vendors by Delay Rate",
            text_auto=".1f"
        )

        fig_vendor.update_layout(
            height=450,
            yaxis_title="",
            xaxis_title="Delay Rate (%)"
        )

        st.plotly_chart(
            fig_vendor,
            use_container_width=True
        )


    st.divider()


    # --------------------------------------------------------
    # Country Performance
    # --------------------------------------------------------

    col3, col4 = st.columns(2)


    with col3:

        country_data = (
            filtered_df
            .groupby("Country")
            .agg(
                Shipments=("Delivery Status", "count"),
                Delayed=("Delay Flag", "sum"),
                Average_Delay=("Delivery Delay Days", "mean")
            )
            .reset_index()
        )

        country_data["Delay Rate %"] = (
            country_data["Delayed"]
            /
            country_data["Shipments"]
            *
            100
        )

        country_data = country_data.sort_values(
            "Delay Rate %",
            ascending=False
        )

        st.subheader("Country Performance")

        st.dataframe(
            country_data.head(15),
            use_container_width=True,
            hide_index=True
        )


    with col4:

        top_country = country_data.head(10)

        fig_country = px.bar(
            top_country,
            x="Delay Rate %",
            y="Country",
            orientation="h",
            title="Countries with Highest Delay Rate",
            text_auto=".1f"
        )

        fig_country.update_layout(
            height=450,
            yaxis_title="",
            xaxis_title="Delay Rate (%)"
        )

        st.plotly_chart(
            fig_country,
            use_container_width=True
        )


    st.divider()


    # --------------------------------------------------------
    # Shipment Mode Performance
    # --------------------------------------------------------

    mode_data = (
        filtered_df
        .groupby("Shipment Mode")
        .agg(
            Shipments=("Delivery Status", "count"),
            Delayed=("Delay Flag", "sum"),
            Average_Delay=("Delivery Delay Days", "mean")
        )
        .reset_index()
    )

    mode_data["Delay Rate %"] = (
        mode_data["Delayed"]
        /
        mode_data["Shipments"]
        *
        100
    )

    st.subheader("Shipment Mode Performance")

    st.dataframe(
        mode_data,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# PAGE 3 — ROOT CAUSE ANALYSIS
# ============================================================

elif page == "Root Cause Analysis":

    st.markdown(
        '<div class="section-header">'
        'Root Cause Analysis'
        '</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Identify the dimensions where shipment delays "
        "are concentrated."
    )


    # --------------------------------------------------------
    # Country Analysis
    # --------------------------------------------------------

    country_rca = (
        filtered_df
        .groupby("Country")
        .agg(
            Shipments=("Delivery Status", "count"),
            Delayed=("Delay Flag", "sum"),
            Average_Delay=("Delivery Delay Days", "mean")
        )
        .reset_index()
    )

    country_rca["Delay Rate %"] = (
        country_rca["Delayed"]
        /
        country_rca["Shipments"]
        *
        100
    )

    country_rca = country_rca.sort_values(
        "Delay Rate %",
        ascending=False
    )


    col1, col2 = st.columns(2)


    with col1:

        fig = px.bar(
            country_rca.head(10),
            x="Delay Rate %",
            y="Country",
            orientation="h",
            title="Countries with Highest Delay Rate",
            text_auto=".1f"
        )

        fig.update_layout(
            height=450,
            xaxis_title="Delay Rate (%)",
            yaxis_title=""
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    with col2:

        st.subheader("Country Risk Table")

        st.dataframe(
            country_rca.head(15),
            use_container_width=True,
            hide_index=True
        )


    st.divider()


    # --------------------------------------------------------
    # Vendor RCA
    # --------------------------------------------------------

    vendor_rca = (
        filtered_df
        .groupby("Vendor")
        .agg(
            Shipments=("Delivery Status", "count"),
            Delayed=("Delay Flag", "sum"),
            Average_Delay=("Delivery Delay Days", "mean")
        )
        .reset_index()
    )

    vendor_rca["Delay Rate %"] = (
        vendor_rca["Delayed"]
        /
        vendor_rca["Shipments"]
        *
        100
    )

    vendor_rca = vendor_rca.sort_values(
        "Delay Rate %",
        ascending=False
    )


    col3, col4 = st.columns(2)


    with col3:

        fig = px.bar(
            vendor_rca.head(10),
            x="Delay Rate %",
            y="Vendor",
            orientation="h",
            title="Vendors with Highest Delay Rate",
            text_auto=".1f"
        )

        fig.update_layout(
            height=450,
            xaxis_title="Delay Rate (%)",
            yaxis_title=""
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    with col4:

        st.subheader("Vendor Risk Table")

        st.dataframe(
            vendor_rca.head(15),
            use_container_width=True,
            hide_index=True
        )


    st.divider()


    # --------------------------------------------------------
    # Shipment Mode RCA
    # --------------------------------------------------------

    mode_rca = (
        filtered_df
        .groupby("Shipment Mode")
        .agg(
            Shipments=("Delivery Status", "count"),
            Delayed=("Delay Flag", "sum"),
            Average_Delay=("Delivery Delay Days", "mean")
        )
        .reset_index()
    )

    mode_rca["Delay Rate %"] = (
        mode_rca["Delayed"]
        /
        mode_rca["Shipments"]
        *
        100
    )

    st.subheader("Shipment Mode Risk")

    st.dataframe(
        mode_rca,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# PAGE 4 — DATA QUALITY
# ============================================================

elif page == "Data Quality":

    st.markdown(
        '<div class="section-header">'
        'Data Quality Monitor'
        '</div>',
        unsafe_allow_html=True
    )


    total_rows = len(df)

    total_columns = len(df.columns)

    missing_cells = (
        df.isnull()
        .sum()
        .sum()
    )

    duplicate_rows = (
        df.duplicated()
        .sum()
    )


    q1, q2, q3, q4 = st.columns(4)


    with q1:

        st.metric(
            "Rows",
            f"{total_rows:,}"
        )


    with q2:

        st.metric(
            "Columns",
            f"{total_columns:,}"
        )


    with q3:

        st.metric(
            "Missing Cells",
            f"{missing_cells:,}"
        )


    with q4:

        st.metric(
            "Duplicate Rows",
            f"{duplicate_rows:,}"
        )


    st.divider()


    # --------------------------------------------------------
    # Missing Values
    # --------------------------------------------------------

    missing = (
        df.isnull()
        .sum()
        .sort_values(
            ascending=False
        )
    )

    missing = missing[
        missing > 0
    ]


    if len(missing) > 0:

        missing_df = pd.DataFrame(
            {
                "Column": missing.index,
                "Missing Values": missing.values,
                "Missing %": (
                    missing.values
                    /
                    len(df)
                    *
                    100
                ).round(2)
            }
        )


        col1, col2 = st.columns(2)


        with col1:

            st.subheader(
                "Missing Values by Column"
            )

            st.dataframe(
                missing_df,
                use_container_width=True,
                hide_index=True
            )


        with col2:

            fig_missing = px.bar(
                missing_df.head(15),
                x="Missing %",
                y="Column",
                orientation="h",
                title="Top Columns with Missing Data",
                text_auto=".1f"
            )

            fig_missing.update_layout(
                height=500,
                xaxis_title="Missing (%)",
                yaxis_title=""
            )

            st.plotly_chart(
                fig_missing,
                use_container_width=True
            )

    else:

        st.success(
            "No missing values found."
        )


    st.divider()


    # --------------------------------------------------------
    # Column Information
    # --------------------------------------------------------

    st.subheader("Dataset Structure")

    structure_df = pd.DataFrame(
        {
            "Column": df.columns,
            "Data Type": df.dtypes.astype(str),
            "Unique Values": [
                df[col].nunique()
                for col in df.columns
            ],
            "Missing Values": [
                df[col].isna().sum()
                for col in df.columns
            ]
        }
    )


    st.dataframe(
        structure_df,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# PAGE 5 — SHIPMENT EXPLORER
# ============================================================

elif page == "Shipment Explorer":

    st.markdown(
        '<div class="section-header">'
        'Shipment Explorer'
        '</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Search and explore individual shipment records."
    )


    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------

    search_text = st.text_input(
        "Search shipment / vendor / country / project"
    )


    explorer_df = filtered_df.copy()


    if search_text:

        search_text = search_text.lower()

        search_columns = [
            col
            for col in [
                "ID",
                "Project Code",
                "Vendor",
                "Country",
                "Shipment Mode",
                "Product Group"
            ]
            if col in explorer_df.columns
        ]

        mask = pd.Series(
            False,
            index=explorer_df.index
        )

        for col in search_columns:

            mask = (
                mask
                |
                explorer_df[col]
                .astype(str)
                .str.lower()
                .str.contains(
                    search_text,
                    na=False
                )
            )

        explorer_df = explorer_df[
            mask
        ]


    st.write(
        f"Showing **{len(explorer_df):,}** records"
    )


    # --------------------------------------------------------
    # Display columns
    # --------------------------------------------------------

    preferred_columns = [
        "ID",
        "Project Code",
        "Country",
        "Vendor",
        "Shipment Mode",
        "Product Group",
        "Scheduled Delivery Date",
        "Delivered to Client Date",
        "Delivery Delay Days",
        "Delivery Status",
        "Freight Cost (USD)"
    ]


    display_columns = [
        col
        for col in preferred_columns
        if col in explorer_df.columns
    ]


    st.dataframe(
        explorer_df[
            display_columns
        ],
        use_container_width=True,
        height=600,
        hide_index=True
    )


    # --------------------------------------------------------
    # Download
    # --------------------------------------------------------

    csv_download = explorer_df.to_csv(
        index=False
    ).encode("utf-8")


    st.download_button(
        "Download Filtered Data",
        data=csv_download,
        file_name="logiguard_filtered_shipments.csv",
        mime="text/csv"
    )


# ============================================================
# 18. FOOTER
# ============================================================

st.divider()

st.caption(
    "SupplySight • Supply Chain Delivery Performance Analytics"
)