from re import findall
from telnetlib import Telnet
from time import sleep


class SEL300:
    """Access any SEL 300 series device using a telnet connection"""
    def __init__(self, ip: str, password1: str='OTTER', password2: str='TAIL', port: int=23, level2: bool=False):
        self.ip = ip
        self.tn = None
        try:
            self.tn = Telnet(ip, port, timeout=10)
            self.tn.write(b'ACC\r\n')
            self.tn.read_until(b'Password: ?')
            self.tn.write((password1 + '\r\n').encode('utf-8'))
            self.tn.read_until(b'=>')
            if level2:
                self.tn.write(b'2AC\r\n')
                self.tn.read_until(b'Password: ?')
                self.tn.write((password2 + '\r\n').encode('utf-8'))
                self.tn.read_until(b'=>>')
        except TimeoutError:
            print('Connection timed out. Check your connection and try again.')

    """ ######## METHODS LEVEL 1 ######## """

    def read_wordbit(self, module: str, wordbit: str):
        """Read any configurable wordbit from the IED"""
        if not self.tn:
            return "Device not connected"

        command = f'FIL SHO {module}.TXT'
        self.tn.write((command + '\r\n').encode('utf-8'))
        reading_expect = self.tn.expect([b'=>>', b'=>'])
        reading = reading_expect[2].decode('utf-8')
        reading2 = reading.split('\n')

        # Detect the module
        module_index_start = module.find('_')
        module_name = module[module_index_start+1:]
        module_index_str = "[" + module_name + "]\r"
        module_index_int = reading2.index(module_index_str)

        reading3 = reading2[module_index_int+1:]

        # Build the Dictionarie
        wordbits_dict = {}
        for item in reading3:
            if ',' in item:
                key, value = item.strip().replace('\r', '').split(',', 1)
                value = value.strip('"')
                wordbits_dict[key] = value
        try:
            return wordbits_dict[wordbit]
        except KeyError:
            return "Wordbit not found"

    def read_firmware(self):
        """Read the IED Firmware"""
        if not self.tn:
            return "Device not connected"

        self.tn.write(b'ID\r\n')
        reading = self.tn.read_until(b'=>', timeout=5).decode('utf-8')
        fid_text = reading.find('FID=')
        first_caracter = fid_text + 4
        last_caracter = reading.find('"', fid_text + 4)

        return reading[first_caracter:last_caracter]

    def read_partnumber(self):
        """Read the IED Part Number"""
        if not self.tn:
            return "Device not connected"

        self.tn.write(b'ID\r\n')
        reading_expect = self.tn.expect([b'=>>', b'=>'])
        reading = reading_expect[2].decode('utf-8')
        text_source = reading.find('PARTNO=')
        reading2 = reading[text_source::]
        reading3 = reading2.split('=')
        reading4 = reading3[1].split('\r\n')
        reading5 = reading4[0].replace(' ', '').replace('"', '')
        final_reading = reading5.split(',')

        return final_reading[0]

    def read_serialnumber(self):
        """Read the IED Serial Number"""
        if not self.tn:
            return "Device not connected"

        self.tn.write(b'ID\r\n')
        reading_expect = self.tn.expect([b'=>>', b'=>'])
        reading = reading_expect[2].decode('utf-8')
        text_source = reading.find('SERIALNO=')
        reading2 = reading[text_source::]
        reading3 = reading2.split('=')
        reading4 = reading3[1].split('\r\n')
        reading5 = reading4[0].split(',')
        final_reading = reading5[0].replace('"', '')

        return final_reading

    def read_dnppoint(self, data_type: str, position: int):
        """
        Read a specific point from DNP Map
        Specify the data type of the point:
        BI = Binary Inputs
        AI = Analog Inputs
        BO = Binary Outputs
        """
        if position < 10:  # Add zero on the left if the position is smaller than 10
            point_position2string = '00' + str(position)
        else:
            point_position2string = '0' + str(position)

        command = f'FIL SHO SET_D1.TXT'
        self.tn.write((command + '\r\n').encode('utf-8'))
        reading = self.tn.read_until(b'=>', timeout=5).decode('utf-8')
        reading2 = reading.split('\r\n')

        for line in reading2:
            if f'{data_type}_{point_position2string}' in line:
                reading3 = line.split(',')
                final_reading = reading3[1].strip('"')
                return final_reading

        return 'Method failed. Check the input parameters'

    def read_dnpmap(self):
        """Return a dictionary of the DNP Map of the specified data type"""
        self.tn.write(b'FIL SHO SET_D1.TXT\r\n')
        reading = self.tn.read_until(b'=>', timeout=5).decode('utf-8')
        text_source = reading.find('[D1]')
        reading2 = reading[text_source::]
        reading3 = reading2.split('\r\n')
        reading3.pop(0)

        final_reading = {}
        for line in reading3:
            try:
                point, wordbit_comma = line.split(',')
                wordbit = wordbit_comma.replace('"', '')
                final_reading[point] = wordbit
            except ValueError:
                pass
        return final_reading

    def read_ser(self, lines: int=1024):
        """Read the IEDs SER. Enter the number of lines if you wish to view a limited quantity of records"""
        command = f'SER {lines}\r\n'
        self.tn.write(command.encode('utf-8'))
        reading = (self.tn.read_until(b'=>')).decode('utf-8')
        reading2 = reading.strip().split('\n')
        list_lines = []

        for ser_lines in reading2[6:-2]:
            if ser_lines.strip():
                list_lines.append(ser_lines)

        final_ser = "\n".join(list_lines)
        return final_ser

    def clear_ser(self):
        """Clear the IEDs SER"""
        self.tn.write(b'SER C\r\n')
        self.tn.read_until(b'Are you sure (Y/N)?')
        self.tn.write(b'Y\r\n')
        sleep(1)
        print('SER Clearing Complete')

    def save_ser(self, lines: int=1024, filename: str='SER_saved'):
        ser_reading = self.read_ser(lines)
        ser_cleaned = "\n".join(line.strip() for line in ser_reading.splitlines())

        with open(filename+'.txt', "w", encoding="utf-8") as file:
            file.write(ser_cleaned + '\n')

        print(f'SER saved successfully as {filename}.txt')


    """ ######## METHODS LEVEL 2 ######## """

    def open_breaker(self):
        """Run the OPEN Command"""
        if not self.tn:
            print("Device not connected")
            return

        self.tn.write(b'OPEN\r\n')
        self.tn.read_until(b'Open Breaker  (Y/N)?')
        self.tn.write(b'Y\r\n')
        sleep(1)
        self.tn.read_until(b'Are you sure (Y/N)?')
        self.tn.write(b'Y\r\n')
        sleep(1)
        print('Open Command executed')
        self.tn.read_until(b'=>>')

    def close_breaker(self):
        """Run the CLOSE Command"""
        if not self.tn:
            print("Device not connected")
            return

        self.tn.write(b'CLOSE\r\n')
        self.tn.read_until(b'Close Breaker  (Y/N)?')
        self.tn.write(b'Y\r\n')
        sleep(1)
        self.tn.read_until(b'Are you sure (Y/N)?')
        self.tn.write(b'Y\r\n')
        sleep(1)
        print('Close Command executed')
        self.tn.read_until(b'=>>')

    def pulse_rb(self, remote_bit: str):
        """Pulses a specific Remote Bit"""
        rb_number = remote_bit.replace('RB', '')

        command = f'CON {rb_number}'
        self.tn.write((command + '\r\n').encode('utf-8'))

        expect_text = f'CONTROL {remote_bit}: '
        x = self.tn.read_until(expect_text.encode('utf-8'))

        final_command = f'PRB {rb_number}'
        self.tn.write((final_command + '\r\n').encode('utf-8'))

        sleep(1)
        self.tn.close()
        self.__init__(self.ip, level2=True)
