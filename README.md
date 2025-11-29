# Gesture-Controlled-Microbot
A full custom-PCB system for wireless, gesture-based robot control. Includes Pico-powered flex-sensor glove (TX), NRF24L01 RF link, and a robot module with TB6612FNG motor driver, boost regulation, and SPI OLED eye animations. Demonstrates hardware, firmware, and system design.

# Features
* Custom-designed PCBs for both TX (glove) and RX (robot)

* Real-time gesture control using three flex sensors mapped to Left / Forward / Right

* Reliable 2.4 GHz wireless communication with NRF24L01+

* Raspberry Pi Pico on both modules (SPI + ADC + PWM control)

* Dual-power system with LiPo + boost regulation

* TB6612FNG motor driver powering two DC motors with PWM speed control

* Two SH1106 SPI OLED displays rendering wandering animated eyes

* Modular and readable MicroPython codebase


# How it Works
**Hand Module (TX)**

The glove uses three flex sensors wired in voltage dividers and read through the Pico’s ADC pins.
Each sensor bend is converted into a 3-bit command mask:

| Gesture | Bitmask | Decimal |
| :------- | :------: | -------: |
| Stop | 000 | 0 |
| Left | 001 | 1 |
| Forward | 010 | 2 |
| Right | 100 | 4 |

This value is transmitted over the NRF24L01+ radio every 50 ms.

**Robot Module (RX)**

The receiving Pico decodes the bitmask and drives a TB6612FNG motor driver using PWM signals.
A separate 6V pack powers the motors, while a 3.7V LiPo → 5V boost converter powers logic.
Two SPI OLED displays render expressive “robot eyes” using lightweight non-blocking animations.

The robot moves immediately upon receiving a valid packet, but continues animating the eyes whenever idle.
