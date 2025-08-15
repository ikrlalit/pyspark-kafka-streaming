from kafka import KafkaProducer
import pandas as pd
import json
import time
from datetime import datetime, timedelta

# GCS file path
gcs_path = 'gs://wk8ga-bucket-ibd/input_data.csv'

# Load data from GCS using gcsfs-compatible interface
df = pd.read_csv(gcs_path)

# Read from Kafka, replace ip with your Kafka broker address
producer = KafkaProducer(
    bootstrap_servers='34.59.88.11:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

topic = "my-topic"
start_time = datetime.utcnow()

for i in range(0, 1000, 10):
    batch = df.iloc[i:i+10].copy()
    
    # Spread timestamps over the batch
    batch["timestamp"] = [(start_time + timedelta(seconds=i + j)).isoformat() for j in range(len(batch))]

    records = batch.to_dict(orient='records')

    for record in records:
        producer.send(topic, record)
    producer.flush()

    print(f"Sent records {i+1} to {i+10}")
    time.sleep(10)

producer.close()
