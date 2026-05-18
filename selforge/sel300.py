from telnetlib import Telnet
from time import sleep
from .ftp import SELFTP
from typing import Literal


class CredentialError(Exception):
    pass

class SEL300:
    """Access any SEL 300 series device using a telnet connection"""
    def __init__(self, ip: str, password1: str='OTTER', password2: str='TAIL', port: int=23, level2: bool=False):
        self.ip = ip
        self.port = port
        self.tn = None
        self.password1 = password1
        self.password2 = password2
        self.level2 = level2

        self.connect()  # Start connection

    def connect(self):
        """Start the connection to the SEL relay"""
        try:
            self.tn = Telnet(self.ip, self.port, timeout=5)
            self._authenticate()
        except TimeoutError:
            print(f'\033[31m{self.ip}: Connection Timed out. [Log ID:1]\033[0m')

    def _authenticate(self):
        """Authenticate to the SEL relay"""
        try:
            # Level 1 Connection
            self.tn.write(b'ACC\r\n')
            self.tn.read_until(b'Password: ?')
            self.tn.write((self.password1 + '\r\n').encode('utf-8'))
            password1_response = self.tn.read_until(b'=>', timeout=5)
            if b'=>' not in password1_response:
                raise CredentialError()

            if self.level2:  # If level2 is True (Required to use level 2 methods), ask for the level 2 password
                self.tn.write(b'2AC\r\n')
                self.tn.read_until(b'Password: ?')
                self.tn.write((self.password2 + '\r\n').encode('utf-8'))
                password2_response = self.tn.read_until(b'=>>', timeout=5)

                if b'=>>' not in password2_response:
                    raise CredentialError()

        except CredentialError:
            print(f'\033[31m{self.ip}: Access Denied. [Log ID: 2]\033[0m')
            self.tn.close()

    def reconnect(self):
        """Reconnect to the SEL relay and clear the terminal"""
        try:
            self.tn.write(b'\r\n')
            self.tn.expect([b'=>', b'=>>'], timeout=5)
            self.tn.read_very_eager()
        except:
            self.connect()


    """ ######## METHODS LEVEL 1 ######## """

    def read_wordbit(self, module: str='', module_index: str='', wordbit: str=''):
        """
        Read any configurable wordbit from the IED. Write the command name as a telnet terminal.

        Args:
            module (str): The name of the module to read the wordbit from.
                Modules included:
                - 'G': Global Settings
                - 'L': Logic Settings
                - 'D': DNP Map Settings
                - 'P': Port Settings
                - 'F': Front Panel Settings
                - 'R': Report Settings
                - 'M': Modbus Settings
                - Empty String: Group Settings

            module_index (str): The index of the module to read the wordbit from.

            wordbit (str): The name of the wordbit to read.

        Returns:
            str: The wordbit from the relay
        """

        # Construct the internal file read command (e.g., FIL SHO SET_L1.TXT)
        # We filter empty strings to handle cases where module or index aren't used
        args = [arg for arg in (module, module_index) if arg]  # Check empty spaces
        command = f'FIL SHO SET_' + ''.join(args) + '.TXT\r\n'

        # The target_marker identifies the start of the relevant section in the output (e.g., [L1])
        target_marker = f'[{module}{module_index}]'

        try:
            # Send command and wait for the relay to return to the prompt
            self.tn.write(command.encode('utf-8'))
            _, _, raw_data = self.tn.expect([b'=>>', b'=>'], timeout=5)

            # Decode and split into lines for processing
            reading = raw_data.decode('utf-8', errors='ignore')
            reading_lines = reading.split('\n')

            # Robust searching: Find the index of the line containing the section marker
            # We use 'in' instead of exact matching to avoid issues with hidden terminal characters
            module_index_int = -1
            for i, line in enumerate(reading_lines):
                if target_marker in line:
                    module_index_int = i
                    break

            # Start parsing from the line immediately following the marker
            relevant_lines = reading_lines[module_index_int + 1:]

            # Build the Dictionary
            wordbits_dict = {}
            for item in relevant_lines:
                if ',' in item:
                    # Clean the line of carriage returns, leading/trailing spaces, and quote
                    clean_line = item.strip().replace('\r', '')
                    parts = clean_line.split(',', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip().strip('"')
                        wordbits_dict[key] = value
                elif '=>' in item:  # Stop processing if we hit the next terminal prompt
                    break

            # Retrieves the value from the dictionary
            if wordbit in wordbits_dict:
                return wordbits_dict[wordbit]
            else:
                print(f'\033[31mMethod execution failed. Check the parameters and try again. [Log ID: 3]\033[0m')

        except KeyError:
            error_msg = f'\033[31mMethod execution failed. Check the parameters and try again. [Log ID: 3]\033[0m'
            print(error_msg)
            self.reconnect()

        finally:
            self.reconnect()


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


    def read_target_value(self, wordbit: str):
        """Read the current value of a binary wordbit"""
        command = f'TAR {wordbit}'
        self.tn.write((command + '\r\n').encode('utf-8'))
        if self.level2:
            reading = self.tn.read_until(b'=>>').decode('utf-8')
            removing_caracteres_1 = reading.replace(f'\x03TAR {wordbit}\r\n\x02\r\n', '')
            removing_caracteres_2 = removing_caracteres_1.replace('\r\n\x03\x02\r\n=>>', '')
        else:
            reading = self.tn.read_until(b'=>').decode('utf-8')
            removing_caracteres_1 = reading.replace(f'\x03TAR {wordbit}\r\n\x02\r\n', '')
            removing_caracteres_2 = removing_caracteres_1.replace('\r\n\x03\x02\r\n=>', '')

        removing_caracteres_3 = removing_caracteres_2.replace('\r\n', ' ')
        reading2 = removing_caracteres_3.split(' ')
        reading3 = [element for element in reading2 if element.strip() != '']

        variables = reading3[:8]
        values = reading3[8:]

        target_dictionary = dict(zip(variables, map(int, values)))
        final_reading = target_dictionary[wordbit]

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


    def read_his(self):
        self.tn.write(b'HIS\r\n')
        reading_expect = self.tn.expect([b'=>>', b'=>'], timeout=5)
        reading2 = reading_expect[2].decode("utf-8").strip().split('\n')

        if "No Data Available" in reading2[1]:
            print("No Data Available")
        else:
            for events in reading2[5:-2]:
                print(events)


    def clear_his(self):
        """Clear the IEDs HIS"""
        self.tn.write(b'HIS C\r\n')
        self.tn.read_until(b'Are you sure (Y,N)?')
        self.tn.write(b'Y\r\n')
        sleep(1)
        print('HIS Clearing Complete')


    def read_time(self):
        """Read the time of the IED"""
        self.tn.write(b'TIME\r\n')
        reading = self.tn.read_until(b'=>').decode('utf-8')
        reading1 = reading.split('\r\n')
        final_reading = reading1[2].replace('\x03\x02', '')
        return final_reading
    

    def generic_command(self, command: str):
        """Execute a generic command in the IED. Use with caution."""
        self.tn.write((command + '\r\n').encode('utf-8'))
        reading_expect = self.tn.read_until(b'=>', timeout=5).decode('utf-8')
        print(reading_expect)


    def telnet_close(self):
        self.tn.close()


    """ ######## METHODS LEVEL 2 ######## """

    def edit_wordbit(self, command: str, parameter: str):
        """Edit a specific parameter of the IED"""
        command_in_bytes = (f'{command}' + '\r\n').encode('utf-8')
        self.tn.write(command_in_bytes)
        self.tn.read_until(b'? ').decode('utf-8')
        parameter_in_bytes = (f'{parameter}' + '\r\n').encode('utf-8')
        self.tn.write(parameter_in_bytes)
        self.tn.read_until(b'? ').decode('utf-8')
        self.tn.write(b'END\r\n')

        print("Writting changes...")
        while True:
            return_message = self.tn.read_until(b'Press RETURN to continue', timeout=3)
            decoded = return_message.decode('utf-8', errors='ignore')

            if "Save Changes(Y/N)?" in decoded:
                self.tn.write(b'Y\r\n')
                sleep(5)
                self.tn.read_until(b'=>>')
                break
            else:
                self.tn.write(b'\r\n')

    def edit_dnpmap(self, point_type: str, point_position: int, new_value: str):
        """Edit a specific point of the DNP Map"""
        # Add a zero on the left if the point position is below 10
        if point_position < 10:
            point_position_string = '00' + str(point_position)
        else:
            point_position_string = str(point_position)

        command = f'SET D 1 {point_type}_{point_position_string}'
        self.tn.write((command + '\r\n').encode('utf-8'))

        self.tn.read_until(b'? ').decode('utf-8')
        self.tn.write(f'{new_value}\r\n'.encode('utf-8'))
        self.tn.read_until(b'? ').decode('utf-8')
        self.tn.write(b'END\r\n')

        print("Writting change in DNP Map 1...")
        while True:
            return_message = self.tn.read_until(b'Press RETURN to continue', timeout=3)
            decoded = return_message.decode('utf-8', errors='ignore')

            if "Save Changes(Y/N)?" in decoded:
                self.tn.write(b'Y\r\n')
                sleep(5)
                self.tn.read_until(b'=>>')
                break
            else:
                self.tn.write(b'\r\n')



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
        self.tn.read_until(expect_text.encode('utf-8'))

        final_command = f'PRB {rb_number}'
        self.tn.write((final_command + '\r\n').encode('utf-8'))

        sleep(1)
        self.tn.close()
        self.__init__(self.ip, level2=True, password1=self.password1, password2=self.password2)


    """ ######## METHODS FTP ######## """

    def upload_file(self, local_file_path: str, event_code: str):
        """FUTURE: Upload a file to the IED using FTP"""
        pass

    
    def download_event(self, event_code: str, event_type: Literal["filtered", "raw"] = "filtered", local_file_path: str = "./"):
        """Download an event file from the IED using FTP"""
        ftp_client = SELFTP(host=self.ip, user='2AC', password=self.password2)

        if event_type == "filtered":
            ftp_client.download_file(f"EVENTS/C4_{event_code}.CEV", local_file_path)
        elif event_type == "raw":
            ftp_client.download_file(f"EVENTS/CR_{event_code}.CEV", local_file_path)
        else:
            raise ValueError("Invalid event type. Use 'filtered' or 'raw'.")