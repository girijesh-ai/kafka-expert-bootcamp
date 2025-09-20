# Lab 1: Environment Setup and Verification

## Objective
Set up your complete Kafka development environment and verify everything is working correctly.

## Prerequisites
- You have read the theory document: `theory/01-kafka-architecture.md`
- You have Docker and Docker Compose installed
- You have Python 3.9+ installed

## Lab Instructions

### Step 1: Environment Setup
**Your Task**: Set up the Python environment using UV

```bash
# Navigate to the project directory
cd /home/spurge/tutorials/kafka

# Run the setup script
./scripts/setup-env.sh

# Activate the virtual environment
source .venv/bin/activate
```

**Verification**:
- Check that confluent-kafka is installed: `pip list | grep confluent-kafka`
- Verify Python version: `python --version`

**Expected Result**: You should see confluent-kafka version 2.11.1 and Python 3.11+

### Step 2: Start Kafka Cluster
**Your Task**: Start the complete Kafka ecosystem using Docker

```bash
# Navigate to docker directory
cd docker

# Start all services in detached mode
docker-compose up -d

# Wait 30 seconds for services to start
sleep 30

# Check that all services are running
docker-compose ps
```

**Verification**: You should see 5 services running:
- kafka-zookeeper (port 2181)
- kafka-broker (port 9092)
- kafka-schema-registry (port 8081)
- kafka-control-center (port 9021)
- kafka-ui (port 8080)

### Step 3: Access Kafka UI
**Your Task**: Verify web interfaces are accessible

1. Open your browser and navigate to: http://localhost:8080
2. You should see the Kafka UI interface
3. Click on "Topics" in the left menu
4. Note: The topics list might be empty - this is normal for a fresh installation

**What to Observe**:
- Clean, modern interface showing cluster information
- No topics listed (we'll create them next)
- Cluster status showing "Connected"

### Step 4: Create Your First Topic
**Your Task**: Create a topic using the command line

```bash
# Connect to the Kafka broker container
docker exec -it kafka-broker bash

# Create a topic named 'intern-topic' with 3 partitions
kafka-topics --bootstrap-server localhost:9092 \
  --topic intern-topic \
  --create \
  --partitions 3 \
  --replication-factor 1

# List all topics to verify creation
kafka-topics --bootstrap-server localhost:9092 --list

# Get detailed information about your topic
kafka-topics --bootstrap-server localhost:9092 \
  --topic intern-topic \
  --describe
```

**Expected Output**:
```
Topic: intern-topic	TopicId: [some-id]	PartitionCount: 3	ReplicationFactor: 1
	Topic: intern-topic	Partition: 0	Leader: 1	Replicas: 1	Isr: 1
	Topic: intern-topic	Partition: 1	Leader: 1	Replicas: 1	Isr: 1
	Topic: intern-topic	Partition: 2	Leader: 1	Replicas: 1	Isr: 1
```

**Questions to Answer**:
1. What does "Partition: 0, Leader: 1" mean?
2. Why do we have 3 partitions?
3. What is the significance of "Isr: 1"?

### Step 5: Test Console Producer and Consumer
**Your Task**: Send and receive messages using built-in tools

#### Producer Test
```bash
# In the same broker container, start a console producer
kafka-console-producer --bootstrap-server localhost:9092 --topic intern-topic

# Type these messages (press Enter after each):
> Hello from the intern!
> This is my first Kafka message
> Learning Kafka step by step
> Message number 4

# Press Ctrl+C to exit the producer
```

#### Consumer Test
```bash
# Open a NEW terminal window
# Connect to the broker container again
docker exec -it kafka-broker bash

# Start a console consumer from the beginning
kafka-console-consumer --bootstrap-server localhost:9092 \
  --topic intern-topic \
  --from-beginning

# You should see all 4 messages you sent
# Press Ctrl+C to exit the consumer
```

**What to Observe**:
- Messages appear in the consumer terminal
- Messages might not be in the exact order you sent them (why?)
- Each message appears exactly once

### Step 6: Python Client Verification
**Your Task**: Create and run a Python test script

```bash
# Return to the project root directory
cd /home/spurge/tutorials/kafka

# Create a test script
cat > test_my_setup.py << 'EOF'
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
EOF

# Make the script executable
chmod +x test_my_setup.py

# Run the test
python test_my_setup.py
```

**Expected Output**:
```
=== Kafka Python Client Test ===

Testing Producer...
Message sent successfully!

Testing Consumer...
Polling for messages (10 seconds max)...
Received message 1:
  Key: b'test-key'
  Value: b'{"student": "intern", "message": "Hello from Python!", "timestamp": 1234567890.123}'
  Partition: 1
  Offset: 0

[... more messages ...]

Consumed 5 messages

=== Test Complete ===
```

### Step 7: Verify in Kafka UI
**Your Task**: Check your work in the web interface

1. Go back to http://localhost:8080
2. Click on "Topics" → "intern-topic"
3. Click on "Messages" tab
4. You should see all the messages you sent
5. Click on different partitions (0, 1, 2) to see message distribution

**Questions to Answer**:
1. Are messages evenly distributed across partitions?
2. Can you find the Python message you sent?
3. What information is displayed for each message?

## Lab Completion Checklist

- [ ] Virtual environment created and activated
- [ ] All Docker services running (5/5)
- [ ] Kafka UI accessible at localhost:8080
- [ ] Topic 'intern-topic' created with 3 partitions
- [ ] Console producer/consumer test successful
- [ ] Python client test script runs without errors
- [ ] Messages visible in Kafka UI

## Understanding Check

Before moving to the next lab, make sure you understand:

1. **Architecture**: What are the roles of ZooKeeper, Broker, and Schema Registry?
2. **Topics and Partitions**: Why do we use partitions? How do they enable scaling?
3. **Producers and Consumers**: What's the difference between publishing and subscribing?
4. **Message Flow**: How does a message get from producer to consumer?

## Troubleshooting

### Common Issues

**Docker containers not starting**:
```bash
# Check Docker status
docker ps -a

# View logs for specific service
docker-compose logs kafka

# Restart services
docker-compose restart
```

**Python import errors**:
```bash
# Verify virtual environment is activated
which python

# Check installed packages
pip list | grep confluent

# Reinstall if needed
pip install confluent-kafka
```

**Connection refused errors**:
```bash
# Check if Kafka is listening on port 9092
netstat -tlnp | grep 9092

# Wait longer for services to start
sleep 60
```

## Next Steps

Once you complete this lab successfully, you're ready for:
- **Lab 2**: Deep dive into producers and message serialization
- **Lab 3**: Advanced consumer patterns and offset management
- **Theory**: Message keys, partitioning strategies, and consumer groups

Congratulations on setting up your first Kafka environment!