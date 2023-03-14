from enlace import *
import time
import numpy as np
import comandos
import random
import comlib as comlib
import serial.tools.list_ports
from packetlib import PacketLib, Packet, Header
from comandos import message_type, flags
from logger import Logger

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyS3"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)

def progressbar(current: int, total: int):
    percent_done = round((current / total)*50)
    percent_remaining = 50 - percent_done
    return f"[{'='*percent_done}{'-'*(percent_remaining)}] {current}/{total}"

SERVER_ID = 1

def main(logger):
    logger.log('Selecionando porta automaticamente...')
    ports = list(serial.tools.list_ports.comports())
    if (len(ports) == 0):
        logger.log('Nenhuma porta encontrada')
        exit(1)
    serialName = ports[0].device
    logger.log(f'Porta selecionada: {serialName}')

    try:
        logger.log("Iniciou o SERVER")
        com1 = enlace(serialName)
        
        com1.enable()
        #logger.log("Esperando um byte de sacrifício")
        #rxBuffer, nRx = com1.getData(1)
        #com1.rx.clearBuffer()
        #time.sleep(.1)

        lib = comlib.ComLib(com1, logger)
        plib = PacketLib(logger)
        
        while True:
            raw_packet = plib.get_next_packet(lib)
            if raw_packet is None:
                logger.log('Timeout, buscando pacote novamente.')
                continue

            packet = Packet.decode(raw_packet, logger)
            
            if packet.header.server_id != SERVER_ID:
                logger.log(f'Pacote recebido não é pra mim (sou o server {SERVER_ID} e pacote era pro {packet.header.server_id}).')
                continue

            if packet.header.message_type != message_type.HELLO_1:
                logger.log('Packet recebido não é um Hello(1).')
                continue

            logger.log('PACOTE HELLO RECEBIDO!')
            total_packets = packet.header.total_packets
            file_id = packet.header.file_id

            # Enviando Ready
            logger.log('Enviando Ready...')
            lib.send(
                Packet(
                    header=Header(
                        message_type=message_type.READY_2,
                        server_id=SERVER_ID,
                        file_id=packet.header.file_id,
                    )
                ).encode(logger)
            )
            break

        cont = 1
        timeout_count = 0
        data = b''
        while cont <= total_packets:
            raw_packet = plib.get_next_packet(lib)

            # TODO: Tratar timeouts
            if raw_packet is None:
                if timeout_count >= 4:
                    logger.log('Mais de 20 segundos sem resposta, encerrando comunicação.')
                    lib.send(
                        Packet(
                            header=Header(
                                message_type=message_type.TIMEOUT_5,
                                server_id=SERVER_ID,
                            ),
                        ).encode(logger)
                    )
                    break

                logger.log('Nenhum novo pacote recebido dentro de 5 segundos.')
                timeout_count += 1
                continue

            packet = Packet.decode(raw_packet, logger)
            if packet.header.server_id != SERVER_ID:
                logger.log('Pacote recebido não é pra mim.')
                continue

            if packet.header.message_type != message_type.DATA_3:
                logger.log('Packet recebido não é um Data(3).')
                continue

            if packet.header.current_packet != cont:
                lib.send(
                    Packet(
                        header=Header(
                            message_type=message_type.ERROR_6,
                            server_id=SERVER_ID,
                            file_id=file_id,
                            restart_from=cont,
                        )
                    ).encode(logger)
                )

                logger.log('Packet recebido não é o esperado. (esperava {}, recebi {}).'.format(cont, packet.header.current_packet))
                continue

            logger.log(f'PACOTE {cont} RECEBIDO!')
            timeout_count = 0
            data += packet.payload
            
            cont+=1

            lib.send(
                Packet(
                    header=Header(
                        message_type=message_type.ACK_4,
                        server_id=SERVER_ID,
                        file_id=file_id,
                        last_successful_packet=cont,
                    )
                ).encode(logger)
            )

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

        f = open(f'files/{file_id}.txt', 'wb')
        f.write(data)
        f.close()

    except KeyboardInterrupt:
        logger.log('interrupted!')
        exit(1)
        
    except Exception as erro:
        logger.log(erro)
        com1.disable()
        exit(1)
        
if __name__ == "__main__":
    logger = Logger('logs/server')
    logger.startThread()
    main(logger)
    exit(1)
