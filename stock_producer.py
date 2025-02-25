from kafka import KafkaProducer
import json
import yfinance as yf
import time

# Set up Kafka producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# List of important stock symbols
stocks = ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA", "NVDA"]

# Function to fetch stock price
def fetch_stock_price(symbol):
    stock = yf.Ticker(symbol)
    data = stock.history(period="1d", interval="1m")
    return data["Close"].iloc[-1]

# Send stock prices to Kafka
while True:
    for stock in stocks:
        try:
            stock_price = fetch_stock_price(stock)
            producer.send("stock_prices", {"symbol": stock, "price": stock_price})
            print(f"Sent: {stock} - {stock_price}")
        except Exception as e:
            print(f"Error fetching {stock}: {e}")
    
    time.sleep(60)  # Fetch every 60 seconds



