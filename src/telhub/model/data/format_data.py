class FormatData:
    # Provides methods to correctly scale the data to the actual value
    # based on its type/range

    @staticmethod
    def temperature(value):
        return value / 10

    @staticmethod
    def torque(value):
        return value / 10

    @staticmethod
    def angle(value):
        return value / 10

    @staticmethod
    def frequency(value):
        return value / 10

    @staticmethod
    def angular_velocity(value):
        return value

    @staticmethod
    def current(value):
        return value / 10

    @staticmethod
    def high_voltage(value):
        return value / 10

    @staticmethod
    def timer(value):
        return value * 0.003
