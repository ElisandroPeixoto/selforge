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

    def read_wordbit(self, module: str, wordbit: str):
        """Read any configurable wordbit from the IED"""
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
