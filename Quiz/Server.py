from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread
from time import *
import random

class Server_UDP:
    def __init__(self, address, door):
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.start = False
        self.clients = []
        self.trivia = []
        self.alreadySent = []
        self.perguntaAtual = None
        self.contadorDeRodadas = 1

        self.cronometro = 10

        self.mapArchive();

        self.sock.bind((address, door))

        print('Conexão iniciada...', )

        self.msg()
        
    def msg(self): #CAPTURA A MENSAGEM DO CLIENTE

        while True:

            data, client_address = self.sock.recvfrom(2048) #BufferSizer == 2048
            data = data.decode('utf-8')

            if not self.isRoomFull() and not self.checkClient(client_address): #VERIFICANDO SE A SALA ESTÁ CHEIA, SE NAO TIVER, ADICIONA O CLIENTE NA LISTA DE CLIENTS
                print(f'Cliente {client_address[0]} se conectou.')
                client = { "IP": client_address[0], "PORTA": client_address[1], "PONTOS": 0 }
                self.clients.append(client) 
                for client in self.clients:
                    self.sock.sendto(f'Jogadores {len(self.clients)} de 5'.encode('utf-8'), (client['IP'], client['PORTA'])) #EXIBE QUANTOS PLAYERS ESTÃO NA SALA

            if (self.checkClient(client_address)):
                if len(self.clients) > 1: #VERIFICA SE HÁ NO MINIMO 2 CLIENTES
                    if data == '/start': #INICIANDO O JOGO
                        Thread(target=self.startGame).start()
                    if not self.start:
                        for clients in self.clients:
                            self.sock.sendto('Para iniciar digite /start'.encode('utf-8'), (clients["IP"], clients["PORTA"]))
                    
                    elif self.start and data != '/start' and client_address not in self.alreadySent:
                        print(f'{client_address}: {data}')
                        self.checkResponse(client_address, data.lower().strip())
                        self.alreadySent.append(client_address)

                    elif client_address in self.alreadySent:
                        self.sock.sendto('Você já respondeu'.encode(), (client_address[0],client_address[1]))
                else:
                    self.sock.sendto('Aguardando mais jogadores se conectar!'.encode('utf-8'), (self.clients[0]["IP"], self.clients[0]["PORTA"]))
            else: #AVISA AO CLIENTE CASO A SALA ESTEJA CHEIA
                self.sock.sendto('isFull'.encode('utf-8'), (client_address[0], client_address[1])) #ESSE ISFULL É A PALAVRA CHAVE DA VERIFICAÇÃO
                  
            
    def isRoomFull(self): #VERIFICA SE A SALA ESTÁ CHEIA
        if len(self.clients) < 5: #MUDAR PARA 5 O NUMERO MÁXIMO DE CLIENTES
            return False
        return True

    def checkClient(self, client): #VERIFICA SE O CLIENTE ESTÁ INSERIDO NA LISTA DE CLIENTES CONECTADOS
        for i in self.clients:
            if i["IP"] == client[0] and i["PORTA"] == client[1]:
                return True
        return False

    def mapArchive(self): #LER O ARQUIVO DA TRIVIA, E FORMATA PARA QUE FIQUE EM JSON
        with open('perguntas.txt', encoding='utf-8') as questions:
            for question in questions:
                if question != '':
                    self.trivia.append(question[:len(question)])
        
            for i in self.trivia:
                pergunta, resposta = self.trivia.pop(0).strip(), self.trivia.pop(0).lower().strip()
                self.trivia.append({ "pergunta": pergunta, "resposta":resposta })

    def checkResponse(self, client, data): #CHECA AS RESPOSTAS
        response = self.perguntaAtual['resposta'].lower().strip()
        for index in range(len(self.clients)):
            if(self.clients[index]["IP"] == client[0] and self.clients[index]["PORTA"] == client[1]):# and self.clients[index] not in self.alreadySent):
                if(data.lower().strip() == response):
                    self.clients[index]["PONTOS"] += 25
                    self.sock.sendto(b'| Acertou :D |', (client[0], client[1]))
        
                elif(data == ''):
                    self.clients[index]["PONTOS"] -= 1
                    self.sock.sendto(b'| Sem resposta :/ |', (client[0], client[1]))

                else:
                    self.clients[index]["PONTOS"] -= 5
                    self.sock.sendto(b'| Incorreta :O |', (client[0], client[1]))
                
    
    def startGame(self):
        self.start = True
  
        #ONDE A MÁGICA ACONTECE
        msg = '''
 15 Segundos para leitura das regras e orientações
        -------------| TEMA |-------------
                    TI em geral

        ------------| REGRAS |------------
            Acertou          => 25 Pontos
            Errou            => -5 Pontos
            Enviou em branco => -1 Ponto

        ------| DICA / ORIENTAÇÃO |------
            Você tem apenas 10 segundos para responder cada pergunta,
            então se você não sabe ou não tem certeza da resposta 
            é melhor apertar "ENTER" e enviar em branco
            do que arriscar e perder -5 pontos ;D

        ---------------------------------
        Ápos o fim da partida os jogadores
        podem digitar novamente /start para recomeçar
        '''
        for clients in self.clients:
            self.sock.sendto(msg.encode('utf-8'), (clients["IP"], clients["PORTA"]))

        for i in range(15, -1, -1):
            print(i)
            sleep(1)

        indiceAnterior = []
        while True:
            randomIndice = random.randint(0, len(self.trivia) - 1) #GERANDO INDICES ALEATORIOS
            if randomIndice not in indiceAnterior:
                indiceAnterior.append(randomIndice)
                print("INDICE", randomIndice, self.trivia)
                pergunta, resposta = self.trivia[randomIndice]["pergunta"], self.trivia[randomIndice]["resposta"] #PERGUNTA E RESPOSTA
                self.perguntaAtual = self.trivia[randomIndice]

                
                if self.contadorDeRodadas <= 5: #MUDA A QUANTIDADE DE RODADAS PARA 5
                    print(f'Inicando a rodada {self.contadorDeRodadas}')
                    print(f"{pergunta}")
                    msg = f'''
                    -------------| INICIANDO A RODADA {str(self.contadorDeRodadas)} |-------------
                    Pergunta: {pergunta}
                    '''
                    for clients in range(len(self.clients)):
                        self.sock.sendto(msg.encode('utf-8'), (self.clients[clients]['IP'], self.clients[clients]['PORTA']))
                        
                    
                    self.cronometer()

                else: #FIM DA PARTIDA, RESETANDO VARIAVEIS
                    self.checkWinner();
                    self.perguntaAtual = None
                    self.contadorDeRodadas = 1
                    for client in self.clients:
                        client['PONTOS'] = 0
                    break
                
                self.alreadySent = []
                self.contadorDeRodadas += 1

    def cronometer(self):
        #CRONOMETRO

        for i in range(10, -1, -1):
            print(i)
            sleep(1)
            Thread(target=self.msg).start()
    

    def checkWinner(self): #CHECA O VENCENDOR DA PARTIDA
        winner = self.clients[0]
        losers = []
        empatados = []
        
        #VERIFICA O VENCEDOR
        for i in range(len(self.clients)):
            for j in range(len(self.clients)):
                if self.clients[i]['PONTOS'] > self.clients[j]['PONTOS'] and self.clients[i]['PONTOS'] > winner['PONTOS']:
                    winner = self.clients[i]
                    
                elif self.clients[i] not in losers and self.clients[i]['PONTOS'] < self.clients[j]['PONTOS']:
                    losers.append(self.clients[i])

        #CHECA EMPATES
        for i in range(len(self.clients)):
            for j in range(len(self.clients)):
                if self.clients[i]['PONTOS'] == self.clients[j]['PONTOS'] and self.clients[i] != self.clients[j] and self.clients[i] not in empatados:
                    if self.clients[i] == winner:
                        winner = None
                    if self.clients[i] in losers:
                        losers.remove(self.clients[i])

                    empatados.append(self.clients[i])

        if winner != None:
            winnerMsg = f'\n -------------------\nVocê venceu, Parabéns!\nPontos: {winner["PONTOS"]}\n ------- FIM -------'
            self.sock.sendto(winnerMsg.encode('utf-8'), (winner['IP'], winner['PORTA']))
       
        if len(losers) > 0:
            for loser in losers:
                loserMsg = f'\n -------------------\nVocê perdeu que pena :(\nPontos: {loser["PONTOS"]}\n ------- FIM -------'
                self.sock.sendto(loserMsg.encode('utf-8'), (loser['IP'], loser['PORTA']))

        if len(empatados) > 0:
            jogadores = ''
            for empate in empatados:
                jogadores += f'-----------------\n|IP: {empate["IP"]}\n|PORTA: {empate["PORTA"]}\n|PONTOS: {empate["PONTOS"]}\n'

            empateMsg = f'\n-------------------\n Empatou | Placar de Empate \n {jogadores}------- FIM -------'
            for i in empatados:
                self.sock.sendto(empateMsg.encode('utf-8'), (i['IP'], i['PORTA']))
        
        placarFinal = [winner] + empatados + losers if winner != None else empatados + losers
        jogadores = '\n- - - - - - -| PLACAR FINAL |- - - - - - -\n'
        cont = 1
        for clients in placarFinal:
          jogadores += f'''
           -------JOGADOR {cont}-------
          |IP: {clients["IP"]} 
          |PORTA: {clients["PORTA"]}
          |PONTOS: {clients["PONTOS"]}
           -----------------------
          '''
          cont += 1
        for clients in placarFinal:
            print('CLIENTE', clients)
            self.sock.sendto(jogadores.encode('utf-8'), (clients["IP"], clients["PORTA"]))
    
if __name__ == '__main__':
    server = Server_UDP('172.23.0.7', 8080) #MUDAR O IP
