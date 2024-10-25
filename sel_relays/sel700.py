from telnetlib import Telnet
from time import sleep


class SEL700:
    """Access any SEL 700 series device using a telnet connection"""
    def __init__(self, ip: str, password1='OTTER', password2='TAIL', porta=23, level2=False):
        self.tn = Telnet(ip, porta, timeout=10)
        self.tn.write(b'ACC\r\n')
        self.tn.read_until(b'Password: ?')
        self.tn.write((password1 + '\r\n').encode('utf-8'))
        self.tn.read_until(b'=>')
        if level2:  # If level2 is True (Required to use level 2 methods), ask for the level 2 password
            self.tn.write(b'2AC\r\n')
            self.tn.read_until(b'Password: ?')
            self.tn.write((password2 + '\r\n').encode('utf-8'))
            self.tn.read_until(b'=>>')

    """ Level 1 Methods"""

    def read_wordbit(self, command: str):
        """Read any configurable wordbit from the IED. Write the command name as a telnet terminal"""
        self.tn.write((command + '\r\n').encode('utf-8'))
        reading = self.tn.read_until(b'=>', timeout=5).decode('utf-8')
        reading2 = reading.split(':= ')
        reading3 = reading2[1].split('\r')
        reading4 = reading3[0].replace('\r', '')
        reading5 = reading3[1].replace('            ', '')
        final_reading = (reading4 + reading5).split('\n\x03\x02')
        return final_reading[0]

    def read_firmware(self):
        """Read the IED Firmware"""
        self.tn.write(b'ID\r\n')
        reading = self.tn.read_until(b'=>', timeout=5).decode('utf-8')
        reading2 = reading.split('=')
        reading3 = reading2[1].split('","')
        final_reading = reading3[0]
        return final_reading

    def read_partnumber(self):
        """Read the IED Part Number"""
        self.tn.write(b'STA\r\n')
        reading = self.tn.read_until(b'=>', timeout=5).decode('utf-8')
        text_source = reading.find('PART NUM = ')
        reading2 = reading[text_source::]
        reading3 = reading2.split('=')
        reading4 = reading3[1].split('\r\n')
        final_reading = reading4[0].replace(' ', '')
        return final_reading

    def read_serialnumber(self):
        """Read the IED Serial Number"""
        self.tn.write(b'STA\r\n')
        reading = self.tn.read_until(b'=>', timeout=5).decode('utf-8')
        text_source = reading.find('Serial Num = ')
        reading2 = reading[text_source::]
        reading3 = reading2.split('=')
        reading4 = reading3[1].split('\r\n')
        reading5 = reading4[0].replace('FID', '')
        final_reading = reading5.replace(" ", "")
        return final_reading

    def read_dnppoint(self, data_type: str, position: int):
        """
        Read an specific point from DNP Map
        Specify the data type of the point:
        BI = Binary Inputs
        AI = Analog Inputs
        BO = Binary Outputs
        """
        if position < 10:  # Add zero on the left if the position is smaller than 10
            point_position2string = '0' + str(position)
        else:
            point_position2string = str(position)

        # Executa o comando
        command = f'SHO D 1 {data_type}_{point_position2string}'
        self.tn.write((command + '\r\n').encode('utf-8'))
        reading = self.tn.read_until(b'=>', timeout=5).decode('utf-8')
        reading2 = reading.split(':= ')
        reading3 = reading2[1].replace('\r\n\x03\x02\r\n=>', '')
        return reading3

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

    def read_ser(self, lines=0):
        """Read the relay's SER. Enter the number of lines if you wish to view a limited quantity of records"""
        command = f'SER {lines}\r\n'
        self.tn.write(command.encode('utf-8'))
        leitura = self.tn.read_until(b'=>>')
        return leitura.decode('utf-8')

    def clear_ser(self):
        """Clear the relay's SER"""
        self.tn.write(b'SER C\r\n')
        self.tn.read_until(b'Are you sure (Y,N)?')
        self.tn.write(b'Y\r\n')
        sleep(1)

    """ Level 2 Methods"""

    def edit_wordbit(self, command: str, parameter: str):
        """Edit a specific parameter of the relay"""
        command_in_bytes = (f'{command}' + '\r\n').encode('utf-8')
        self.tn.write(command_in_bytes)
        self.tn.read_until(b'? ').decode('utf-8')

        parameter_in_bytes = (f'{parameter}' + '\r\n').encode('utf-8')
        self.tn.write(parameter_in_bytes)

        self.tn.read_until(b'? ').decode('utf-8')
        self.tn.write(b'END\r\n')
        self.tn.read_until(b'Save changes (Y,N)? ')
        self.tn.write(b'Y\r\n')
        sleep(5)

    def edit_dnpmap(self, point_type, point_position, new_value):
        """Edit an specific point of the DNP Map"""
        # Add a zero on the left if the point position is below 10
        if point_position < 10:
            point_position_string = '0' + str(point_position)
        else:
            point_position_string = str(point_position)

        comando = f'SET D 1 {point_type}_{point_position_string} {new_value}'
        self.tn.write((comando + '\r\n').encode('utf-8'))

        self.tn.read_until(b'Save changes (Y,N)? ')
        self.tn.write(b'Y\r\n')
        sleep(5)
        self.tn.read_until(b'=>>')

    def open_breaker(self):
        """Run the OPEN Command"""
        self.tn.write(b'OPEN\r\n')
        self.tn.read_until(b'Open Breaker (Y,N)?')
        self.tn.write(b'Y\r\n')
        sleep(1)

    def close_breaker(self):
        """Run the CLOSE Command"""
        self.tn.write(b'CLOSE\r\n')
        self.tn.read_until(b'Close Breaker (Y,N)?')
        self.tn.write(b'Y\r\n')
        sleep(1)

    def pulse_rb(self, remotebit):
        """Pulses an specific Remote Bit"""
        command = f'CON {remotebit} P'
        self.tn.write((command + '\r\n').encode('utf-8'))
        sleep(1)
