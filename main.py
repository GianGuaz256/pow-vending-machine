#!/usr/bin/env python3
"""
Bitcoin Lightning Vending Machine - Main Entry Point
Simple launcher for the vending machine application
"""
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main entry point"""
    try:
        from src.vending_machine import main as vending_main
        vending_main()
    except ImportError as e:
        print(f"Error importing vending machine: {e}")
        print("Make sure you're running from the project root directory")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting vending machine: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 