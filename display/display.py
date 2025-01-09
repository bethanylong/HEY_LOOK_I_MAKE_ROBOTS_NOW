"""
adafruit recommendation:
https://learn.adafruit.com/monochrome-oled-breakouts/python-setup#speeding-up-the-display-on-raspberry-pi-3041506

For the best performance, especially if you are doing fast animations, you'll want to tweak the I2C core to run at 1MHz. By default it may be 100KHz or 400KHz

To do this edit the config with sudo nano /boot/firmware/config.txt

and add to the end of the file

dtparam=i2c_baudrate=1000000
"""

import adafruit_ssd1306
import board
import busio
from PIL import Image, ImageDraw, ImageFont

I2C = busio.I2C(board.SCL, board.SDA)
WIDTH = 128
HEIGHT = 64
ADDR = 0x3c  # found with `sudo i2cdetect -y 1`
OLED = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, I2C, addr=ADDR)

OLED.fill(0)
OLED.show()

if __name__ == "__main__":
    image = Image.new("1", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, WIDTH, HEIGHT), outline=255, fill=255)
    border = 5
    draw.rectangle((border, border, WIDTH - border - 1, HEIGHT - border - 1), outline=0, fill=0)
    font = ImageFont.load_default()
    text = "Hi there!"
    bbox = font.getbbox(text)
    font_width, font_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((WIDTH // 2 - font_width // 2, HEIGHT // 2 - font_height // 2), text, font=font, fill=2555)
    OLED.image(image)
    OLED.show()
