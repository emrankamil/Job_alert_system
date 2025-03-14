from os import environ
import json
import uuid
import mmh3
from typing import List

from confluent_kafka import Producer
from db.models.job import JobPosting

config = {
    "bootstrap.servers": environ.get(
        "KAFKA_URL", "localhost:9092"
    ),  # Kafka broker address
    "acks": "all",  # Ensures message durability
}


def delivery_callback(err, msg):
    if err:
        print("ERROR: Message failed delivery: {}".format(err))
    else:
        print(
            "Produced event to topic {topic}: key = {key:12}value = {value:12}".format(
                topic=msg.topic(),
                key=msg.key().decode("utf-8"),
                value=msg.value().decode("utf-8"),
            )
        )


def stream_jobs_data(jobs: List[JobPosting]):
    # Create Producer instance
    producer = Producer(config)

    # Optional per-message delivery callback (triggered by poll() or flush())
    # when a message has been successfully delivered or permanently
    # failed delivery (after retries).

    # Produce data by selecting random values from these lists.
    topic = environ.get("KAFKA_TOPIC", "kafka-job-stream")
    num_partitions = int(environ.get("KAFKA_PARTITIONS", 3))
    print(f"Producing to topic {topic} with {num_partitions} partitions)")

    for job in jobs:

        # Generate a UUID for the key
        job["id"] = str(uuid.uuid4())
        # Convert data to JSON format
        message_value = json.dumps(job)

        # Use the UUID as the key for partitioning
        partition = mmh3.hash(job["id"]) % num_partitions
        # Send message with key (UUID for partitioning)
        producer.produce(
            topic,
            key=job["id"],
            value=message_value,
            # partition=partition,
            callback=delivery_callback,
        )

    # Block until the messages are sent.
    producer.poll(10000)
    producer.flush()
