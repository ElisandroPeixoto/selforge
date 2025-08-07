from telnetlib import Telnet
from time import sleep


class SEL300:
    """Access any SEL 300 series device using a telnet connection"""
    def __init__(self, ip: str, password1: str='OTTER', password2: str='TAIL', port: int=23, level2: bool=False):
        self.ip = ip
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

    """ ######## METHODS LEVEL 1 ######## """

    def read_firmware(self):
        self.tn.write(b'ID\r\n')
        reading = self.tn.read_until(b'=>', timeout=5).decode('utf-8')
        fid_text = reading.find('FID=')
        first_caracter = fid_text+4
        last_caracter = reading.find('"', fid_text+4)
        return reading[first_caracter:last_caracter]
