#!/bin/bash

# Kafka Tutorial Environment Setup Script
# Using UV for fast Python package management

set -e

echo "Setting up Kafka Tutorial Environment with UV"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

echo "UV version: $(uv --version)"

# Create virtual environment with uv
echo "Creating virtual environment..."
uv venv --python 3.11

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies directly
echo "Installing core dependencies..."
uv pip install confluent-kafka[avro,json,protobuf] pandas numpy aiofiles prometheus-client structlog python-dotenv pyyaml click rich

echo "Installing development dependencies..."
uv pip install pytest pytest-cov pytest-asyncio black ruff mypy

echo "Installing documentation dependencies..."
uv pip install mkdocs mkdocs-material

echo "Installing visualization dependencies..."
uv pip install matplotlib seaborn plotly

# Verify installation
echo "Verifying Kafka client installation..."
python -c "import confluent_kafka; print(f'Confluent Kafka version: {confluent_kafka.__version__}')"

echo "Environment setup complete!"
echo ""
echo "To activate the environment manually:"
echo "  source .venv/bin/activate"
echo ""
echo "To start Kafka cluster:"
echo "  cd docker && docker-compose up -d"
echo ""
echo "To access Kafka UI:"
echo "  http://localhost:8080"