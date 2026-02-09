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
    
    /* Custom Table Styling - X Inspired */
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
        width: 140px; /* Reverted to default for Pipeline */
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
        width: 140px; /* Reverted to default for Pipeline */
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
    
    .pipeline-table .total-row td {
        background-color: #16181C;
        font-weight: 700;
        border-top: 1px solid #2F3336;
        border-bottom: none;
        color: #FFFFFF;
        text-align: center !important;
    }
    
    .deficit-negative {
        color: #F4212E;
        font-weight: 600;
    }

    /* Chart Container with Light Border */
    /* Target Streamlit Plotly containers directly */
    div[data-testid="stPlotlyChart"] {
        border: 1px solid #2F3336;
        border-radius: 12px;
        padding: 0 !important;
        background-color: #0E1117;
        margin-top: 5px !important; /* Nudge down to match table start */
        margin-bottom: 1.5rem;
        width: 100% !important;
        height: 300px !important; /* Adjusted to keep bottom aligned */
    }
    
    /* Chart Headers Refinement */
    .chart-header, .stMarkdown h3 {
        margin-top: 0 !important;
        margin-bottom: 0.5rem !important; /* Standard positive margin */
        text-align: left !important;
        margin-left: 15px !important;
        font-weight: 600;
        font-size: 1.1rem;
        color: #E7E9EA;
        height: 1.5rem; /* Fixed height for top alignment */
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
        margin-bottom: 1.5rem;
        padding: 0 !important;
    }
    
    .scroll-area {
        height: 305px !important; /* Exact match with Funnel height */
        max-height: 305px !important;
        overflow-y: auto;
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

    /* Responsive Adjustments & Zoom Safety */
    @media (max-width: 1400px) {
        .dashboard-title { font-size: 1.4rem !important; }
        .header-container { padding: 0.25rem 0 !important; }
    }

    @media (max-width: 1200px) {
        [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
            gap: 1rem !important;
        }
        .dashboard-title { font-size: 1.25rem !important; }
    }

    @media (max-width: 768px) {
        .dashboard-title { font-size: 1.1rem !important; }
        .stMarkdown h3 { font-size: 1.1rem !important; }
        .pipeline-table { font-size: 0.75rem !important; }
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

    /* Styled Radio as Tabs */
    div[data-testid="stRadio"] > label {
        display: none !important;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] {
        flex-direction: row !important;
        gap: 1.25rem !important;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] label {
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
        cursor: pointer !important;
    }

    /* Hide the radio circle */
    div[data-testid="stRadio"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
        font-size: 0.875rem !important;
        font-weight: 600 !important;
        color: #71767B !important;
        transition: color 0.2s ease;
        margin: 0 !important;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] label:hover div[data-testid="stMarkdownContainer"] p {
        color: #E7E9EA !important;
    }

    /* Selection Indicator (Green Underline) */
    div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) div[data-testid="stMarkdownContainer"] p {
        color: #00BA7C !important;
        border-bottom: 2px solid #00BA7C;
        padding-bottom: 2px;
    }

    /* Hide radio input circle specifically */
    div[data-testid="stRadio"] div[role="radiogroup"] [data-testid="stWidgetLabel"] {
        display: none !important;
    }

    /* Target the radio button element itself to hide the circle */
    div[data-testid="stRadio"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] ~ div {
        display: none !important;
    }
    
    /* Alternative more robust circle hiding */
    div[data-testid="stRadio"] div[role="radiogroup"] label [class*="st-"] {
        /* We want to hide the SVG or the circle but NOT the text container */
    }
    
    /* Surgical hide of the radio circle/dot */
    div[data-testid="stRadio"] div[role="radiogroup"] label div:first-child:not([data-testid="stMarkdownContainer"]) {
        display: none !important;
    }

    .header-container {
        padding: 0.5rem 0 0.75rem 0 !important; /* Reduced top padding */
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
# Adjusted Ratios: Brand(1.5), Tabs(1.8), Filters(1, 1, 1, 1)
col_brand, col_tabs, col1, col2, col3, col4 = st.columns([1.5, 1.8, 1, 1, 1, 1])

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
    # Custom Radio Tabs (Using horizontal radio for toggle feel)
    tab_choice = st.radio("Nav", ["Executive Overview", "Deep Dive & Insights"], horizontal=True, label_visibility="collapsed")

with col1:
    month_options = df.sort_values('Month222')['Month_Year'].dropna().unique().tolist()
    selected_months = st.multiselect("Month", options=month_options, placeholder="Month", label_visibility="collapsed")

with col2:
    avp_options = sorted(df['AVP'].dropna().unique().tolist())
    selected_avp = st.multiselect("AVP", options=avp_options, placeholder="AVP", label_visibility="collapsed")

with col3:
    brand_options = sorted(df['Brand Name'].dropna().unique().tolist())
    selected_brand = st.multiselect("Brand Name", options=brand_options, placeholder="Brand Name", label_visibility="collapsed")

with col4:
    type_options = sorted(df['Type'].dropna().unique().tolist())
    selected_type = st.multiselect("Type", options=type_options, placeholder="Type", label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# --- Filter Logic ---
filtered_df = df.copy()

if selected_months:
    filtered_df = filtered_df[filtered_df['Month_Year'].isin(selected_months)]

if selected_avp:
    filtered_df = filtered_df[filtered_df['AVP'].isin(selected_avp)]

if selected_brand:
    filtered_df = filtered_df[filtered_df['Brand Name'].isin(selected_brand)]

if selected_type:
    filtered_df = filtered_df[filtered_df['Type'].isin(selected_type)]

# Execute shared data preparation
agg_df, display_df, total_data = prepare_shared_data(filtered_df)

# ==========================================
# MAIN CONTENT
# ==========================================
if tab_choice == "Executive Overview":
    # --- FY'25 - 26 Summary Table (Placed after Filters) ---
    if not rev_df.empty:
        st.markdown("### FY'25 - 26 Insights")
        
        # Process Revenue Data
        def clean_currency(val):
            if isinstance(val, str):
                val = val.replace('₹', '').replace(',', '').replace(' Cr', '').strip()
                return float(val) if val else 0.0
            return float(val) if val else 0.0

        rev_cols_map = {
            'SBUs': 'SBUs',
            'Annual Target111': 'Annual Target',
            'H1 Target111': 'H1 Target',
            'H1 Achieved111': 'H1 Achieved',
            'H1 Deficit111': 'H1 Deficit',
            'H2 Target111': 'H2 Target',
            'H2 Target + H1 Deficit111': 'H1 Deficit + H2 Target',
            'Balance H2 Target111': 'Balance H2 Target'
        }
        
        needed_cols = list(rev_cols_map.keys())
        available_cols = [c for c in needed_cols if c in rev_df.columns]
        
        summary_df = rev_df[available_cols].copy()
        summary_df.rename(columns=rev_cols_map, inplace=True)
        
        numeric_cols = [
            'Annual Target', 'H1 Target', 'H1 Achieved', 'H1 Deficit', 
            'H2 Target', 'H1 Deficit + H2 Target', 'Balance H2 Target'
        ]
        
        for col in numeric_cols:
            if col in summary_df.columns:
                summary_df[col] = summary_df[col].apply(clean_currency) / 10000000
        
        # Calculate Total Row
        total_rev_row = summary_df[numeric_cols].sum()
        total_rev_dict = {'SBUs': 'TOTAL'}
        for col in numeric_cols:
            total_rev_dict[col] = total_rev_row[col]
            
        def fmt_curr(val):
            return f"₹{val:.2f} Cr"

        # HTML Construction - Professional Single Table with Sticky Header/Footer
        rev_html = '<div class="table-wrapper" style="margin-top: 8px;">'
        rev_html += '<div class="insights-scroll-area">'
        rev_html += '<table class="pipeline-table insights-table" style="margin:0;">'
        
        # Header (Sticky in scroll-area via CSS or standard structure)
        rev_html += '<thead style="position: sticky; top: 0; z-index: 10;"><tr>'
        rev_html += '<th>SBUs</th>'
        rev_html += '<th>Annual Target</th>'
        rev_html += '<th>H1 Target</th>'
        rev_html += '<th>H1 Achieved</th>'
        rev_html += '<th>H1 Deficit</th>'
        rev_html += '<th>H2 Target</th>'
        rev_html += '<th>H1 Deficit + H2 Target</th>'
        rev_html += '<th>Balance H2 Target</th>'
        rev_html += '</tr></thead>'
        
        rev_html += '<tbody>'
        for _, row in summary_df.iterrows():
            sbu = row.get('SBUs', '')
            if pd.isna(sbu) or str(sbu).strip() == '':
                continue
                
            rev_html += f"<tr><td>{sbu}</td>"
            rev_html += f"<td>{fmt_curr(row.get('Annual Target', 0))}</td>"
            rev_html += f"<td>{fmt_curr(row.get('H1 Target', 0))}</td>"
            rev_html += f"<td>{fmt_curr(row.get('H1 Achieved', 0))}</td>"
            
            deficit = row.get('H1 Deficit', 0)
            rev_html += f"<td class='deficit-negative'>▼ {fmt_curr(abs(deficit))}</td>" 
            
            rev_html += f"<td>{fmt_curr(row.get('H2 Target', 0))}</td>"
            rev_html += f"<td>{fmt_curr(row.get('H1 Deficit + H2 Target', 0))}</td>"
            rev_html += f"<td>{fmt_curr(row.get('Balance H2 Target', 0))}</td>"
            rev_html += "</tr>"
        rev_html += "</tbody>"
        
        # Footer
        rev_html += '<tfoot style="position: sticky; bottom: 0; z-index: 10;">'
        rev_html += "<tr class='total-row'>"
        rev_html += '<td>TOTAL</td>'
        rev_html += f'<td>{fmt_curr(total_rev_dict["Annual Target"])}</td>'
        rev_html += f'<td>{fmt_curr(total_rev_dict["H1 Target"])}</td>'
        rev_html += f'<td>{fmt_curr(total_rev_dict["H1 Achieved"])}</td>'
        rev_html += f'<td class="deficit-negative">▼ {fmt_curr(abs(total_rev_dict["H1 Deficit"]))}</td>'
        rev_html += f'<td>{fmt_curr(total_rev_dict["H2 Target"])}</td>'
        rev_html += f'<td>{fmt_curr(total_rev_dict["H1 Deficit + H2 Target"])}</td>'
        rev_html += f'<td>{fmt_curr(total_rev_dict["Balance H2 Target"])}</td>'
        rev_html += "</tr></tfoot>"
        
        rev_html += "</table></div></div>"
        st.markdown(rev_html, unsafe_allow_html=True)
        # Add significant vertical spacing after the first section
        st.markdown('<div style="margin-bottom: 1rem;"></div>', unsafe_allow_html=True)


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
        margin=dict(t=30, b=10, l=120, r=10), # Large left margin for annotations
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E7E9EA", size=10),
        height=305,
        showlegend=False,
        yaxis=dict(
            showticklabels=False, # Hide default right-aligned labels
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
            x=-0.35, # Adjusted for visibility within the 120px margin
            y=row['Stage'],
            text=f"<b>{row['Stage']}</b>",
            showarrow=False,
            xref="paper",
            yref="y",
            xanchor="left",
            font=dict(color="#E7E9EA", size=11.5), # Increased from 10
        )
    fig.update_traces(
        textfont=dict(size=11.5), # Increased font size within bars
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


else:
    # ==========================================
    # TAB 2: DEEP DIVE & INSIGHTS
    # ==========================================
    st.markdown("## Deep Dive Analysis")
    
    # 1. KPIs
    total_pipeline = total_data['C0'] + total_data['C1'] + total_data['C2']
    total_closed = total_data['C3']
    conversion_rate = (total_closed / total_pipeline * 100) if total_pipeline > 0 else 0
    
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Total Pipeline (C0-C2)", f"₹{total_pipeline/10000000:.1f} Cr")
    kpi2.metric("Total Closed (C3)", f"₹{total_closed/10000000:.1f} Cr", delta=f"{conversion_rate:.1f}% Conv. Rate")
    
    # Top Brand
    brand_perf = filtered_df.groupby('Brand Name')['C3'].sum().sort_values(ascending=False)
    top_brand = brand_perf.index[0] if not brand_perf.empty else "N/A"
    top_brand_val = brand_perf.iloc[0] if not brand_perf.empty else 0
    kpi3.metric("Top Brand (by Closed Deal)", top_brand, f"₹{top_brand_val/10000000:.1f} Cr")
    
    st.markdown("---")
    
    # 2. Advanced Charts (Row 1)
    row1_col1, row1_col2 = st.columns(2)
    
    with row1_col1:
        # Group by AVP
        avp_metrics = filtered_df.groupby('AVP')[['C0', 'C1', 'C2', 'C3']].sum().reset_index()
        avp_metrics['Total Pipeline'] = (avp_metrics['C0'] + avp_metrics['C1'] + avp_metrics['C2']) / 10000000
        avp_metrics['Realized Value'] = avp_metrics['C3'] / 10000000
        
        # Avoid Clutter: Filter out zero values if needed, or keep all
        fig_scatter = px.scatter(
            avp_metrics,
            x='Total Pipeline',
            y='Realized Value',
            color='AVP',
            size='Realized Value',
            hover_name='AVP',
            text='AVP',
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig_scatter.update_traces(textposition='top center')
        fig_scatter.update_layout(
            xaxis_title="Pipeline Opportunity (₹ Cr)",
            yaxis_title="Closed Revenue (₹ Cr)",
            showlegend=False,
            height=360,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E7E9EA"),
            margin=dict(t=20, b=40, l=40, r=20)
        )
        st.markdown('<div class="chart-header">Conversion Efficiency</div>', unsafe_allow_html=True)
        st.plotly_chart(fig_scatter, use_container_width=True, config={'responsive': True, 'displayModeBar': False})
        
    with row1_col2:
        # Group for Treemap - Filter out nulls
        tree_df = filtered_df[filtered_df['C3'] > 0].copy()
        # Remove rows with null or empty Type/Brand Name
        tree_df = tree_df.dropna(subset=['Type', 'Brand Name'])
        tree_df = tree_df[(tree_df['Type'].str.strip() != '') & (tree_df['Brand Name'].str.strip() != '')]
        
        if not tree_df.empty:
            fig_tree = px.treemap(
                tree_df,
                path=[px.Constant("All"), 'Type', 'Brand Name'],
                values='C3',
                color='C3',
                color_continuous_scale='Greens'
            )
            fig_tree.update_layout(
                height=360,
                margin=dict(t=20, l=10, r=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#E7E9EA")
            )
            st.markdown('<div class="chart-header">Revenue Landscape</div>', unsafe_allow_html=True)
            st.plotly_chart(fig_tree, use_container_width=True, config={'responsive': True, 'displayModeBar': False})
        else:
            st.info("No closed deals to display in Treemap.")

    # 3. Trends & Performance (Row 2)
    row2_col1, row2_col2 = st.columns(2)
    
    with row2_col1:
        avp_perf = filtered_df.groupby('AVP')['C3'].sum().reset_index().sort_values('C3', ascending=True)
        avp_perf['C3_Cr'] = avp_perf['C3'] / 10000000
        
        fig_avp = px.bar(avp_perf, y='AVP', x='C3_Cr', orientation='h', text_auto='.1f', color='C3_Cr', color_continuous_scale='Blues')
        fig_avp.update_layout(
            xaxis_title="C3 Value (₹ Cr)", 
            yaxis_title=None, 
            showlegend=False, 
            height=340, 
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)", 
            font=dict(color="#E7E9EA"),
            margin=dict(t=20, b=40, l=20, r=20)
        )
        st.markdown('<div class="chart-header">AVP Leaderboard</div>', unsafe_allow_html=True)
        st.plotly_chart(fig_avp, use_container_width=True, config={'responsive': True, 'displayModeBar': False})

    with row2_col2:
        monthly_trend = agg_df.copy()
        monthly_trend['C0_Cr'] = monthly_trend['C0'] / 10000000
        monthly_trend['C3_Cr'] = monthly_trend['C3'] / 10000000
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=monthly_trend['Month_Year'], y=monthly_trend['C0_Cr'], mode='lines+markers', name='C0 (Ideation)'))
        fig_trend.add_trace(go.Scatter(x=monthly_trend['Month_Year'], y=monthly_trend['C3_Cr'], mode='lines+markers', name='C3 (Closed)'))
        fig_trend.update_layout(
            yaxis_title="Value (₹ Cr)", 
            hovermode="x unified", 
            legend=dict(orientation="h", y=1.2, x=0), 
            height=340, 
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)", 
            font=dict(color="#E7E9EA"),
            margin=dict(t=20, b=40, l=40, r=20)
        )
        st.markdown('<div class="chart-header">Monthly Revenue Trend</div>', unsafe_allow_html=True)
        st.plotly_chart(fig_trend, use_container_width=True, config={'responsive': True, 'displayModeBar': False})

    # 4. Advanced AI Insights
    st.markdown("### 🤖 Advanced AI Insights")
    
    insights = []
    
    # A. Forecast & Potential Unlock
    c2_potential = (total_data['C2'] * 0.5) / 10000000 # 50% of Negotiation
    if c2_potential > 0:
        insights.append(f"🔮 **Revenue Forecast**: Pipeline data suggests a potential unlock of **₹{c2_potential:.2f} Cr** from deals currently in 'Negotiation' (assuming 50% closure probability). Focus on closing these C2 deals.")

    # B. Concentration Risk
    top_3_brands_val = brand_perf.head(3).sum()
    total_brands_val = brand_perf.sum()
    if total_brands_val > 0:
        conc_ratio = (top_3_brands_val / total_brands_val) * 100
        if conc_ratio > 70:
            insights.append(f"⚖️ **High Concentration Risk**: The top 3 brands contribute **{conc_ratio:.1f}%** of total closed revenue. Diversify efforts across other brands to mitigate risk.")

    # C. Stalled Opportunities (High Pipeline but Low Closure)
    # Group by Brand, check High C1+C2 but Low C3
    brand_pipeline = filtered_df.groupby('Brand Name')[['C1', 'C2', 'C3']].sum()
    stalled_brands = brand_pipeline[(brand_pipeline['C1'] + brand_pipeline['C2'] > 50000000) & (brand_pipeline['C3'] == 0)] # > 5Cr pipeline, 0 closed
    if not stalled_brands.empty:
        count_stalled = len(stalled_brands)
        example_brand = stalled_brands.index[0]
        insights.append(f"🐢 **Stalled Opportunities**: There are **{count_stalled}** brands (e.g., **{example_brand}**) with significant pipeline value (>₹5 Cr) but zero closures. Immediate review required.")

    # D. Efficiency Insight
    # Find AVP with High Pipeline but Low Conversion
    if not avp_metrics.empty:
        avp_metrics['Conv'] = (avp_metrics['Realized Value'] / avp_metrics['Total Pipeline']).fillna(0)
        low_conv_avp = avp_metrics[avp_metrics['Total Pipeline'] > 5].sort_values('Conv').head(1) # >5Cr pipeline
        if not low_conv_avp.empty:
            name = low_conv_avp.iloc[0]['AVP']
            rate = low_conv_avp.iloc[0]['Conv'] * 100
            insights.append(f"🎯 **Coaching Opportunity**: **{name}** has a strong pipeline but a lower conversion rate (**{rate:.1f}%**). Support them in 'Negotiation' to 'Closed' transitions.")

    # Render Insights
    for i in insights:
        st.info(i)
    
    if not insights:
        st.success("✅ Dashboard reflects stable performance. No critical anomalies detected.")

