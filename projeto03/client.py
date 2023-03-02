from enlace import *
import time
import numpy as np
from comandos import command_type, packet_type
import random
import comlib as comlib
import serial.tools.list_ports
from packetlib import PacketLib

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyS3"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
#serialName = "COM3"                  # Windows(variacao de)

ports = list(serial.tools.list_ports.comports())
if (len(ports) == 0):
    print('Nenhuma porta encontrada')
    exit(1)
serialName = ports[len(ports)-1].device
print(f'Porta selecionada: {serialName}')

def main():
    try:
        print("Iniciou o main")
        print("-------------------------")

        com1 = enlace(serialName)
        com1.enable()
        lib = comlib.ComLib(com1)
        
        plib = PacketLib()
        
        while True:
            lib.send(
                plib.build_command_packet(command_type.PING)
            )
            packet_bytes = plib.get_next_packet(lib)
            if packet_bytes is None:
                print('PONG não recebido')
                continue
            else:
                packet = plib.decode_packet(packet_bytes)
                break

        print(packet)

        print("-------------------------")
        print("Comunicação aberta - CLIENT")
        print("-------------------------")

        f = open("i01_pikachu.png", "rb")
        dados = f.read()
        f.close()

        packet_queue = plib.split_into_packets(dados, 10)
        # print('Pacotes a serem enviados:', packet_queue)

        errored = False

        for packet in packet_queue:
            lib.send(packet)
            time.sleep(0.005)
            response = plib.get_next_packet(lib)
            if response is None:
                print('Nenhum pacote recebido. Timeout.')
                break
            else:
                print('Pacote recebido:', plib.decode_packet(response))
                if plib.decode_packet(response)['type'] == packet_type.COMMAND and plib.decode_packet(response)['metadata']['command'] == command_type.ACK:
                    print('ACK recebido.')
                elif plib.decode_packet(response)['type'] == packet_type.COMMAND and plib.decode_packet(response)['metadata']['command'] == command_type.NACK:
                    print('NACK recebido.')
                    errored = True
                    break

        if errored:
            print('Erro ao enviar pacotes.')
        else:
            print('Pacotes enviados com sucesso. Aguardando TRANSMISSION_OK do server.')
            response = plib.get_next_packet(lib)
            if response is None:
                print('Nenhum pacote recebido. Timeout.')
            else:
                print('Pacote recebido:', plib.decode_packet(response))
                if plib.decode_packet(response)['type'] == packet_type.COMMAND and plib.decode_packet(response)['metadata']['command'] == command_type.TRANSMISSION_OK:
                    print('OK recebido.')
                else:
                    print('Pacote recebido não é um OK.')

        # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com1.disable()
        
    except KeyboardInterrupt:
        print('interrupted!')
        exit(1)

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
