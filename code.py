import socketpool
import wifi
import time
import board
import busio
import digitalio
import binascii
import sys

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

def blink_onboard_led(num_blinks):
    for i in range(num_blinks):
        led.value = True
        time.sleep(0.2)
        led.value = False
        time.sleep(0.2)

try:
    import adafruit_minimqtt.adafruit_minimqtt as MQTT
except ImportError as e:
    print("Additional libraries must be installed before using device.")
    blink_onboard_led(2)
    raise e

try:
    from config import config
except ImportError as e:
    print("config.py file not provided. Please check your installation")
    blink_onboard_led(2)
    raise e

if config['mqtt']['ssl']:
    try:
        import ssl
    except ImportError as e:
        print("Unable to use SSL with installed CircuitPython firmware version")
        blink_onboard_led(2)
        raise e

uart = busio.UART(
    tx=config['uart']['pins']['tx'],
    rx=config['uart']['pins']['rx'],
    baudrate=config['uart']['format']['baudrate'],
    bits=config['uart']['format']['bits'],
    parity=config['uart']['format']['parity'],
    stop=config['uart']['format']['stop'],
    timeout=config['uart']['timeout']
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

def rs232_command(command):
    msg = rs232_build(command)
    print('Sending RS232C command: 0x{}'.format(binascii.hexlify(msg).decode()))

    respone = None
    try:
        uart.write(msg)
        time.sleep(0.1)
        response = uart.read(1)
    except Exception as e:
        print('Failed to send RS232 command {}{}'.format(type(e).__name__, e))
        #sys.print_exception(e)
        return False

    if response != None:
        if response[0] == rs232_convert(config['rs232']['ack']):
            return True
        elif response[0] == rs232_convert(config['rs232']['nak']):
            print('Device did not acknowledge command')
        else:
            print('Invalid response from device: 0x{}'.format(binascii.hexlify(response).decode()))
    else:
        print('Invalid response from device')
    return False

def rs232_status(status):
    msg = rs232_build(config['rs232']['request'] + status)
    print('Requesting device status: 0x{}'.format(binascii.hexlify(msg).decode()))

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

def connect_wlan(ssid, pw):
    # See the MAC address in the wireless chip OTP
    print('MAC Address: ' + binascii.hexlify(wifi.radio.mac_address,':').decode())

    # Attempt connection 3 times with second delay
    attempts = 3
    print('Connecting to WiFi AP')
    while attempts > 0:
        wifi.radio.connect(ssid, pw)
        if wifi.radio.enabled:
            break
        attempts -= 1
        if attempts > 0:
            print('Failed to connect')
            time.sleep(1)
            print('Re-attempting connection...')

    if not wifi.radio.enabled:
        blink_onboard_led(2)
        raise RuntimeError('Wi-Fi connection failed')

    print('Connected to Wireless Network')
    print('IP Address: ' + str(wifi.radio.ipv4_address))
    print('Hostname: ' + wifi.radio.hostname)

    return socketpool.SocketPool(wifi.radio)

pool = connect_wlan(config['wlan']['ssid'], config['wlan']['pw'])

def connect(mqtt_client, userdata, flags, rc):
    print('Successfully connected to MQTT broker')
    print("Flags: {0}\nRC: {1}".format(flags, rc))
def disconnect(mqtt_client, userdata, rc):
    print('Disconnected from MQTT broker')
def subscribe(mqtt_client, userdata, topic, granted_qos):
    print("Subscribed to {0} with QOS level {1}".format(topic, granted_qos))
def unsubscribe(mqtt_client, userdata, topic, pid):
    print("Unsubscribed from {0} with PID {1}".format(topic, pid))
def publish(mqtt_client, userdata, topic, pid):
    print("Published to {0} with PID {1}".format(topic, pid))

def message(mqtt_client, topic, message):
    led.value = True
    print('Received MQTT Data: Topic = {}, Message = {}'.format(topic, message))

    if not message in config['mqtt']['message']:
        print('Unknown message')
        led.value = False
        return

    command = config['mqtt']['message'][message]
    if not command in config['rs232']['command']:
        print('Unknown command')
        led.value = False
        return

    rs232_command(config['rs232']['command'][command])
    led.value = False

print('Initializing MQTT Client and connecting to {} service.'.format(config['mqtt']['url']))

ssl_context = None
client_port = 1883
if config['mqtt']['ssl']:
    ssl_context = ssl.create_default_context()
    client_port = 8883
if 'port' in config['mqtt']:
    client_port = config['mqtt']['port']

client_id = None
if 'client_id' in config['mqtt']:
    client_id = config['mqtt']['client_id']

client = MQTT.MQTT(
    broker=config['mqtt']['url'],
    port=client_port,
    client_id=client_id,
    username=config['mqtt']['user'],
    password=config['mqtt']['key'],
    keep_alive=config['mqtt']['keepalive'],
    recv_timeout=config['mqtt']['timeout'],
    socket_pool=pool,
    socket_timeout=config['wlan']['timeout'],
    connect_retries=5,
    is_ssl=config['mqtt']['ssl'],
    ssl_context=ssl_context
)

client.on_connect = connect
client.on_disconnect = disconnect
client.on_subscribe = subscribe
client.on_unsubscribe = unsubscribe
client.on_publish = publish
client.on_message = message

try:
    client.connect()
except MQTT.MMQTTException as e:
    print('Could not connect to MQTT server')
    blink_onboard_led(2)
    raise e

# Double check that we're connected
timeout = config['mqtt']['timeout']
while not client.is_connected() and timeout > 0:
    time.sleep(1)
    timeout-=1

feed_endpoint = '{:s}/feeds/{:s}'.format(config['mqtt']['user'], config['mqtt']['feed'])
print('Subscribing to MQTT feed endpoint: {}'.format(feed_endpoint))
try:
    client.subscribe(feed_endpoint)
except MQTT.MMQTTException as e:
    print('Could not subscribe to MQTT feed')
    blink_onboard_led(2)
    raise e

# Double check that we've subscribed
timeout = config['mqtt']['timeout']
while len(client._subscribed_topics) < 1 and timeout > 0:
    time.sleep(1)
    timeout-=1

# Indicate that the program has fully initialized
blink_onboard_led(3)

while True:
    try:
        client.loop()
    except (ValueError, RuntimeError, MQTT.MMQTTException) as e:
        if not client.is_connected():
            print('Error encountered while handling MQTT message')
            print('Reconnecting to MQTT broker')
            client.reconnect()
            continue
    time.sleep(1)

print('Deinitializing program')
uart.deinit()
client.disconnect()
wifi.radio.enabled = False

print('Attempting reset')
machine.reset()
