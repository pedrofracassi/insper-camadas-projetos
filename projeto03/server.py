from enlace import *
import time
import numpy as np
import comandos
import random
import comlib as comlib
import serial.tools.list_ports
from packetlib import PacketLib

print('Selecionando porta automaticamente...')
ports = list(serial.tools.list_ports.comports())
if (len(ports) == 0):
    print('Nenhuma porta encontrada')
    exit(1)
serialName = ports[0].device
print(f'Porta selecionada: {serialName}')

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyS3"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)

def progressbar(current: int, total: int):
    return f"[{'='*current}{'-'*(total-current)}] {current}/{total}"

def main():
    try:
        print("Iniciou o SERVER")
        com1 = enlace(serialName)
        
        com1.enable()
#        print("Esperando um byte de sacrifício")
#        rxBuffer, nRx = com1.getData(1)
#        com1.rx.clearBuffer()
#        time.sleep(.1)

        lib = comlib.ComLib(com1)
        plib = PacketLib()
        
        packet = None
        while True:
            packet_bytes = plib.get_next_packet(lib)
            if packet_bytes is None:
                continue
            else:
                packet = plib.decode_packet(packet_bytes)
                print('Pacote recebido:', packet)
                break

        if (packet['type'] == comandos.packet_type.COMMAND and packet['metadata']['command'] == comandos.command_type.PING):
            print('PING recebido')
            lib.send(
                plib.build_command_packet(comandos.command_type.PONG)
            )
            print('PONG enviado')

        print("-------------------------")
        print("Comunicação aberta - SERVER")
        print("-------------------------")

        last_index = 0
        dados = b''
        while True:
            packet_bytes = plib.get_next_packet(lib)
            print('\n'*3)
            if packet_bytes is None:
                print('Pacote não recebido')
                break
            else:
                try:
                    packet = plib.decode_packet(packet_bytes)
                    print('Pacote recebido:', packet)
                    if (packet['type'] == comandos.packet_type.DATA):
                        print('Dado recebido:', packet['data'])

                        if (packet['metadata']['index'] != last_index + 1):
                            print('Índice inválido')
                            lib.send(
                                plib.build_command_packet(comandos.command_type.NACK)
                            )
                            break

                        dados = dados + packet['data']

                        last_index = packet['metadata']['index']
                        lib.send(
                            plib.build_command_packet(comandos.command_type.ACK) # FORÇAR ACK AQUI  
                        )
                        print('ACK enviado')

                        print(progressbar(packet['metadata']['index'], packet['metadata']['total']))

                        if (packet['metadata']['index'] == packet['metadata']['total']):
                            print('Último pacote recebido')
                            break
                except Exception as e:
                    print(e)
                    print('Pacote inválido')
                    lib.send(
                        plib.build_command_packet(comandos.command_type.NACK)
                    )
                    break

        lib.send(
            plib.build_command_packet(comandos.command_type.TRANSMISSION_OK)
        )

        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com1.disable()

        print('Dados recebidos:', dados)

    except KeyboardInterrupt:
        print('interrupted!')
        exit(1)

        '''


        txBuffer = b'\xAA\xBB\x00'
       
        print("meu array de bytes tem tamanho {}" .format(len(txBuffer)))

        #faça aqui uma conferência do tamanho do seu txBuffer, ou seja, quantos bytes serão enviados.
       
            
        #finalmente vamos transmitir os todos. Para isso usamos a funçao sendData que é um método da camada enlace.
        #faça um print para avisar que a transmissão vai começar.
        #tente entender como o método send funciona!
        #Cuidado! Apenas trasmita arrays de bytes!
               
        
        com1.sendData(np.asarray(txBuffer))  #as array apenas como boa pratica para casos de ter uma outra forma de dados
          
        # A camada enlace possui uma camada inferior, TX possui um método para conhecermos o status da transmissão
        # O método não deve estar fincionando quando usado como abaixo. deve estar retornando zero. Tente entender como esse método funciona e faça-o funcionar.
        txSize = com1.tx.getStatus()
        print('enviou = {}' .format(txSize))
        
        #Agora vamos iniciar a recepção dos dados. Se algo chegou ao RX, deve estar automaticamente guardado
        #Observe o que faz a rotina dentro do thread RX
        #print um aviso de que a recepção vai começar.
        
        #Será que todos os bytes enviados estão realmente guardadas? Será que conseguimos verificar?
        #Veja o que faz a funcao do enlaceRX  getBufferLen
      
        #acesso aos bytes recebidos
        txLen = len(txBuffer)
        rxBuffer, nRx = com1.getData(txLen)
        # print("recebeu {} bytes" .format(len(rxBuffer)))
        
        for i in range(len(rxBuffer)):
            print("({}/{}) recebeu {}" .format(rxBuffer[i], i, len(rxBuffer)))
        

        print("Salvando dados")
        print(" - {}".format(imageW))
        f = open(imageW, 'wb')
        f.write(rxBuffer)

        f.close()
    '''
        # Encerra comunicação
        
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()
        exit(1)
        

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
    exit(1)
