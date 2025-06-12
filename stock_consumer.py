from kafka import KafkaConsumer
import json
import psycopg2
from collections import deque
import statistics

# Configuration
DB_NAME = "etl_pipeline"
DB_USER = "postgres"
DB_PASSWORD = "yourpassword" # REMEMBER TO CHANGE THIS!
DB_HOST = "localhost"
DB_PORT = "5433"
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
KAFKA_TOPIC = 'stock_prices'

# Rolling window size for analytics (5 minutes = 5 data points if fetched every minute)
WINDOW_SIZE = 5

# Dictionary to store rolling prices for each stock symbol
# Format: { 'SYMBOL': deque([price1, price2, ...]) }
stock_price_windows = {}

# Connect to PostgreSQL
try:
    conn = psycopg2.connect(f"dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} host={DB_HOST} port={DB_PORT}")
    cur = conn.cursor()
    print("Successfully connected to PostgreSQL")
except Exception as e:
    print(f"Error connecting to PostgreSQL: {e}")
    exit()

# Kafka Consumer setup
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_deserializer=lambda x: json.loads(x.decode('utf-8')) if x else None,
    # auto_offset_reset='earliest' # Uncomment if you want to read from the beginning of the topic
)
print(f"Kafka Consumer connected to topic: {KAFKA_TOPIC}")


# Store data and calculate analytics in PostgreSQL
for message in consumer:
    try:
        if message.value:
            data = message.value
            symbol = data.get("symbol")
            price = data.get("price")
            timestamp_str = data.get("timestamp")
            volume = data.get("volume") # Volume is now streamed from producer

            if None in [symbol, price, timestamp_str]:
                print(f"Skipping incomplete message: {data}")
                continue

            print(f"Received: Symbol={symbol}, Price={price:.2f}, Time={timestamp_str}, Volume={volume}")

            # --- Rolling Window and Analytics Calculation ---
            if symbol not in stock_price_windows:
                stock_price_windows[symbol] = deque(maxlen=WINDOW_SIZE)

            stock_price_windows[symbol].append(price)

            sma_5min = None
            volatility_5min = None

            if len(stock_price_windows[symbol]) == WINDOW_SIZE:
                # Calculate SMA
                sma_5min = sum(stock_price_windows[symbol]) / WINDOW_SIZE

                # Calculate Volatility (Standard Deviation)
                if WINDOW_SIZE > 1: # Need at least 2 points for stdev
                    volatility_5min = statistics.stdev(stock_price_windows[symbol])
                else:
                    volatility_5min = 0.0

                print(f"  {symbol} - SMA({WINDOW_SIZE}min): {sma_5min:.2f}, Volatility({WINDOW_SIZE}min): {volatility_5min:.2f}")

            # --- Store data in PostgreSQL ---
            # Adjusted INSERT query to match your existing table columns
            # Assuming 'id' is auto-incrementing and thus not included in the INSERT
            insert_query = """
            INSERT INTO stock_prices (symbol, price, timestamp, volume, sma_5min, volatility_5min)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cur.execute(insert_query,
                        (symbol, price, timestamp_str, volume, sma_5min, volatility_5min))
            conn.commit()
            print(f"Stored: {symbol} - Price: {price:.2f} with analytics.")

        else:
            print("Warning: Received an empty message.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON message: {e} - Message: {message.value}")
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
    except Exception as e:
        print(f"Error consuming messages: {e}")

cur.close()
conn.close()
print("Consumer stopped. Database and Kafka connections closed.")
