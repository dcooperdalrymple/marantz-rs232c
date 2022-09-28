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
        'feed': 'SUBSCRIPTION_FEED',
        'keepalive': 300
    },

    'uart': {
        'id': 1,
        'timeout': 2000,
        'pins': {
            'tx': 4,
            'rx': 5,
            'rts': 7,
            'cts': 6
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
