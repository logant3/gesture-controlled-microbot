from machine import Pin, PWM, SPI
from nrf24l01 import NRF24L01
from sh1106 import SH1106_SPI
from roboeyes import RoboEyes
import time, urandom, math


#   Setting eyes up on SPI1

spi1 = SPI(1, baudrate=9000000, polarity=0, phase=0,
           sck=Pin(14), mosi=Pin(15))

# Left screen pin assignments
dcL  = Pin(12, Pin.OUT)
rstL = Pin(13, Pin.OUT)
csL  = Pin(9, Pin.OUT)
oledL = SH1106_SPI(128, 64, spi1, dcL, rstL, csL)

# Right screen pin assignments
dcR  = Pin(21, Pin.OUT)
rstR = Pin(26, Pin.OUT)
csR  = Pin(20, Pin.OUT)
oledR = SH1106_SPI(128, 64, spi1, dcR, rstR, csR)

oledL.fill(0); oledL.show()
oledR.fill(0); oledR.show()

# Safe show callbacks

def show_left(re):
    oledL.show()

def show_right(re):
    oledR.show()



# Define eyes

leftEye  = RoboEyes(oledL, 128, 64, frame_rate=30, on_show=show_left)
rightEye = RoboEyes(oledR, 128, 64, frame_rate=30, on_show=show_right)

leftEye.cyclops  = True
rightEye.cyclops = True


# Define eyes dimensions

EYE_W = 50    # eye width
EYE_H = 50    # eye height
EYE_R = 25    # eye radius

leftEye.eyes_width(EYE_W, EYE_W)
rightEye.eyes_width(EYE_W, EYE_W)

leftEye.eyes_height(EYE_H, EYE_H)
rightEye.eyes_height(EYE_H, EYE_H)

leftEye.eyes_radius(EYE_R, EYE_R)
rightEye.eyes_radius(EYE_R, EYE_R)
 
# Center the eyes on the OLED screens
def center_eye(re):
    re.eyeLx = re.eyeLxNext = (128 - EYE_W)//2 + 3
    re.eyeLy = re.eyeLyNext = (64  - EYE_H)//2

center_eye(leftEye)
center_eye(rightEye)



SAFE_MARGIN = 4   # keep all eye movements within 4 pixels on top and bottom

def apply_vertical_clamp(re):
    # Keep left eye within safe margin zones
    if re.eyeLy < SAFE_MARGIN:
        re.eyeLy = SAFE_MARGIN
    if re.eyeLy + re.eyeLheightCurrent > (64 - SAFE_MARGIN):
        re.eyeLy = 64 - SAFE_MARGIN - re.eyeLheightCurrent

    # Keep right eye within safe margin zones
    if re.eyeRy < SAFE_MARGIN:
        re.eyeRy = SAFE_MARGIN
    if re.eyeRy + re.eyeRheightCurrent > (64 - SAFE_MARGIN):
        re.eyeRy = 64 - SAFE_MARGIN - re.eyeRheightCurrent


# override roboeyes so we can include the vertical safety clamp after roboeyes runs
_original_update = RoboEyes.update

def safe_update(self):
    _original_update(self)
    apply_vertical_clamp(self)

RoboEyes.update = safe_update



# Blink and idle declarations

leftEye.set_idle_mode(True, interval=2, variation=2)
rightEye.set_idle_mode(True, interval=2, variation=2)

leftEye.set_auto_blinker(True, interval=2, variation=3)
rightEye.set_auto_blinker(True, interval=2, variation=3)

leftEye.mood = 4 #happy mood
rightEye.mood = 4




FORWARD_SPEED = 35000 # motor speed for forward
TURN_SPEED = 18000 #motor speed for turns

# Motor driver pin assignments

AIN1 = Pin(3, Pin.OUT)
AIN2 = Pin(4, Pin.OUT)
BIN1 = Pin(6, Pin.OUT)
BIN2 = Pin(7, Pin.OUT)

PWMA = PWM(Pin(2)); PWMA.freq(1000)
PWMB = PWM(Pin(5)); PWMB.freq(1000)

STBY = Pin(8, Pin.OUT); STBY.value(1)

#transciever pin assignments and setup

spi0 = SPI(0, baudrate=4000000, polarity=0, phase=0,
           sck=Pin(18), mosi=Pin(19), miso=Pin(16))

csn = Pin(17, Pin.OUT, value=1)
ce  = Pin(22, Pin.OUT, value=0)

nrf = NRF24L01(spi0, csn, ce, channel=76, payload_size=1)
nrf.open_rx_pipe(0, b"BOT01")
nrf.start_listening()


#definitions for moving functions


def stop():
    AIN1.value(0); AIN2.value(0)
    BIN1.value(0); BIN2.value(0)
    PWMA.duty_u16(0)
    PWMB.duty_u16(0)

def forward():
    AIN1.value(1); AIN2.value(0)
    BIN1.value(1); BIN2.value(0)
    PWMA.duty_u16(FORWARD_SPEED)
    PWMB.duty_u16(FORWARD_SPEED)

def left():
    AIN1.value(0); AIN2.value(1)
    BIN1.value(1); BIN2.value(0)
    PWMA.duty_u16(TURN_SPEED)
    PWMB.duty_u16(TURN_SPEED)

def right():
    AIN1.value(1); AIN2.value(0)
    BIN1.value(0); BIN2.value(1)
    PWMA.duty_u16(TURN_SPEED)
    PWMB.duty_u16(TURN_SPEED)



while True:
    if nrf.any():
        mask = nrf.recv()[0]

        left_cmd    = bool(mask & 0b001)
        forward_cmd = bool(mask & 0b010)
        right_cmd   = bool(mask & 0b100)

        if forward_cmd:
            forward()
            leftEye.mood = 4
            rightEye.mood = 4
        elif left_cmd:
            left()
        elif right_cmd:
            right()
        else:
            stop()
            leftEye.mood = 2
            rightEye.mood = 2

    leftEye.update()
    rightEye.update()

