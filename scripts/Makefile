# Bitcoin Lightning Vending Machine - Makefile
# Simplified build and deployment commands

.PHONY: help setup setup-mac install test test-mac simulate clean deploy

# Default target
help:
	@echo "Bitcoin Lightning Vending Machine - Build Commands"
	@echo "=================================================="
	@echo ""
	@echo "Setup Commands:"
	@echo "  setup       - Full setup for Raspberry Pi"
	@echo "  setup-mac   - Setup for Mac development/testing"
	@echo "  install     - Install system dependencies (Pi only)"
	@echo ""
	@echo "Testing Commands:"
	@echo "  test        - Run component tests"
	@echo "  test-mac    - Run Mac-specific tests"
	@echo "  simulate    - Run vending machine simulator"
	@echo ""
	@echo "Deployment Commands:"
	@echo "  deploy      - Deploy to production (systemd service)"
	@echo "  clean       - Clean build artifacts"

# Setup for Raspberry Pi
setup: install
	@echo "Setting up for Raspberry Pi..."
	cd .. && python3 -m venv venv
	cd .. && source venv/bin/activate && pip install --upgrade pip
	cd .. && source venv/bin/activate && pip install -r config/requirements.txt
	@echo "✓ Raspberry Pi setup complete"

# Setup for Mac development
setup-mac:
	@echo "Setting up for Mac development..."
	cd .. && python3 -m venv venv
	cd .. && source venv/bin/activate && pip install --upgrade pip
	cd .. && source venv/bin/activate && pip install -r config/requirements-mac.txt
	@echo "✓ Mac setup complete"

# Install system dependencies (Raspberry Pi only)
install:
	@echo "Installing system dependencies..."
	chmod +x install.sh
	./install.sh

# Run component tests
test:
	@echo "Running component tests..."
	cd .. && python tests/test_components.py

# Run Mac-specific tests
test-mac:
	@echo "Running Mac tests..."
	cd .. && python tests/test_mac.py

# Run vending machine simulator
simulate:
	@echo "Starting vending machine simulator..."
	cd .. && python tests/simulator.py

# Deploy to production (systemd service)
deploy:
	@echo "Deploying to production..."
	sudo systemctl stop bitcoin-vending.service || true
	sudo systemctl daemon-reload
	sudo systemctl enable bitcoin-vending.service
	sudo systemctl start bitcoin-vending.service
	@echo "✓ Service deployed and started"
	@echo "Monitor with: sudo journalctl -u bitcoin-vending.service -f"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	cd .. && rm -rf venv/
	cd .. && rm -rf __pycache__/
	cd .. && rm -rf src/__pycache__/
	cd .. && rm -rf tests/__pycache__/
	cd .. && find . -name "*.pyc" -delete
	cd .. && find . -name ".DS_Store" -delete
	@echo "✓ Clean complete"

# Quick development workflow targets
dev-setup: setup-mac test-mac
	@echo "✓ Development environment ready"

pi-setup: setup test
	@echo "✓ Raspberry Pi environment ready"

# Status check
status:
	@echo "Checking system status..."
	sudo systemctl status bitcoin-vending.service || echo "Service not running"
	@echo ""
	@echo "Recent logs:"
	sudo journalctl -u bitcoin-vending.service --no-pager -n 10 || echo "No service logs"

# Start/stop service
start:
	sudo systemctl start bitcoin-vending.service
	@echo "✓ Service started"

stop:
	sudo systemctl stop bitcoin-vending.service
	@echo "✓ Service stopped"

restart:
	sudo systemctl restart bitcoin-vending.service
	@echo "✓ Service restarted"

# View logs
logs:
	sudo journalctl -u bitcoin-vending.service -f

# Development mode (runs directly, not as service)
run:
	@echo "Running in development mode..."
	cd .. && source venv/bin/activate && python src/vending_machine.py 