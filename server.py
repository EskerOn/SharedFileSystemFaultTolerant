import socket
import threading
import sys
from jsonutils import decodeJSON, encodeJSON, messageType
import time
import logging
import pickle
import argparse
logging.StreamHandler(sys.stdout)
logging.basicConfig(format='%(asctime)s %(message)s', datefmt=' %I:%M:%S %p')
## getting the hostname by socket.gethostname() method
hostname = socket.gethostname()
## getting the IP address using socket.gethostbyname() method
port= 1908
def parseArgs():
    global ip_address, port

    desc = "servidor de chat"
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument("--ip", "-i", help="Ip adress")
    parser.add_argument("--port", "-p", help="port")
    args = parser.parse_args()
    if args.ip :
        ip_adress = args.ip
    if args.port :
        port = args.port


class Server():

    def __init__(self, port):

        self.HOST = "192.168.8.2"
        self.PORT = port
        self.MAX_CONNECTIONS = 4
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.backupserv=[]
        try:
            self.server.bind(("", self.PORT))
        except OSError:
            try:
                self.PORT+=1
                self.server.bind(("", self.PORT))
            except OSError:
                try:
                    self.PORT+=1
                    self.server.bind(("", self.PORT))
                except OSError:
                    self.server.bind(("", self.PORT))
                
        self.server.listen(self.MAX_CONNECTIONS)
        print("Server en la IP : {} PORT : {} para {} conexiones".format(self.HOST, self.PORT, self.MAX_CONNECTIONS))
        
        self.clients = dict()
        #self.rooms = dict()
        self.clientsSem = threading.Lock()

        while True :
            try:
                connection, addr = self.server.accept()
                self.clientsSem.acquire()
                self.clients[connection] = ""
                print(addr)
                self.clientsSem.release()
                print("{} conectado con puerto {}".format(addr[0], addr[1]))
                self.backupserv.append(addr[0])
                self.myThread = threading.Thread(target= self.clientThread, args=(connection, addr))
                self.myThread.setDaemon = True
                self.myThread.start()
            except (KeyboardInterrupt, SystemError):
                socket.close()
                print("Servidor cerrado?")
                raise
    def sendBackUp(self):
        return self.clients

    def clientThread(self, connection, addr):
        while True:
            try:
                message = connection.recv(1024)
                message = decodeJSON(message)
                messagetype = message['type']
                #Chose or chage username
                if messagetype == messageType['username']:
                    username = message['content']
                    print("Solicitud de asignacion de usuario <{}>".format(username))
                    self.clientsSem.acquire()
                    if self.getUserFromName(username):
                        connection.send(encodeJSON(messageType['username'], "NOT OK"))
                        print("Solicitud para el usuario <{}> denegada, usuario ya registrado".format(username))
                    else :
                        connection.send(encodeJSON(messageType['username'], "OK"))
                        print("Solicitud para el usuario <{}> aprobada".format(username))
                        self.clients[connection] = username
                        self.broadcast(encodeJSON(messageType['login'], "{}".format(username)), connection)
                        time.sleep(1.0)
                        connection.send(encodeJSON(messageType['info'], self.getAllUsers()))
                        self.broadcast(encodeJSON(messageType['info'], self.getAllUsers()), connection)
                        connection.send(encodeJSON(messageType['back'], self.getbackup()))
                        self.broadcast(encodeJSON(messageType['back'], self.getbackup()), connection)
                        print("Usuario {} registrado".format(username))
                    self.clientsSem.release()
                #chatroom
                elif messagetype == messageType['request']:
                    #self.backup(encodeJSON(messageType['back'], self.getbackup()))
                    if "OK" in message['content']:
                        reciver = message['target']
                        self.clientsSem.acquire()
                        reciver = self.getUserFromName(reciver)
                        self.clientsSem.release()
                        ip_host = addr[0]
                        port_host = message['content'].split("-")[1]
                        if reciver :
                            try:
                                reciver.send(encodeJSON(messageType['request'], "OK-{}-{}".format(ip_host, port_host)))
                                print("Solicitud de envio de archivo del usuario [{}] al usuario [{}] aceptada\nProcediendo a la creacion del servidor UDP en IP: {} Puerto: {}".format(self.clients[connection], self.clients[reciver], ip_host, port_host))
                            except :
                                connection.send(encodeJSON(messageType['error'], ">Failed to send confirmation to {}".format(message['target'])))
                    elif "NO" in message['content']:
                        pass
                    else:
                    #if message['content'] != "OK" or message['content'] != "NO":
                        reciver = message['target']
                        self.clientsSem.acquire()
                        reciver = self.getUserFromName(reciver)
                        self.clientsSem.release()
                        if reciver :
                            try:
                                reciver.send(encodeJSON(messageType['request'], "El usuario {} esta tratando de enviarte un archivo <{}>.\n¿Aceptar la transferencia?".format(self.clients[connection], message['content']), self.clients[connection]))
                                print("Enviando solicitud de envio de archivo del usuario [{}] al usuario [{}]".format(self.clients[connection], self.clients[reciver]))
                            except :
                                connection.send(encodeJSON(messageType['error'], ">Failed to send message to {}".format(message['target'])))

                #Get server info
                elif messagetype == messageType['info']:
                    if message['content']  == "users":
                        self.clientsSem.acquire()
                        print("El usuario [{}] solicito actualizacion de los clientes conectados al servidor.".format(self.clients[connection]))
                        connection.send(encodeJSON(messageType['info'], self.getAllUsers()))
                        self.clientsSem.release()
                        time.sleep(0.5)
                #logout
                elif messagetype == messageType['logout']:
                    self.clientsSem.acquire()
                    print("Desconexion del usuario [{}]".format(self.clients[connection]))
                    self.removeUser(connection)
                    self.broadcast(encodeJSON(messageType['logout'], "{}".format(username)), connection)
                    self.clientsSem.release()
                    break
            except:
                pass

    def getUserFromName(self, username):
        for connection, user in self.clients.items():
            if user == username :
                return connection
        return False 

    def broadcast(self, message, sender):
        disconectedClienst = []
        for client in self.clients :
            if client != sender:
                try:
                    client.send(message)
                except :
                    disconectedClienst.append(client)
        for client in disconectedClienst:
            self.removeUser(client)
    
    def backup(self, message):
        disconectedClienst = []
        for client in self.clients :
            try:
                client.send(message)
                print("sendbkp")
            except :
                disconectedClienst.append(client)
        for client in disconectedClienst:
            self.removeUser(client)

    def getbackup(self):
        usern = ""
        if len(self.backupserv) > 0:
            for user in self.backupserv:
                usern += "{} ".format(user)
            return usern
        else :
            return "None"

    def removeUser(self, connection):
        if connection in self.clients :
            self.clients.pop(connection)

    def getAllUsers(self):
        usern = ""
        if len(self.clients) > 0:
            for _, user in self.clients.items():
                usern += "{} ".format(user)
            print("Usuarios: " + usern)
            return usern
        else :
            return "ws"
if __name__ == "__main__":           
    parseArgs()
    server = Server(int(port))
                        

