import time
from enum import Enum

import board
import digitalio
import serial

import adafruit_ahtx0
import adafruit_character_lcd.character_lcd as characterlcd

from gpiozero import PWMLED, Button


# LCD dimensions
LCD_COLUMNS = 16
LCD_ROWS = 2

# default set point in degrees Fahrenheit
DEFAULT_SET_POINT = 72.0

UART_PORT = "/dev/serial0"
UART_BAUD = 115200


class Mode(Enum):
    OFF = 0
    HEAT = 1
    COOL = 2


# hardware setup

# I2C for the AHT20 temperature and humidity sensor
i2c = board.I2C()  # uses SDA and SCL

sensor = adafruit_ahtx0.AHTx0(i2c)

# parallel 16x2 LCD using same pins as DisplayTest.py
lcd_rs = digitalio.DigitalInOut(board.D17)
lcd_en = digitalio.DigitalInOut(board.D27)
lcd_d4 = digitalio.DigitalInOut(board.D5)
lcd_d5 = digitalio.DigitalInOut(board.D6)
lcd_d6 = digitalio.DigitalInOut(board.D13)
lcd_d7 = digitalio.DigitalInOut(board.D26)

lcd = characterlcd.Character_LCD_Mono(
    lcd_rs,
    lcd_en,
    lcd_d4,
    lcd_d5,
    lcd_d6,
    lcd_d7,
    LCD_COLUMNS,
    LCD_ROWS,
)

# LEDs
red_led = PWMLED(18)   # heating indicator
blue_led = PWMLED(21)  # cooling indicator

# buttons
mode_button = Button(12, pull_up=True, bounce_time=0.05)   # off / heat / cool
up_button = Button(25, pull_up=True, bounce_time=0.05)     # raise set point
down_button = Button(24, pull_up=True, bounce_time=0.05)   # lower set point

# UART for sending data to server
uart = serial.Serial(UART_PORT, UART_BAUD, timeout=1)


# global state
mode = Mode.OFF
set_point = DEFAULT_SET_POINT
last_uart_time = 0.0
last_display_toggle = 0.0
show_temp_line = True
led_state = "OFF"


def cycle_mode():
    global mode
    if mode == Mode.OFF:
        mode = Mode.HEAT
    elif mode == Mode.HEAT:
        mode = Mode.COOL
    else:
        mode = Mode.OFF


def increase_set_point():
    global set_point
    set_point += 1.0


def decrease_set_point():
    global set_point
    set_point -= 1.0


mode_button.when_pressed = cycle_mode
up_button.when_pressed = increase_set_point
down_button.when_pressed = decrease_set_point


def stop_pulses():
    """Stop any ongoing pulses on both LEDs."""
    red_led.source = None
    blue_led.source = None
    red_led.off()
    blue_led.off()


def update_leds(current_temp_f):
    """Set LED behavior based on mode and temperature."""
    global led_state, mode, set_point

    if mode == Mode.OFF:
        if led_state != "OFF":
            stop_pulses()
            led_state = "OFF"
        return

    if mode == Mode.HEAT:
        # blue off in heat mode
        blue_led.source = None
        blue_led.off()

        if current_temp_f < set_point:
            # heat on, red fades
            if led_state != "HEAT_FADE":
                red_led.source = None
                red_led.off()
                red_led.pulse(
                    fade_in_time=1.0,
                    fade_out_time=1.0,
                    background=True,
                )
                led_state = "HEAT_FADE"
        else:
            # at or above set point, red solid
            if led_state != "HEAT_SOLID":
                red_led.source = None
                red_led.value = 1.0
                led_state = "HEAT_SOLID"

    elif mode == Mode.COOL:
        # red off in cool mode
        red_led.source = None
        red_led.off()

        if current_temp_f > set_point:
            # cool on, blue fades
            if led_state != "COOL_FADE":
                blue_led.source = None
                blue_led.off()
                blue_led.pulse(
                    fade_in_time=1.0,
                    fade_out_time=1.0,
                    background=True,
                )
                led_state = "COOL_FADE"
        else:
            # at or below set point, blue solid
            if led_state != "COOL_SOLID":
                blue_led.source = None
                blue_led.value = 1.0
                led_state = "COOL_SOLID"


def mode_label():
    if mode == Mode.OFF:
        return "OFF"
    if mode == Mode.HEAT:
        return "HEAT"
    return "COOL"


def update_display(current_temp_f):
    """Update both LCD lines and alternate second line text."""
    global show_temp_line, last_display_toggle

    now = time.time()

    if now - last_display_toggle >= 5.0:
        show_temp_line = not show_temp_line
        last_display_toggle = now

    # first line date and time
    line1 = time.strftime("%m/%d %H:%M:%S")
    if len(line1) > LCD_COLUMNS:
        line1 = line1[:LCD_COLUMNS]

    if show_temp_line:
        # show current temperature
        line2 = "Temp {:5.1f}F".format(current_temp_f)
    else:
        # show mode and set point
        line2 = "{} {:4.0f}F".format(mode_label(), set_point)

    if len(line2) > LCD_COLUMNS:
        line2 = line2[:LCD_COLUMNS]

    lcd.clear()
    lcd.message = line1 + "\n" + line2


def send_uart(current_temp_f):
    """Send state, current temp, and set point over UART every thirty seconds."""
    global last_uart_time

    now = time.time()
    if now - last_uart_time < 30.0:
        return

    state_text = mode_label().lower()
    data = "{},{:.2f},{:.2f}\n".format(state_text, current_temp_f, set_point)
    uart.write(data.encode("utf8"))
    last_uart_time = now


def main():
    lcd.clear()
    lcd.message = "Thermostat\nStarting up"
    time.sleep(2.0)

    try:
        while True:
            # read sensor and convert to Fahrenheit
            temp_c = sensor.temperature
            current_temp_f = temp_c * 9.0 / 5.0 + 32.0

            update_leds(current_temp_f)
            update_display(current_temp_f)
            send_uart(current_temp_f)

            time.sleep(0.5)

    except KeyboardInterrupt:
        lcd.clear()
        stop_pulses()
        lcd.message = "Shutting down"
        time.sleep(1.0)
        lcd.clear()
        # optionally deinit LCD pins
        lcd_rs.deinit()
        lcd_en.deinit()
        lcd_d4.deinit()
        lcd_d5.deinit()
        lcd_d6.deinit()
        lcd_d7.deinit()


if __name__ == "__main__":
    main()
