from enlace import *
import time
import numpy as np
from comandos import dados, flags
import random
import lib as comlib
import serial.tools.list_ports

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

        # command_count = random.randint(10, 30)
        command_count = 2
        print(f"Quantidade de comandos: {command_count}")

        commands = []
        for i in range(command_count):
            commands.append(
                random.randint(1, 9)
            )

        print(f"Comandos: {commands}")

        com1 = enlace(serialName)
        com1.enable()
        lib = comlib.ComLib(com1)

        time.sleep(.2)
        lib.send(b'\x00')
        time.sleep(1)
        
        
        lib.send(flags.IM_HERE)
        lib.waitFor(flags.GO_AHEAD)

        print("-------------------------")
        print("Comunicação aberta - CLIENT")
        print("-------------------------")

        lib.send(flags.START_TRANSMISSION)
        lib.waitFor(flags.GO_AHEAD)

        for command in commands:
            lib.send(flags.START_COMMAND)
            lib.waitFor(flags.GO_AHEAD)
            time.sleep(0.3)
            lib.send(dados[command])
            time.sleep(0.3)
            lib.send(flags.END_COMMAND)
            lib.waitFor(flags.GO_AHEAD)

        lib.send(flags.COMMANDS_DONE)
        lib.waitFor(flags.FEEDBACK_READY)
        time.sleep(0.3)
        lib.send(flags.GO_AHEAD)
        feedback = lib.getAllUntil(flags.FEEDBACK_DONE) # y
        time.sleep(0.3)
        feedback_cmd_count = int.from_bytes(feedback, "big")
        if (feedback_cmd_count != command_count):
            lib.send(flags.FEEDBACK_ERROR)
        else:
            lib.send(flags.FEEDBACK_OK)
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
