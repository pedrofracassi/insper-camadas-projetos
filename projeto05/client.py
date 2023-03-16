from enlace import *
import time
import datetime
import numpy as np
from comandos import message_type, flags
import random
import comlib as comlib
import serial.tools.list_ports
from packetlib import PacketLib, Packet, Header
from logger import Logger
from random import randrange

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyS3"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
#serialName = "COM3"                  # Windows(variacao de)

FILE_ID = randrange(255)
SERVER_ID = 1

def main(logger):
    # read data from beemovie.txt
    with open('beemovie.txt', 'rb') as f:
        data = f.read()

    ports = list(serial.tools.list_ports.comports())
    if (len(ports) == 0):
        logger.log('Nenhuma porta encontrada')
        exit(1)
    serialName = ports[len(ports)-1].device
    logger.log(f'Porta selecionada: {serialName}')

    try:
        logger.log("Iniciou o main")
        logger.log("-------------------------")

        com1 = enlace(serialName)
        com1.enable()
        lib = comlib.ComLib(com1, logger)
        plib = PacketLib(logger)
        
        data_blocks = plib.split_data(data, 114)
        total_packets = len(data_blocks)

        inicia = False
        while not inicia:

            lib.send(
                Packet(
                    header=Header(
                        total_packets=total_packets,
                        message_type=message_type.HELLO_1,
                        server_id=SERVER_ID,
                        file_id=FILE_ID,
                    )
                ).encode(logger)
            )

            raw_packet = plib.get_next_packet(lib)

            if raw_packet is None:
                logger.log('Nenhum pacote recebido')
                continue

            packet = Packet.decode(raw_packet, logger)

            #if True:
            if packet.header.message_type == message_type.READY_2:
                inicia = True
                logger.log('-------------------------')
                logger.log('Iniciando comunicação')
                logger.log('-------------------------')
            else:
                logger.log('-------------------------')
                logger.log('Erro ao iniciar comunicação')
                logger.log('-------------------------')

        cont = 1
        timeout_counter = 0
        last_packet_was_mock_wrong_order = False
        while cont <= total_packets:
            
            # Mock pacote fora de cordem (30% de chance)
            '''
            if randrange(100) > 70 and not last_packet_was_mock_wrong_order:
                cont = randrange(total_packets)
                last_packet_was_mock_wrong_order = True
                logger.log(f'Pacote {cont} enviado fora de ordem (mock)')
            else:
                last_packet_was_mock_wrong_order = False
            '''
            
            if timeout_counter >= 4:
                logger.log('Tempo demais sem receber um ACK. Encerrando comunicação.')
                lib.send(
                    Packet(
                        header=Header(
                            message_type=message_type.TIMEOUT_5,
                            server_id=SERVER_ID,
                            file_id=FILE_ID,
                            last_successful_packet=cont-1,
                        ),
                        payload=block,
                    ).encode(logger)
                )
                break
            block = data_blocks[cont-1]
            logger.log('Enviando pacote {}'.format(cont))
            lib.send(
                Packet(
                    header=Header(
                        message_type=message_type.DATA_3,
                        server_id=SERVER_ID,
                        file_id=FILE_ID,
                        total_packets=len(data_blocks),
                        current_packet=cont,
                        payload_size=len(block),
                    ),
                    payload=block,
                ).encode(logger)
            )

            raw_packet = plib.get_next_packet(lib)
            if raw_packet is None:
                logger.log(f'ACK do pacote {cont} não recebido dentro do tempo limite (5s). Repetindo pacote {cont}.')
                timeout_counter+=1
                continue

            packet = Packet.decode(raw_packet, logger)

            if packet.header.message_type == message_type.ACK_4:
                logger.log(f'ACK do pacote {cont} recebido!')
                cont+=1
                timeout_counter = 0
                continue
            elif packet.header.message_type == message_type.ERROR_6:
                logger.log(f'Servidor reportou erro e solicitou continuar do pacote {packet.header.restart_from}.')
                fake_wrong_packet_sent = True
                cont = packet.header.restart_from
                continue

        logger.log('-------------------------') 
        logger.log(data)

        if cont >= total_packets:
            logger.log('-------------------------')
            logger.log('Transmissão feita com sucesso')
            logger.log('-------------------------')
        else:
            logger.log("-------------------------")
            logger.log("Erro na transmissão.")
            logger.log("-------------------------")
        

        com1.disable()

    except Exception as e:
        logger.log(e)
        com1.disable()
        logger.log('interrupted!')
        exit(1)

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    logger = Logger('logs/client')
    logger.startThread()
    main(logger)
