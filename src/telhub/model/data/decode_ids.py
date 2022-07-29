# This file specifies the CAN and data ID mappings. Each piece of data stored in the database has a local
# "DATA ID", which is seperate from the vehicles "CAN ID". This allows us to change the CAN ID on the car
# and keep the DATA ID the same in our system.

from decode import *

# Defines a mapping of CAN ID to DATA ID
DECODE_IDS = {
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "160": 5,
    "161": 6,
    "162": 7,
    "165": 8,
    "166": 9,
    "167": 10,
    "170": 11,
    "171": 12,
    "172": 13,
    "514": 14,
    "768": 15,
    "769": 16
}

# Defines the supported DATA IDs in our system with their associated name and processing class
# Import this dictionary to get access to processing any message (with the values() method)
DATA_IDS = {
    1: {
        "device": "accumulator status",
        "decode_class": Decode1,
    },
    2: {
        "device": "BMS status",
        "decode_class": Decode2,
    },
    3: {
        "device": "shutdown control",
        "decode_class": Decode3,
    },
    4: {
        "device": "cell data",
        "decode_class": Decode4,
    },
    5: {
        "device": "temperatures (igbt modules, gate driver board)",
        "decode_class": Decode5,
    },
    6: {
        "device": "temperatures (control board)",
        "decode_class": Decode6,
    },
    7: {
        "device": "temperatures (motor)",
        "decode_class": Decode7,
    },
    8: {
        "device": "motor position information",
        "decode_class": Decode8,
    },
    9: {
        "device": "current information",
        "decode_class": Decode9,
    },
    10: {
        "device": "voltage information",
        "decode_class": Decode10,
    },
    11: {
        "device": "internal states",
        "decode_class": Decode11,
    },
    12: {
        "device": "fault codes",
        "decode_class": Decode12,
    },
    13: {
        "device": "torque and timer",
        "decode_class": Decode13,
    },
    14: {
        "device": "current limits",
        "decode_class": Decode14,
    },
    15: {
        "device": "nerduino accelerometer",
        "decode_class": Decode15,
    },
    16: {
        "decode": "nerduino humidity",
        "decode_class": Decode16,
    }
}
