import adafruit_ssd1306
import adafruit_ads1x15.ads1115
from adafruit_ads1x15.analog_in import AnalogIn
import board
import busio
from PIL import Image, ImageDraw, ImageFont
import time

I2C = busio.I2C(board.SCL, board.SDA)
WIDTH = 128
HEIGHT = 64
ADDR = 0x3c  # found with `sudo i2cdetect -y 1`
OLED = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, I2C, addr=ADDR)

ADS = adafruit_ads1x15.ads1115.ADS1115(I2C)
CHAN = AnalogIn(ADS, adafruit_ads1x15.ads1115.P0)

OLED.fill(0)
OLED.show()

if __name__ == "__main__":
    # eww
    try:
        image = Image.new("1", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default(size=36.0)
        while True:
            #pretty_voltage = round(CHAN.voltage, 3)
            #print(pretty_voltage)

            max_voltage = 3.3
            if CHAN.voltage > max_voltage:
                percent_brightness = 100
            elif CHAN.voltage < 0:  # ???
                percent_brightness = 0
            else:
                #percent_brightness = round(100 * CHAN.voltage / max_voltage, 1)
                percent_brightness = int(100 * CHAN.voltage / max_voltage)

            image = Image.new("1", (WIDTH, HEIGHT))
            draw = ImageDraw.Draw(image)
            draw.rectangle((0, 0, WIDTH, HEIGHT), outline=255, fill=255)
            #border = 5
            #draw.rectangle((border, border, WIDTH - border - 1, HEIGHT - border - 1), outline=0, fill=0)
            draw.rectangle((0, 0, WIDTH - 1, HEIGHT - 1), outline=0, fill=0)
            #text = f"{pretty_voltage}V"
            text = f"{percent_brightness}%"
            bbox = font.getbbox(text)
            font_width, font_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text((WIDTH // 2 - font_width // 2, HEIGHT // 2 - font_height // 2 - 10), text, font=font, fill=255)
            #OLED.fill(0)
            #OLED.show()
            OLED.image(image)
            OLED.show()
            time.sleep(0.1)

    except KeyboardInterrupt:
        OLED.fill(0)
        OLED.show()
