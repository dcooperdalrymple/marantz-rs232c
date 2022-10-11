# Pico W Marantz Controller
Control a Marantz audio receiver wirelessly with a Pico W in CircuitPython via RS-232C utilizing MQTT. This program is currently optimized for operation of the Marantz SR6400/SR5400.

## Compatible Hardware
To use this software, you must utilize a UART to RS-232 TTL level converter. *Do not connect your Pico directly to RS-232!* Also ensure that your level converter is 3.3v compatible. Here are a number of boards that should be compatible with minor adjustments:
* [Waveshare RS232 Board](http://www.waveshare.com/wiki/RS232_Board)
* [Waveshare Pico-2CH-RS232](https://www.waveshare.com/wiki/Pico-2CH-RS232) - _Doesn't support CTS/RTS_
* [SparkFun RS232 Shifter - SMD](https://www.sparkfun.com/products/449) - _Doesn't support CTS/RTS_

If you're feeling particularly handy, you can also build one yourself using an MAX3232/SP3232 IC.

## Firmware
Before writing to your Pico W, you will need to install the latest [CircuitPython 8.x firmware](https://circuitpython.org/board/raspberry_pi_pico_w/) to your device (previous versions of CircuitPython do not support the wireless functionality of the Pico W). Then, you can transfer [code.py](code.py) and [config.py](config.py) (after configuring for your wireless network) to your Pico W.

### Library Requirements
Adafruit's CircuitPython (8.x) doesn't include an MQTT client library by default. You will need to obtain `adafruit_minimqtt` library and add it to the `/lib/` folder in your device's main directory before using this program. You can grab the latest release of `adafruit_minimqtt` on the official [GitHub repository](https://github.com/adafruit/Adafruit_CircuitPython_MiniMQTT/) or by extracting it from the [CircuitPython library bundle](https://circuitpython.org/libraries).

For more information on how to install CircuitPython libraries, see this [Adafruit guide](https://learn.adafruit.com/welcome-to-circuitpython/circuitpython-libraries).

## MQTT Configuration Examples
You will need to set up an MQTT server using your own hardware or an online service before controlling this device. Here are some examples of standard MQTT settings within [config.py](config.py):

### Adafruit IO
```
'mqtt': {
    'client_id': 'RANDOM',
    'url': 'io.adafruit.com',
    'user': 'YOUR_USERNAME',
    'key': 'AIO_KEY',
    'feed': 'FEED_NAME',
    'keepalive': 300
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
After completing the initialization process (usually takes 3+ seconds), the onboard LED should blink 3 times to indicate a successful wireless and MQTT connection. If any error occurred in the process, the device will only blink 2 times then stop operation. It is recommended to debug the device at this time to see where the error might have occurred (see section below).

After this point, the onboard LED will be used to indicate whenever a valid message is received from the MQTT broker with a single blink while the incoming message is being processed.

## Debugging
It is highly recommended that you test this device over USB-UART using a CircuitPython enhanced IDE such as [Thonny](https://thonny.org/) before final deployment. Most network and MQTT connection details will be logged.

To ensure that your RS232C device is working properly, it may be helpful to utilize a USB-to-RS232 dongle connected to your computer and viewing the incoming data on a serial monitor. Make sure that the dongle's settings match the Pico's UART settings (as defined in [config.py](config.py)).

## Notes
* This program is fairly basic as of its first release. It could benefit from better device, server, and command abstraction to make it a more capable program depending on your needs and audio receiver model. Hopefully, this is a good starting point for you to develop it further for your specific requirements.
* Status calls are functionally operational, but not currently implemented. This could be useful to better indicate power status, control volume, and confirm that commands executed successfully.
