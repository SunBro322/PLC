import snap7

# Main Class
class PLC:
    def __init__(self, IP, RACK):
        self.IP = IP
        self.RACK = RACK
        self.SLOT = 2
        self.PLC = snap7.client.Client()
        self.state = ''
        self.cpustate = ''

    def ConnectToPLC(self): # Connecting to PLC
        self.state = self.PLC.get_connected()
        self.cpustate = self.PLC.get_cpu_state()
        if not self.state:
            self.PLC.connect(self.IP, self.RACK, self.SLOT)

    def DisconncetToPLC(self): # Disconnecting
        self.state = self.PLC.get_connected()
        self.cpustate = self.PLC.get_cpu_state() # Getting CPU status
        self.PLC.disconnect()

    def ReadFrom(self, DB_NUMBER, START_ADRESS, SIZE, COUNT): # Read analog value from PLC
        self.DB_NUMBER = DB_NUMBER
        self.START_ADRESS = START_ADRESS
        self.SIZE = SIZE
        self.COUNT = COUNT
        db = self.PLC.db_read(DB_NUMBER, START_ADRESS, SIZE)
        RealResult = snap7.util.get_real(db, COUNT)
        return RealResult

    def ReadFrom_Bool(self, DB_NUMBER, START_ADRESS, SIZE, byte, bool): # Read bool value from PLC
        self.DB_NUMBER = DB_NUMBER
        self.START_ADRESS = START_ADRESS
        self.SIZE = SIZE
        self.byte = byte
        self.bool = bool
        db = self.PLC.db_read(DB_NUMBER, START_ADRESS, SIZE)
        BoolResult = snap7.util.get_bool(db, byte, bool)
        return BoolResult