# Real-Time Stock Price Streaming Pipeline

## 📌 Overview
This project streams **real-time stock prices** using **Kafka, Zookeeper, and PostgreSQL**. The producer fetches stock prices via **Yahoo Finance (yFinance)** and sends them to a Kafka topic. The consumer reads from Kafka and stores the data in **PostgreSQL**.

## 🛠️ Technologies Used
- **Kafka** – Real-time message streaming
- **Zookeeper** – Kafka's cluster management
- **Yahoo Finance API** – Fetching stock prices
- **PostgreSQL** – Storing stock data
- **Python (kafka-python, yfinance, psycopg2)** – Data processing & Kafka communication

## 🚀 Setup & Execution Guide

### 1️⃣ Install Dependencies
```sh
pip install -r requirements.txt

## Ensure Kafka & Zookeeper are running:

cd D:\data_engineering\kafka
.\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties
.\bin\windows\kafka-server-start.bat .\config\server.properties

## Create Kafka Topic

.\bin\windows\kafka-topics.bat --create --topic stock_prices --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1


