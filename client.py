import socket
import threading
import sys
import pickle
from jsonutils import encodeJSON, decodeJSON, messageType
import time
from notifications import Notitfication
import os
import random
import tqdm
import _thread
import json
from server import Server
SEPARATOR = "<SEPARATOR>"
connected = True
BUFFER_SIZE = 1024 * 4 #4KB
## getting the hostname by socket.gethostname() method
hostname = socket.gethostname()
## getting the IP address using socket.gethostbyname() method
ip_address = socket.gethostbyname(hostname)

class Client():

    def __init__(self, host, port):
        self.HOST = host
        self.PORT = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.message = dict()
        self.status = ""
        self.conected = False
        self.waiting = False
        self.validUser = False
        self.reciver = None
        self.window = None
        self.user = ""
        self.online_clients = "None"
        self.file_TCP = None
        self.backup=[]
        self.clients=[]
        self.cola=[]
        self.clients_comps = []
        try:
            self.client.connect((self.HOST, self.PORT))
            print("[SERVER]: Conexion establecida")
        except socket.error:
            print("constructor error")
        _thread.start_new_thread(Server, (2000, ))

    def startListenServer(self):
        self.reciver = threading.Thread(target=self.reciveMessage)
        self.reciver.setDaemon(True)
        self.reciver.start()

    def reciveMessage(self):
        while True :
            try:
                #print("recibiendo mensajes")
                message = self.client.recv(8192)
                message = decodeJSON(message)
                if message['type'] == messageType['login']:
                    Notitfication("Usuario conectado", "El usuario {} se ha conectado con el servidor".format(message['content']))   
                    self.online_clients = message['content']
                    self.updateList(self.online_clients.split(" "))
                    time.sleep(2)
                    self.window.actualizarContactos()
                if message['type'] == messageType['info']:
                    self.online_clients = message['content']
                    self.updateList(self.online_clients.split(" "))
                    time.sleep(2)
                    self.window.actualizarContactos()
                if message['type'] == messageType['request']:
                    print("llego la petición")
                    if "OK" in message['content']:
                        _, ip_h, port_h = message['content'].split("-")                        
                        senderThread = threading.Thread(target=self.createTCPSender, args= (ip_h, port_h))
                        senderThread.start()
                        senderThread.join()
                    elif "NO" in message['content']:
                        pass
                    #if message['content'] != "OK" or message['content'] != "NO":
                    else:
                        Notitfication("Solicitud de tranferencia de archivo", message['content'])
                        if self.window.askmsg("Aviso!", message['content']):
                            port_tcp = 5001
                            reciverThread = threading.Thread(target=self.createTCPReciver, args= (port_tcp, ))
                            reciverThread.start()
                            self.client.send(encodeJSON(messageType['request'], "OK-{}".format(port_tcp), message['target']))
                            reciverThread.join()
                        else :
                            Notitfication("Solicitud rechazada", "La solicitud de transferencia de archivos fue rechacahzada")
                if message['type'] == messageType['back']:
                    self.backup=message['content'].split()
                    time.sleep(0.5)
                    print("me llego el backup: {}".format(self.backup))
                if message['type'] == messageType['update']:
                    self.updateDir(message['target'], message['content'])
                if message['type'] == messageType['upsignal']:
                    self.window.sendTree()
                if message['type'] == messageType['filesend']:
                    info=message['content'].split("#")
                    self.sendRequestFile(self.window.rootPath+"\\"+info[0], info[1])
                if message['type'] == messageType['remotedel']:
                    print("voy a eliminar"+message['content'])
                    os.remove(message['content'])
                    self.window.sendTree()
                if message['type'] == messageType['test']:
                    if "SY" in message['content']:
                        print("Set en mis datos")
                        try:
                            info=message['content'].split("*")#############
                            self.sendRequestFile(self.window.rootPath+"\\"+info[0], info[1])#################
                            self.client.send(encodeJSON(messageType['test'], "UV", ""))
                            print("Enviando solicitud de actualización de respaldo a vecino")
                        except :
                            print("Falla crítica")
                    elif "SV" in message['content']:
                        print("Set en los datos del vecino, añadida accion a la cola")
                        self.cola.append(message)
                        print(self.cola)
                    elif "UY" in message['content']:
                        print("Actualizando datos con los datos del respaldo de vecino")  
                        self.myThread = threading.Thread(target = self.atenderSolicitudFinal)
                        self.myThread.setDaemon = True
                        self.myThread.start()
                    elif "UV" in message['content']:
                        print("Actualizando datos de respaldo del vecino")
                    elif "CA" in message['content']:
                        print("Mandando datos a vecino: {}".format(message['target']))
                    elif "LP" in message['content']:
                        print("Accediendo a lista de pendientes de: {}".format(message['target']))
                        if len(self.cola) > 0:
                            self.myThread = threading.Thread(target = self.enviarLista, args=(message['target'], ))
                            self.myThread.setDaemon = True
                            self.myThread.start()
                    elif "RFF" in message['content']:
                        print("Restaurando de caída: {}".format(message['target']))                        
                        try:
                            self.client.send(encodeJSON(messageType['test'], "LP", ""))
                            print("Enviando solicitud de acceso a respaldo a vecino")
                        except :
                            print("Falla crítica")
                    else:
                        print("simón, ya escuché")
                    time.sleep(0.5)
            except socket.error:
                self.repair()
            except ValueError:
                pass

    def validUserName(self, user):
        self.user = user
        self.client.send(encodeJSON(messageType['username'], str(user)))
        messageyype = messageType['none']
        while messageyype != messageType['username'] :
            message = self.client.recv(1024)
            message = decodeJSON(message)
            messageyype = message['type']
        self.status = message['content']
        if self.status == "OK":
            return True
        else :
            return False

    def enviarLista(self, tar):
        while(len(self.cola) > 0):
            time.sleep(2.0)
            instruction = self.cola.pop()
            try:
                self.client.send(encodeJSON(messageType['test'], "UY", tar))
                print("Enviando instruccion")
            except :
                print("Falla crítica")
    def createTCPSender(self, ip, port):
        sender = socket.socket()
        sender.connect((ip, int(port)))
        name = os.path.basename(self.file_TCP)
        filesize = os.path.getsize(self.file_TCP)
        sender.send(f"{name}{SEPARATOR}{filesize}".encode())
        progress = tqdm.tqdm(range(filesize), f"Sending {name}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(self.file_TCP, "rb") as f:
            for _ in progress:
                # read the bytes from the file
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    # file transmitting is done
                    break
                # we use sendall to assure transimission in 
                # busy networks
                sender.sendall(bytes_read)
                # update the progress bar
                progress.update(len(bytes_read))
        # close the socket
        sender.close()
        print("Se envio por completo")

    def atenderSolicitudFinal(self):
        time.sleep(5.0)
        print("Solicitud procesada exitosamente")

    def createTCPReciver(self, port):
        receiver = socket.socket()
        # bind the socket to our local address
        receiver.bind(("0.0.0.0", port))
        receiver.listen(1)
        sender_socket, address = receiver.accept()
        print(f"[+] {address} is connected.")
        received = sender_socket.recv(BUFFER_SIZE).decode()
        name, filesize = received.split(SEPARATOR)
        # remove absolute path if there is
        name = os.path.basename(name)
        # convert to integer
        filesize = int(filesize)
        # start receiving the file from the socket
        # and writing to the file stream
        progress = tqdm.tqdm(range(filesize), f"Receiving {name}", unit="B", unit_scale=True, unit_divisor=1024)
        folder_path = self.window.rootPath+"\\"
        file_name = folder_path + name
        with open(file_name, "wb") as f:
            for _ in progress:
                # read 1024 bytes from the socket (receive)
                bytes_read = sender_socket.recv(BUFFER_SIZE)
                if not bytes_read:    
                    # nothing is received
                    # file transmitting is done
                    break
                # write to the file the bytes we just received
                f.write(bytes_read)
                # update the progress bar
                progress.update(len(bytes_read))

        # close the client socket
        sender_socket.close()
        # close the server socket
        receiver.close()

        Notitfication("Archivo guardado", "El archivo {} fue guardado en: {}".format(name, folder_path))

    def setWindow(self, win):
        print("ventana añadida")
        self.window = win

    def updateDir(self, user, tree):
        self.window.updateDir(user, json.loads(tree))

    def updateList(self, received):
        for element in received:
            if element in self.clients:
                pass
            else:
                self.clients.append(element)
    def testEnvio(self, dest, mode,accion):
        try:            
            self.client.send(encodeJSON(messageType['test'],mode, dest, accion))#################
            print("Solicito a servidor comunicación con: {}".format(dest))
        except socket.error:
            print("f")
            self.repair()
    def sendRequestFile(self, title, destin):
        try:
            self.file_TCP = title
            self.client.send(encodeJSON(messageType['request'], os.path.basename(title), destin))
            print("Envío solicitud")
        except socket.error:
            self.repair()
    def sendSignalTo(self, destino):
        try:
            self.client.send(encodeJSON(messageType['upsignal'], destino))
            print("le voy a pedir update a: {}".format(destino))
        except socket.error:
            self.repair()
    def sendFileReqTo(self,filedir, sender, receiver):
        aux=filedir+"#"+sender
        try:
            print("le voy a pedir archivo a: {}".format(receiver))
            self.client.send(encodeJSON(messageType['filesend'], aux,receiver))
        except socket.error:
            self.repair()
    def updateclients(self):
        return self.clients
    def remoteDelete(self, filedir, client):
        try:
            self.client.send(encodeJSON(messageType['remotedel'],filedir,client))
        except socket.error:
            self.repair()
    def disconect(self):
        try:
            self.client.send(encodeJSON(messageType['logout']))
            Notitfication("Desconeccion de usuario", "El usuario {} se ha desconectado del servidor".format(self.user))
        except socket.error:
            self.repair()
    
    def repair(self):
        connected = False          
        self.client = socket.socket()          
        print( "connection lost... reconnecting" )
        backport=2000          
        while not connected:
            if (backport>=2004 or backport==2000):
                ip=self.backup.pop(0)
                print(ip)                
            try:
                print("intentando conectar con: {}".format(ip))                                   
                self.client.connect((ip,backport))  
                connected = True
                print("Coneccion exitosa")
                if connected==True:
                    try:
                        self.validUserName(self.user)
                    except ValueError:
                        time.sleep(1)
                        self.validUserName(self.user)            
            except socket.error:
                backport+=1                  
                time.sleep( 2 )

    def sendFileTree(self, tree):
        print("Enviando")
        test = encodeJSON(messageType['update'], json.dumps(tree), self.user)
        print(sys.getsizeof(test))
        self.client.send(test)
        print("Enviado")
        
    
    def setUserName(self, username):
        self.username = username
        self.waiting = False

    def getUserName(self):
        while self.waiting :
            pass
        return self.username
