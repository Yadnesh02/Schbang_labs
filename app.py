import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import load_google_sheet_data, load_revenue_summary_data

# Page Config
st.set_page_config(
    page_title="Financial Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .stBlock, .stPlotlyChart {
        border-radius: 10px;
        overflow: hidden;
    }
    div[data-testid="stMetric"] {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
    }
    
    /* Custom Table Styling (Dark Theme for both tables) */
    .pipeline-table {
        width: 100%;
        border-collapse: collapse;
        font-family: "Source Sans Pro", sans-serif;
        color: #FAFAFA;
        margin-top: 20px;
        margin-bottom: 30px;
    }
    .pipeline-table th {
        background-color: #0d47a1; /* Blue header */
        color: white;
        padding: 12px;
        text-align: right; 
        font-weight: bold;
        border-bottom: 2px solid #1e88e5;
    }
    .pipeline-table th:first-child {
        text-align: left; 
    }
    .pipeline-table td {
        padding: 12px;
        text-align: right;
        border-bottom: 1px solid #333;
        background-color: #1e1e1e; /* Dark row background */
    }
    .pipeline-table td:first-child {
        text-align: left;
        font-weight: 500;
        background-color: #262730; /* Slightly lighter for first column */
    }
    .pipeline-table tr:hover td {
        background-color: #333;
    }
    .pipeline-table .total-row td {
        background-color: #2d2d3a;
        font-weight: bold;
        border-top: 2px solid #555;
        color: #ffffff;
    }
    .deficit-negative {
        color: #FF5252; /* Bright red for visibility on dark background */
        font-weight: bold;
    }

    /* Scrollable Canvas for Summary Table */
    .summary-scroll-container {
        max-height: 350px; 
        overflow-y: auto;
        border: 1px solid #333;
        border-radius: 4px;
        margin-bottom: 30px;
    }
    .summary-scroll-container th {
        position: sticky;
        top: 0;
        z-index: 2;
        box-shadow: 0 2px 2px -1px rgba(0, 0, 0, 0.4);
    }
    .summary-scroll-container .total-row td {
        position: sticky;
        bottom: 0;
        z-index: 2;
        box-shadow: 0 -2px 2px -1px rgba(0, 0, 0, 0.4);
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


# --- Filters (Placed at Top) ---
st.title("Financial Dashboard")
# st.markdown("### Filters")

with st.container():
    col1, col2, col3, col4 = st.columns(4)

    # 1. Month Filter
    with col1:
        month_options = df.sort_values('Month222')['Month_Year'].dropna().unique().tolist()
        selected_months = st.multiselect("Month", options=month_options)

    # 2. AVP Filter
    with col2:
        avp_options = sorted(df['AVP'].dropna().unique().tolist())
        selected_avp = st.multiselect("AVP", options=avp_options)

    # 3. Brand Name Filter
    with col3:
        brand_options = sorted(df['Brand Name'].dropna().unique().tolist())
        selected_brand = st.multiselect("Brand Name", options=brand_options)

    # 4. Type Filter
    with col4:
        type_options = sorted(df['Type'].dropna().unique().tolist())
        selected_type = st.multiselect("Type", options=type_options)

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



# --- Tabs ---
tab1, tab2 = st.tabs(["Executive Overview", "Deep Dive & Insights"])

# ==========================================
# TAB 1: EXECUTIVE OVERVIEW
# ==========================================
with tab1:
    # --- FY'25 - 26 Summary Table (Placed after Filters) ---
    if not rev_df.empty:
        st.markdown("### FY'25 - 26 Summary")
        
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

        # HTML Construction (Using dark theme class pipeline-table)
        rev_html = '<div class="summary-scroll-container">'
        rev_html += '<table class="pipeline-table">'
        rev_html += '<thead><tr>'
        rev_html += '<th>SBUs</th><th>Annual Target</th><th>H1 Target</th><th>H1 Achieved</th><th>H1 Deficit</th><th>H2 Target</th><th>H1 Deficit + H2 Target</th><th>Balance H2 Target</th>'
        rev_html += '</tr></thead><tbody>'
        
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
            
        # Total Row
        rev_html += "<tr class='total-row'><td>TOTAL</td>"
        rev_html += f"<td>{fmt_curr(total_rev_dict['Annual Target'])}</td>"
        rev_html += f"<td>{fmt_curr(total_rev_dict['H1 Target'])}</td>"
        rev_html += f"<td>{fmt_curr(total_rev_dict['H1 Achieved'])}</td>"
        rev_html += f"<td class='deficit-negative'>▼ {fmt_curr(abs(total_rev_dict['H1 Deficit']))}</td>"
        rev_html += f"<td>{fmt_curr(total_rev_dict['H2 Target'])}</td>"
        rev_html += f"<td>{fmt_curr(total_rev_dict['H1 Deficit + H2 Target'])}</td>"
        rev_html += f"<td>{fmt_curr(total_rev_dict['Balance H2 Target'])}</td>"
        rev_html += "</tr>"
        
        rev_html += "</tbody></table></div>"
        st.markdown(rev_html, unsafe_allow_html=True)


    # --- Pipeline Section ---
    st.markdown("### C0-C3 Pipeline")

    # Aggregation
    agg_df = filtered_df.groupby(['Month_Sort', 'Month_Year'])[cols_to_sum].sum().reset_index()
    agg_df = agg_df.sort_values('Month_Sort')
    display_df = agg_df.drop(columns=['Month_Sort'])

    # Totals
    total_row = display_df[cols_to_sum].sum()
    total_data = {'Month_Year': 'TOTAL'}
    for col in cols_to_sum:
        total_data[col] = total_row[col]

    # Funnel Data
    c0_count = (filtered_df['C0'] != 0).sum()
    c1_count = (filtered_df['C1'] != 0).sum()
    c2_count = (filtered_df['C2'] != 0).sum()
    c3_count = (filtered_df['C3'] != 0).sum()

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
        margin=dict(t=30, b=20, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white", size=14),
        height=350,
        showlegend=False,
        title=dict(text="C3 Funnel", x=0.5, font=dict(size=18))
    )

    def fmt_cr(val):
        return f"₹{val/10000000:.1f} Cr"

    # Construct HTML Table
    html = '<table class="pipeline-table">'
    html += '<thead><tr><th>Month</th><th>C0 - Ideation</th><th>C1 - Pitch</th><th>C2 - Negotiation</th><th>C3 - Closed</th></tr></thead>'
    html += '<tbody>'
    for index, row in display_df.iterrows():
        html += f"<tr><td>{row['Month_Year']}</td><td style='text-align:right'>{fmt_cr(row['C0'])}</td><td style='text-align:right'>{fmt_cr(row['C1'])}</td><td style='text-align:right'>{fmt_cr(row['C2'])}</td><td style='text-align:right'>{fmt_cr(row['C3'])}</td></tr>"
    html += f"<tr class='total-row'><td>TOTAL</td><td style='text-align:right'>{fmt_cr(total_data['C0'])}</td><td style='text-align:right'>{fmt_cr(total_data['C1'])}</td><td style='text-align:right'>{fmt_cr(total_data['C2'])}</td><td style='text-align:right'>{fmt_cr(total_data['C3'])}</td></tr>"
    html += '</tbody></table>'

    # Layout
    col_table, col_funnel = st.columns([1.5, 1])
    with col_table:
        st.markdown(html, unsafe_allow_html=True)
    with col_funnel:
        st.markdown("##### C3 Funnel")
        st.plotly_chart(fig, use_container_width=True)


# ==========================================
# TAB 2: DEEP DIVE & INSIGHTS
# ==========================================
with tab2:
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
    st.markdown("### 📊 Strategic View")
    row1_col1, row1_col2 = st.columns(2)
    
    with row1_col1:
        st.markdown("##### Efficiency Matrix (Pipeline vs Closed)")
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
            xaxis_title="Active Pipeline Opportunity (₹ Cr)",
            yaxis_title="Closed Revenue (₹ Cr)",
            showlegend=False,
            height=400,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with row1_col2:
        st.markdown("##### Revenue Landscape (Sector & Brand)")
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
                height=400,
                margin=dict(t=0, l=0, r=0, b=0),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white")
            )
            st.plotly_chart(fig_tree, use_container_width=True)
        else:
            st.info("No closed deals to display in Treemap.")

    # 3. Trends & Performance (Row 2)
    st.markdown("### 📈 Trends & Performance")
    row2_col1, row2_col2 = st.columns(2)
    
    with row2_col1:
        st.markdown("##### AVP Leaderboard")
        avp_perf = filtered_df.groupby('AVP')['C3'].sum().reset_index().sort_values('C3', ascending=True)
        avp_perf['C3_Cr'] = avp_perf['C3'] / 10000000
        
        fig_avp = px.bar(avp_perf, y='AVP', x='C3_Cr', orientation='h', text_auto='.1f', color='C3_Cr', color_continuous_scale='Blues')
        fig_avp.update_layout(xaxis_title="C3 Value (₹ Cr)", yaxis_title=None, showlegend=False, height=350, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
        st.plotly_chart(fig_avp, use_container_width=True)

    with row2_col2:
        st.markdown("##### Monthly Trend")
        monthly_trend = agg_df.copy()
        monthly_trend['C0_Cr'] = monthly_trend['C0'] / 10000000
        monthly_trend['C3_Cr'] = monthly_trend['C3'] / 10000000
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=monthly_trend['Month_Year'], y=monthly_trend['C0_Cr'], mode='lines+markers', name='C0 (Ideation)'))
        fig_trend.add_trace(go.Scatter(x=monthly_trend['Month_Year'], y=monthly_trend['C3_Cr'], mode='lines+markers', name='C3 (Closed)'))
        fig_trend.update_layout(yaxis_title="Value (₹ Cr)", hovermode="x unified", legend=dict(orientation="h", y=1.1), height=350, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
        st.plotly_chart(fig_trend, use_container_width=True)

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

