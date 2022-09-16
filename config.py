config = {
    'country': 'COUNTRY_CODE',
    'timezone' : "VALID_TIMEZONE",

    'wlan': {
        'ssid': 'WIFI_SSID',
        'pw': 'WIFI_PASSWORD'
    },

    'mqtt': {
        'client_id': 'RANDOM',
        'url': 'SERVER_DOMAIN',
        'user': 'USERNAME',
        'key': 'PASSWORD_OR_KEY',
        'feed': 'SUBSCRIPTION_FEED'
    },

    'uart': {
        'id': 0,
        'timeout': 2,
        'pins': {
            'tx': 0,
            'rx': 1,
            'rts': 3,
            'cts': 2
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
            'input_tape': 'BA'
        },
        "status": {
            'power': 'A',
            'video_input': 'B',
            'audio_input': 'C',
            'volumn': 'H'
        }
    }
}
