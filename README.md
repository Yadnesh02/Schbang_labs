# Financial Dashboard - C0C3 Vibe

A comprehensive Streamlit-based financial dashboard for tracking pipeline performance, revenue targets, and business insights.

## Features

- **Executive Overview**: FY'25-26 summary with H1/H2 targets and C0-C3 pipeline tracking
- **Deep Dive Analysis**: Advanced visualizations including efficiency matrices, revenue landscapes, and trend analysis
- **AI-Powered Insights**: Automated forecasting, concentration risk assessment, and opportunity identification
- **Interactive Filters**: Filter by month, AVP, brand name, and type

## Prerequisites

- Python 3.8 or higher
- Google Sheets access (for data source)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/YOUR_USERNAME/C0C3-Vibe.git
cd C0C3-Vibe
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure Google Sheets access:
   - Update the Google Sheets URL in `utils.py`
   - Ensure the sheet is publicly accessible or configure authentication

## Running Locally

```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

## Deployment to Streamlit Community Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click "New app"
5. Select your repository, branch, and `app.py` as the main file
6. Click "Deploy"

## Project Structure

```
C0C3-Vibe/
├── app.py                 # Main Streamlit application
├── utils.py              # Data loading utilities
├── requirements.txt      # Python dependencies
├── .streamlit/
│   └── config.toml      # Streamlit configuration
└── README.md            # This file
```

## Configuration

The app uses custom Streamlit theming configured in `.streamlit/config.toml`. You can modify the theme colors and settings there.

## Data Source

This dashboard connects to Google Sheets for real-time data. Make sure your Google Sheet has the following structure:
- Pipeline data with columns: Month222, AVP, Brand Name, Type, C0, C1, C2, C3
- Revenue summary with FY targets and achievements

## License

This project is private and proprietary.
