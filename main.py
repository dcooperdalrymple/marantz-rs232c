import rp2
from machine import Pin
import network
import ubinascii
import time
import upip
import sys
from config import config

rp2.country(config['country'])
led = Pin('LED', Pin.OUT)

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
    print('mac = ' + mac)

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
        print('Connected')
        status = wlan.ifconfig()
        print('ip = ' + status[0])
        return wlan

wlan = connect_wlan(config['wlan']['ssid'], config['wlan']['pw'])

# Attempt to install umqtt
print('Installing MQTT Server')
upip.install('umqtt.simple')
#upip.install('umqtt.robust')
try:
    #from umqtt.robust import MQTTClient
    from umqtt.simple import MQTTClient
except Exception as e:
    print('Unable to install umqtt.simple from micropython.org {}{}'.format(type(e).__name__, e))
    sys.exit()

print('Initializing MQTT Client and connecting to {} service.'.format(config['mqtt']['url']))
client = MQTTClient(
    client_id=bytes('client_' + config['mqtt']['client_id'], 'utf-8'),
    server=config['mqtt']['url'],
    user=config['mqtt']['user'],
    password=config['mqtt']['key'],
    keepalive=0,
    ssl=False
)
try:
    client.connect()
    print('Successfully connected to MQTT server')
except Exception as e:
    print('could not connect to MQTT server {}{}'.format(type(e).__name__, e))
    sys.exit()

def feed_callback(topic, msg):
    print('Received Data:  Topic = {}, Msg = {}'.format(topic, msg))
    recieved_data = str(msg,'utf-8')            #   Recieving Data
    if recieved_data=="0":
        led.value(0)
    if recieved_data=="1":
        led.value(1)

feed_endpoint = bytes('{:s}/feeds/{:s}'.format(config['mqtt']['user'], config['mqtt']['feed']), 'utf-8')
print('MQTT feed endpoint: {}'.format(str(feed_endpoint, 'utf-8')))
client.set_callback(feed_callback)
client.subscribe(feed_endpoint)

print('Subscribed and listening to MQTT feed')
while True:
    try:
        client.check_msg()
    except:
        print('Disconnecting from MQTT server')
        client.disconnect()
        print('Exiting from program')
        sys.exit()
