# Gets the time value in seconds of a string time ("YYYY-MM-DDT00:00:00.000Z") 
#   - only uses the hour, minutes, seconds, and milliseconds fields
#   - useful for graphing with time on the x axis in excel
#   - returns a double time in seconds (decimals go to millisecond precision)
def getDoubleTime(string_time):
    hour =   int(string_time[11:13])
    minute = int(string_time[14:16])
    sec =    int(string_time[17:19])
    milli =  int(string_time[20:23])

    return (hour * 3600) + (minute * 60) + (sec * 1) + (milli * 0.001)


# Processes the data bytes of a CAN message to remove brackets and commas
# Transforms input of "[1,1,1,1,1,1,1,1]" into a list of 8 ones
def process_data_bytes(data_bytes):
    data_bytes = data_bytes[1:-1] # remove brackets at start and end
    seperated = data_bytes.split(",")
    return [int(x) for x in seperated]