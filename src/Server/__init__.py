from Config import HOST, PORT, BUFFER_SIZE, ENCODING,  NUM_PLAYERS
from Connection import Connection
from Data import Data
from threading import Thread
from json import loads, dumps

class Server(Connection):
  def __init__(self, host=HOST, port=PORT, buffer_size=BUFFER_SIZE, encoding=ENCODING):
    Connection.__init__(self, host, port, buffer_size, encoding)
    self.sock.bind(self.addr)
    self.sock.listen()

    self.clients = []
    self.num_clients = -1 # Para indexar a lista de clientes corretamente, se inicia com -1
    self.data = Data()

  def start(self):
    print('Aguardando jogadores...')

    while (True):
      sock_client, addr = self.sock.accept()
      ip, name = addr
      client = {'sock': sock_client, 'ip': ip, 'name': name}
  
      if (self.num_clients < NUM_PLAYERS - 1):
        print(f'Jogador {name} entrou!')
        self.num_clients += 1
        self.data.setTurn(name) # O primeiro jogador que clicar comeca jogando
        self.clients.append(client)
        Thread(target=self.handlerClient, args=(self.num_clients,), daemon=True).start()
        
        self.data.setName(name)
        self.data.setStarted(True) if (self.num_clients == NUM_PLAYERS - 1) else self.data.setStarted(False)

        self.broadcom(self.data.toString())
        print(self.data.toString())
      else:
        print('Sala cheia!')

  def handlerClient(self, num_client):
    client = self.clients[self.num_clients]
    sock, _, name = client.values()

    while (True):
      try:
        recv_data = loads(self.recv(sock))
        names = [client['name'] for client in self.clients]
        next_player = filter(lambda name: name != recv_data['name'], names).__next__()        
        
        self.data.setFromDict(recv_data)
        print(self.data.toString())
        # Se nao tiver ganhador, trocar o turno
        self.data.setTurn(next_player)
        self.broadcom(self.data.toString())
        if (self.data.getWinner() != None): self.data.resetInfo()
        
      except:
        print(f'<{name}>: Desconectou')
        self.shutdown()
        break

  def shutdown(self):
    for sock in [s['sock'] for s in self.clients]: sock.close()
    self.num_clients = -1
    self.data = Data()
    self.clients = []

  def broadcom(self, data):
    for sock in [s['sock'] for s in self.clients]:
      self.send(sock, data)
  
  def startThread(self):
    Thread(target=self.start, daemon=True).start()