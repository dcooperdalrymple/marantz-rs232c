import board

config = {
    'wlan': {
        'ssid': 'WIFI_SSID',
        'pw': 'WIFI_PASSWORD'
        'timeout': 10 # in seconds, used with socket pool
    },

    'mqtt': {
        'url': 'SERVER_DOMAIN',
        'user': 'USERNAME',
        'key': 'PASSWORD_OR_KEY',
        'feed': 'SUBSCRIPTION_FEED',
        #'client_id': 'RANDOM',
        'ssl': False,
        #'port': 1883, # 8883 for SSL
        'keepalive': 300, # in seconds
        'timeout': 30, # in seconds, must be higher than socket timeout
        'message': {
            '1': 'power_off',
            '2': 'power_on',
            '3': 'input_tv',
            '4': 'input_cd',
            '5': 'input_tape',
            '6': 'volume_up',
            '7': 'volume_down'
        }
    },

    'uart': {
        'id': 1,
        'timeout': 2, # in seconds
        'pins': {
            'tx': board.GP4,
            'rx': board.GP5
        },
        'format': {
            'baudrate': 9600,
            'bits': 8,
            'parity': None,
            'stop': 1
        }
    },

    'rs232': {
        'start': '@',
        'id': '1',
        'end': 0x0D,
        'request': '?',
        'ack': 0x06,
        'nak': 0x15,
        'buffer_size': 32,
        'command': {
            'power': 'A0',
            'power_on': 'A1',
            'power_off': 'A2',
            'input_tv': 'B1',
            'input_cd': 'B9',
            'input_tape': 'BA',
            'volume_up': 'G0',
            'volume_down': 'G1'
        },
        "status": {
            'power': 'A',
            'video_input': 'B',
            'audio_input': 'C',
            'volumn': 'H'
        }
    }
}
