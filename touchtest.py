import time
import framebuf
from machine import Pin, SPI, I2C

class ST7789:
    def __init__(self, spi, width, height, cs, dc, reset, bl):
        self.spi = spi
        self.width = width
        self.height = height
        self.cs = Pin(cs, Pin.OUT)
        self.dc = Pin(dc, Pin.OUT)
        self.reset = Pin(reset, Pin.OUT)
        self.bl = Pin(bl, Pin.OUT)

        self.cs.value(1)
        self.dc.value(0)
        self.reset.value(1)
        self.bl.value(1)

        self.buffer = bytearray(self.width * self.height * 2)
        self.framebuffer = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.RGB565)

        self.init_display()

    def init_display(self):
        print("Initializing display")
        self.reset.value(1)
        time.sleep_ms(50)
        self.reset.value(0)
        time.sleep_ms(50)
        self.reset.value(1)
        time.sleep_ms(150)

        self._write_cmd(0x11)  # Sleep out
        time.sleep_ms(120)
        
        self._write_cmd(0x36)
        self._write_data(0x00)  # MADCTL: left to right, top to bottom
        
        self._write_cmd(0x3A)
        self._write_data(0x05)  # COLMOD: 16-bit color

        self._write_cmd(0x29)  # Display on
        time.sleep_ms(100)
        print("Display initialized")

    def _write_cmd(self, cmd):
        self.cs.value(0)
        self.dc.value(0)
        self.spi.write(bytearray([cmd]))
        self.cs.value(1)

    def _write_data(self, data):
        self.cs.value(0)
        self.dc.value(1)
        self.spi.write(bytearray([data]))
        self.cs.value(1)

    def fill(self, color):
        self.framebuffer.fill(color)
        self.show()

    def show(self):
        self._write_cmd(0x2A)  # Column address set
        self._write_data(0x00)
        self._write_data(0x00)  # Start column
        self._write_data((self.width - 1) >> 8)
        self._write_data((self.width - 1) & 0xFF)  # End column

        self._write_cmd(0x2B)  # Row address set
        self._write_data(0x00)
        self._write_data(0x00)  # Start row
        self._write_data((self.height - 1) >> 8)
        self._write_data((self.height - 1) & 0xFF)  # End row

        self._write_cmd(0x2C)  # Memory write
        self.cs.value(0)
        self.dc.value(1)
        self.spi.write(self.buffer)
        self.cs.value(1)
        print("Display buffer updated")

class TouchPanel:
    def __init__(self, i2c):
        self.i2c = i2c
        self.addr = 0x51  # Use previous address

    def read_touch(self):
        try:
            data = self.i2c.readfrom(self.addr, 6)
            print(f"Raw touch data: {data}")
            if data[0] == 0x01:  # Data valid
                x = (data[3] << 8) | data[4]
                y = (data[1] << 8) | data[2]
                return x, y
        except Exception as e:
            print(f"Touch read error at address {hex(self.addr)}:", e)
        return None, None

# Simplified touch detection without debounce for debugging
def detect_touch(touch_panel):
    x, y = touch_panel.read_touch()
    if x is not None and y is not None:
        return x, y
    return None, None

# Test program to strobe screen on touch
spi = SPI(2, baudrate=40000000, polarity=1, phase=1, sck=Pin(6), mosi=Pin(7))
cs = 5
dc = 4
reset = 8
bl = 15

# Initialize display
display = ST7789(spi, 240, 320, cs, dc, reset, bl)
display.fill(0xFFFF)
display.show()

# Initialize touch panel with the correct address
i2c = I2C(1, scl=Pin(10), sda=Pin(11), freq=100000)  # Lower I2C frequency to reduce noise
touch = TouchPanel(i2c)

# Main loop to detect touch and update display
while True:
    x, y = detect_touch(touch)
    if x is not None and y is not None:
        print(f"Touch detected at address 0x51: ({x}, {y})")
        # Strobe screen between purple and black
        display.fill(0xF81F)  # Purple
        display.show()
        time.sleep(0.1)
        display.fill(0x0000)  # Black
        display.show()
        time.sleep(0.1)
    else:
        print("No touch detected")
    time.sleep(0.1)
