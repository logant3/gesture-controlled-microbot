from machine import Pin, SPI, ADC
from nrf24l01 import NRF24L01
import time, struct


# Flex sensor assignments
flex_left    = ADC(26)   # ADC0
flex_forward = ADC(27)   # ADC1
flex_right   = ADC(28)   # ADC2

# test LED
led = Pin(22, Pin.OUT)


# NRF24L01 on SPI0 pin assignments

spi = SPI(
    0,
    baudrate=4000000,
    polarity=0,
    phase=0,
    sck=Pin(2),      # SPI0 SCK
    mosi=Pin(19),    # SPI0 MOSI
    miso=Pin(4)      # SPI0 MISO
)

csn = Pin(17, Pin.OUT, value=1)   # CSN
ce  = Pin(6,  Pin.OUT, value=0)   # CE

ADDRESS = b"BOT01"
CHANNEL = 76
PAYLOAD = 1

radio = NRF24L01(spi, csn, ce, channel=CHANNEL, payload_size=PAYLOAD)
radio.open_tx_pipe(ADDRESS)

print("TX READY")

# BUILD CONTROL MASK

def read_mask():
    left_raw    = flex_left.read_u16()
    forward_raw = flex_forward.read_u16()
    right_raw   = flex_right.read_u16()

    # threshold values for 
    left     = 1 if left_raw    < 22000 else 0
    forward  = 1 if forward_raw < 22000 else 0
    right    = 1 if right_raw   < 22000 else 0

    mask = (left << 0) | (forward << 1) | (right << 2)

    return mask


while True:
    mask = read_mask()
    packet = struct.pack("B", mask)

    # LED on when commands are sent
    led.value(1 if mask != 0 else 0)

    try:
        radio.send(packet)
        print("Sent mask:", mask)
    except OSError as e:
        print("TX error:", e)

    time.sleep(0.03)
