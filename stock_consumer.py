from kafka import KafkaConsumer
import json
import psycopg2

# Connect to PostgreSQL
conn = psycopg2.connect("dbname=etl_pipeline user=postgres password=yourpassword host=localhost port=5433")
cur = conn.cursor()

# Kafka Consumer setup
consumer = KafkaConsumer(
    'stock_prices',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')) if x else None
)

# Store data in PostgreSQL
for message in consumer:
    try:
        if message.value:  # Ensure the message is not empty
            data = message.value
            print(f"Received: {data}")  # Debugging print
            cur.execute("INSERT INTO stock_prices (symbol, price) VALUES (%s, %s)", (data["symbol"], data["price"]))
            conn.commit()
            print(f"Stored: {data}")
        else:
            print("Warning: Received an empty message.")
    except Exception as e:
        print(f"Error consuming messages: {e}")


