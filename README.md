## 🚀 Setup & Execution Guide (Conceptual)

To run this pipeline, you will need the following infrastructure services running:

- **Apache Kafka & Zookeeper:** (e.g., locally, via Docker, or a cloud service like AWS MSK)
- **PostgreSQL Database:** (e.g., locally, via Docker, or a cloud service like AWS RDS)

### 1. Infrastructure Setup (Conceptual)

* **Kafka & Zookeeper:**
    * Download and install Apache Kafka from [kafka.apache.org](https://kafka.apache.org/downloads).
    * Start Zookeeper: `bin/windows/zookeeper-server-start.bat config/zookeeper.properties` (adjust path)
    * Start Kafka: `bin/windows/kafka-server-start.bat config/server.properties` (adjust path)
    * Create Kafka Topic: `bin/windows/kafka-topics.bat --create --topic stock_prices --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1`
* **PostgreSQL Database:**
    * Ensure a database named `etl_pipeline` exists.
    * Update your `stock_prices` table with analytics columns:
        ```sql
        ALTER TABLE stock_prices
        ADD COLUMN sma_5min NUMERIC DEFAULT NULL,
        ADD COLUMN volatility_5min NUMERIC DEFAULT NULL;
        ```
    * **Important:** Configure database connection details (DB_USER, DB_PASSWORD, DB_HOST, DB_PORT) in `stock_consumer.py` and `dashboard.py` (preferably via environment variables, not hardcoded passwords!).

### 2. Python Application Setup

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run the Producer:**
    ```bash
    python stock_producer.py
    ```
3.  **Run the Consumer:**
    ```bash
    python stock_consumer.py
    ```
4.  **Run the Dashboard:**
    ```bash
    streamlit run dashboard.py
    ```

---

By including these notes, anyone looking at your GitHub repo will clearly understand the project's requirements and how it's designed to operate. It's perfectly fine to focus on the application code for your GitHub showcase!
