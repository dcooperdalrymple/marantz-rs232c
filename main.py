import rp2
import machine
from machine import Pin, UART
import network
import ubinascii
import time
import upip
import sys
from config import config

rp2.country(config['country'])

led = Pin('LED', Pin.OUT)

uart = UART(
    config['uart']['id'],
    baudrate=config['uart']['format']['baudrate'],
    bits=config['uart']['format']['bits'],
    parity=config['uart']['format']['parity'],
    stop=config['uart']['format']['stop'],
    tx=Pin(config['uart']['pins']['tx']),
    rx=Pin(config['uart']['pins']['rx']),
    rts=Pin(config['uart']['pins']['rts']),
    cts=Pin(config['uart']['pins']['cts']),
    timeout=config['uart']['timeout'],
    timeout_char=config['uart']['timeout'],
    flow=UART.RTS | UART.CTS
)

def rs232_convert(c):
    if isinstance(c, str):
        if len(c) == 1:
            return ord(c)
        else:
            return False
    else:
        return int(c)
def rs232_build(data):
    msg = bytearray()
    msg.append(rs232_convert(config['rs232']['start']))
    msg.append(rs232_convert(config['rs232']['id']))
    if isinstance(data, str) and len(data) > 1:
        for i in data:
            msg.append(rs232_convert(i))
    else:
        msg.append(rs232_convert(data))
    msg.append(rs232_convert(config['rs232']['end']))
    return msg

def rs232_command(command, timeout=2):
    msg = rs232_build(command)
    print('Sending RS232C command: 0x{}'.format(msg.hex()))

    respone = None
    try:
        uart.write(msg)
        time.sleep(0.1)
        response = uart.read(1)
    except Exception as e:
        print('Failed to send RS232 command {}{}'.format(type(e).__name__, e))
        sys.print_exception(e)
        return False

    if response != None:
        if response[0] == rs232_convert(config['rs232']['ack']):
            return True
        elif response[0] == rs232_convert(config['rs232']['nak']):
            print('Device did not acknowledge command')
        else:
            print('Invalid response from device: 0x{}'.format(response.hex()))
    else:
        print('Invalid response from device')
    return False

def rs232_status(status):
    msg = rs232_build(config['rs232']['request'] + status)
    print('Requesting device status: 0x{}'.format(msg.hex()))

    try:
        uart.write(msg)
        time.sleep(0.1)
        response = uart.readline()
        print(response)
        if response == None or len(response) < 4:
            return False

        if response[0] != rs232_convert(config['rs232']['start']):
            return False

        id = response[1]
        if id < rs232_convert("0") or id > rs232_convert("9"):
            return False

        buffer = []
        for i in range(2, len(response)):
            if response[i] == config['rs232']['end']:
                break
            buffer.append(response[i])
        return buffer

    except Exception as e:
        print('Failed to request RS232 status {}{}'.format(type(e).__name__, e))

    return False

def blink_onboard_led(num_blinks):
    for i in range(num_blinks):
        led.on()
        time.sleep(.2)
        led.off()
        time.sleep(.2)

def connect_wlan(ssid, pw):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    # If you need to disable powersaving mode
    # wlan.config(pm = 0xa11140)

    # See the MAC address in the wireless chip OTP
    mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
    print('MAC Address: ' + mac)

    wlan.connect(ssid, pw)

    # Wait for connection with 10 second timeout
    timeout = 10
    while timeout > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        timeout -= 1
        print('Waiting for connection...')
        time.sleep(1)

    # Handle connection error
    # Error meanings
    # 0  Link Down
    # 1  Link Join
    # 2  Link NoIp
    # 3  Link Up
    # -1 Link Fail
    # -2 Link NoNet
    # -3 Link BadAuth

    wlan_status = wlan.status()
    blink_onboard_led(wlan_status)

    if wlan_status != 3:
        raise RuntimeError('Wi-Fi connection failed')
    else:
        print('Connected to Wireless Network')
        status = wlan.ifconfig()
        print('IP Address: ' + status[0])
        return wlan

wlan = connect_wlan(config['wlan']['ssid'], config['wlan']['pw'])

# Attempt to import or install umqtt
try:
    from umqtt.simple import MQTTClient
except ImportError as i:
    print('Installing MQTT Server')
    upip.install('umqtt.simple')
    try:
        from umqtt.simple import MQTTClient
    except Exception as e:
        print('Unable to install umqtt.simple from micropython.org')
        sys.print_exception(e)
        sys.exit()

print('Initializing MQTT Client and connecting to {} service.'.format(config['mqtt']['url']))
client = MQTTClient(
    client_id=bytes('client_' + config['mqtt']['client_id'], 'utf-8'),
    server=config['mqtt']['url'],
    user=config['mqtt']['user'],
    password=config['mqtt']['key'],
    keepalive=config['mqtt']['keepalive'],
    ssl=False
)
try:
    client.connect()
    print('Successfully connected to MQTT server')
except Exception as e:
    print('Could not connect to MQTT server')
    sys.print_exception(e)
    sys.exit()

def feed_callback(topic, msg):
    print('Received Data:  Topic = {}, Msg = {}'.format(topic, msg))
    received_data = str(msg, 'utf-8')
    if received_data == "1":
        led.value(0)
        rs232_command(config['rs232']['command']['power_off'])
    elif received_data == "2":
        led.value(1)
        rs232_command(config['rs232']['command']['power_on'])
    elif received_data == "3":
        led_prev = led.value()
        led.value(not led_prev)
        rs232_command(config['rs232']['command']['input_tv'])
        led.value(led_prev)
    elif received_data == "4":
        led_prev = led.value()
        led.value(not led_prev)
        rs232_command(config['rs232']['command']['input_cd'])
        led.value(led_prev)
    elif received_data == "5":
        led_prev = led.value()
        led.value(not led_prev)
        rs232_command(config['rs232']['command']['input_tape'])
        led.value(led_prev)
    elif received_data == "6":
        led_prev = led.value()
        led.value(not led_prev)
        rs232_command(config['rs232']['command']['volume_up'])
        led.value(led_prev)
    elif received_data == "7":
        led_prev = led.value()
        led.value(not led_prev)
        rs232_command(config['rs232']['command']['volume_down'])
        led.value(led_prev)

feed_endpoint = bytes('{:s}/feeds/{:s}'.format(config['mqtt']['user'], config['mqtt']['feed']), 'utf-8')
print('MQTT feed endpoint: {}'.format(str(feed_endpoint, 'utf-8')))
client.set_callback(feed_callback)
client.subscribe(feed_endpoint)

print('Subscribed and listening to MQTT feed')
while True:
    try:
        client.wait_msg()
    except Exception as e:
        print('Error encountered while handling MQTT message')
        sys.print_exception(e)

        print('Disconnecting from MQTT server')
        client.disconnect()
        break

print('Deinitializing program')
uart.deinit()
wlan.disconnect()
print('Attempting reset')
machine.reset()
