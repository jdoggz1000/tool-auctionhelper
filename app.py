import streamlit as st
import pandas as pd
import re
from playwright.sync_api import sync_playwright

# Set up the page layout
st.set_page_config(page_title="Auction Bid Tracker", page_icon="", layout="wide")
st.title(" Auction Bid Tracker")

# 1. Function to scrape the current price from the URL
def fetch_current_bid(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=15000)
            
            # Wait up to 10 seconds for the element with id="fixedheading" to load
            page.wait_for_selector("#fixedheading", timeout=10000)
            price_text = page.inner_text("#fixedheading")
            browser.close()
            
            # Get the text, which will look like: "444    (6 bidders)    $210"
            # Extract the dollar amount using regex
            matches = re.findall(r'\$([0-9,]+(?:\.[0-9]{2})?)', price_text)
            if matches:
                # Return the match (remove commas if there are any, e.g., $1,200 -> 1200)
                return float(matches[0].replace(',', ''))
            return 0.0
    except Exception:
        # If it times out or fails to find the element
        return None

# 3. Sidebar for File Upload
st.sidebar.header("Upload your Data")
uploaded_file = st.sidebar.file_uploader("Upload your Auction CSV/Excel File", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Load the file
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    # Standardize column names (strip whitespaces)
    df.columns = df.columns.str.strip()
    
    # Filter only to items where you have set a Max Bid
    if 'Max Bid' in df.columns:
        df['Max Bid'] = pd.to_numeric(df['Max Bid'].astype(str).str.replace(r'[\$,]', '', regex=True), errors='coerce')
        df = df.dropna(subset=['Max Bid'])
        
        st.write(f"### Tracking {len(df)} items with active Max Bids")
        
        # Refresh Button
        if st.button("🔄 Refresh Latest Bids"):
            current_bids = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Loop through all filtered items to get prices
            for idx, row in enumerate(df.itertuples()):
                url = getattr(row, 'URL')
                status_text.text(f"Fetching Lot {getattr(row, 'Lot')}...")
                
                bid = fetch_current_bid(url)
                current_bids.append(bid)
                
                # Update progress bar
                progress_bar.progress((idx + 1) / len(df))
            
            status_text.text("Finished fetching bids!")
            df['Current Bid'] = current_bids
            
            # Determine Status
            def determine_status(row):
                if pd.isna(row['Current Bid']):
                    return "⚠️ Error Fetching"
                elif row['Current Bid'] > row['Max Bid']:
                    return "🔴 Exceeded Max Bid"
                else:
                    return "🟢 Within Budget"

            df['Status'] = df.apply(determine_status, axis=1)
            
            # Display results beautifully
            display_df = df[['Lot', 'Description', 'Max Bid', 'Current Bid', 'Status', 'URL']]
            
            # Apply color coding to the dataframe
            def style_status(val):
                color = '#ff4b4b' if 'Exceeded' in val else '#09ab3b' if 'Within' in val else '#ffa421'
                return f'color: {color}; font-weight: bold'

            styled_df = display_df.style.map(style_status, subset=['Status'])\
                                        .format({'Max Bid': '${:,.2f}', 'Current Bid': '${:,.2f}'}, na_rep="N/A")
            
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
            
            # Summary Metrics
            within_budget = len(df[df['Status'] == '🟢 Within Budget'])
            out_of_budget = len(df[df['Status'] == '🔴 Exceeded Max Bid'])
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Items within Budget", within_budget)
            col2.metric("Items Exceeded", out_of_budget)
            col3.metric("Total Max Bid Exposure", f"${df['Max Bid'].sum():,.2f}")
            
    else:
        st.error("Could not find a 'Max Bid' column in your file. Please verify your column headers.")
else:
    st.info("👈 Please upload your Catalog Export CSV or Excel file to get started.")