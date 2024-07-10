from machine import Pin, I2C
import time

# PCF85063 I2C address
PCF85063_ADDRESS = 0x51

# PCF85063 Registers
PCF85063_CTRL1 = 0x00
PCF85063_CTRL2 = 0x01
PCF85063_SECONDS = 0x04
PCF85063_MINUTES = 0x05
PCF85063_HOURS = 0x06
PCF85063_DAY = 0x07
PCF85063_WEEKDAY = 0x08
PCF85063_MONTH = 0x09
PCF85063_YEAR = 0x0A

# Initialize I2C on GPIO10 (SCL) and GPIO11 (SDA)
i2c = I2C(1, scl=Pin(10), sda=Pin(11), freq=400000)

def write_register(address, register, value):
    i2c.writeto_mem(address, register, bytes([value]))

def read_register(address, register, length):
    return i2c.readfrom_mem(address, register, length)

def bcd_to_int(bcd):
    return ((bcd >> 4) * 10) + (bcd & 0x0F)

def int_to_bcd(n):
    return ((n // 10) << 4) | (n % 10)

def set_rtc_time():
    # Disable the RTC before setting time
    write_register(PCF85063_ADDRESS, PCF85063_CTRL1, 0x20)  # Stop the clock
    time.sleep(0.1)
    
    # Set the date and time
    year = int_to_bcd(24)  # Year (24 for 2024, the century is handled separately if needed)
    month = int_to_bcd(7)  # Month (1-12, 7 for July)
    day = int_to_bcd(10)   # Day (1-31)
    weekday = int_to_bcd(3)  # Weekday (0-6, assuming 0 is Sunday)
    hours = int_to_bcd(15)  # Hours (0-23, 15 for 3 PM)
    minutes = int_to_bcd(42) # Minutes (0-59)
    seconds = int_to_bcd(0)  # Seconds (0-59)
    
    write_register(PCF85063_ADDRESS, PCF85063_SECONDS, seconds)
    write_register(PCF85063_ADDRESS, PCF85063_MINUTES, minutes)
    write_register(PCF85063_ADDRESS, PCF85063_HOURS, hours)
    write_register(PCF85063_ADDRESS, PCF85063_DAY, day)
    write_register(PCF85063_ADDRESS, PCF85063_WEEKDAY, weekday)
    write_register(PCF85063_ADDRESS, PCF85063_MONTH, month)
    write_register(PCF85063_ADDRESS, PCF85063_YEAR, year)
    
    # Enable the RTC
    write_register(PCF85063_ADDRESS, PCF85063_CTRL1, 0x00)  # Start the clock

def read_rtc_time():
    # Read the date and time
    seconds = bcd_to_int(read_register(PCF85063_ADDRESS, PCF85063_SECONDS, 1)[0])
    minutes = bcd_to_int(read_register(PCF85063_ADDRESS, PCF85063_MINUTES, 1)[0])
    hours = bcd_to_int(read_register(PCF85063_ADDRESS, PCF85063_HOURS, 1)[0])
    day = bcd_to_int(read_register(PCF85063_ADDRESS, PCF85063_DAY, 1)[0])
    weekday = bcd_to_int(read_register(PCF85063_ADDRESS, PCF85063_WEEKDAY, 1)[0])
    month = bcd_to_int(read_register(PCF85063_ADDRESS, PCF85063_MONTH, 1)[0])
    year = bcd_to_int(read_register(PCF85063_ADDRESS, PCF85063_YEAR, 1)[0]) + 2000  # Assuming century is 2000+

    print(f"Date: {year}-{month:02d}-{day:02d}")
    print(f"Time: {hours:02d}:{minutes:02d}:{seconds:02d}")

def main():
    print("Setting RTC time...")
    set_rtc_time()
    
    print("Reading back RTC time...")
    read_rtc_time()

if __name__ == "__main__":
    main()
