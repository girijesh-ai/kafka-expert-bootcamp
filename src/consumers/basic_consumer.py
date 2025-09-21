#!/usr/bin/env python3
"""
Basic Kafka Consumer Example
Demonstrates fundamental consumer concepts
"""
import json
import signal
import sys
from typing import List, Optional
from confluent_kafka import Consumer, KafkaError


class BasicConsumer:
    """Simple Kafka consumer for learning purposes"""

    def __init__(self,
                 topics: List[str],
                 group_id: str,
                 bootstrap_servers: str = 'localhost:9092'):
        """
        Initialize the consumer

        Args:
            topics: List of topics to subscribe to
            group_id: Consumer group identifier
            bootstrap_servers: Comma-separated list of broker addresses
        """
        self.topics = topics
        self.running = True

        self.config = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'client.id': f'{group_id}-client',

            # Offset management
            'auto.offset.reset': 'earliest',  # Start from beginning if no offset
            'enable.auto.commit': False,      # Manual offset commit for reliability

            # Session management
            'session.timeout.ms': 30000,     # 30 seconds
            'heartbeat.interval.ms': 10000,  # 10 seconds
            'max.poll.interval.ms': 300000,  # 5 minutes

            # Performance settings
            'fetch.min.bytes': 1,            # Minimum bytes to fetch
        }

        self.consumer = Consumer(self.config)
        print(f"Consumer initialized for group: {group_id}")
        print(f"Subscribed to topics: {topics}")

    def start_consuming(self):
        """
        Start the main consumer loop
        """
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        try:
            # Subscribe to topics
            self.consumer.subscribe(self.topics)
            print("Starting consumer loop...")
            print("Press Ctrl+C to stop")
            print("-" * 50)

            while self.running:
                # Poll for messages
                msg = self.consumer.poll(timeout=1.0)

                if msg is None:
                    continue

                if msg.error():
                    self._handle_error(msg.error())
                    continue

                # Process the message
                self._process_message(msg)

        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            self._cleanup()

    def _process_message(self, msg):
        """
        Process a single message

        Args:
            msg: Kafka message object
        """
        try:
            # Extract message details
            topic = msg.topic()
            partition = msg.partition()
            offset = msg.offset()
            key = msg.key()
            value = msg.value()
            timestamp = msg.timestamp()

            # Deserialize JSON value
            if value:
                data = json.loads(value.decode('utf-8'))
            else:
                data = None

            # Print message details
            print(f"Received message:")
            print(f"  Topic: {topic}")
            print(f"  Partition: {partition}")
            print(f"  Offset: {offset}")
            print(f"  Key: {key}")
            print(f"  Timestamp: {timestamp}")
            print(f"  Data: {data}")
            print("-" * 30)

            # Simulate message processing
            self._business_logic(data)

            # Commit offset after successful processing
            self.consumer.commit(msg)

        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            # Handle poison messages appropriately

        except Exception as e:
            print(f"Error processing message: {e}")
            # In production, might want to send to dead letter queue

    def _business_logic(self, data):
        """
        Simulate business logic processing

        Args:
            data: Deserialized message data
        """
        if not data:
            return

        # Example: Process different types of user events
        action = data.get('action')
        user_id = data.get('user_id')

        if action == 'login':
            print(f"   User {user_id} logged in")
        elif action == 'purchase':
            amount = data.get('amount', 0)
            print(f"   User {user_id} made purchase: ${amount}")
        elif action == 'logout':
            print(f"   User {user_id} logged out")
        else:
            print(f"   Unknown action: {action}")

    def _handle_error(self, error):
        """
        Handle consumer errors

        Args:
            error: KafkaError object
        """
        if error.code() == KafkaError._PARTITION_EOF:
            # End of partition - not really an error
            print("Reached end of partition")
        else:
            print(f"Consumer error: {error}")

    def _signal_handler(self, signum, frame):
        """
        Handle shutdown signals gracefully
        """
        print(f"\nReceived signal {signum}, shutting down...")
        self.running = False

    def _cleanup(self):
        """
        Clean up resources
        """
        print("Closing consumer...")
        self.consumer.close()
        print("Consumer closed successfully")


# Example usage
if __name__ == "__main__":
    # Consumer configuration
    topics = ['user-events']
    group_id = 'tutorial-consumer-group'

    # Create and start consumer
    consumer = BasicConsumer(
        topics=topics,
        group_id=group_id
    )

    consumer.start_consuming()