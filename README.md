# Pico W Marantz Controller
Control a Marantz audio receiver wirelessly with a Pico W in MicroPython via RS-232C utilizing MQTT. This program is currently optimized for operation of the Marantz SR6400/SR5400.

## Compatible Hardware
To use this software, you must utilize a UART to RS-232 TTL level converter. *Do not connect your Pico directly to RS-232!* Also ensure that your level converter is 3.3v compatible. Here are a number of boards that should be compatible with minor adjustments:
* [Waveshare RS232 Board](http://www.waveshare.com/wiki/RS232_Board)
* [Waveshare Pico-2CH-RS232](https://www.waveshare.com/wiki/Pico-2CH-RS232) - _Doesn't support CTS/RTS_
* [SparkFun RS232 Shifter - SMD](https://www.sparkfun.com/products/449) - _Doesn't support CTS/RTS_

If you're feeling particularly handy, you can also build one yourself using an MAX3232/SP3232 IC.

## Firmware
Before writing to your Pico W, you will need to install the latest [MicroPython firmware](https://micropython.org/download/rp2-pico-w/) to your device. Then, you can transfer [main.py](https://github.com/dcooperdalrymple/rpi-pico-w-marantz-rs232c/blob/main/main.py) and [config.py](https://github.com/dcooperdalrymple/rpi-pico-w-marantz-rs232c/blob/main/config.py) (after configuring for your wireless network) to your Pico W.

## MQTT Configuration Examples
You will need to set up an MQTT server using your own hardware or an online service before controlling this device. Here are some examples of standard MQTT settings within [config.py](https://github.com/dcooperdalrymple/rpi-pico-w-marantz-rs232c/blob/main/config.py):

### Adafruit IO
```
'mqtt': {
    'client_id': 'RANDOM',
    'url': 'io.adafruit.com',
    'user': 'YOUR_USERNAME',
    'key': 'AIO_KEY',
    'feed': 'FEED_NAME'
}
```

## MQTT Commands
All commands are based on a subscription feed with a single integer value.

| Value | Command            |
| ----- | ------------------ |
| 1     | Power Off          |
| 2     | Power On           |
| 3     | Input TV           |
| 4     | Input CD           |
| 5     | Input Tape         |
| 6     | Volume Up (+1db)   |
| 7     | Volume Down (-1db) |

## Onboard LED
The onboard LED will blink initially with the status of the wireless connection (3 blinks indicates a successful connection; see [main.py](https://github.com/dcooperdalrymple/rpi-pico-w-marantz-rs232c/blob/main/main.py#L133) for more details).

After this point, it will be used to indicate the power status of the device based on the last power-related MQTT command. This power indication won't be accurate if the front panel power button is used. It will also flash whenever a valid MQTT command is being processed.

## Debugging
It is highly recommended that you test this device over USB-UART using a Micropython enhanced IDE such as [Thonny](https://thonny.org/) before final deployment. Most network and MQTT connection details will be logged.

To ensure that your RS232C device is working properly, it may be helpful to utilize a USB-to-RS232 dongle connected to your computer and viewing the incoming data on a serial monitor. Make sure that the dongle's settings match the Pico's UART settings (as defined in [config.py](https://github.com/dcooperdalrymple/rpi-pico-w-marantz-rs232c/blob/main/config.py)).

## Notes
* This program is fairly basic as of its first release. It could benefit from better device, server, and command abstraction to make it a more capable program depending on your needs and audio receiver model. Hopefully, this is a good starting point for you to develop it further for your specific requirements.
* Status calls are functionally operational, but not currently implemented. This could be useful to better indicate power status, control volume, and confirm that commands executed successfully.
