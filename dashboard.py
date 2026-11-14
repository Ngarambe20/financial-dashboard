import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf

st.set_page_config(page_title="Financial Dashboard", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #2b2f42; color: white; }
    .metric-box { background-color: #1e2233; padding: 15px; border-radius: 5px; border: 1px solid #3b415a; }
    .news-box { background-color: #1e2233; padding: 15px; border-radius: 5px; margin-bottom: 10px; border: 1px solid #3b415a; }
    </style>
""", unsafe_allow_html=True)

st.title("Financial Modeling Exploration Dashboard")

col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    ticker = st.selectbox("Pick Ticker:", ["AAPL", "MSFT", "CSCO", "TSLA"])
with col2:
    model_type = st.selectbox("Pick a Model:", ["Random Forest Regressor 120/30", "XGBoost Classifier", "LSTM Neural Network"])
with col3:
    st.write("Dashboard Info Link")

st.markdown("---")
left_col, mid_col, right_col = st.columns([3, 6, 3])

with left_col:
    st.metric(label="Current Portfolio Value", value="$144.6k", delta="44.65%")
    portfolio_data = {
        "Ticker": ["PEAK", "BAC", "GILD", "T", "KIM", "HAL", "AAPL"],
        "Current Value": ["$59,214.08", "$7,416.78", "$4,595.61", "$4,338.76", "$6,508.14", "$6,307.02", "$12,450.00"],
        "% Gain": ["27.44%", "14.20%", "18.30%", "1.04%", "35.68%", "14.01%", "12.50%"]
    }
    st.dataframe(pd.DataFrame(portfolio_data), hide_index=True, use_container_width=True)

with mid_col:
    st.markdown(f"<h4 style='text-align: center;'> {ticker} Closing Price</h4>", unsafe_allow_html=True)

    @st.cache_data
    def get_data(symbol):
        try:
            df = yf.download(symbol, start="2020-01-01", progress=False)
            if not df.empty:
                return df.reset_index()
        except Exception:
            pass
        url = "https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv"
        df = pd.read_csv(url)
        return df.rename(columns={'Date': 'Date', 'AAPL.Close': 'Close'})

    df = get_data(ticker)

    if not df.empty:
        # --- THE FIX: Flatten MultiIndex columns if yfinance was used ---
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] for col in df.columns]
        # Ensure 'Close' is a standard column
        if 'Close' not in df.columns:
            close_col = [c for c in df.columns if 'Close' in str(c)][0]
            df['Close'] = df[close_col]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['Date'].astype(str).tolist(), y=df['Close'].tolist(), 
                                 line=dict(color='#00ff00', width=2)))
        fig.update_layout(
            paper_bgcolor='#1e2233', plot_bgcolor='#2b2f42',
            margin=dict(l=0, r=0, t=20, b=0), height=350,
            xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#3b415a')
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with right_col:
    st.markdown(f"<h5 style='text-align: center;'>News for {ticker}</h5>", unsafe_allow_html=True)
    mock_news = [
        {"title": f"{ticker} leverages on every drop", "date": "Fri 20 Aug 2021"},
        {"title": f"{ticker} gains 1% in post-earnings action", "date": "Thu 19 Aug 2021"},
        {"title": f"{ticker} CEO discusses Q4 2021 results", "date": "Wed 18 Aug 2021"}
    ]
    for news in mock_news:
        st.markdown(f"""
        <div class="news-box">
            <p style="font-size: 12px; margin-bottom: 2px;">{news['date']}</p>
            <p style="font-size: 14px;">{news['title']}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<h5 style='text-align: center; margin-top: 20px;'>Top Sentiment: Technology</h5>", unsafe_allow_html=True)
    sentiment_data = {
        "Ticker": ["JNPR", "AMAT", "TXN", "CRM", "NTAP", "ADBE", "FFIV", "WDC"],
        "Sentiment": ["Weak", "Very Weak", "Weak", "Weak", "Weak", "Very Weak", "Weak", "Weak"],
        "Trend": ["down", "down", "down", "down", "down", "down", "down", "down"]
    }
    st.dataframe(pd.DataFrame(sentiment_data), hide_index=True, use_container_width=True)

st.markdown("---")
st.markdown("<h5 style='text-align: center;'>Valuation Comparisons</h5>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

tickers_list = ["AAPL", "MSFT", "NVDA", "ORCL", "ADBE", "CRM", "CSCO", "INTC"]
pe_ratios = [30.4, 36.5, 93.0, 15.6, 49.6, 42.2, 21.9, 12.5]
ps_ratios = [33.0, 15.1, 41.8, 5.5, 9.6, 8.1, 5.5, 3.3]
ev_sales = [25.5, 12.4, 19.3, 4.3, 9.5, 8.8, 4.3, 3.1]
ev_ebitda = [69.6, 22.3, 55.9, 13.7, 26.0, 23.4, 13.7, 6.9]

def create_bar_chart(x_data, title):
    fig = go.Figure(go.Bar(
        x=x_data, y=tickers_list, orientation='h', text=x_data, textposition='outside', marker=dict(color='#6a7ca8')
    ))
    fig.update_layout(
        paper_bgcolor='#2b2f42', plot_bgcolor='#2b2f42', font=dict(color='white'),
        height=300, margin=dict(l=0, r=0, t=30, b=0), showlegend=False,
        title=dict(text=title, x=0.5, font=dict(size=12)),
        xaxis=dict(showgrid=False, showticklabels=False), yaxis=dict(showgrid=False)
    )
    return fig

with c1: st.plotly_chart(create_bar_chart(pe_ratios, "P/E Ratio"), use_container_width=True)
with c2: st.plotly_chart(create_bar_chart(ps_ratios, "P/S Ratio"), use_container_width=True)
with c3: st.plotly_chart(create_bar_chart(ev_sales, "EV/SALES Ratio"), use_container_width=True)
with c4: st.plotly_chart(create_bar_chart(ev_ebitda, "EV/EBITDA Ratio"), use_container_width=True)
