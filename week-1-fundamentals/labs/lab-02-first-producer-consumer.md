# Lab 2: Build Your First Producer and Consumer

## Objective
Build production-ready Python producer and consumer applications from scratch, understanding message flow and partitioning concepts.

## Prerequisites
- Completed Lab 1 (Environment Setup)
- Read Tutorial 2 (First Producer Consumer)
- Kafka cluster running
- Virtual environment activated

## Your Mission

You are building a real-time user activity tracking system. Your task is to:
1. Create a producer that sends user events
2. Build a consumer that processes these events
3. Understand message partitioning and ordering
4. Handle errors gracefully

## Part 1: Create Directory Structure

**Your Task**: Set up the proper Python package structure

```bash
# Create source directories
mkdir -p src/producers src/consumers src/common

# Create empty __init__.py files
touch src/__init__.py
touch src/producers/__init__.py
touch src/consumers/__init__.py
touch src/common/__init__.py
```

## Part 2: Build the Producer

**Your Task**: Create `src/producers/user_event_producer.py`

### Requirements:
1. Send user events (login, purchase, logout) to 'user-events' topic
2. Use user_id as message key for consistent partitioning
3. Include proper error handling and delivery callbacks
4. Add configuration for reliability (acks='all', retries)

### Starter Code Template:
```python
#!/usr/bin/env python3
"""
User Event Producer
Sends user activity events to Kafka
"""
import json
import time
from typing import Dict, Any, Optional
from confluent_kafka import Producer, KafkaError

class UserEventProducer:
    def __init__(self, bootstrap_servers: str = 'localhost:9092'):
        # TODO: Configure the producer with reliability settings
        self.config = {
            # Add your configuration here
        }

        # TODO: Initialize the producer
        self.producer = None

    def send_user_event(self, user_id: str, event_type: str, **kwargs) -> bool:
        """
        Send a user event to Kafka

        Args:
            user_id: User identifier
            event_type: Type of event (login, purchase, logout)
            **kwargs: Additional event data

        Returns:
            bool: True if message queued successfully
        """
        # TODO: Create message payload
        message = {
            'user_id': user_id,
            'event_type': event_type,
            'timestamp': time.time(),
            **kwargs
        }

        # TODO: Send message to Kafka
        # Use user_id as key
        # Add delivery callback

        pass

    def _delivery_callback(self, err, msg):
        """Callback for message delivery status"""
        # TODO: Handle delivery success/failure
        pass

    def close(self):
        """Flush and close producer"""
        # TODO: Flush remaining messages and close
        pass

# Test your producer
if __name__ == "__main__":
    producer = UserEventProducer()

    # Send test events
    events = [
        ('user_123', 'login', {'ip': '192.168.1.100'}),
        ('user_456', 'purchase', {'product': 'laptop', 'amount': 999.99}),
        ('user_123', 'logout', {}),
    ]

    for user_id, event_type, data in events:
        producer.send_user_event(user_id, event_type, **data)

    producer.close()
    print("Producer test completed!")
```

**Hints**:
- Use `acks='all'` for maximum reliability
- Add `retries=3` for automatic retry
- Use `json.dumps()` to serialize message value
- The delivery callback receives `err` and `msg` parameters

## Part 3: Build the Consumer

**Your Task**: Create `src/consumers/user_event_consumer.py`

### Requirements:
1. Subscribe to 'user-events' topic
2. Process different event types with appropriate business logic
3. Use manual offset commits for reliability
4. Handle JSON deserialization errors
5. Implement graceful shutdown

### Starter Code Template:
```python
#!/usr/bin/env python3
"""
User Event Consumer
Processes user activity events from Kafka
"""
import json
import signal
import sys
from confluent_kafka import Consumer, KafkaError

class UserEventConsumer:
    def __init__(self, group_id: str, bootstrap_servers: str = 'localhost:9092'):
        # TODO: Configure the consumer
        self.config = {
            # Add your configuration here
        }

        # TODO: Initialize consumer and state
        self.consumer = None
        self.running = True

    def start_consuming(self):
        """Start the consumer loop"""
        # TODO: Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._shutdown_handler)

        try:
            # TODO: Subscribe to topics
            # TODO: Start polling loop
            while self.running:
                # TODO: Poll for messages
                # TODO: Handle message or error
                pass

        finally:
            self._cleanup()

    def _process_message(self, msg):
        """Process a single message"""
        try:
            # TODO: Extract message details
            topic = msg.topic()
            partition = msg.partition()
            offset = msg.offset()
            key = msg.key()
            value = msg.value()

            # TODO: Deserialize JSON value

            # TODO: Process based on event type

            # TODO: Commit offset after successful processing

        except json.JSONDecodeError:
            # TODO: Handle malformed JSON
            pass
        except Exception as e:
            # TODO: Handle processing errors
            pass

    def _process_login_event(self, data):
        """Process login event"""
        # TODO: Implement login logic
        pass

    def _process_purchase_event(self, data):
        """Process purchase event"""
        # TODO: Implement purchase logic
        pass

    def _process_logout_event(self, data):
        """Process logout event"""
        # TODO: Implement logout logic
        pass

    def _shutdown_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\nShutting down consumer...")
        self.running = False

    def _cleanup(self):
        """Clean up resources"""
        # TODO: Close consumer
        pass

# Test your consumer
if __name__ == "__main__":
    consumer = UserEventConsumer(group_id='lab-consumer-group')
    consumer.start_consuming()
```

