#!/usr/bin/env python3
"""
Test script to verify Python Kafka client setup
"""
from confluent_kafka import Producer, Consumer, KafkaError
import json
import time

def test_producer():
    """Test Kafka producer functionality"""
    print("Testing Producer...")

    config = {
        'bootstrap.servers': 'localhost:9092',
        'client.id': 'intern-producer'
    }

    producer = Producer(config)

    # Send a test message
    test_data = {
        'student': 'intern',
        'message': 'Hello from Python!',
        'timestamp': time.time()
    }

    producer.produce(
        'intern-topic',
        value=json.dumps(test_data),
        key='test-key'
    )

    # Wait for message delivery
    producer.flush()
    print("Message sent successfully!")

def test_consumer():
    """Test Kafka consumer functionality"""
    print("Testing Consumer...")

    config = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'intern-consumer-group',
        'auto.offset.reset': 'earliest'
    }

    consumer = Consumer(config)
    consumer.subscribe(['intern-topic'])

    print("Polling for messages (10 seconds max)...")

    message_count = 0
    start_time = time.time()

    while time.time() - start_time < 10:
        msg = consumer.poll(1.0)

        if msg is None:
            continue

        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(f"Error: {msg.error()}")
                break

        message_count += 1
        print(f"Received message {message_count}:")
        print(f"  Key: {msg.key()}")
        print(f"  Value: {msg.value()}")
        print(f"  Partition: {msg.partition()}")
        print(f"  Offset: {msg.offset()}")
        print()

    consumer.close()
    print(f"Consumed {message_count} messages")

if __name__ == "__main__":
    print("=== Kafka Python Client Test ===")
    print()

    # Test producer
    test_producer()
    print()

    # Wait a moment
    time.sleep(2)

    # Test consumer
    test_consumer()
    print()
    print("=== Test Complete ===")
