from format_data import FormatData


class DecodeSignedInt:
    def __init__(self, byte_vals, length=8):
        # splits the given bytes into pairs of 2 for each value encoded
        self.byte_vals = [byte_vals[i : i + 2] for i in range(0, length, 2)]

    @staticmethod
    def twos_comp(val, bits):
        # compute the 2's complement of int value val
        if (val & (1 << (bits - 1))) != 0:
            val = val - (1 << bits)
        return val

    @staticmethod
    def find_byte(data):
        # finds the full byte value by combining both byte values in
        # the pair, using little endian format
        first_byte = data[1] << 8
        full_byte = first_byte | data[0]

        return full_byte

    def decode(self):
        # finds the decoded 2's complement value for all of the byte values
        parsed_vals = [self.find_byte(byte_val) for byte_val in self.byte_vals]

        int_vals = [self.twos_comp(val, 16) for val in parsed_vals]

        return int_vals


class Decode1():
    def __init__(self, byte_vals):
        # inits the byte vals
        self.byte_vals = byte_vals

    def values(self):
        return {
            "Pack Inst Voltage": self.byte_vals[0] << 8 | self.byte_vals[1],
            "Pack Current": self.byte_vals[2] << 8 | self.byte_vals[3],
            "Pack Amphours": self.byte_vals[4] << 8 | self.byte_vals[5],
            "Pack SOC": self.byte_vals[6],
            "Pack Health": self.byte_vals[7],
        }


class Decode2():
    def __init__(self, byte_vals):
        # inits the byte vals
        self.byte_vals = byte_vals

    def values(self):
        return {
            "Failsafe Statuses": "{:08b}".format(self.byte_vals[0]),
            "DTC Status 1": "{:08b}".format(self.byte_vals[1]),
            "DTC Status 2": "{:016b}".format(self.byte_vals[2] << 8 | self.byte_vals[3]),
            "Current Limits Status": "{:016b}".format(self.byte_vals[4] << 8 | self.byte_vals[5]),
            "Average Temp": DecodeSignedInt.twos_comp(self.byte_vals[6], 8),
            "Internal Temp": DecodeSignedInt.twos_comp(self.byte_vals[7], 8),
        }


class Decode3():
    def __init__(self, byte_vals):
        # inits the byte vals
        self.byte_vals = byte_vals

    def values(self):
        return {
            "MPE State": self.byte_vals[0]
        }


class Decode4():
    def __init__(self, byte_vals):
        # inits the byte vals
        self.byte_vals = byte_vals

    def values(self):
        return {
            "High Cell Voltage": self.byte_vals[0] << 8 | self.byte_vals[1],
            "High Cell Voltage ID": self.byte_vals[2],
            "Low Cell Voltage": self.byte_vals[3] << 8 | self.byte_vals[4],
            "Low Cell Voltage ID": self.byte_vals[5],
            "Average Cell Voltage": self.byte_vals[6] << 8 | self.byte_vals[7],
        }


class Decode5(DecodeSignedInt):  # Temps (IGBT modules, Gate Driver Board)
    def __init__(self, byte_vals):
        super().__init__(byte_vals)

    def values(self):
        module_a, module_b, module_c, gate_driver_board = [
            FormatData.temperature(val) for val in self.decode()
        ]

        return {
            "Module A Temperature": module_a,
            "Module B Temperature": module_b,
            "Module C Temperature": module_c,
            "Gate Driver Board Temperature": gate_driver_board,
        }


class Decode6(DecodeSignedInt):  # Temps (Control Board, RTD #1-3)
    def __init__(self, byte_vals):
        super().__init__(byte_vals)

    def values(self):
        vals = self.decode()

        control_board, rtd_1, rtd_2, rtd_3 = [
            FormatData.temperature(val) for val in vals
        ]

        return {
            "Control Board Temperature": control_board,
            "RTD #1 Temperature": rtd_1,
            "RTD #2 Temperature": rtd_2,
            "RTD #3 Temperature": rtd_3,
        }


class Decode7(DecodeSignedInt):  # Temps (RTD #4-5, Motor), Torque Shudder
    def __init__(self, byte_vals):
        super().__init__(byte_vals)

    def values(self):
        vals = self.decode()

        rtd_4, rtd_5, motor = [FormatData.temperature(val) for val in vals[:3]]
        torque_shudder = FormatData.torque(vals[3])

        return {
            "RTD #4 Temperature": rtd_4,
            "RTD #5 Temperature": rtd_5,
            "Motor Temperature": motor,
            "Torque Shudder": torque_shudder,
        }


class Decode8(DecodeSignedInt):  # Motor angle, speed, frequency
    def __init__(self, byte_vals):
        super().__init__(byte_vals)

    def values(self):
        vals = self.decode()

        motor_angle = FormatData.angle(vals[0])
        motor_speed = FormatData.angular_velocity(vals[1])
        elec_output_freq = FormatData.frequency(vals[2])
        del_res_filt = FormatData.angle(vals[3])

        return {
            "Motor Angle (Electrical)": motor_angle,
            "Motor Speed": motor_speed,
            "Electrical Output Frequency": elec_output_freq,
            "Delta Resolver Filtered": del_res_filt,
        }


