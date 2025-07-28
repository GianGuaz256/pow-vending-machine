#!/usr/bin/env python3
"""
Simple USB MDB Test - Following User's Exact Example
Tests MDB connection using the exact approach provided by the user
"""

import serial

def main():
    """Test MDB USB connection exactly as specified by user"""
    print("Simple USB MDB Test - User's Exact Example")
    print("="*50)
    
    try:
        # User's exact implementation
        ser = serial.Serial() #Create Serial Object
        ser.baudrate = 115200 #Set the appropriate BaudRate
        ser.timeout = 50 #The maximum timeout that the program waits for a reply. If 0 is used, the pot is blocked until readline returns
        ser.port = '/dev/ttyACM0' # Specify the device file descriptor
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
        print("\n✓ SUCCESS: MDB USB interface is working!")
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        print("\nTroubleshooting:")
        print("1. Check that /dev/ttyACM0 exists: ls -la /dev/ttyACM*")
        print("2. Add user to dialout group: sudo usermod -a -G dialout $USER")
        print("3. Logout and login again")
        print("4. Verify USB MDB device is connected")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 