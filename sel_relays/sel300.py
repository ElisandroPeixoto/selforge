from telnetlib import Telnet
from time import sleep


class SEL300:
    def __init__(self, ip, porta=23, nivel2=False):
        self.tn = Telnet(ip, porta, timeout=10)
        self.tn.write(b'acc\r\n')
        self.tn.read_until(b'Password: ?')
        self.tn.write(b'OTTER\r\n')
        self.tn.read_until(b'=>')
        if nivel2:
            self.tn.write(b'2AC\r\n')
            self.tn.read_until(b'Password: ?')
            self.tn.write(b'EQ.PR0T@eqtl\r\n')
            # Retorna uma tupla cujo indice 0 corresponde ao indice da resposta obtida da lista
            resposta = self.tn.expect([b'=>>', b'Password: ?'], timeout=5)
            if resposta[0] == 0:
                pass
            else:
                self.tn.write(b'TAIL\r\n')
                self.tn.read_until(b'=>>')

    """Metodos Nivel 1"""
    def ler_set1(self):
        """Retorna um dicionario contendo o pacote lido (Ex: SET1, L1, etc)"""
        comando = f'FIL SHO SET_1.txt'
        self.tn.write((comando + '\r\n').encode('utf-8'))
        leitura = self.tn.read_until(b'=>', timeout=5).decode('utf-8')
        filtro1 = leitura.find('[1]')
        mapa = leitura[filtro1 + 3::]
        mapa2 = mapa.strip().split('\r\n')
        mapa_final = {}

        for linhas_mapa in mapa2:
            if "," in linhas_mapa:
                variavel, valor = linhas_mapa.split(",")
                valor2 = valor.replace('"', '')
                mapa_final[variavel] = valor2

        mapa_final = {variavel: valor for variavel, valor in mapa_final.items()}
        return mapa_final

    def ler_modelo(self):
        self.tn.write(b'ID\r\n')
        leitura = self.tn.read_until(b'=>', timeout=5).decode('utf-8')
        texto = leitura.find('FID=')
        return leitura[texto+4:texto+38]

    def part_number(self):
        pass

    def serial_number(self):
        pass

    def ler_mapadnp3(self, tipo_ponto):
        """Retorna um dicionario contendo o mapa DNP3 do rele"""
        comando = 'FIL SHO SET_D1.TXT'
        self.tn.write((comando + '\r\n').encode('utf-8'))
        leitura = self.tn.read_until(b'=>', timeout=5).decode('utf-8')
        filtro1 = leitura.find('[D1]')
        mapa = leitura[filtro1+4::]
        mapa2 = mapa.strip().split('\r\n')

        mapa_final = {}
        for linhas_mapa in mapa2:
            if "," in linhas_mapa:
                ponto, variavel = linhas_mapa.split(",")
                variavel2 = variavel.replace('"', '')
                mapa_final[ponto] = variavel2

        mapa_final = {ponto: variavel for ponto, variavel in mapa_final.items() if ponto.startswith(tipo_ponto)}
        return mapa_final

    """Metodos Nivel 2"""

    def escrever_variavel(self, comando, parametro):
        pass

    def alterar_mapadnp3(self, tipo_ponto, posicao_ponto, novo_valor):
        # Adiciona o zero a esquerda nos pontos menores que 10 e transforma em string
        if posicao_ponto < 10:
            posicao_ponto_string = '00' + str(posicao_ponto)
        else:
            posicao_ponto_string = '0' + str(posicao_ponto)

        comando = f'SET D 1 {tipo_ponto}_{posicao_ponto_string} TERSE'
        valor = f'{novo_valor}\r\n'.encode('utf-8')
        self.tn.write((comando + '\r\n').encode('utf-8'))
        self.tn.read_until(b'? ')
        self.tn.write(valor)
        self.tn.read_until(b'? ')
        self.tn.write(b'END\r\n')
        self.tn.read_until(b'Save Changes(Y/N)? ')
        self.tn.write(b'Y\r\n')
        sleep(10)
        self.tn.read_until(b'=>>')
