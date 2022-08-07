"""
This file specifes the CAN and data ID mappings. There are three levels of IDs specified:
    - External Message ID (actual CAN message id)
    - Internal Message ID (internal id for messages to allow easier changing of external ids)
    - Data ID (id for individual data values contained in the messages)
"""

from model.data.decode import *

# Mapping from external to internal message IDs
MESSAGE_IDS = {
    1: 1,
    2: 2,
    3: 3,
    4: 4,
    160: 5,
    161: 6,
    162: 7,
    165: 8,
    166: 9,
    167: 10,
    170: 11,
    171: 12,
    172: 13,
    514: 14,
    768: 15,
    769: 16,
    192: 17
}


# Mapping from internal message IDs to information used to decode the message
DECODE_DATA = {
    1: {
        "description": "accumulator status",
        "decoder": decode1
    },
    2: {
        "description": "BMS status",
        "decoder": decode2
    },
    3: {
        "description": "shutdown control",
        "decoder": decode3
    },
    4: {
        "description": "cell data",
        "decoder": decode4
    },
    5: {
        "description": "temperatures (igbt modules, gate driver board)",
        "decoder": decode5
    },
    6: {
        "description": "temperatures (control board)",
        "decoder": decode6,
    },
    7: {
        "description": "temperatures (motor)",
        "decoder": decode7,
    },
    8: {
        "description": "motor position information",
        "decoder": decode8,
    },
    9: {
        "description": "current information",
        "decoder": decode9,
    },
    10: {
        "description": "voltage information",
        "decode_class": decode10,
    },
    11: {
        "description": "internal states",
        "decoder": decode11,
    },
    12: {
        "description": "fault codes",
        "decoder": decode12,
    },
    13: {
        "description": "torque and timer",
        "decoder": decode13,
    },
    14: {
        "description": "current limits",
        "decoder": decode14,
    },
    15: {
        "description": "nerduino accelerometer",
        "decoder": decode15,
    },
    16: {
        "description": "nerduino humidity",
        "decoder": decode16,
    },
    17: {
        "description": "commanded data",
        "decoder": decode17
    }
}

# Mapping from data ids to their description (potentially add format information)
DATA_IDS = {
    1: "Pack Inst Voltage",
    2: "Pack Current",
    3: "Pack Amphours",
    4: "Pack SOC",
    5: "Pack Health",
    6: "Failsafe Statuses",
    6: "DTC Status 1",
    6: "DTC Status 2",
    6: "Current Limits Status",
    6: "Average Temp",
    6: "Internal Temp",
    6: "MPE State",
    6: "High Cell Voltage",
    6: "High Cell Voltage ID",
    6: "Low Cell Voltage",
    6: "Low Cell Voltage ID",
    6: "Average Cell Voltage",
    6: "Module A Temperature",
    6: "Module B Temperature",
    6: "Module C Temperature",
    6: "Gate Driver Board Temperature",
    6: "Control Board Temperature",
    6: "RTD #1 Temperature",
    6: "RTD #2 Temperature",
    6: "RTD #3 Temperature",
    6: "RTD #4 Temperature",
    6: "RTD #5 Temperature",
    6: "Motor Temperature",
    6: "Torque Shudder",
    6: "Motor Angle (Electrical)",
    6: "Motor Speed",
    6: "Electrical Output Frequency",
    6: "Delta Resolver Filtered",
    6: "Phase A Current",
    6: "Phase B Current",
    6: "Phase C Current",
    6: "DC Bus Current",
    6: "DC Bus Voltage",
    6: "Output Voltage",
    6: "VAB_Vd Voltage",
    6: "VAB_Vq Voltage",
    1: "VSM State",
    1: "Inverter State",
    1: "Relay State",
    1: "Inverter Run Mode",
    1: "Inverter Active Discharge State",
    1: "Inverter Command Mode",
    1: "Inverter Enable State",
    1: "Inverter Enable Lockout",
    1: "Direction Command",
    1: "BMS Active",
    1: "BMS Limiting Torque",
    6: "POST Fault Lo",
    6: "POST Fault Hi",
    6: "Run Fault Lo",
    6: "Run Fault Hi",
    6: "Commanded Torque",
    6: "Torque Feedback",
    6: "Power on Timer",
    6: "Pack DCL",
    6: "Pack CCL",
    6: "TCU X-Axis Acceleration",
    6: "TCU Y-Axis Acceleration",
    6: "TCU Z-Axis Acceleration",
    6: "TCU Temperature C",
    6: "TCU Temperature F",
    6: "Relative Humidity",
    6: "Torque Command",
    6: "Speed Command",
    6: "Direction Command",
    6: "Inverter Enable",
    6: "Inverter Discharge",
    6: "Speed Mode Enable",
    6: "Commanded Torque Limit"
}

