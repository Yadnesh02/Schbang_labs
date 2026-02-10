import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils import load_google_sheet_data, load_revenue_summary_data
import os
import base64

# Handle Favicon / Logo
fav_icon = "📊"
for ext in ["png", "jpg", "jpeg"]:
    if os.path.exists(f"logo.{ext}"):
        fav_icon = f"logo.{ext}"
        break

# Page Config
st.set_page_config(
    page_title="Schbang C0-C3",
    page_icon=fav_icon,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - X (Twitter) Inspired Professional Design
st.markdown("""
<style>
    /* Force Dark Theme - Override System Preferences */
    :root {
        color-scheme: dark !important;
    }
    
    html, body, [class*="css"], .stApp, [data-testid="stAppViewContainer"] {
        background-color: #0E1117 !important;
        color: #E7E9EA !important;
    }
    
    /* Force dark background on main container */
    .main, .block-container, [data-testid="stAppViewContainer"] > div {
        background-color: #0E1117 !important;
    }
    
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        font-size: 0.875rem; /* ~14px base */
    }
    
    /* Reduce top padding */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    
    /* Main title styling */
    h1 {
        font-size: 1.75rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
        margin-bottom: 1.5rem !important;
    }
    
    /* Section headers */
    h2, h3 {
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        margin-top: 1rem !important;
        margin-bottom: 0.75rem !important;
    }
    
    h5 {
        font-size: 0.95rem !important;
        font-weight: 600 !important;
    }
    
    /* Metrics styling */
    div[data-testid="stMetric"] {
        background-color: #16181C;
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #2F3336;
    }
    
    div[data-testid="stMetric"] label {
        font-size: 0.875rem !important;
        color: #71767B !important;
    }
    
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
    }
    
    /* Custom Table Styling - Dark Theme */
    .pipeline-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #E7E9EA;
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
        font-size: 0.85rem;
    }
    
    .pipeline-table th {
        background-color: #16181C;
        color: #71767B;
        padding: 0.75rem 1rem;
        text-align: center;
        font-weight: 600;
        border-bottom: 1px solid #2F3336;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        white-space: nowrap;
    }
    
    .pipeline-table th:first-child {
        text-align: center;
        position: sticky;
        left: 0;
        z-index: 3;
        background-color: #16181C;
        width: 140px;
        min-width: 140px;
    }

    /* Specialized Insights Table Styling */
    .insights-table th:first-child {
        text-align: center;
        position: sticky;
        left: 0;
        z-index: 3;
        background-color: #16181C;
        width: 190px;
        min-width: 190px;
    }
    
    .pipeline-table td {
        padding: 0.75rem 1rem;
        text-align: center;
        border-bottom: 1px solid #2F3336;
        background-color: #0E1117;
    }
    
    .pipeline-table td:first-child {
        text-align: center;
        font-weight: 500;
        background-color: #16181C;
        color: #E7E9EA;
        position: sticky;
        left: 0;
        z-index: 1;
        width: 140px;
        min-width: 140px;
    }

    .insights-table td:first-child {
        text-align: center;
        font-weight: 500;
        background-color: #16181C;
        color: #E7E9EA;
        position: sticky;
        left: 0;
        z-index: 1;
        width: 190px;
        min-width: 190px;
    }
    
    .pipeline-table tr:hover td {
        background-color: #1A1D23;
    }
    
    .pipeline-table td {
        padding: 0.5rem 1rem !important; /* Reduced for compact height */
        text-align: center;
        border-bottom: 1px solid #2F3336;
        background-color: #0E1117;
    }
    
    .pipeline-table .total-row td {
        background-color: #16181C;
        font-weight: 700;
        border-top: 1px solid #2F3336;
        border-bottom: none;
        color: #FFFFFF;
        text-align: center !important;
        padding: 0.5rem 1rem !important; /* Matches data rows */
    }
    
    .deficit-negative {
        color: #F4212E;
        font-weight: 600;
    }

    /* Chart Container with Dark Border */
    div[data-testid="stPlotlyChart"] {
        border: 1px solid #2F3336;
        border-radius: 12px;
        padding: 0.5rem !important;
        margin-bottom: 0.5rem !important; /* Reduced to pull next section up */
        width: 100% !important;
        height: auto !important; 
        min-height: 150px;
        overflow: hidden; /* Restored to prevent row bleeding */
        box-sizing: border-box;
    }
    
    /* Chart Headers Refinement */
    .chart-header, .stMarkdown h3 {
        margin-top: 1rem !important; /* Moved down slightly */
        margin-bottom: 0.5rem !important;
        text-align: left !important;
        margin-left: 0 !important;
        font-weight: 600;
        font-size: 1rem;
        color: #E7E9EA;
        height: 1.5rem;
        display: flex;
        align-items: center;
    }
    
    .trend-up { color: #00BA7C !important; font-size: 0.8rem; margin-left: 8px; font-weight: 700; width: 45px; display: inline-block; text-align: left; }
    .trend-down { color: #F4212E !important; font-size: 0.8rem; margin-left: 8px; font-weight: 700; width: 45px; display: inline-block; text-align: left; }
    .trend-neutral { color: #71767B !important; font-size: 0.8rem; margin-left: 8px; font-weight: 700; width: 45px; display: inline-block; text-align: left; }
    .trend-pct { font-size: 0.65rem; opacity: 0.7; margin-left: 2px; font-weight: 400; }
    
    /* Scrollable Layout for Tables */
    .table-wrapper {
        border: 1px solid #2F3336;
        border-radius: 12px;
        overflow: hidden;
        margin-top: 0 !important;
        margin-bottom: 0.5rem !important; /* Reduced to pull next section up */
        padding: 0 !important;
    }
    
    .scroll-area {
        height: 207px !important; /* Synced with Funnel Chart height */
        max-height: 207px !important;
        overflow-y: hidden; /* Remove scrollbar */
    }

    .insights-scroll-area {
        max-height: 250px; /* Show 5 complete rows, 6th accessible via scroll */
        overflow-y: auto;
    }

    .insights-table tbody::after {
        content: "";
        display: block;
        height: 25px; /* Prevent total row overlap only in Insights */
    }

    .scroll-area::-webkit-scrollbar {
        width: 6px;
    }
    
    .scroll-area::-webkit-scrollbar-track {
        background: transparent;
    }
    
    .scroll-area::-webkit-scrollbar-thumb {
        background: #2F3336;
        border-radius: 10px;
    }
    
    .scroll-area::-webkit-scrollbar-thumb:hover {
        background: #3F4346;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-size: 0.9375rem;
        font-weight: 600;
        padding: 0.5rem 0;
    }
    
    /* Unified Single-Row Header Styling */
    [data-testid="stMultiSelect"] label {
        display: none !important;
    }

    /* Fix text color visibility in filters and inputs */
    [data-testid="stMultiSelect"] div[data-baseweb="select"] {
        color: #E7E9EA !important;
    }
    
    [data-testid="stMultiSelect"] input {
        color: #E7E9EA !important;
    }
    
    [data-testid="stMultiSelect"] span {
        color: #E7E9EA !important;
    }
    
    /* Fix dropdown menu text */
    [role="listbox"] {
        background-color: #16181C !important;
    }
    
    [role="option"] {
        color: #E7E9EA !important;
        background-color: #16181C !important;
        font-size: 0.8rem !important;
        padding-top: 4px !important;
        padding-bottom: 4px !important;
    }
    
    /* Expand dropdown width */
    [role="listbox"] {
        min-width: 250px !important;
    }
    
    [role="option"]:hover {
        background-color: #1A1D23 !important;
    }
    
    /* Shrink multiselect tags */
    [data-testid="stMultiSelect"] [data-baseweb="tag"] {
        font-size: 0.7rem !important;
        height: 22px !important;
    }
    
    /* Fix selectbox text */
    [data-baseweb="select"] {
        color: #E7E9EA !important;
    }
    
    [data-baseweb="select"] input {
        color: #E7E9EA !important;
    }
    
    /* Fix all input text colors */
    input, textarea, select {
        color: #E7E9EA !important;
    }

    [data-testid="stHorizontalBlock"] {
        align-items: center !important;
        gap: 0.5rem !important;
    }

    .dashboard-title {
        font-size: 1.6rem !important;
        font-weight: 800 !important;
        margin: 0 !important;
        padding-right: 0.5rem !important;
        letter-spacing: -0.02em;
        white-space: nowrap;
        
        /* Shimmer Animation */
        background: linear-gradient(
            to right,
            #FFFFFF 20%,
            #71767B 40%,
            #71767B 60%,
            #FFFFFF 80%
        );
        background-size: 200% auto;
        color: #000;
        background-clip: text;
        text-fill-color: transparent;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 5s linear infinite;
    }

    @keyframes shine {
        to {
            background-position: 200% center;
        }
    }

    /* Comprehensive Responsive Design for All Laptop Sizes */
    
    /* MacBook Pro 16" & Large Laptops (1728px+) - Optimal */
    @media (min-width: 1728px) {
        .pipeline-table { font-size: 0.9rem; }
        .chart-header { font-size: 1.1rem; }
    }
    
    /* MacBook Pro 14" & Standard Laptops (1512px - 1727px) */
    @media (max-width: 1727px) and (min-width: 1512px) {
        .dashboard-title { font-size: 1.5rem !important; }
        .pipeline-table { font-size: 0.85rem; }
        .chart-header { font-size: 1.05rem; }
        .scroll-area { height: 207px !important; max-height: 207px !important; }
    }
    
    /* MacBook Pro 13" & Medium Laptops (1440px - 1511px) */
    @media (max-width: 1511px) and (min-width: 1440px) {
        .dashboard-title { font-size: 1.4rem !important; }
        .pipeline-table { font-size: 0.8rem; }
        .pipeline-table th, .pipeline-table td { padding: 0.6rem 0.8rem; }
        .chart-header { font-size: 1rem; }
        .scroll-area { height: 207px !important; max-height: 207px !important; }
        .header-container { padding: 0.4rem 0 0.6rem 0 !important; }
    }
    
    /* MacBook Air & Smaller Laptops (1366px - 1439px) */
    @media (max-width: 1439px) and (min-width: 1366px) {
        .dashboard-title { font-size: 1.3rem !important; }
        .pipeline-table { font-size: 0.75rem; }
        .pipeline-table th, .pipeline-table td { padding: 0.5rem 0.7rem; }
        .chart-header { font-size: 0.95rem; }
        .scroll-area { height: 207px !important; max-height: 207px !important; }
        .insights-scroll-area { max-height: 220px; }
        .header-container { padding: 0.3rem 0 0.5rem 0 !important; }
        [data-testid="stHorizontalBlock"] { gap: 0.4rem !important; }
    }
    
    /* Small Laptops & Tablets (1200px - 1365px) */
    @media (max-width: 1365px) and (min-width: 1200px) {
        .dashboard-title { font-size: 1.2rem !important; }
        .pipeline-table { font-size: 0.7rem; }
        .pipeline-table th, .pipeline-table td { padding: 0.4rem 0.6rem; }
        .chart-header { font-size: 0.9rem; }
        .scroll-area { height: 207px !important; max-height: 207px !important; }
        .insights-scroll-area { max-height: 200px; }
        [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
            gap: 0.5rem !important;
        }
        .header-container { padding: 0.25rem 0 0.4rem 0 !important; }
    }
    
    /* Tablets & Small Screens (768px - 1199px) */
    @media (max-width: 1199px) and (min-width: 768px) {
        .dashboard-title { font-size: 1.1rem !important; }
        .pipeline-table { font-size: 0.65rem; }
        .pipeline-table th, .pipeline-table td { padding: 0.35rem 0.5rem; }
        .chart-header, .stMarkdown h3 { font-size: 0.85rem !important; }
        .scroll-area { height: 207px !important; max-height: 207px !important; }
        .insights-scroll-area { max-height: 180px; }
        [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
            gap: 0.5rem !important;
        }
    }
    
    /* Mobile Devices (< 768px) */
    @media (max-width: 767px) {
        .dashboard-title { font-size: 1rem !important; }
        .pipeline-table { font-size: 0.6rem; }
        .pipeline-table th, .pipeline-table td { padding: 0.3rem 0.4rem; }
        .chart-header, .stMarkdown h3 { font-size: 0.8rem !important; }
        div[data-testid="stPlotlyChart"] { height: 180px !important; }
        .scroll-area { height: 185px !important; max-height: 185px !important; }
        .insights-scroll-area { max-height: 160px; }
    }

    /* Table Responsiveness Enhancements */
    .table-wrapper {
        width: 100%;
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch;
    }

    .pipeline-table {
        min-width: 600px; /* Force scroll on narrow screens instead of squashing */
        width: 100%;
    }

    /* Professional Pill-Style Toggle for Type */
    div[data-testid="stRadio"] > label {
        display: none !important;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] {
        background-color: #16181C !important;
        border-radius: 100px !important;
        padding: 2px !important; /* Reduced from 4px */
        gap: 2px !important; /* Reduced from 4px */
        border: 1px solid #2F3336 !important;
        display: flex !important;
        flex-direction: row !important;
        width: fit-content !important;
        margin-top: 2px !important;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] label {
        background-color: transparent !important;
        border-radius: 100px !important;
        padding: 4px 12px !important; /* Reduced from 6px 16px */
        margin: 0 !important;
        cursor: pointer !important;
        transition: all 0.2s ease-in-out !important;
        flex: 1 !important;
        min-width: 70px !important; /* Reduced from 80px */
        justify-content: center !important;
        white-space: nowrap !important; /* Prevent text wrap */
    }

    /* Hide the default radio circle/dot */
    div[data-testid="stRadio"] div[role="radiogroup"] label div:first-child:not([data-testid="stMarkdownContainer"]) {
        display: none !important;
    }

    /* Target the text container */
    div[data-testid="stRadio"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
        font-size: 0.75rem !important; /* Reduced from 0.8rem */
        font-weight: 600 !important;
        color: #71767B !important;
        margin: 0 !important;
        text-align: center !important;
        text-transform: uppercase !important;
        letter-spacing: 0.02em !important;
        white-space: nowrap !important; /* Extra insurance */
    }

    /* Active State: The "Pill" effect */
    div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) {
        background-color: #2F3336 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) div[data-testid="stMarkdownContainer"] p {
        color: #FFFFFF !important;
    }

    /* Hover effect for inactive */
    div[data-testid="stRadio"] div[role="radiogroup"] label:not(:has(input:checked)):hover div[data-testid="stMarkdownContainer"] p {
        color: #E7E9EA !important;
    }

    .header-container {
        padding: 0.5rem 0 0.75rem 0 !important;
        border-bottom: 1px solid #2F3336;
        margin-bottom: 1.5rem !important;
    }

    /* Target the main container */
    .block-container {
        padding-top: 1.5rem !important; /* Reduced from 3.5rem */
    }
    

</style>
""", unsafe_allow_html=True)

# Load Data
df = load_google_sheet_data()
# Default filter: Start from October 2025 onwards
if not df.empty:
    df = df[df['Month222'] >= '2025-10-01']
rev_df = load_revenue_summary_data()

if df.empty:
    st.error("Failed to load data. Please check the internet connection or Google Sheet permissions.")
    st.stop()

# --- Prepare Pipeline Data (for Filters) ---
df['Month_Year'] = df['Month222'].dt.strftime('%b %Y')
df['Month_Sort'] = df['Month222'].dt.to_period('M')

# Ensure C columns are numeric
cols_to_sum = ['C0', 'C1', 'C2', 'C3']
for col in cols_to_sum:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# Prepare shared aggregation data
def prepare_shared_data(filtered_df):
    # Aggregation
    agg_df = filtered_df.groupby(['Month_Sort', 'Month_Year'])[cols_to_sum].sum().reset_index()
    agg_df = agg_df.sort_values('Month_Sort')
    display_df = agg_df.drop(columns=['Month_Sort'])

    # Totals
    total_row = display_df[cols_to_sum].sum()
    total_data = {'Month_Year': 'TOTAL'}
    for col in cols_to_sum:
        total_data[col] = total_row[col]
    return agg_df, display_df, total_data


# --- Consolidated Header Row ---
st.markdown('<div class="header-container">', unsafe_allow_html=True)
# Ratios: Logo/Title, Nav Tabs, Type Toggle, Month, SBUs
col_brand, col_tabs, col_type, col_month, col_sbu = st.columns([1.8, 1.6, 1.0, 1.0, 1.0])

with col_brand:
    # Look for common logo filenames
    logo_file = None
    for ext in ["png", "jpg", "jpeg"]:
        if os.path.exists(f"logo.{ext}"):
            logo_file = f"logo.{ext}"
            break
            
    if logo_file:
        with open(logo_file, "rb") as f:
            logo_data = base64.b64encode(f.read()).decode()
        ext = logo_file.split(".")[-1].lower()
        mime_type = f"image/{'png' if ext == 'png' else 'jpeg'}"
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 12px; margin-top: -2px;">
                <img src="data:{mime_type};base64,{logo_data}" style="height: 32px; width: auto; object-fit: contain;">
                <div class="dashboard-title">Schbang C0-C3</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="dashboard-title">Schbang C0-C3</div>', unsafe_allow_html=True)

with col_tabs:
    # Custom Radio Tabs
    tab_choice = st.radio("Nav", ["Executive Overview", "Deep Dive & Insights"], horizontal=True, label_visibility="collapsed")

with col_type:
    # Professional pill-style toggle for Type
    selected_type = st.radio("Type", options=["VAS", "Retainer"], index=0, horizontal=True, label_visibility="collapsed")

with col_month:
    month_options = df.sort_values('Month222')['Month_Year'].dropna().unique().tolist()
    selected_months = st.multiselect("Month", options=month_options, placeholder="Month", label_visibility="collapsed")

with col_sbu:
    sbu_options = sorted(df['SBUs'].dropna().unique().tolist())
    selected_sbu = st.multiselect("SBUs", options=sbu_options, placeholder="SBUs", label_visibility="collapsed")

st.markdown('</div>', unsafe_allow_html=True)

# --- Filter Logic ---
filtered_df = df.copy()

if selected_months:
    filtered_df = filtered_df[filtered_df['Month_Year'].isin(selected_months)]

if selected_sbu:
    filtered_df = filtered_df[filtered_df['SBUs'].isin(selected_sbu)]

# Type Toggle Filtering (Always applies since it's a radio)
filtered_df = filtered_df[filtered_df['Type'] == selected_type]

# Execute shared data preparation
agg_df, display_df, total_data = prepare_shared_data(filtered_df)

# Consolidate Calculations for Insights (Shared by both tabs)
brand_perf = filtered_df.groupby('Brand Name')['C3'].sum().sort_values(ascending=False)
avp_metrics = filtered_df.groupby('AVP')[['C0', 'C1', 'C2', 'C3']].sum().reset_index()
avp_metrics['Total Pipeline'] = (avp_metrics['C0'] + avp_metrics['C1'] + avp_metrics['C2']) / 10000000
avp_metrics['Realized Value'] = avp_metrics['C3'] / 10000000

# ==========================================
# MAIN CONTENT
# ==========================================
if tab_choice == "Executive Overview":



    # --- Pipeline Section ---
    # Using pre-computed agg_df, display_df, and total_data

    # Funnel Data - Redefined Status-based Logic
    # C0-Ideation: Column J (C0 (Ideation/ Brainstorming Stage)) not blank
    c0_count = filtered_df['C0 (Ideation/ Brainstorming Stage)'].notna().sum()
    
    # C1-Pitch: Column L (C1 (Pitch Stage)) in ('C2', 'Pitch Completed', 'Proposal Sent', 'Round 2 Needed')
    pitch_statuses = ['C2', 'Pitch Completed', 'Proposal Sent', 'Round 2 Needed']
    c1_count = filtered_df['C1 (Pitch Stage)'].isin(pitch_statuses).sum()
    
    # C2-Negotiation: Column O (C2 (Negotiation Stage)) not 'Lost' and not blank
    c2_count = filtered_df[
        filtered_df['C2 (Negotiation Stage)'].notna() & 
        (filtered_df['C2 (Negotiation Stage)'].str.strip() != 'Lost') &
        (filtered_df['C2 (Negotiation Stage)'].str.strip() != '')
    ].shape[0]
    
    # C3-Closed: Column Q (C3 (Deal Closed Stage)) == 'Won'
    c3_count = (filtered_df['C3 (Deal Closed Stage)'].str.strip() == 'Won').sum()

    funnel_data = pd.DataFrame({
        'Stage': ['C0 - Ideation', 'C1 - Pitch', 'C2 - Negotiation', 'C3 - Closed'],
        'Count': [c0_count, c1_count, c2_count, c3_count]
    })

    fig = go.Figure(go.Funnel(
        y = funnel_data['Stage'],
        x = funnel_data['Count'],
        textposition = "inside",
        textinfo = "value+percent initial",
        opacity = 0.9, 
        marker = {"color": ["#1565C0", "#1976D2", "#42A5F5", "#90CAF9"]}, 
        connector = {"fillcolor": "#E0E0E0"}
    ))
    fig.update_layout(
        margin=dict(t=8, b=18, l=135, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E7E9EA", size=10),
        height=207,
        showlegend=False,
        yaxis=dict(
            showticklabels=False,
            automargin=False
        ),
        hoverlabel=dict(
            bgcolor="#16181C",
            bordercolor="#2F3336",
            font_size=11,
            font_family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif",
            font_color="white",
            align="left"
        )
    )
    
    # Add manual left-aligned annotations for stage names
    for i, row in funnel_data.iterrows():
        fig.add_annotation(
            x=-0.3,
            y=row['Stage'],
            text=f"<b>{row['Stage']}</b>",
            showarrow=False,
            xref="paper",
            yref="y",
            xanchor="left",
            font=dict(color="#E7E9EA", size=11),
        )
    fig.update_traces(
        textfont=dict(size=10),
        textinfo="value+percent initial",
        texttemplate="%{value}<br>%{percentInitial:.0%}",
        hovertemplate=(
            "<b>%{y}</b><br><br>"
            "Initial: <b>%{percentInitial:.0%}</b><br>"
            "Previous: <b>%{percentPrevious:.0%}</b>"
            "<extra></extra>"
        )
    )

    def fmt_cr(val):
        return f"₹{val/10000000:.1f} Cr"

    # Construct HTML Table with Trends
    html = '<div class="table-wrapper">'
    html += '<div class="scroll-area">'
    html += '<table class="pipeline-table" style="margin:0;">'
    html += '<thead><tr><th>Month</th><th>C0 - Ideation</th><th>C1 - Pitch</th><th>C2 - Negotiation</th><th>C3 - Closed</th></tr></thead>'
    html += '<tbody>'
    
    for i in range(len(display_df)):
        row = display_df.iloc[i]
        prev_row = display_df.iloc[i-1] if i > 0 else None
        
        row_html = f"<tr><td>{row['Month_Year']}</td>"
        for col in cols_to_sum:
            val = row[col]
            trend_html = '<span class="trend-neutral">-<span class="trend-pct">0%</span></span>' # Baseline for first row
            
            if prev_row is not None:
                p_val = prev_row[col]
                if p_val > 0:
                    diff = ((val - p_val) / p_val) * 100
                    if diff > 0.5:
                        trend_html = f'<span class="trend-up">▲<span class="trend-pct">{diff:.0f}%</span></span>'
                    elif diff < -0.5:
                        trend_html = f'<span class="trend-down">▼<span class="trend-pct">{abs(diff):.0f}%</span></span>'
                    else:
                        trend_html = f'<span class="trend-neutral">-<span class="trend-pct">0%</span></span>'
            
            row_html += f"<td>{fmt_cr(val)}{trend_html}</td>"
        row_html += "</tr>"
        html += row_html
        
    html += f"<tr class='total-row'><td>TOTAL</td><td>{fmt_cr(total_data['C0'])}</td><td>{fmt_cr(total_data['C1'])}</td><td>{fmt_cr(total_data['C2'])}</td><td>{fmt_cr(total_data['C3'])}</td></tr>"
    html += '</tbody></table></div>'

    # Layout - Balanced Alignment with Fine-Tuned Spacer Column
    # ROW 1: Headers aligned on the same horizontal line
    col_h_table, col_h_spacer, col_h_funnel = st.columns([1.5, 0.05, 1])
    with col_h_table:
        st.markdown('<div class="chart-header">C0-C3 Pipeline</div>', unsafe_allow_html=True)
    with col_h_funnel:
        st.markdown('<div class="chart-header">Funnel Analysis</div>', unsafe_allow_html=True)

    # ROW 2: Content aligned on the same horizontal line
    col_c_table, col_c_spacer, col_c_funnel = st.columns([1.5, 0.05, 1])
    with col_c_table:
        st.markdown(html, unsafe_allow_html=True)
    with col_c_funnel:
        st.plotly_chart(fig, use_container_width=True, config={'responsive': True, 'displayModeBar': False})

    # 4. c0c3 Insights (Consolidated Executive Insights)
    st.markdown('<div class="chart-header" style="margin-top: -1rem; margin-bottom: 0.5rem;">C0-C3 Insights</div>', unsafe_allow_html=True)
    
    # --- Calculate metrics for insights ---
    # Bottleneck Logic
    deals_with_c0 = filtered_df['C0 (Ideation/ Brainstorming Stage)'].notna().sum()
    deals_with_c1 = filtered_df['C1 (Pitch Stage)'].notna().sum()
    deals_with_c2 = filtered_df['C2 (Negotiation Stage)'].notna().sum()
    deals_with_c3 = (filtered_df['C3 (Deal Closed Stage)'].str.strip() == 'Won').sum()
    
    c0_to_c1 = (deals_with_c1 / deals_with_c0 * 100) if deals_with_c0 > 0 else 0
    c1_to_c2 = (deals_with_c2 / deals_with_c1 * 100) if deals_with_c1 > 0 else 0
    c2_to_c3 = (deals_with_c3 / deals_with_c2 * 100) if deals_with_c2 > 0 else 0
    
    conv_data = pd.Series({'C0→C1': c0_to_c1, 'C1→C2': c1_to_c2, 'C2→C3': c2_to_c3})
    bottleneck_stage = conv_data.idxmin()
    bottleneck_rate = conv_data.min()

    insights = []
    
    # A. Forecast & Potential Unlock
    c2_potential = (total_data['C2'] * 0.5) / 10000000 # 50% of Negotiation
    if c2_potential > 0:
        insights.append(f"🔮 **Revenue Forecast**: Pipeline data suggests a potential unlock of **₹{c2_potential:.2f} Cr** from deals currently in 'Negotiation' (assuming 50% closure probability). Focus on closing these C2 deals.")

    # B. Bottleneck Alert
    insights.append(f"⚠️ **Bottleneck Alert**: The lowest conversion rate is at **{bottleneck_stage}** stage (**{bottleneck_rate:.1f}%**). Focus on improving this transition to unlock pipeline potential.")

    # C. Top Performer
    if not avp_metrics.empty:
        avp_metrics['Conv'] = (avp_metrics['Realized Value'] / avp_metrics['Total Pipeline']).fillna(0)
        top_avp = avp_metrics.sort_values('Realized Value', ascending=False).iloc[0]
        insights.append(f"🏆 **Top Performer**: **{top_avp['AVP']}** is leading with **₹{top_avp['Realized Value']:.1f} Cr** realized value and **{top_avp['Conv']*100:.1f}%** conversion rate.")

    # D. Concentration Risk
    top_3_brands_val = brand_perf.head(3).sum()
    total_brands_val = brand_perf.sum()
    if total_brands_val > 0:
        conc_ratio = (top_3_brands_val / total_brands_val) * 100
        risk_level = "HIGH" if conc_ratio > 50 else "MEDIUM" if conc_ratio > 30 else "LOW"
        insights.append(f"⚖️ **Concentration Risk ({risk_level})**: The top 3 brands contribute **{conc_ratio:.1f}%** of revenue. {'Consider diversifying client base.' if risk_level == 'HIGH' else 'Monitor closely.' if risk_level == 'MEDIUM' else 'Healthy distribution.'}")

    # E. Stalled Opportunities
    brand_pipeline = filtered_df.groupby('Brand Name')[['C1', 'C2', 'C3']].sum()
    stalled_brands = brand_pipeline[(brand_pipeline['C1'] + brand_pipeline['C2'] > 50000000) & (brand_pipeline['C3'] == 0)]
    if not stalled_brands.empty:
        count_stalled = len(stalled_brands)
        example_brand = stalled_brands.index[0]
        insights.append(f"🐢 **Stalled Opportunities**: There are **{count_stalled}** brands (e.g., **{example_brand}**) with significant pipeline value (>₹5 Cr) but zero closures. Immediate review required.")

    # Render Insights
    for i in insights:
        st.info(i)
    
    if not insights:
        st.success("✅ Dashboard reflects stable performance. No critical anomalies detected.")


else:
    # ==========================================
    # TAB 2: DEEP DIVE & INSIGHTS
    # ==========================================
    
    # Calculate KPIs needed for insights
    total_pipeline = total_data['C0'] + total_data['C1'] + total_data['C2']
    total_closed = total_data['C3']
    total_pipeline_cr = total_pipeline / 10000000
    total_closed_cr = total_closed / 10000000

    # Calculate comprehensive AVP metrics for insight 3
    avp_perf = filtered_df.groupby('AVP').agg({
        'C0': 'sum',
        'C1': 'sum',
        'C2': 'sum',
        'C3': 'sum'
    }).reset_index()
    avp_perf['Closed Revenue (Cr)'] = avp_perf['C3'] / 10000000

    
    # ROW 1: Pipeline Conversion Funnel Analytics
    conv_col1, conv_col2 = st.columns([1.6, 1])
    
    with conv_col1:
        st.markdown('<div class="chart-header">Stage Conversion Rates</div>', unsafe_allow_html=True)
        # Calculate stage-wise deal counts
        total_deals = len(filtered_df)
        deals_with_c0 = filtered_df['C0 (Ideation/ Brainstorming Stage)'].notna().sum()
        deals_with_c1 = filtered_df['C1 (Pitch Stage)'].notna().sum()
        deals_with_c2 = filtered_df['C2 (Negotiation Stage)'].notna().sum()
        deals_with_c3 = (filtered_df['C3 (Deal Closed Stage)'] == 'Won').sum()
        
        # Calculate conversion rates
        c0_to_c1_rate = (deals_with_c1 / deals_with_c0 * 100) if deals_with_c0 > 0 else 0
        c1_to_c2_rate = (deals_with_c2 / deals_with_c1 * 100) if deals_with_c1 > 0 else 0
        c2_to_c3_rate = (deals_with_c3 / deals_with_c2 * 100) if deals_with_c2 > 0 else 0
        overall_conv = (deals_with_c3 / deals_with_c0 * 100) if deals_with_c0 > 0 else 0
        
        conversion_data = pd.DataFrame({
            'Stage': ['Overall', 'C2→C3', 'C1→C2', 'C0→C1'],
            'Conversion Rate': [overall_conv, c2_to_c3_rate, c1_to_c2_rate, c0_to_c1_rate],
            'Color': ['#00BA7C', '#42A5F5', '#1976D2', '#1565C0']
        })
        
        # Chart logic follows below (Title moved to header row)

        
        fig_conv = go.Figure(data=[
            go.Bar(
                x=conversion_data['Conversion Rate'],
                y=conversion_data['Stage'],
                orientation='h',
                text=[f'{x:.1f}%' for x in conversion_data['Conversion Rate']],
                textposition='outside',
                marker=dict(color=conversion_data['Color']),
                hovertemplate='<b>%{y}</b><br>Conversion: %{x:.1f}%<extra></extra>'
            )
        ])
        fig_conv.update_layout(
            xaxis_title='Conversion Rate (%)',
            yaxis_title=None,
            height=250,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E7E9EA", size=10),
            margin=dict(t=10, b=35, l=10, r=40),
            showlegend=False,
            bargap=0.4,
            xaxis=dict(fixedrange=True, range=[0, 100]),
            yaxis=dict(fixedrange=True)
        )
        st.plotly_chart(fig_conv, use_container_width=True, config={'displayModeBar': False, 'scrollZoom': False}, key="funnel_chart")
    
    with conv_col2:
        st.markdown('<div class="chart-header">Pipeline Health Metrics</div>', unsafe_allow_html=True)
        # Metrics logic follows below

        # Find bottleneck (lowest conversion rate)
        min_conv_idx = conversion_data.iloc[:-1]['Conversion Rate'].idxmin()
        bottleneck_stage = conversion_data.iloc[min_conv_idx]['Stage']
        bottleneck_rate = conversion_data.iloc[min_conv_idx]['Conversion Rate']
        
        # Create metrics HTML manually to keep inside container
        metrics_html = f"""
        <div style='height: 250px; display: flex; flex-direction: column; justify-content: center; border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 0.8rem;'>
            <div style='display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; gap: 0.6rem; height: 100%;'>
                <div style='background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 12px; display: flex; flex-direction: column; justify-content: center;'>
                    <div style='font-size: 0.75rem; color: #8B949E; margin-bottom: 0.3rem;'>Total Deals</div>
                    <div style='font-size: 1.4rem; font-weight: 700; color: #E7E9EA;'>{deals_with_c0:,}</div>
                </div>
                <div style='background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 12px; display: flex; flex-direction: column; justify-content: center;'>
                    <div style='font-size: 0.75rem; color: #8B949E; margin-bottom: 0.3rem;'>Closed Deals</div>
                    <div style='font-size: 1.4rem; font-weight: 700; color: #E7E9EA;'>{deals_with_c3:,}</div>
                </div>
                <div style='background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 12px; display: flex; flex-direction: column; justify-content: center;'>
                    <div style='font-size: 0.75rem; color: #8B949E; margin-bottom: 0.3rem;'>Win Rate</div>
                    <div style='font-size: 1.4rem; font-weight: 700; color: #00BA7C;'>{overall_conv:.1f}%</div>
                </div>
                <div style='background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 12px; display: flex; flex-direction: column; justify-content: center;'>
                    <div style='font-size: 0.75rem; color: #8B949E; margin-bottom: 0.3rem;'>Realized (C3)</div>
                    <div style='font-size: 1.4rem; font-weight: 700; color: #42A5F5;'>₹{total_data['C3']/10000000:.2f} Cr</div>
                </div>
            </div>
        </div>
        """
        st.markdown(metrics_html, unsafe_allow_html=True)
    
    st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
    
    # ROW 2: Team Performance Matrix
    st.markdown('<div class="chart-header">Performance Matrix: Pipeline vs Conversion</div>', unsafe_allow_html=True)
    
    # Calculate comprehensive AVP metrics
    avp_perf = filtered_df.groupby('AVP').agg({
        'C0': 'sum',
        'C1': 'sum',
        'C2': 'sum',
        'C3': 'sum'
    }).reset_index()
    
    avp_perf['Total Pipeline (Cr)'] = (avp_perf['C0'] + avp_perf['C1'] + avp_perf['C2']) / 10000000
    avp_perf['Closed Revenue (Cr)'] = avp_perf['C3'] / 10000000
    avp_perf['Conversion Rate (%)'] = (avp_perf['C3'] / avp_perf['C0'] * 100).fillna(0)
    
    # Count deals per AVP
    avp_deal_counts = filtered_df.groupby('AVP').size().reset_index(name='Deal Count')
    avp_perf = avp_perf.merge(avp_deal_counts, on='AVP')
    avp_perf['Avg Deal Size (Cr)'] = (avp_perf['Closed Revenue (Cr)'] / avp_perf['Deal Count']).fillna(0)
    
    # Performance scatter plot - Full width
    fig_perf = px.scatter(
        avp_perf,
        x='Total Pipeline (Cr)',
        y='Conversion Rate (%)',
        size='Closed Revenue (Cr)',
        color='Closed Revenue (Cr)',
        text='AVP',
        color_continuous_scale='Viridis',
        hover_data={'Total Pipeline (Cr)': ':.2f', 
                   'Conversion Rate (%)': ':.1f',
                   'Closed Revenue (Cr)': ':.2f',
                   'Avg Deal Size (Cr)': ':.2f'}
    )
    fig_perf.update_traces(textposition='top center', textfont=dict(size=11))
    
    # Calculate y-axis range with padding to prevent label clipping
    if len(avp_perf) > 0:
        max_conversion = avp_perf['Conversion Rate (%)'].max()
        y_max_perf = max_conversion * 1.30  # Add 30% padding above max value
    else:
        y_max_perf = 100
    
    fig_perf.update_layout(
        xaxis_title='Total Pipeline (₹ Cr)',
        yaxis_title='Conversion Rate (%)',
        height=250,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E7E9EA", size=10),
        margin=dict(t=35, b=35, l=45, r=20),
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', fixedrange=True),
        yaxis=dict(
            showgrid=True, 
            gridcolor='rgba(255,255,255,0.05)', 
            fixedrange=True,
            range=[0, y_max_perf]
        ),
        showlegend=False
    )
    st.plotly_chart(fig_perf, use_container_width=True, config={'displayModeBar': False, 'scrollZoom': False}, key="perf_matrix")
    
    st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
    
    # ROW 3: Revenue Analysis
    rev_col1, rev_col2 = st.columns(2)
    
    with rev_col1:
        st.markdown('<div class="chart-header">Revenue Shares By Brands</div>', unsafe_allow_html=True)
        # Top brands revenue concentration + Others
        brand_revenue = filtered_df.groupby('Brand Name')['C3'].sum().sort_values(ascending=False)
        total_revenue = brand_revenue.sum()
        
        if total_revenue > 0:
            top_5 = brand_revenue.head(5)
            others_sum = brand_revenue.iloc[5:].sum()
            treemap_df = pd.DataFrame([
                {'Brand': b, 'Revenue (Cr)': v / 10000000, 'Share': (v / total_revenue * 100)}
                for b, v in top_5.items()
            ])
            
            if others_sum > 0:
                others_row = pd.DataFrame([{
                    'Brand': 'Others',
                    'Revenue (Cr)': others_sum / 10000000,
                    'Share': (others_sum / total_revenue * 100)
                }])
                treemap_df = pd.concat([treemap_df, others_row], ignore_index=True)
                
            # Professional color palette - sophisticated gradient
            color_palette = [
                '#0A4D68',  # Deep teal (darkest)
                '#088395',  # Ocean blue
                '#05BFDB',  # Bright cyan
                '#00D9FF',  # Vibrant cyan
                '#7FDBFF',  # Light cyan
                '#B8E6F0'   # Pale cyan (lightest - for Others)
            ]
            
            # Assign colors based on revenue (highest to lowest)
            treemap_df['Color'] = color_palette[:len(treemap_df)]
            
            # Determine text color based on background brightness
            def get_text_color(hex_color):
                # Convert hex to RGB
                hex_color = hex_color.lstrip('#')
                r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
                # Calculate luminance
                luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
                return '#FFFFFF' if luminance < 0.6 else '#1A1A1A'
            
            treemap_df['TextColor'] = treemap_df['Color'].apply(get_text_color)
            
            fig_brands = px.treemap(
                treemap_df,
                path=['Brand'],
                values='Revenue (Cr)',
                color='Color',
                color_discrete_map={c: c for c in color_palette}
            )
            
            fig_brands.update_traces(
                textinfo="label+text",
                text=[f"₹{r:.1f}Cr ({s:.1f}%)" for r, s in zip(treemap_df['Revenue (Cr)'], treemap_df['Share'])],
                hovertemplate='<b>%{label}</b><br>Revenue: ₹%{value:.2f}Cr<extra></extra>',
                textfont=dict(size=11),
                marker=dict(
                    colors=treemap_df['Color'].tolist(),
                    line=dict(color='#2C2C2C', width=2)
                )
            )
            
            fig_brands.update_layout(
                height=250,
                margin=dict(t=5, b=5, l=5, r=5),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_brands, use_container_width=True, config={'displayModeBar': False, 'scrollZoom': False}, key="treemap_chart")
        else:
            st.info("No C3 revenue data available for current selection.")
    
    with rev_col2:
        st.markdown('<div class="chart-header">Pipeline vs Closed Revenue Trends (with Forecast)</div>', unsafe_allow_html=True)
        # Monthly trend with insights
        monthly_trend = agg_df.copy()
        monthly_trend['C0_Cr'] = monthly_trend['C0'] / 10000000
        monthly_trend['C3_Cr'] = monthly_trend['C3'] / 10000000
        monthly_trend['Pipeline Coverage'] = (monthly_trend['C0'] / monthly_trend['C3']).fillna(0)
        
        # Simple linear regression forecast for next 2 months (using numpy only)
        import numpy as np
        
        # Prepare data for forecasting
        n_months = len(monthly_trend)
        X = np.arange(n_months)
        
        # Simple linear regression function
        def simple_forecast(x, y, future_x):
            # Calculate slope and intercept
            x_mean = np.mean(x)
            y_mean = np.mean(y)
            slope = np.sum((x - x_mean) * (y - y_mean)) / np.sum((x - x_mean) ** 2)
            intercept = y_mean - slope * x_mean
            # Predict future values
            return slope * future_x + intercept
        
        # Forecast Pipeline (C0) and Closed (C3)
        y_c0 = monthly_trend['C0_Cr'].values
        y_c3 = monthly_trend['C3_Cr'].values
        
        # Generate forecasts for next 2 months (Feb 2026, Mar 2026)
        future_months = ['Feb 2026', 'Mar 2026']
        forecast_c0 = [simple_forecast(X, y_c0, n_months), simple_forecast(X, y_c0, n_months + 1)]
        forecast_c3 = [simple_forecast(X, y_c3, n_months), simple_forecast(X, y_c3, n_months + 1)]

        
        # Combine actual and forecast data
        all_months = list(monthly_trend['Month_Year']) + future_months
        
        fig_trend = go.Figure()
        
        # Actual Pipeline (C0) - solid line
        fig_trend.add_trace(go.Scatter(
            x=monthly_trend['Month_Year'], 
            y=monthly_trend['C0_Cr'], 
            mode='lines+markers+text', 
            name='Pipeline (C0)',
            line=dict(color='#1565C0', width=2),
            marker=dict(size=8),
            text=[f'₹{val:.1f}Cr' for val in monthly_trend['C0_Cr']],
            textposition='top center',
            textfont=dict(size=7)
        ))
        
        # Forecast Pipeline (C0) - dashed line
        fig_trend.add_trace(go.Scatter(
            x=[monthly_trend['Month_Year'].iloc[-1]] + future_months,
            y=[monthly_trend['C0_Cr'].iloc[-1]] + list(forecast_c0),
            mode='lines+markers+text',
            name='Pipeline (Forecast)',
            line=dict(color='#1565C0', width=2, dash='dash'),
            marker=dict(size=8, symbol='diamond'),
            text=[''] + [f'₹{val:.1f}Cr' for val in forecast_c0],
            textposition='top center',
            textfont=dict(size=7)
        ))
        
        # Actual Closed (C3) - solid line
        fig_trend.add_trace(go.Scatter(
            x=monthly_trend['Month_Year'], 
            y=monthly_trend['C3_Cr'], 
            mode='lines+markers+text', 
            name='Closed (C3)',
            line=dict(color='#00BA7C', width=2),
            marker=dict(size=8),
            text=[f'₹{val:.1f}Cr' for val in monthly_trend['C3_Cr']],
            textposition='bottom center',
            textfont=dict(size=7)
        ))
        
        # Forecast Closed (C3) - dashed line
        fig_trend.add_trace(go.Scatter(
            x=[monthly_trend['Month_Year'].iloc[-1]] + future_months,
            y=[monthly_trend['C3_Cr'].iloc[-1]] + list(forecast_c3),
            mode='lines+markers+text',
            name='Closed (Forecast)',
            line=dict(color='#00BA7C', width=2, dash='dash'),
            marker=dict(size=8, symbol='diamond'),
            text=[''] + [f'₹{val:.1f}Cr' for val in forecast_c3],
            textposition='bottom center',
            textfont=dict(size=7)
        ))
        
        # Calculate y-axis range with padding to prevent label clipping
        all_values = list(monthly_trend['C0_Cr']) + list(monthly_trend['C3_Cr']) + list(forecast_c0) + list(forecast_c3)
        max_value = max(all_values)
        y_max = max_value * 1.25  # Add 25% padding above max value
        
        fig_trend.update_layout(
            yaxis_title='Value (₹ Cr)',
            xaxis_title=None,
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                bgcolor='rgba(0,0,0,0)',
                font=dict(size=9)
            ),
            height=250,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E7E9EA", size=10),
            margin=dict(t=45, b=30, l=45, r=45),
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', fixedrange=True),
            yaxis=dict(
                showgrid=True, 
                gridcolor='rgba(255,255,255,0.05)', 
                fixedrange=True,
                range=[0, y_max]
            )
        )
        st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False, 'scrollZoom': False}, key="trends_chart")
    


