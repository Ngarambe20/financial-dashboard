import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf

st.set_page_config(page_title="Financial Dashboard", layout="wide")

# Custom CSS for styling and color fixes
st.markdown("""
    <style>
    /* Main background */
    .stApp { background-color: #2b2f42; color: white; }

    /* TAB STYLING FIX */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; background-color: #1e2233; padding: 10px; border-radius: 5px; }

    /* Make ALL tab text white by default */
    .stTabs [data-baseweb="tab"] { 
        height: 50px; 
        white-space: pre-wrap; 
        background-color: transparent; 
        color: white !important; /* Forces text to be white */
        font-weight: 500; 
        border-radius: 4px; 
        padding: 10px 20px; 
    }

    /* Make the ACTIVE tab stand out */
    .stTabs [aria-selected="true"] { 
        background-color: #3b415a !important; 
        color: white !important; 
        font-weight: bold; 
        border-bottom: 3px solid #ff4b4b !important; 
    }

    /* Dropdown styling */
    .stSelectbox div[data-baseweb="select"] > div { background-color: white; color: black; }
    .stSelectbox label, .stRadio label { color: #a0aabf !important; }

    /* News box styling */
    .news-box { background-color: #1e2233; padding: 15px; border-radius: 5px; margin-bottom: 10px; border: 1px solid #3b415a; }
    .text-green { color: #00ff00 !important; font-weight: bold; }
    .text-red { color: #ff4b4b !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("Financial Modeling Exploration Dashboard")

tab1, tab2, tab3 = st.tabs(["Portfolio Performance", "Model Performance", "Jupyter Notebook"])

with tab1:
    # Top Controls
    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
    with col1:
        ticker = st.selectbox("Pick Ticker:", ["AAPL", "MSFT", "CSCO", "TSLA", "NVDA"])
    with col2:
        st.selectbox("Pick a Model:", ["Random Forest Regressor 120/30"])
    with col3:
        st.write("") 
    with col4:
        st.markdown("<h4 style='text-align: right;'><a href='#' style='color: white; text-decoration: none;'>Dashboard Info Link</a></h4>", unsafe_allow_html=True)

    # Time Filters
    st.markdown("---")
    f_col1, f_col2, f_col3 = st.columns([4, 2, 2])
    with f_col1:
        st.markdown("<p style='color: #a0aabf;'>Pick How You Want to Analyze Data:</p>", unsafe_allow_html=True)
        st.selectbox("Ticker Filter", ["Ticker"], label_visibility="collapsed")
    with f_col2:
        st.markdown("<p style='color: #a0aabf;'>Filter Data:</p>", unsafe_allow_html=True)
        st.selectbox("Select Ticker", [ticker], label_visibility="collapsed")
    with f_col3:
        st.markdown("<p style='color: #a0aabf;'>Time Range:</p>", unsafe_allow_html=True)
        time_range = st.radio("Time", ["7 Days", "30 Days", "1 Year", "All"], horizontal=True, label_visibility="collapsed")

    # Data fetching
    @st.cache_data
    def get_data(symbol):
        try:
            df = yf.download(symbol, start="2020-01-01", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = [col[0] for col in df.columns]
                df = df.reset_index()
                if 'index' in df.columns:
                    df = df.rename(columns={'index': 'Date'})
                return df
        except Exception:
            pass
        url = "https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv"
        df = pd.read_csv(url)
        return df.rename(columns={'Date': 'Date', 'AAPL.Close': 'Close', 'AAPL.Open': 'Open', 'AAPL.High': 'High', 'AAPL.Low': 'Low', 'AAPL.Volume': 'Volume'})

    df = get_data(ticker)

    # --- MAIN LAYOUT ---
    left_col, mid_col, right_col = st.columns([3, 5, 3])

    with left_col:
        st.markdown("<p style='color: #a0aabf;'>Sample Portfolio (10 Shares)</p>", unsafe_allow_html=True)
        if not df.empty and 'Close' in df.columns:
            latest_price = df['Close'].iloc[-1]
            portfolio_value = latest_price * 10
            st.markdown(f"<h2 style='margin-top: -15px;'>${portfolio_value:,.2f} <span class='text-green' style='font-size: 16px;'>▲ Live</span></h2>", unsafe_allow_html=True)

            portfolio_data = {
                "Ticker": [ticker],
                "Shares": [10],
                "Value": [f"${portfolio_value:,.2f}"],
                "Gain": ["<span class='text-green'>+5.2%</span>"]
            }
            html_table = pd.DataFrame(portfolio_data).to_html(escape=False, index=False, classes='table')
            st.markdown(f"<div style='background-color: #1e2233; color: white; padding: 10px; border-radius: 5px;'>{html_table}</div>", unsafe_allow_html=True)

    with mid_col:
        st.markdown(f"<h4 style='text-align: center; color: white;'>{ticker} Closing Price</h4>", unsafe_allow_html=True)

        if df is not None and not df.empty:
            if time_range == "7 Days": df_filtered = df.tail(7)
            elif time_range == "30 Days": df_filtered = df.tail(30)
            elif time_range == "1 Year": df_filtered = df.tail(365)
            else: df_filtered = df

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_filtered['Date'].astype(str).tolist(), y=df_filtered['Close'].tolist(), line=dict(color='#00ff00', width=2)))
            fig.update_layout(
                paper_bgcolor='#1e2233', plot_bgcolor='#3b415a',
                margin=dict(l=10, r=10, t=20, b=10), height=350,
                xaxis=dict(showgrid=False), 
                yaxis=dict(showgrid=True, gridcolor='#2b2f42', title="Price")
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with right_col:
        st.markdown(f"<h5 style='text-align: center; background-color: #3b415a; padding: 5px; border-radius: 5px 5px 0 0; color: white;'>News for {ticker}</h5>", unsafe_allow_html=True)
        mock_news = [
            {"title": f"{ticker} leverages on new market data", "date": "Fri 20 Aug 2021 08:14"},
            {"title": f"{ticker} gains 1% in post-earnings action", "date": "Thu 19 Aug 2021 09:46"},
            {"title": f"{ticker} CEO discusses Q4 2021 results", "date": "Wed 18 Aug 2021 20:40"}
        ]
        for news in mock_news:
            st.markdown(f"""
            <div class="news-box">
                <p style="font-size: 12px; margin-bottom: 2px; color: #a0aabf;">{news['date']}</p>
                <p style="font-size: 14px; color: white;">{news['title']}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<h5 style='text-align: center; background-color: #3b415a; padding: 5px; border-radius: 5px 5px 0 0; margin-top: 20px; color: white;'>Top Sentiment: Technology</h5>", unsafe_allow_html=True)
        sentiment_data = {
            "Ticker": ["JNPR", "AMAT", "TXN", "CRM", "NTAP", "ADBE", "FFIV", "WDC"],
            "Sentiment": ["<span class='text-green'>Weak</span>", "<span class='text-red'>Very Weak</span>", "<span class='text-green'>Weak</span>", "<span class='text-green'>Weak</span>", "<span class='text-green'>Weak</span>", "<span class='text-red'>Very Weak</span>", "<span class='text-green'>Weak</span>", "<span class='text-green'>Weak</span>"],
            "Trend": ["<span class='text-red'>down</span>", "<span class='text-red'>down</span>", "<span class='text-red'>down</span>", "<span class='text-red'>down</span>", "<span class='text-red'>down</span>", "<span class='text-red'>down</span>", "<span class='text-red'>down</span>", "<span class='text-red'>down</span>"]
        }
        html_sentiment = pd.DataFrame(sentiment_data).to_html(escape=False, index=False, classes='table')
        st.markdown(f"<div style='background-color: #1e2233; color: white; padding: 10px; border-radius: 5px;'>{html_sentiment}</div>", unsafe_allow_html=True)

    # --- BOTTOM VALUATION CHARTS ---
    st.markdown("---")
    st.markdown("<h5 style='text-align: center; color: white;'>Valuation Comparisons</h5>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    tickers_list = ["INTC", "CSCO", "CRM", "ADBE", "ORCL", "NVDA", "MSFT", "AAPL"]
    pe_ratios = [12.5, 21.9, 42.2, 49.6, 15.6, 93.0, 36.5, 30.4]
    ps_ratios = [3.3, 5.5, 8.1, 9.6, 5.5, 41.8, 15.1, 33.0]
    ev_sales = [3.1, 4.3, 8.8, 9.5, 4.3, 19.3, 12.4, 25.5]
    ev_ebitda = [6.9, 13.7, 23.4, 26.0, 13.7, 55.9, 22.3, 69.6]

    def create_bar_chart(x_data, title):
        fig = go.Figure(go.Bar(
            x=x_data, y=tickers_list, orientation='h', text=x_data, textposition='inside', 
            insidetextanchor='end', marker=dict(color='#6a7ca8')
        ))
        fig.update_layout(
            paper_bgcolor='#2b2f42', plot_bgcolor='#2b2f42', font=dict(color='white'),
            height=300, margin=dict(l=0, r=0, t=30, b=0), showlegend=False,
            title=dict(text=title, x=0.5, font=dict(size=12, color='#a0aabf')),
            xaxis=dict(showgrid=False, showticklabels=False), yaxis=dict(showgrid=False)
        )
        colors = ['#2e4a8a' if t == ticker else '#6a7ca8' for t in tickers_list]
        fig.update_traces(marker_color=colors)
        return fig

    with c1: st.plotly_chart(create_bar_chart(pe_ratios, "P/E Ratio Comparison"), use_container_width=True)
    with c2: st.plotly_chart(create_bar_chart(ps_ratios, "P/S Ratio Comparison"), use_container_width=True)
    with c3: st.plotly_chart(create_bar_chart(ev_sales, "EV/SALES Ratio Comparison"), use_container_width=True)
    with c4: st.plotly_chart(create_bar_chart(ev_ebitda, "EV/EBITDA Ratio Comparison"), use_container_width=True)

with tab2:
    st.write("Model Performance metrics go here.")

with tab3:
    st.write("Jupyter Notebook code goes here.")