class Decode9(DecodeSignedInt):  # Currents (3 Phases, DC Bus)
    def __init__(self, byte_vals):
        super().__init__(byte_vals)

    def values(self):
        vals = self.decode()

        phase_a, phase_b, phase_c, dc_bus = [FormatData.current(val) for val in vals]

        return {
            "Phase A Current": phase_a,
            "Phase B Current": phase_b,
            "Phase C Current": phase_c,
            "DC Bus Current": dc_bus,
        }


class Decode10(DecodeSignedInt):  # Voltages (DC Bus, Output)
    def __init__(self, byte_vals):
        super().__init__(byte_vals)

    def values(self):
        vals = self.decode()

        dc_bus, output, vab_vd, vbc_vq = [FormatData.high_voltage(val) for val in vals]

        return {
            "DC Bus Voltage": dc_bus,
            "Output Voltage": output,
            "VAB_Vd Voltage": vab_vd,
            "VBC_Vq Voltage": vbc_vq,
        }


class Decode11:  # Internal States
    def __init__(self, byte_vals):
        # converts all bytes into the equivalent 8 bit binary values
        self.byte_vals = ["{:08b}".format(i) for i in byte_vals]

    def values(self):
        # The byte values can be manually reviewed with the documentation
        # in case any information is needed, so no decoding is needed
        return {
            "VSM State": int(self.byte_vals[1]) << 8 | int(self.byte_vals[0]),
            "Inverter State": self.byte_vals[2],
            "Relay State": self.byte_vals[3],
            "Inverter Run Mode": self.byte_vals[4][0],
            "Inverter Active Discharge State": self.byte_vals[4][5:],
            "Inverter Command Mode": self.byte_vals[5],
            "Inverter Enable State": self.byte_vals[6][0],
            "Inverter Enable Lockout": self.byte_vals[6][7],
            "Direction Command": self.byte_vals[7][0],
            "BMS Active": self.byte_vals[7][1],
            "BMS Limiting Torque": self.byte_vals[7][2],
        }


class Decode12:  # Fault Codes
    def __init__(self, byte_vals):
        # converts all bytes into the equivalent 16 bit binary values
        self.byte_vals = [
            "{:016b}".format(byte_vals[i+1] << 8 | byte_vals[i])
            for i in range(0, 8, 2)
        ]

    def values(self):
        # The byte values can be manually reviewed with the documentation
        # in case any information is needed, so no decoding is needed
        return {
            "POST Fault Lo": self.byte_vals[0],
            "POST Fault Hi": self.byte_vals[1],
            "Run Fault Lo": self.byte_vals[2],
            "Run Fault Hi": self.byte_vals[3],
        }


class Decode13(DecodeSignedInt):  # Torque and Timer
    def __init__(self, byte_vals):
        self.byte_vals = [byte_vals[i : i + 2] for i in range(0, 4, 2)]
        self.timer_bytes = byte_vals[4:]

    def find_timer_byte(self):
        first_byte = self.timer_bytes[3] << 24
        second_byte = self.timer_bytes[2] << 16
        third_byte = self.timer_bytes[1] << 8
        full_byte = first_byte | second_byte | third_byte | self.timer_bytes[0]

        return full_byte

    def values(self):
        vals = self.decode()
        timer_val = self.find_timer_byte()

        commanded_torque, torque_feedback = [FormatData.torque(val) for val in vals]
        timer_sec = FormatData.timer(timer_val)

        return {
            "Commanded Torque": commanded_torque,
            "Torque Feedback": torque_feedback,
            "Power on Timer": timer_sec,
        }

class Decode14(): # Current limits
    def __init__(self, byte_vals):
        self.byte_vals = byte_vals

    def values(self):
        return {
            "Pack DCL": self.byte_vals[0] << 8 | self.byte_vals[1],
            "Pack CCL": self.byte_vals[3] << 8 | self.byte_vals[2],
        }

class Decode15(DecodeSignedInt): # nerduino accelerometer
    def __init__(self, byte_vals):
        super().__init__(byte_vals, 6)

    def values(self):
        vals = self.decode()

        return {
            "X-Axis": vals[0],
            "Y-Axis": vals[1],
            "Z-Axis": vals[2],
        }

class Decode16(): # nerduino humidity
    def __init__(self, byte_vals):
        self.byte_vals = byte_vals

    def values(self):
        temp = self.byte_vals[1] << 8 | self.byte_vals[0]
        humid = self.byte_vals[3] << 8 | self.byte_vals[2]

        tempF = -49 + (315 * temp / 65535.0)
        tempC = -45 + (175 * temp / 65535.0)
        relHumid = 100 * humid / 65535.0

        return {
            "Temp C": tempC,
            "Temp F": tempF,
            "Relative Humidity": relHumid,
        }