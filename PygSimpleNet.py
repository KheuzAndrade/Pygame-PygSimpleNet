####################################
#            PYGSIMPLENET          #
#            VERSION: 1.0          #
#       AUTHOR: SAMUEL ANDRADE     #
####################################

import socket
import threading
import select
import zlib
import time
import atexit

class Timer():
    def __init__(self):
        self.lastTime = time.time()
    def getTimer(self):
        return time.time() - self.lastTime
    def resetTimer(self):
        self.lastTime = time.time()

class ServerManager():
    def __init__(self, host="localhost", port=12750):
        self.host = host
        self.port = port
        self.buffersize = 8192
        self.address_list = {}
        self.init_ID = 0

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(0)

        print("\nServer started")
        print("Host: " + self.host)
        print("Port: " + str(self.port))
        print("Server running...\n")

        self.run()

    def disconnect(self, client, addr):
        client.close()
        del self.address_list[addr]
        print("Player disconnected from server: ["+str(addr[0])+":"+str(addr[1])+"]")

    def on_connected(self, client, addr):
        self.address_list[addr] = {}
        self.init_ID += 1
        self.address_list[addr]["ID"] = self.init_ID
        self.address_list[addr]["Received"] = {}
        print("New Player Connected: ["+str(addr[0])+":"+str(addr[1])+"]")

        while True:
            try:
                read_sockets, write_sockets, error_sockets = select.select([client], [], [], 0.1)
                if read_sockets:
                    data = client.recv(self.buffersize)
                    received_data = eval(zlib.decompress(data).decode())
                    if not "disconnect" in received_data:
                        self.address_list[addr]["Received"] = {"Dict": received_data["Dict"], "Once": received_data["Once"]}
                        data = {"ID":self.address_list[addr]["ID"], "players":self.address_list}
                    else:
                        self.disconnect(client, addr)
                client.send(zlib.compress(str(data).encode()))
            except:
                pass

    def run(self):
        while True:
            client, addr = self.sock.accept()
            threading.Thread(target=self.on_connected, args=(client, addr)).start()

class ClientManager():
    def quit(self):
        data = str({"disconnect":True}).encode()
        self.sock.send(zlib.compress(data))
        print("Disconnected.")

    def __init__(self, host="localhost", port=12750, buffer_adjustment=True, receive_time=0.022, update_time=0.033):
        self.host = host
        self.port = port
        self.buffer_adjustment = buffer_adjustment
        self.buffersize = 8192
        self.receive_time = receive_time
        self.recv_timer = Timer()
        self.update_time = update_time
        self.update_timer = Timer()
        self.send_dict = {}
        self.send_once = {}
        self.players = {}
        self.ID = 0
        self.received_data = None
        self.connected = False

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        atexit.register(self.quit)
        self.connected = True

    def receive_data(self):
        if self.recv_timer.getTimer() >= self.receive_time:
            try:
                read_sockets, write_sockets, error_sockets = select.select([self.sock], [], [], 0.1)
                if read_sockets:
                    data = self.sock.recv(self.buffersize)

                    if self.buffer_adjustment:
                        self.buffer_adjustment = max(self.buffer_adjustment, len(data))

                    self.received_data = eval(zlib.decompress(data).decode())
                    self.ID = self.received_data["ID"]

                    for addr in self.received_data["players"]:
                        if not self.received_data["players"][addr]["ID"] == self.ID:
                            self.players[addr] = {"Dict":self.received_data["players"][addr]["Received"]["Dict"], "Once":self.received_data["players"][addr]["Received"]["Once"]}
                        if addr in self.players:
                            self.players[addr]["Dict"].update(self.received_data["players"][addr]["Received"]["Dict"])
                            self.players[addr]["Once"].update(self.received_data["players"][addr]["Received"]["Once"])
                    for addr in self.players:
                        if not addr in self.received_data["players"]:
                            del self.players[addr]
            except:
                pass

            self.recv_timer.resetTimer()
            
        if self.update_timer.getTimer() >= self.update_time:
            try:
                data = str({"Dict": self.send_dict, "Once": self.send_once}).encode()
                self.sock.send(zlib.compress(data))
                self.send_once = {}
            except:
                pass
            self.update_timer.resetTimer()
