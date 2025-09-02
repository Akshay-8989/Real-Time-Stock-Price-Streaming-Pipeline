
from kafka import KafkaProducer
import json
import yfinance as yf
import time
from datetime import datetime

# Set up Kafka producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# List of important stock symbols
stocks = ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA", "NVDA"]

# Function to fetch stock data (including timestamp and volume)
def fetch_stock_data(symbol):
    stock = yf.Ticker(symbol)
    data = stock.history(period="1d", interval="1m")
    if not data.empty:
        latest_row = data.iloc[-1]
        return {
            "price": latest_row["Close"],
            "timestamp": latest_row.name.isoformat(), # Convert pandas timestamp to ISO format string
            "volume": latest_row["Volume"]
        }
    return None

# Send stock prices to Kafka
while True:
    for stock in stocks:
        try:
            stock_data = fetch_stock_data(stock)
            if stock_data:
                message = {
                    "symbol": stock,
                    "price": stock_data["price"],
                    "timestamp": stock_data["timestamp"],
                    "volume": stock_data["volume"]
                }
                producer.send("stock_prices", message)
                print(f"Sent: {stock} - Price: {stock_data['price']:.2f}, Timestamp: {stock_data['timestamp']}")
            else:
                print(f"No data fetched for {stock}")
        except Exception as e:
            print(f"Error fetching or sending {stock}: {e}")

    time.sleep(60)

