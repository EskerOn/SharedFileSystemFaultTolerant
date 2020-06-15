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
ip_address = None
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
        self.pro_mode = False
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
        self.validUsers = ["A","B","C","D"]
        self.activeNodes = {"A" : False,"B" : False,"C" : False,"D" : False}
        self.actionList = [[],[],[],[]]        
        #self.rooms = dict()
        self.clientsSem = threading.Lock()
        self.myThread = threading.Thread(target = self.interface)
        self.myThread.setDaemon = True
        self.myThread.start() 

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
                message = connection.recv(8192)
                message = decodeJSON(message)
                messagetype = message['type']
                #Chose or chage username
                if messagetype == messageType['username']:
                    username = message['content']
                    print("Solicitud de asignacion de usuario <{}>".format(username))
                    if self.validName(username):
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
                            self.activeNodes[username] = True
                            print(self.activeNodes)
                            if self.pro_mode:
                                print("KKKKK")
                                self.myThread = threading.Thread(target = self.restoreFromFall, args=(connection, ))
                                self.myThread.setDaemon = True
                                self.myThread.start()
                        self.clientsSem.release()
                    else:
                        connection.send(encodeJSON(messageType['username'], "NOT OK"))
                        print("Solicitud para el usuario <{}> denegada, usuario ya registrado".format(username))
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

                elif messagetype == messageType['update']:
                    print("Tratando de enviar la actualizacion")
                    self.broadcast(encodeJSON(message['type'], message['content'], message['target']), connection)
                elif messagetype == messageType['upsignal']:
                    reciver=message['content']
                    self.clientsSem.acquire()
                    reciver = self.getUserFromName(reciver)
                    self.clientsSem.release()
                    reciver.send(encodeJSON(messageType['upsignal']))
                elif messagetype == messageType['filesend']:
                    reciver=message['target']
                    self.clientsSem.acquire()
                    reciver = self.getUserFromName(reciver)
                    self.clientsSem.release()
                    reciver.send(encodeJSON(messageType['filesend'], message['content']))
                elif messagetype == messageType['remotedel']:
                    print("recibo el delete")
                    reciver=message['target']
                    self.clientsSem.acquire()
                    reciver = self.getUserFromName(reciver)
                    self.clientsSem.release()
                    reciver.send(encodeJSON(messageType['remotedel'], message['content']))
                elif messagetype == messageType['test']:
                    if "SY" in message['content']:
                        print("Nodo activo: {}. Tomando acción necesaria.".format(self.activeNodes[message['target']]))
                        if (self.activeNodes[message['target']]):
                            print("Establecer conexión con: {}".format(message['target']))
                            print(self.validUsers.index(message['target']))                        
                            reciver = message['target']
                            self.clientsSem.acquire()
                            reciver = self.getUserFromName(reciver)
                            self.clientsSem.release()
                            if reciver :
                                try:
                                    reciver.send(encodeJSON(messageType['test'], "SY", self.clients[connection]))
                                    print("Enviando solicitud de [{}] al usuario [{}]".format(self.clients[connection], self.clients[reciver]))
                                except :
                                    connection.send(encodeJSON(messageType['error'], ">Failed to send message to {}".format(message['target'])))                        
                        else:                                                
                            reciver = self.getVecino(message['target'])
                            self.clientsSem.acquire()
                            reciver = self.getUserFromName(reciver)
                            self.clientsSem.release()
                            if reciver :
                                try:
                                    reciver.send(encodeJSON(messageType['test'], "SV", self.clients[connection]))
                                    print("Enviando solicitud de [{}] al usuario [{}]".format(self.clients[connection], self.clients[reciver]))
                                except :
                                    connection.send(encodeJSON(messageType['error'], ">Failed to send message to {}".format(message['target'])))
                    elif "UV" in message['content']:
                        print("Nodo activo: {}. Tomando acción necesaria.".format(self.activeNodes[self.getVecino(self.clients[connection])]))
                        if (self.activeNodes[self.getVecino(self.clients[connection])]):
                            print("Establecer conexión con: {}".format(self.getVecino(self.clients[connection])))
                            print(self.validUsers.index(self.getVecino(self.clients[connection])))
                            reciver = self.getVecino(self.clients[connection])
                            self.clientsSem.acquire()
                            reciver = self.getUserFromName(reciver)
                            self.clientsSem.release()
                            if reciver :
                                try:
                                    reciver.send(encodeJSON(messageType['test'], "UV", self.clients[connection]))
                                    print("Enviando solicitud de [{}] al usuario [{}]".format(self.clients[connection], self.clients[reciver]))
                                except :
                                    connection.send(encodeJSON(messageType['error'], ">Failed to send message to {}".format(message['target'])))                        
                        else:                                                
                            reciver = self.getVecino(message['target'])
                            self.clientsSem.acquire()
                            reciver = self.getUserFromName(reciver)
                            self.clientsSem.release()
                            if reciver :
                                try:
                                    reciver.send(encodeJSON(messageType['test'], "NS", self.clients[connection]))
                                    print("Enviando solicitud de [{}] al usuario [{}]".format(self.clients[connection], self.clients[reciver]))
                                except :
                                    connection.send(encodeJSON(messageType['error'], ">Failed to send message to {}".format(message['target'])))
                    elif "UY" in message['content']:
                        print("Establecer conexión con: {}".format(message['target']))
                        print(self.validUsers.index(message['target']))                        
                        reciver = message['target']
                        self.clientsSem.acquire()
                        reciver = self.getUserFromName(reciver)
                        self.clientsSem.release()
                        if reciver :
                            try:
                                reciver.send(encodeJSON(messageType['test'], "UY", self.clients[connection]))
                                print("Enviando solicitud de [{}] al usuario [{}]".format(self.clients[connection], self.clients[reciver]))
                            except :
                                connection.send(encodeJSON(messageType['error'], ">Failed to send message to {}".format(message['target'])))
                    elif "LP" in message['content']:                        
                        reciver = self.getVecino(self.clients[connection])
                        self.clientsSem.acquire()
                        reciver = self.getUserFromName(reciver)
                        self.clientsSem.release()
                        if reciver :
                            try:
                                reciver.send(encodeJSON(messageType['test'], "LP", self.clients[connection]))
                                print("Solicitando lista de pendientes de {} a {}".format(self.clients[connection], self.getVecino(self.clients[connection])))
                            except :
                                connection.send(encodeJSON(messageType['error'], ">Failed to send message to {}".format(self.clients[connection])))
            except:
                print("Conexión perdida con: {}".format(username))
                self.removeUser(connection)
                break
        self.activeNodes[username] = False
        print(self.activeNodes)

    def validName(self, username):
        for user in self.validUsers:
            if user == username:
                return True
        return False
    def allOnline(self):
        return (self.activeNodes["A"] and self.activeNodes["B"] and self.activeNodes["C"] and self.activeNodes["D"])

    def restoreFromFall(self, tar):
        time.sleep(4.0)
        tar.send(encodeJSON(messageType['test'], "RFF", self.getVecino(self.clients[tar])))

    def interface(self):
        while True:
            aux = input("[Server]: ")
            if aux == "backup":
                self.copiar()                
            elif aux == "pro_mode 1":
                print("Modo pro activado")
                self.pro_mode = True
            elif aux == "pro_mode 0":
                print("Modo pro desactivado")
                self.pro_mode = False
    def copiar(self):
        for connection, user in self.clients.items():
            try:
                connection.send(encodeJSON(messageType['test'], "CA", self.getVecino(self.clients[connection]) ) )
                print("{} iniciando copias a: {}".format(self.clients[connection], self.getVecino(self.clients[connection]) ) )
            except :
                print("Falla crítica en copias")

    def getVecino(self, nodo):
        return self.validUsers[(self.validUsers.index(nodo) + 1) % 4]

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
                        

