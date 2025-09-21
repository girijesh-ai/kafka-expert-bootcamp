#!/usr/bin/env python3
"""
Basic Kafka Producer Example
Demonstrates fundamental producer concepts
"""
import json
import time
from typing import Dict, Any, Optional
from confluent_kafka import Producer, KafkaError


class BasicProducer:
    """Simple Kafka producer for learning purposes"""

    def __init__(self, bootstrap_servers: str = 'localhost:9092'):
        """
        Initialize the producer with basic configuration

        Args:
            bootstrap_servers: Comma-separated list of broker addresses
        """
        self.config = {
            'bootstrap.servers': bootstrap_servers,
            'client.id': 'basic-producer',

            # Reliability settings
            'acks': 'all',  # Wait for all replicas to acknowledge
            'retries': 3,   # Retry failed sends
            'retry.backoff.ms': 100,

            # Performance settings
            'batch.size': 16384,  # Batch size in bytes
            'linger.ms': 5,       # Wait up to 5ms to batch messages
            'compression.type': 'snappy',  # Compress messages
        }

        self.producer = Producer(self.config)
        print(f"Producer initialized with brokers: {bootstrap_servers}")

    def send_message(self,
                    topic: str,
                    value: Dict[str, Any],
                    key: Optional[str] = None) -> bool:
        """
        Send a single message to Kafka

        Args:
            topic: Target topic name
            value: Message payload (will be JSON serialized)
            key: Optional message key for partitioning

        Returns:
            bool: True if message sent successfully
        """
        try:
            # Serialize the message value to JSON
            serialized_value = json.dumps(value)

            # Produce the message
            self.producer.produce(
                topic=topic,
                value=serialized_value,
                key=key,
                callback=self._delivery_callback
            )

            # Poll for delivery events (non-blocking)
            self.producer.poll(0)

            return True

        except Exception as e:
            print(f"Error sending message: {e}")
            return False

    def _delivery_callback(self, err: Optional[KafkaError], msg):
        """
        Callback function called when message delivery completes

        Args:
            err: Error object if delivery failed
            msg: Message object with delivery details
        """
        if err is not None:
            print(f"Message delivery failed: {err}")
        else:
            print(f"Message delivered to partition {msg.partition()} "
                  f"at offset {msg.offset()}")

    def flush_and_close(self):
        """
        Ensure all messages are sent and close the producer
        """
        print("Flushing remaining messages...")
        remaining = self.producer.flush(timeout=10)

        if remaining > 0:
            print(f"Warning: {remaining} messages not delivered")
        else:
            print("All messages delivered successfully")


# Example usage and testing
if __name__ == "__main__":
    # Create producer instance
    producer = BasicProducer()

    # Sample data to send
    sample_messages = [
        {
            'user_id': 'user_001',
            'action': 'login',
            'timestamp': time.time(),
            'ip_address': '192.168.1.100'
        },
        {
            'user_id': 'user_002',
            'action': 'purchase',
            'product_id': 'prod_123',
            'amount': 29.99,
            'timestamp': time.time()
        },
        {
            'user_id': 'user_001',
            'action': 'logout',
            'timestamp': time.time()
        }
    ]

    topic_name = 'user-events'

    print(f"Sending {len(sample_messages)} messages to topic '{topic_name}'")
    print("-" * 50)

    # Send each message
    for i, message in enumerate(sample_messages):
        # Use user_id as key for consistent partitioning
        key = message.get('user_id')

        success = producer.send_message(
            topic=topic_name,
            value=message,
            key=key
        )

        if success:
            print(f"Queued message {i+1}")
        else:
            print(f"Failed to queue message {i+1}")

        # Small delay between messages
        time.sleep(0.1)

    # Ensure all messages are sent
    producer.flush_and_close()
    print("Producer example completed!")
