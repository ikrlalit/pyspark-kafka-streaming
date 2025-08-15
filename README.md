# PySpark Kafka Streaming on Google Cloud Platform (GCP)

This project demonstrates **real-time data streaming** using **Apache Kafka** as a message broker and **PySpark Structured Streaming** as the consumer, deployed on **Google Cloud Platform (GCP)**.  
It uses **separate Virtual Machines (VMs)** for:
- **Kafka Server**
- **Kafka Producer** (`producer.py`)
- **Kafka Consumer** (`consumer.py`)

---

## 📂 Project Structure

```
.
├── producer.py        # Kafka Producer script
├── consumer.py        # PySpark Kafka Consumer script
├── input_data.csv     # Sample input dataset
└── README.md          # Project documentation
```

---

## ⚙️ GCP Deployment Architecture

**VM 1 - Kafka Server**
- Runs Kafka in KRaft mode (without ZooKeeper)
- Listens on **public IP** for incoming producer and consumer connections

**VM 2 - Kafka Producer**
- Reads CSV data (from Google Cloud Storage)
- Sends batches of messages to Kafka topic

**VM 3 - Kafka Consumer**
- Runs PySpark Structured Streaming job to read from Kafka
- Parses and prints data in real time

---

## 🛠 Prerequisites

Before deploying, ensure you have:
- **Google Cloud Platform project** with billing enabled
- **3 Compute Engine VMs** (Ubuntu recommended)
- **Java (OpenJDK 17)** installed on Kafka VM
- **Python 3.8+** installed on Producer & Consumer VMs
- **Apache Spark** installed on Consumer VM
- Necessary Python libraries:
  ```bash
  pip install pyspark kafka-python pandas
  ```
- Firewall rules allowing ports **9092** and **9093** for Kafka

  **Note:** To run a Kafka consumer, you can also use a managed Spark cluster service such as Google Cloud Dataproc.
---

## 🚀 Step 1: Kafka Setup (VM 1)

Follow the instrunctions below:

1. SSH into Kafka VM:
   ```bash
   gcloud compute ssh kafka-vm --zone <ZONE>
   ```
2. Install Java:
   ```bash
   sudo apt install openjdk-17-jdk -y
   ```
3. Download & Extract Kafka:
   ```bash
   wget https://dlcdn.apache.org/kafka/4.0.0/kafka_2.13-4.0.0.tgz
   tar -xzf kafka_2.13-4.0.0.tgz
   mv kafka_2.13-4.0.0 kafka
   cd kafka
   ```
4. Generate Cluster UUID:
   ```bash
   export KAFKA_CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"
   ```
5. Format Storage:
   ```bash
   bin/kafka-storage.sh format --standalone -t $KAFKA_CLUSTER_ID -c config/server.properties
   ```
6. Edit `config/server.properties`:
   ```
   listeners=PLAINTEXT://0.0.0.0:9092
   advertised.listeners=PLAINTEXT://<KAFKA_VM_PUBLIC_IP>:9092
   ```
7. Allow ports 9092 & 9093 in VPC Firewall:
   ```bash
   gcloud compute firewall-rules create allow-kafka --allow tcp:9092,tcp:9093
   ```
8. Start Kafka:
   ```bash
   bin/kafka-server-start.sh config/server.properties
   ```
9. Create Topic:
   ```bash
   bin/kafka-topics.sh --create --topic my-topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
   ```

---

## 📤 Step 2: Producer Setup (VM 2)

1. SSH into Producer VM:
   ```bash
   gcloud compute ssh producer-vm --zone <ZONE>
   ```
2. Install dependencies:
   ```bash
   pip install kafka-python pandas
   ```
3. Update `producer.py`:
   ```python
   bootstrap_servers='KAFKA_VM_PUBLIC_IP:9092'
   ```
4. Run producer:
   ```bash
   python producer.py
   ```

---

## 📥 Step 3: Consumer Setup (VM 3)

1. SSH into Consumer VM:
   ```bash
   gcloud compute ssh consumer-vm --zone <ZONE>
   ```
2. Install dependencies:
   ```bash
   pip install pyspark kafka-python pandas
   ```
3. Update `consumer.py`:
   ```python
   .option("kafka.bootstrap.servers", "KAFKA_VM_PUBLIC_IP:9092")
   ```
4. Run consumer:
   ```bash
   spark-submit consumer.py
   ```

---

## 📊 Sample Output

**Producer (VM 2):**
```
Sent records 1 to 10
Sent records 11 to 20
...
```

**Consumer (VM 3):**
```
+---+-----+-------------------+
|id |value|timestamp          |
+---+-----+-------------------+
|1  |100  |2025-08-15 10:00:01|
|2  |200  |2025-08-15 10:00:02|
...
```

---

## 🧹 Stopping Kafka (VM 1)

```bash
cd kafka
bin/kafka-server-stop.sh
```

---

## 📚 References
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [PySpark Structured Streaming](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html)
- [kafka-python Client](https://kafka-python.readthedocs.io/en/master/)
