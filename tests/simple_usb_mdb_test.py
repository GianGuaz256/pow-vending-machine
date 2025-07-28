#!/usr/bin/env python3
"""
Simple USB MDB Test - Following User's Exact Example
Tests MDB connection using the exact approach provided by the user
"""

import serial
import os
import sys

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))

from config import config

def main():
    """Test MDB connection exactly as specified by user"""
    print("Simple MDB Test - User's Exact Example")
    print("="*50)
    print(f"Device: {config.mdb.serial_port}")
    print(f"Baud Rate: {config.mdb.baud_rate}")
    
    try:
        # User's exact implementation but with configured port
        ser = serial.Serial() #Create Serial Object
        ser.baudrate = 115200 #Set the appropriate BaudRate
        ser.timeout = 50 #The maximum timeout that the program waits for a reply. If 0 is used, the pot is blocked until readline returns
        ser.port = config.mdb.serial_port # Use configured device file descriptor
        ser.open() #Open the serial connection
        ser.write(b'V\n') #Write the version command "V\n" encoded in Binary
        s = ser.readline() # Read the response
        print('Version:' + s.decode('ascii')) 
        
        # Test additional commands as shown in the Qibixx documentation
        commands = [
            ('R\n', 'Reset'),
            ('S\n', 'Setup'), 
            ('P\n', 'Poll'),
            ('T\n', 'Status')
        ]
        
        print("\nTesting additional commands:")
        for cmd, name in commands:
            print(f"Sending {name} command: {cmd.strip()}")
            ser.write(cmd.encode('ascii'))
            response = ser.readline()
            if response:
                print(f"  Response: {response.decode('ascii').strip()}")
            else:
                print(f"  No response")
        
        ser.close()
        print("\n✓ SUCCESS: MDB interface is working!")
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        print("\nTroubleshooting:")
        print(f"1. Check that {config.mdb.serial_port} exists")
        print("2. Add user to dialout group: sudo usermod -a -G dialout $USER")
        print("3. Logout and login again")
        print("4. Verify MDB device is connected and powered")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 