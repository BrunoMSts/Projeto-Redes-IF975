from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread
from time import sleep

class Client_UDP:
    def __init__(self):
        self.client = socket(AF_INET, SOCK_DGRAM)
        self.address = 'localhost'
        self.door = 8555
        self.chosingDestiny()

        Thread(target=self.sendMsg).start()
        
    def chosingDestiny(self): #ESCOLHE O DESTINO
        self.address = input('Endereço IP: ')
        self.door = int(input('Porta de destino: '))
        print(f'\nConectado ao destino: {self.address}')
        print('Digite qualquer coisa para se conectar ao servidor!')

    def sendMsg(self): #MANDA A MSG
        while True:
            data = input().encode('utf-8')
            self.client.sendto(data, (self.address, self.door))
            Thread(target=self.getMessageFromServer).start()

    def getMessageFromServer(self):
        serverData, serverAddress = self.client.recvfrom(2048)
        if(serverData.decode('utf-8') == 'isFull'):
            print('A sala está cheia, espere alguem sair!')
            
        else:
            print('\n',serverData.decode('utf-8'),'\n')
        
        Thread(target=self.getMessageFromServer).start()

if __name__ == '__main__':
    client = Client_UDP()