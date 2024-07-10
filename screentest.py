# Standalone screen testing program that displays Hi world on the touchscreen. Driver is included for the ST7789. Usually have to run it twice so there's a possibilty I'm missing something.



import time
import framebuf
from machine import Pin, SPI

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

    def text(self, text, x, y, color):
        self.framebuffer.text(text, x, y, color)
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

# Test program to display "Hi world"
spi = SPI(2, baudrate=40000000, polarity=1, phase=1, sck=Pin(6), mosi=Pin(7))
cs = 5
dc = 4
reset = 8
bl = 15

display = ST7789(spi, 240, 320, cs, dc, reset, bl) #240x320 frame buffer despite 240x280 screen resolution, to prevent garbage on the screen

# Clear the display with a white background
display.fill(0xFFFF)

# Display "Hi world" in black color
display.text('Hi Emily', 90, 140, 0x0000)

while True:
    pass  # Keep the display on
