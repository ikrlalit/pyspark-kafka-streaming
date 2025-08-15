from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, to_timestamp
from pyspark.sql.types import StructType, IntegerType, TimestampType

# Initialize Spark session
spark = SparkSession.builder \
    .appName("KafkaSparkStreamingPrintRecords") \
    .getOrCreate()

# Set log level to reduce verbosity
spark.sparkContext.setLogLevel("WARN")

# Define schema for Kafka message value
schema = StructType() \
    .add("id", IntegerType()) \
    .add("value", IntegerType()) \
    .add("timestamp", TimestampType())

# Read from Kafka, replace ip with your Kafka broker address 
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "34.59.88.11:9092") \
    .option("subscribe", "my-topic") \
    .option("startingOffsets", "earliest") \
    .load()

# Parse JSON data from Kafka message value
parsed = df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*") \
    .withColumn("timestamp", to_timestamp("timestamp"))

# Just print the records with their timestamp
query = parsed.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", False) \
    .start()

query.awaitTermination()
