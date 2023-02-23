from enlace import *
import time
import numpy as np
import comandos
import random
import lib as comlib
from comandos import dados, flags
import serial.tools.list_ports

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
# serialName = "COM4"                  # Windows(variacao de)

def main():
    try:
        print("Iniciou o SERVER")
        com1 = enlace(serialName)
        
        com1.enable()
        print("Esperando um byte de sacrifício")
        rxBuffer, nRx = com1.getData(1)
        com1.rx.clearBuffer()
        time.sleep(.1)

        lib = comlib.ComLib(com1)

        lib.waitFor(flags.IM_HERE)
        lib.send(flags.GO_AHEAD)

        print("-------------------------")
        print("Comunicação aberta - SERVER")
        print("-------------------------")

        try:
            lib.waitFor(flags.START_TRANSMISSION)
            lib.send(flags.GO_AHEAD)

            all_commands = []

            while True:
                time.sleep(0.1)
                print('Esperando pedido de comando')
                flag = lib.waitFor([flags.START_COMMAND, flags.COMMANDS_DONE])
                if flag == flags.COMMANDS_DONE:
                    break
                lib.send(flags.GO_AHEAD)
                print('Comando autorizado, aguardando dados')
                collected = lib.getAllUntil(flags.END_COMMAND)
                print(collected)
                all_commands.append(collected)
                print('Comando recebido, liberando próxima requisição')
                time.sleep(0.3)
                lib.send(flags.GO_AHEAD)

            print('Recebidos todos os comandos')
            print(all_commands)

            lib.send(flags.FEEDBACK_READY)
            lib.waitFor(flags.GO_AHEAD)
            time.sleep(0.5)
            print('Sending feedback count')
            lib.send(len(all_commands).to_bytes(1, 'big'))
            time.sleep(0.3)
            lib.send(flags.FEEDBACK_DONE)
            result = lib.waitFor([flags.FEEDBACK_OK, flags.FEEDBACK_ERROR])
            
            if result == flags.FEEDBACK_OK:
                print('COMANDOS RECEBIDOS COM SUCESSO')
            elif result == flags.FEEDBACK_ERROR:
                print('ERRO NO RECEBIMENTO DOS COMANDOS')

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
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com1.disable()
        
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()
        exit(1)
        

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
    exit(1)
