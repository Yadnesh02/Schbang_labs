import pandas as pd
import streamlit as st

@st.cache_data(ttl=600)  # Cache for 10 minutes to support "real-time" but not spam
def load_google_sheet_data():
    """
    Fetches data from the specified public Google Sheet.
    Returns a dataframe with relevant columns, including parsed dates.
    """
    # Public URL for CSV export of the 'Base_Data' sheet
    # Using the gviz API is often more reliable for export than the /export format for public sheets
    sheet_id = "1MbhJ_8sI1-j7N6vb_tJfipoDx7mTQ1SpQSEVoJw1bp4"
    sheet_name = "Base_Data" # Ensure this matches exactly
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    
    try:
        # Read CSV
        df = pd.read_csv(url)
        
        # Strip whitespace from column names to prevent matching issues
        df.columns = df.columns.astype(str).str.strip()
        
        # Ensure we have the columns we expect to filter on
        # BH -> Month222, BF -> AVP, B -> Brand Name, C -> Type
        required_cols = ['Month222', 'AVP', 'Brand Name', 'Type']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            st.warning(f"Note: Some expected columns are missing: {', '.join(missing_cols)}. Dashboard functionality might be limited.")
            # Map available columns as best as possible or continue
        
        # Parse Dates
        if 'Month222' in df.columns:
            df['Month222'] = pd.to_datetime(df['Month222'], dayfirst=True, errors='coerce')
        
        return df
        
    except Exception as e:
        st.error(f"Error loading data from Google Sheet: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=600)
def load_revenue_summary_data():
    """
    Fetches data from the 'Revenue_Summary' sheet.
    """
    sheet_id = "1MbhJ_8sI1-j7N6vb_tJfipoDx7mTQ1SpQSEVoJw1bp4"
    sheet_name = "Revenue_Summary"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    
    try:
        df = pd.read_csv(url)
        return df
    except Exception as e:
        st.error(f"Error loading Revenue Summary: {e}")
        return pd.DataFrame()
