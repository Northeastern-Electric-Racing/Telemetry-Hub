from model.data.data import ProcessData as pd, FormatData as fd
from typing import Any, Dict, List


def decode1(data: List[int]) -> Dict[int, Any]:
    return {
        1: pd.big_endian(data[0:2]),
        2: pd.big_endian(data[2:4]),
        3: pd.big_endian(data[4:6]),
        4: data[6],
        5: data[7]
    }

def decode2(data: List[int]) -> Dict[int, Any]:
    return {
        6: "{:08b}".format(data[0]),
        7: "{:08b}".format(data[1]),
        8: "{:016b}".format(pd.big_endian(data[2:4])),
        9: "{:016b}".format(pd.big_endian(data[4:6])),
        10: pd.twos_comp(data[6], 8),
        11: pd.twos_comp(data[7], 8)
    }

def decode3(data: List[int]) -> Dict[int, Any]:
    return {
        12: data[0]
    }

def decode4(data: List[int]) -> Dict[int, Any]:
    return {
        13: pd.big_endian(data[0:2]),
        14: data[2],
        15: pd.big_endian(data[3:5]),
        16: data[5],
        17: pd.big_endian(data[6:8])
    }

def decode5(data: List[int]) -> Dict[int, Any]:
    decoded_data = pd.default_decode(data)
    final_data = [fd.temperature(d) for d in decoded_data]
    return {
        18: final_data[0],
        19: final_data[1],
        20: final_data[2],
        21: final_data[3]
    }

def decode6(data: List[int]) -> Dict[int, Any]:
    decoded_data = pd.default_decode(data)
    final_data = [fd.temperature(d) for d in decoded_data]
    return {
        22: final_data[0],
        23: final_data[1],
        24: final_data[2],
        25: final_data[3]
    }

def decode7(data: List[int]) -> Dict[int, Any]:
    decoded_data = pd.default_decode(data)
    final_data = [fd.temperature(d) for d in decoded_data[:3]]
    return {
        26: final_data[0],
        27: final_data[1],
        28: final_data[2],
        29: fd.torque(decoded_data[3])
    }

def decode8(data: List[int]) -> Dict[int, Any]:
    decoded_data = pd.default_decode(data)
    return {
        30: fd.angle(decoded_data[0]),
        31: fd.angular_velocity(decoded_data[1]),
        32: fd.frequency(decoded_data[2]),
        33: fd.angle(decoded_data[3])
    }

def decode9(data: List[int]) -> Dict[int, Any]:
    decoded_data = pd.default_decode(data)
    final_data = [fd.current(d) for d in decoded_data]
    return {
        34: final_data[0],
        35: final_data[1],
        36: final_data[2],
        37: final_data[3]
    }

def decode10(data: List[int]) -> Dict[int, Any]:
    decoded_data = pd.default_decode(data)
    final_data = [fd.high_voltage(d) for d in decoded_data]
    return {
        38: final_data[0],
        39: final_data[1],
        40: final_data[2],
        41: final_data[3]
    }

def decode11(data: List[int]) -> Dict[int, Any]:
    decoded_data = ["{:08b}".format(d) for d in data]
    return {
        42: decoded_data[0] + decoded_data[1],
        43: decoded_data[2],
        44: decoded_data[3],
        45: decoded_data[4][0],
        46: decoded_data[4][5:],
        47: decoded_data[5],
        48: decoded_data[6][0],
        49: decoded_data[6][7],
        50: decoded_data[7][0],
        51: decoded_data[7][1],
        52: decoded_data[7][2]
    }

def decode12(data: List[int]) -> Dict[int, Any]:
    grouped_data = pd.big_endian(pd.group_bytes(data))
    decoded_data = ["{:016b}".format(d) for d in grouped_data]
    return {
        53: decoded_data[0],
        54: decoded_data[1],
        55: decoded_data[2],
        56: decoded_data[3]
    }

def decode13(data: List[int]) -> Dict[int, Any]:
    decoded_data = pd.default_decode(data[:4])
    timer_data = pd.little_endian(data[4:])
    return {
        57: fd.torque(decoded_data[0]),
        58: fd.torque(decoded_data[1]),
        59: fd.timer(timer_data)
    }

def decode14(data: List[int]) -> Dict[int, Any]:
    return {
        60: pd.little_endian(data[0:2]),
        61: pd.little_endian(data[2:4])
    }

def decode15(data: List[int]) -> Dict[int, Any]:
    decoded_data = pd.default_decode(data)
    return {
        62: decoded_data[0],
        63: decoded_data[1],
        64: decoded_data[2]
    }

def decode16(data: List[int]) -> Dict[int, Any]:
    temp = pd.little_endian(data[0:2])
    humid = pd.little_endian(data[2:4])
    tempF = -49 + (315 * temp / 65535.0)
    tempC = -45 + (175 * temp / 65535.0)
    relHumid = 100 * humid / 65535.0 
    return {
        65: tempC,
        66: tempF,
        67: relHumid
    }

def decode17(data: List[int]) -> Dict[int, Any]:
    decoded_data = pd.default_decode(data)

    return {
        68: fd.torque(decoded_data[0]),
        69: fd.angular_velocity(decoded_data[1]),
        70: data[4],
        71: data[5] & 1,
        72: (data[5] >> 1) & 1,
        73: (data[5] >> 2) & 1,
        74: fd.torque(decoded_data[3])
    }