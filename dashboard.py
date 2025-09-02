
import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
import time

# --- Database Configuration (make sure this matches your consumer config) ---
DB_NAME = "etl_pipeline"
DB_USER = "postgres"
DB_PASSWORD = "yourpassword" # REMEMBER TO CHANGE THIS!
DB_HOST = "localhost"
DB_PORT = "5433"

# --- Streamlit App ---
st.set_page_config(layout="wide")
st.title("📈 Real-Time Stock Price Dashboard")

# Auto-refresh mechanism
placeholder = st.empty()

# Function to fetch data from PostgreSQL
@st.cache_data(ttl=5) # Cache data for 5 seconds to reduce DB load
def fetch_latest_stock_data():
    try:
        conn = psycopg2.connect(f"dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} host={DB_HOST} port={DB_PORT}")
        cur = conn.cursor()

        # Fetch latest price, SMA, Volatility for each stock
        query_latest = """
        SELECT
            s.symbol,
            s.price,
            s.timestamp,
            s.volume,
            s.sma_5min,
            s.volatility_5min
        FROM
            stock_prices s
        INNER JOIN (
            SELECT
                symbol,
                MAX(timestamp) AS max_timestamp
            FROM
                stock_prices
            GROUP BY
                symbol
        ) AS latest_times ON s.symbol = latest_times.symbol AND s.timestamp = latest_times.max_timestamp
        ORDER BY s.symbol;
        """
        cur.execute(query_latest)
        latest_data = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        df_latest = pd.DataFrame(latest_data, columns=column_names)
        conn.close()
        return df_latest
    except Exception as e:
        st.error(f"Error fetching latest data from database: {e}")
        return pd.DataFrame()

# Function to fetch historical data for a specific stock (for charting)
@st.cache_data(ttl=10) # Cache for 10 seconds
def fetch_historical_stock_data(symbol, limit=30):
    try:
        conn = psycopg2.connect(f"dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} host={DB_HOST} port={DB_PORT}")
        cur = conn.cursor()
        query_historical = f"""
        SELECT timestamp, price, sma_5min, volatility_5min
        FROM stock_prices
        WHERE symbol = %s
        ORDER BY timestamp DESC
        LIMIT %s;
        """
        cur.execute(query_historical, (symbol, limit))
        historical_data = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        df_historical = pd.DataFrame(historical_data, columns=column_names)
        df_historical['timestamp'] = pd.to_datetime(df_historical['timestamp'])
        df_historical = df_historical.sort_values('timestamp')
        conn.close()
        return df_historical
    except Exception as e:
        st.error(f"Error fetching historical data for {symbol}: {e}")
        return pd.DataFrame()

# Main loop for auto-refresh
while True:
    with placeholder.container():
        st.markdown("### Latest Prices & Analytics")
        df_latest = fetch_latest_stock_data()
        if not df_latest.empty:
            st.dataframe(df_latest.set_index('symbol'), use_container_width=True)

            st.markdown("### Stock Price Trends")
            selected_symbol = st.selectbox("Select a Stock to View Trend:", df_latest['symbol'].unique())

            if selected_symbol:
                df_historical = fetch_historical_stock_data(selected_symbol, limit=30)
                if not df_historical.empty:
                    # Plot Price and SMA
                    fig_price = px.line(df_historical, x='timestamp', y=['price', 'sma_5min'],
                                        title=f"{selected_symbol} Price & 5-min SMA Over Time")
                    st.plotly_chart(fig_price, use_container_width=True)

                    # Plot Volatility
                    fig_volatility = px.line(df_historical, x='timestamp', y='volatility_5min',
                                             title=f"{selected_symbol} 5-min Volatility Over Time",
                                             labels={'volatility_5min': 'Volatility (Std Dev)'})
                    st.plotly_chart(fig_volatility, use_container_width=True)
                else:
                    st.info(f"No historical data available yet for {selected_symbol} (or not enough for analytics).")
        else:
            st.info("No stock data available yet. Ensure producer and consumer are running.")


    time.sleep(5)