**Hints**:
- Use `enable.auto.commit=False` for manual commits
- Call `consumer.commit(msg)` after successful processing
- Handle `KafkaError._PARTITION_EOF` separately from real errors
- Use `consumer.subscribe(['user-events'])` to subscribe

## Part 4: Create the Topic

**Your Task**: Create the topic with proper configuration

```bash
# Create topic with 3 partitions
docker exec -it kafka-broker kafka-topics \
  --bootstrap-server localhost:9092 \
  --topic user-events \
  --create \
  --partitions 3 \
  --replication-factor 1 \
  --if-not-exists

# Verify topic creation
docker exec -it kafka-broker kafka-topics \
  --bootstrap-server localhost:9092 \
  --topic user-events \
  --describe
```

## Part 5: Test Your Implementation

### Test 1: Basic Functionality

1. **Start your consumer**:
```bash
python src/consumers/user_event_consumer.py
```

2. **In another terminal, run your producer**:
```bash
python src/producers/user_event_producer.py
```

**Expected Behavior**:
- Consumer receives all messages sent by producer
- Messages with same user_id go to same partition
- No errors or crashes

### Test 2: Message Ordering

**Your Task**: Verify partitioning behavior

```bash
# Create a test script to send multiple events for same user
cat > test_ordering.py << 'EOF'
from src.producers.user_event_producer import UserEventProducer
import time

producer = UserEventProducer()

# Send multiple events for same user quickly
for i in range(5):
    producer.send_user_event('user_999', 'click', page=f'page_{i}')
    time.sleep(0.1)

producer.close()
EOF

python test_ordering.py
```

**Question**: Do all events for `user_999` go to the same partition? Why is this important?

### Test 3: Multiple Consumers

**Your Task**: Test consumer group behavior

1. **Start first consumer**:
```bash
python src/consumers/user_event_consumer.py
```

2. **Start second consumer in new terminal**:
```bash
python src/consumers/user_event_consumer.py
```

3. **Send messages**:
```bash
python src/producers/user_event_producer.py
```

**Observation**: How do messages get distributed between the two consumers?

## Part 6: Verify in Kafka UI

**Your Task**: Use the web interface to inspect your work

1. Go to http://localhost:8080
2. Navigate to Topics → user-events
3. Click on "Messages" tab
4. Examine message distribution across partitions

**Questions to Answer**:
1. Which partition has the most messages?
2. Can you identify messages from the same user_id?
3. What does the message timestamp tell you?

## Part 7: Error Testing

**Your Task**: Test error handling

### Test Invalid JSON
```bash
# Send malformed message using console producer
docker exec -it kafka-broker kafka-console-producer \
  --bootstrap-server localhost:9092 \
  --topic user-events

# Type: {invalid json}
# Press Ctrl+C to exit
```

**Question**: How does your consumer handle the malformed message?

### Test Consumer Restart
1. Stop your consumer (Ctrl+C)
2. Send more messages with producer
3. Restart consumer

**Question**: Does the consumer pick up where it left off? Why?

## Deliverables

Submit the following completed files:
- [ ] `src/producers/user_event_producer.py` - Working producer
- [ ] `src/consumers/user_event_consumer.py` - Working consumer
- [ ] Screenshot of Kafka UI showing your messages
- [ ] Answers to all questions in this lab

## Success Criteria

Your implementation should:
- [ ] Send messages without errors
- [ ] Consume messages reliably
- [ ] Handle different event types correctly
- [ ] Use proper partitioning (same user_id → same partition)
- [ ] Commit offsets manually
- [ ] Handle JSON decode errors gracefully
- [ ] Shut down gracefully on Ctrl+C

## Going Further (Optional Challenges)

1. **Add Message Headers**: Include metadata like event source, version
2. **Implement Dead Letter Queue**: Handle poison messages
3. **Add Metrics**: Count processed messages by type
4. **Batch Processing**: Process multiple messages before committing
5. **Configuration File**: Load settings from external config

## Troubleshooting

### Common Issues:

**ImportError: No module named 'confluent_kafka'**
```bash
# Make sure virtual environment is activated
source .venv/bin/activate
```

**Connection refused to localhost:9092**
```bash
# Check if Kafka is running
docker ps
docker-compose logs kafka
```

**Messages not appearing in consumer**
```bash
# Check topic exists and has messages
docker exec -it kafka-broker kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic user-events \
  --from-beginning
```

## Next Lab Preview

In Lab 3, you'll learn:
- Advanced serialization with Avro and Schema Registry
- Exactly-once processing semantics
- Consumer group rebalancing strategies
- Performance optimization techniques

Great job building your first Kafka applications! You're now ready to handle real-world message streaming scenarios.