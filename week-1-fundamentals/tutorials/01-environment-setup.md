# Week 1 Tutorial: Environment Setup

## Prerequisites

- Docker and Docker Compose installed
- Python 3.9+ installed
- Basic command line knowledge
- Text editor or IDE

## Step 1: Clone and Setup Project

```bash
# Navigate to the kafka tutorial directory
cd /home/spurge/tutorials/kafka

# Run the environment setup script
./scripts/setup-env.sh
```

**What this script does:**
1. Installs UV package manager if not present
2. Creates a Python virtual environment
3. Installs all required dependencies
4. Verifies Kafka client installation

## Step 2: Activate Virtual Environment

```bash
# Activate the virtual environment
source .venv/bin/activate

# Verify Python environment
python --version
pip list | grep confluent-kafka
```

**Expected Output:**
```
Python 3.11.x
confluent-kafka    2.3.0
```

## Step 3: Start Kafka Cluster

```bash
# Navigate to docker directory
cd docker

# Start the complete Kafka ecosystem
docker-compose up -d

# Verify services are running
docker-compose ps
```

**Expected Services:**
- `kafka-zookeeper` (port 2181)
- `kafka-broker` (port 9092)
- `kafka-schema-registry` (port 8081)
- `kafka-control-center` (port 9021)
- `kafka-ui` (port 8080)

## Step 4: Verify Kafka Installation

```bash
# Check Kafka broker logs
docker-compose logs kafka

# Verify broker is accepting connections
docker exec kafka-broker kafka-topics --bootstrap-server localhost:9092 --list
```

## Step 5: Access Management UIs

### Kafka UI (Recommended for beginners)
- URL: http://localhost:8080
- Username: None (open access)
- Features: Topic management, message browsing, consumer groups

### Confluent Control Center
- URL: http://localhost:9021
- Username: None (open access)
- Features: Advanced monitoring, stream processing

## Step 6: Create Your First Topic

```bash
# Connect to Kafka broker container
docker exec -it kafka-broker bash

# Create a test topic
kafka-topics --bootstrap-server localhost:9092 \
  --topic test-topic \
  --create \
  --partitions 3 \
  --replication-factor 1

# List topics to verify creation
kafka-topics --bootstrap-server localhost:9092 --list

# Get topic details
kafka-topics --bootstrap-server localhost:9092 \
  --topic test-topic \
  --describe
```

**Expected Output:**
```
Topic: test-topic	TopicId: xyz	PartitionCount: 3	ReplicationFactor: 1
	Topic: test-topic	Partition: 0	Leader: 1	Replicas: 1	Isr: 1
	Topic: test-topic	Partition: 1	Leader: 1	Replicas: 1	Isr: 1
	Topic: test-topic	Partition: 2	Leader: 1	Replicas: 1	Isr: 1
```

## Step 7: Test Basic Producer/Consumer

### Producer Test
```bash
# Start console producer
kafka-console-producer --bootstrap-server localhost:9092 --topic test-topic

# Type some messages (press Enter after each):
> Hello Kafka!
> This is my first message
> Learning Kafka is awesome
# Press Ctrl+C to exit
```

### Consumer Test
```bash
# In a new terminal, start console consumer
docker exec -it kafka-broker bash

kafka-console-consumer --bootstrap-server localhost:9092 \
  --topic test-topic \
  --from-beginning

# You should see the messages you sent earlier
# Press Ctrl+C to exit
```

## Step 8: Verify Python Client

Create a simple test script:

```bash
# Return to project root
cd /home/spurge/tutorials/kafka

# Create test directory
mkdir -p tests/integration

# Create simple test script
cat > tests/integration/test_connection.py << 'EOF'
from confluent_kafka import Producer, Consumer, KafkaError
import json

def test_producer_consumer():
    # Producer configuration
    producer_config = {
        'bootstrap.servers': 'localhost:9092',
        'client.id': 'test-producer'
    }

    # Consumer configuration
    consumer_config = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'test-group',
        'auto.offset.reset': 'earliest'
    }

    # Test producer
    producer = Producer(producer_config)

    test_message = {
        'message': 'Hello from Python!',
        'timestamp': '2024-01-01T00:00:00Z'
    }

    producer.produce(
        'test-topic',
        value=json.dumps(test_message),
        key='test-key'
    )
    producer.flush()
    print("Message sent successfully!")

    # Test consumer
    consumer = Consumer(consumer_config)
    consumer.subscribe(['test-topic'])

    print("Consuming messages for 10 seconds...")
    timeout_count = 0

    while timeout_count < 10:
        msg = consumer.poll(1.0)

        if msg is None:
            timeout_count += 1
            continue

        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(f"Error: {msg.error()}")
                break

        print(f"Received: key={msg.key()}, value={msg.value()}")
        break

    consumer.close()
    print("Test completed successfully!")

if __name__ == "__main__":
    test_producer_consumer()
EOF

# Run the test
python tests/integration/test_connection.py
```

**Expected Output:**
```
Message sent successfully!
Consuming messages for 10 seconds...
Received: key=b'test-key', value=b'{"message": "Hello from Python!", "timestamp": "2024-01-01T00:00:00Z"}'
Test completed successfully!
```

## Step 9: Environment Verification Checklist

- [ ] UV package manager installed
- [ ] Virtual environment activated
- [ ] confluent-kafka library installed
- [ ] Docker containers running (5 services)
- [ ] Kafka UI accessible at http://localhost:8080
- [ ] Test topic created successfully
- [ ] Console producer/consumer working
- [ ] Python client test passed

## Troubleshooting

### Common Issues

1. **Port conflicts**: Check if ports 2181, 8080, 8081, 9021, 9092 are available
2. **Docker memory**: Ensure Docker has at least 4GB RAM allocated
3. **Virtual environment**: Make sure you activated the venv before running Python scripts

### Useful Commands

```bash
# Check running containers
docker ps

# View Kafka logs
docker-compose logs kafka

# Stop all services
docker-compose down

# Clean up volumes (removes all data)
docker-compose down -v

# Restart specific service
docker-compose restart kafka
```

## Next Steps

Now that your environment is set up, you're ready to dive deep into Kafka fundamentals in the next tutorial where we'll explore:

- Topic and partition concepts in detail
- Message serialization and deserialization
- Producer and consumer configuration options
- Offset management strategies

Your Kafka journey has officially begun!