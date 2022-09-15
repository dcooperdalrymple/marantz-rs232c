# Pico W Marantz Controller
Control a Marantz SR6400/SR5400 wirelessly with a Pico W in MicroPython via RS-232C utilizing MQTT.

## Compatible Hardware
To use this software, you must utilize a UART to RS-232 TTL level converter. *Do not connect your Pico directly to RS-232!* Also ensure that your level converter is 3.3v compatible. Here are a number of compatible boards that should be compatible with minor adjustments:
* [Waveshare RS232 Board](http://www.waveshare.com/wiki/RS232_Board)
* [Waveshare Pico-2CH-RS232](https://www.waveshare.com/wiki/Pico-2CH-RS232) - _Doesn't support CTS/RTS_
* [SparkFun RS232 Shifter - SMD](https://www.sparkfun.com/products/449) - _Doesn't support CTS/RTS_

If you're feeling particularly handy, you can also build one yourself using an MAX3232/SP3232 IC.

## MQTT Configuration Examples

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
