import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd
from datetime import date, timedelta

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="BullPen Dashboard", layout="wide", page_icon="📈")

# Custom CSS to make metrics look good
st.markdown("""
<style>
div[data-testid="metric-container"] {
    background-color: #262730;
    border: 1px solid #464b5f;
    padding: 5% 5% 5% 10%;
    border-radius: 5px;
    color: rgb(30, 103, 119);
    overflow-wrap: break-word;
}
/* Break lines in metrics */
div[data-testid="metric-container"] > label {
  font-size: 1.2rem;
}
</style>
""", unsafe_allow_html=True)

st.title(" Bullpen Dashboard ")
st.markdown("Real-time financial dashboard for analyzing Equities and Crypto.")

# --- 2. SIDEBAR ---
st.sidebar.header(" Dashboard Settings")
st.sidebar.info("Project by: Aaish And Aayush")

# Expanded Asset List
ticker_dict = {
    "Apple Inc": "AAPL",
    "Tesla Motors": "TSLA",
    "Google (Alphabet)": "GOOGL",
    "Microsoft": "MSFT",
    "Bitcoin (USD)": "BTC-USD",
    "Ethereum (USD)": "ETH-USD",
    "Reliance Ind (India)": "RELIANCE.NS",
    "Tata Consultancy (India)": "TCS.NS"
}

selected_name = st.sidebar.selectbox("Select Asset", list(ticker_dict.keys()))
selected_ticker = ticker_dict[selected_name]

# Date Range
start_date = st.sidebar.date_input("Start Date", date.today() - timedelta(days=365))
end_date = st.sidebar.date_input("End Date", date.today())

# Technical Indicators
st.sidebar.subheader("Technical Indicators")
ma_days = st.sidebar.slider("Moving Average (Days)", 10, 200, 50)

# --- 3. DATA LOADING ---
@st.cache_data
def load_data(ticker, start, end):
    try:
        data = yf.download(ticker, start=start, end=end)
        # Fix for yfinance multi-index columns
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        data.reset_index(inplace=True)
        return data
    except Exception as e:
        st.error(f"Data Load Error: {e}")
        return None

data = load_data(selected_ticker, start_date, end_date)

# --- 4. MAIN INTERFACE ---
if data is not None and not data.empty:
    
    # --- A. METRICS ROW ---
    current_price = data['Close'].iloc[-1]
    prev_price = data['Close'].iloc[-2]
    daily_change = current_price - prev_price
    pct_change = (daily_change / prev_price) * 100
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current Price", f"{current_price:.2f}", f"{pct_change:.2f}%")
    col2.metric("Day High", f"{data['High'].iloc[-1]:.2f}")
    col3.metric("Day Low", f"{data['Low'].iloc[-1]:.2f}")
    col4.metric("Total Volume", f"{data['Volume'].iloc[-1]:,}")

    st.markdown("---")

    # --- B. TABS LAYOUT ---
    tab1, tab2, tab3 = st.tabs([" Price Charts", " Raw Data", " About"])

    with tab1:
        # Moving Average Calculation
        data[f'MA{ma_days}'] = data['Close'].rolling(window=ma_days).mean()

        # Main Chart
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=data['Date'], open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="OHLC"))
        fig.add_trace(go.Scatter(x=data['Date'], y=data[f'MA{ma_days}'], opacity=0.7, line=dict(color='cyan', width=2), name=f'{ma_days}-Day MA'))
        
        fig.update_layout(title=f'{selected_name} Price Trend', xaxis_rangeslider_visible=False, template="plotly_dark", height=600)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Historical Data Dictionary")
        st.dataframe(data.sort_values(by='Date', ascending=False), use_container_width=True)
        
        # Download Button
        csv = data.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Data as CSV", data=csv, file_name=f"{selected_ticker}_data.csv", mime="text/csv")

    with tab3:
        st.markdown(f"""
        ### Analysis Report for {selected_name}
        **Objective:** To analyze the volatility and trend direction of the asset using Python.
        
        **Methodology:**
        1. Data fetched live via `yfinance` API.
        2. Visualization rendered using `Plotly` for interactivity.
        """)

else:
    st.error("No data available for this selection.")