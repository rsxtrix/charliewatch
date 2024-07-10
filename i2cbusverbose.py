from machine import Pin, I2C
import time

# Initialize I2C on GPIO10 (SCL) and GPIO11 (SDA)
i2c = I2C(1, scl=Pin(10), sda=Pin(11), freq=400000)

# Address and register for the capacitive touch device
TOUCH_ADDRESS = 0x51
TOUCH_REGISTER = 0x2B

def read_register(address, register, length):
    try:
        data = i2c.readfrom_mem(address, register, length)
        return data
    except Exception as e:
        print(f"Failed to read from address 0x{address:X}, register 0x{register:X}: {e}")
        return None

def main():
    print("Scanning I2C bus...")
    devices = i2c.scan()
    if devices:
        print("I2C devices found:", [hex(device) for device in devices])
    else:
        print("No I2C devices found")

    # Try reading from the capacitive touch device
    print(f"Attempting to read from device at address 0x{TOUCH_ADDRESS:X}, register 0x{TOUCH_REGISTER:X}...")
    data = read_register(TOUCH_ADDRESS, TOUCH_REGISTER, 1)
    if data:
        print(f"Data read from device at address 0x{TOUCH_ADDRESS:X}: {data}")
    else:
        print(f"No response from device at address 0x{TOUCH_ADDRESS:X}")

if __name__ == "__main__":
    main()
