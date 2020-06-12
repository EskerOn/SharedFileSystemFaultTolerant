from tkinter import *
from tkinter import ttk
from tkinter.font import Font
import tkinter.filedialog
import socket
import threading
import client
import time
from os import getcwd
import os
from tkinter import messagebox
from PIL import Image
from PIL import ImageTk

import os
from utils import *
import math
import _thread
chatrooms = []
users = []
socketclient = None

clientapp = None
clientroot = None
root = None
username = ""
tabIndex=0
chatsLog = dict()

socketcreated = False
# ------------------- [START GLOBAL VARIABLES] -------------------
IMG_WIDTH = 70
IMG_HEIGHT = 70
MAX_COLUMNS = 4

#FILE IMAGE
img = Image.open(os.getcwd() + r"\res\file.png")
img = img.resize((IMG_WIDTH, IMG_HEIGHT), Image.ANTIALIAS)
fileImg = ImageTk.PhotoImage(img)

#FOLDER IMAGE
img = Image.open(os.getcwd() + r"\res\folder.png")
img = img.resize((IMG_WIDTH, IMG_HEIGHT), Image.ANTIALIAS)
folderImg = ImageTk.PhotoImage(img)

#AUDIO IMAGE
img = Image.open(os.getcwd() + r"\res\audio_file.png")
img = img.resize((IMG_WIDTH, IMG_HEIGHT), Image.ANTIALIAS)
audioImg = ImageTk.PhotoImage(img)

#PDF IMAGE
img = Image.open(os.getcwd() + r"\res\pdf_file.png")
img = img.resize((IMG_WIDTH, IMG_HEIGHT), Image.ANTIALIAS)
pdfImg = ImageTk.PhotoImage(img)

#IMAGE IMAGE
img = Image.open(os.getcwd() + r"\res\image_file.png")
img = img.resize((IMG_WIDTH, IMG_HEIGHT), Image.ANTIALIAS)
imgImg = ImageTk.PhotoImage(img)

#TEXT IMAGE
img = Image.open(os.getcwd() + r"\res\text_file.png")
img = img.resize((IMG_WIDTH, IMG_HEIGHT), Image.ANTIALIAS)
txtImg = ImageTk.PhotoImage(img)

#CODE IMAGE
img = Image.open(os.getcwd() + r"\res\code_file.png")
img = img.resize((IMG_WIDTH, IMG_HEIGHT), Image.ANTIALIAS)
codeImg = ImageTk.PhotoImage(img)

#EXEL IMAGE
img = Image.open(os.getcwd() + r"\res\exel_file.png")
img = img.resize((IMG_WIDTH, IMG_HEIGHT), Image.ANTIALIAS)
exelImg = ImageTk.PhotoImage(img)

#WORD IMAGE
img = Image.open(os.getcwd() + r"\res\word_file.png")
img = img.resize((IMG_WIDTH, IMG_HEIGHT), Image.ANTIALIAS)
wordImg = ImageTk.PhotoImage(img)

#POWER IMAGE
img = Image.open(os.getcwd() + r"\res\powerpoint_file.png")
img = img.resize((IMG_WIDTH, IMG_HEIGHT), Image.ANTIALIAS)
poweImg = ImageTk.PhotoImage(img)

#VIDEO IMAGE
img = Image.open(os.getcwd() + r"\res\video_file.png")
img = img.resize((IMG_WIDTH, IMG_HEIGHT), Image.ANTIALIAS)
videoImg = ImageTk.PhotoImage(img)

#ZIP IMAGE
img = Image.open(os.getcwd() + r"\res\zip_file.png")
img = img.resize((IMG_WIDTH, IMG_HEIGHT), Image.ANTIALIAS)
zipImg = ImageTk.PhotoImage(img)

# ------------------- [ENDS GLOBAL VARIABLES] -------------------

class Login(Frame):

    def __init__(self, parent):
        self.parent = parent
        self.parent.title("FTP v1.0 beta [Login]")
        self.TITLE_FONT = Font(parent, family="Courier", size=24)
        self.HEADER_FONT = Font(parent, family="Courier", size=16)
        self.NORMAL_FONT = Font(parent, family="Courier", size=10)
        self.BG_COLOR = '#313131'
        self.FG_COLOR = '#DDDDDD'
        self.parent.resizable(False, False)
        self.x = int((self.parent.winfo_screenwidth() - self.parent.winfo_reqwidth()) / 5.4)
        self.y = int((self.parent.winfo_screenheight() - self.parent.winfo_reqheight()) / 1.9)
        self.parent.geometry("{}x{}".format(self.x, self.y))
        self.initComponents()

        self.topLevel = None


    def initComponents(self):
        #Direccion IP.
        Label(self.parent, text = "Direccion IP: ", font = self.NORMAL_FONT).grid(row = 0, column = 0, padx = 5, pady = 5, sticky = 'w')
        self.ip_str = StringVar()
        self.ip_str.set("127.0.0.1")
        self.ip_entry = Entry(self.parent, textvariable = self.ip_str, width = 28, font = self.NORMAL_FONT)
        self.ip_entry.grid(row = 1, column = 0, padx = 5, pady = 5, sticky ='w')

        #Carpeta compartida.
        Label(self.parent, text = "Carpeta compartida :", font = self.NORMAL_FONT).grid(row = 2, column = 0, padx = 5, pady = 5, sticky = 'w')
        self.panel_folder = Frame(self.parent)
        self.shared_folder_str = StringVar()
        self.shared_folder_str.set("C:\\Users\\alexe\\Downloads\\concurrente")
        self.folder_entry = Entry(self.panel_folder, textvariable = self.shared_folder_str, width = 20, font = self.NORMAL_FONT)
        self.folder_entry.grid(row = 0, column = 0, padx = 2, pady = 2)
        self.btn_folder = Button(self.panel_folder, text = "Buscar", font = self.NORMAL_FONT, command = self.searchFolder)
        self.btn_folder.grid(row = 0, column = 1, padx = 2, pady = 2, )
        self.panel_folder.grid(row= 3, column = 0, padx = 5, pady = 5)

        self.user_txt = Label(self.parent, text = "Nombre de equipo: ", font = self.NORMAL_FONT)
        self.user_txt.grid(row = 4, column = 0, padx = 5, pady = 5, sticky = 'w')
        self.user_str = StringVar()
        self.user_str.set("Edgar")
        self.user_entry = Entry(self.parent, textvariable = self.user_str, width = 28, font = self.NORMAL_FONT)
        self.user_entry.grid(row = 5, column = 0, padx = 5, pady = 5, sticky = 'w')
        self.user_entry.focus_set()

        self.btn_aceptar = Button(self.parent, text = "Aceptar", font = self.NORMAL_FONT, command = self.connectToServer)
        self.btn_aceptar.grid(row = 6, column = 0, padx = 5, pady = 5)

        self.btn_aceptar = Button(self.parent, text = "Cancelar", font = self.NORMAL_FONT, command = self.closeApp)
        self.btn_aceptar.grid(row = 7, column = 0, padx = 5, pady = 5)
    
    def popupmsg(self, error, msg):
        LARGE_FONT= ("Verdana", 12)
        NORM_FONT = ("Helvetica", 10)
        SMALL_FONT = ("Helvetica", 8)
        popup = Tk()
        popup.wm_title(error)
        label = ttk.Label(popup, text=msg, font=NORM_FONT)
        label.pack(side="top", fill="x", pady=10)
        B1 = ttk.Button(popup, text="Okay", command = popup.destroy)
        B1.pack()
        popup.mainloop()
    
    def searchFolder(self):
        file_c = tkinter.filedialog.askdirectory(initialdir = os.path.expanduser("~/"),title = "Select shared folder")
        file_name = os.path.basename(file_c)
        self.shared_folder_str.set(file_c)

    def connectToServer(self):
        global socketcreated, socketclient, clientapp, clientroot, username

        anyError = False
        try :
            socket.inet_aton(self.ip_str.get())
            p = 1908
        except OSError:
            self.popupmsg("Error!", "IP no valida, favor de ingresar una ip valida")
            anyError = True
        except ValueError:
            self.popupmsg("Error!", "Puerto no valido, favor de ingresar un puerto valido")
            anyError = True
        username = self.user_str.get()
        if username == str():
            self.popupmsg("Error!", "Usuario vacio, ingrese un usuario")
            anyError = True
        elif ' ' in username :
            self.popupmsg("Error!", "El usuario no puede contener espacios, intente nuevamente")
            anyError = True
        if not anyError and not socketcreated:
            socketclient = client.Client("127.0.0.1", 1908) ####################################################
            socketcreated = True
        if not socketclient.validUserName(self.user_str.get()):
            username = self.user_str.get()
            self.popupmsg("Error!", "El usuario usado, ingrese otro usuario")
            anyError = True
        else :
            socketclient.startListenServer()           
            time.sleep(1)
            self.topLevel = Toplevel()
            app = MainApp(self.topLevel, self.shared_folder_str.get(), self.user_str.get())
            self.topLevel.protocol("WM_DELETE_WINDOW", lambda : self.onClosing(self.topLevel))
            self.topLevel.mainloop()


    def onClosing(self, frame):
        frame.destroy()

    def closeApp(self):
        exit(1)

class MainApp(Frame):

    global fileImg, folderImg, audioImg, pdfImg, imgImg, txtImg, codeImg, exelImg, wordImg, poweImg, videoImg, zipImg

    def __init__(self, parent, path : str, name : str):
        self.parent = parent
        self.parent.title("FTP v1.0 beta [Main Window]")
        self.TITLE_FONT = Font(parent, family="Courier", size=24)
        self.HEADER_FONT = Font(parent, family="Courier", size=16)
        self.NORMAL_FONT = Font(parent, family="Courier", size=10)
        self.BG_COLOR = '#313131'
        self.FG_COLOR = '#DDDDDD'
        self.parent.resizable(False, False)
        self.parent.tk_setPalette(background = self.BG_COLOR, foreground = self.FG_COLOR)
        self.x = int((self.parent.winfo_screenwidth() - self.parent.winfo_reqwidth()) / 1.7)
        self.y = int((self.parent.winfo_screenheight() - self.parent.winfo_reqheight()) / 1.6)
        self.parent.geometry("{}x{}".format(self.x, self.y))
        self.rootPath = path
        self.username = name
        self.onlineComputers = []
        self.computer = Computer(name, path)
        #self.computer2 = Computer("Alejandro", "C:\\Users\\52951\\Downloads")
        self.computers = list()
        self.computers.append(self.computer)
        #self.computers.append(self.computer2)
        self.tabs = list()
        self.current_tab = None
        socketclient.setWindow(self)
        self.initComponents()

    def initComponents(self):
        self.tabsFrame = ttk.Notebook(self.parent, height = self.y, width = int(self.y * 1.45)) 
        #self.tabsFrame = ttk.Notebook(self.parent)
        #self.tabsFrame.pack(fill = 'both', side = LEFT)
        self.tabsFrame.grid(row = 0, column = 0, columnspan = 2)
        self.tabsFrame.bind("<<NotebookTabChanged>>", self.changeTab)
        self.initTabs(self)
        self.current_tab = self.tabs[0]
        print("n tabs = ", len(self.tabs))
        separacion = 15
        sep_y = 5

        #self.side_panel = Frame(self.parent, width = myTab.winfo_screenwidth() - self.x)
        self.side_panel = Frame(self.parent, width = self.x - int(self.y * 1.45))

        self.info_panel = Frame(self.side_panel)
        Label(self.info_panel, text = "Info panel").grid(row = 0, column = 0, padx = separacion)
        Label(self.info_panel, text = "Nombre del archivo").grid(row = 1, column = 0, padx = separacion)
        self.name_str = StringVar()
        self.name_str.set(" ")
        Entry(self.info_panel, textvariable = self.name_str, state = DISABLED).grid(row = 2, column = 0, padx = separacion)
        Label(self.info_panel, text = "Tamaño").grid(row = 3, column = 0, padx = separacion)
        self.file_size_str = StringVar()
        self.file_size_str.set(" ")
        Entry(self.info_panel, textvariable = self.file_size_str, state = DISABLED).grid(row = 4, column = 0, padx = separacion)
        Label(self.info_panel, text = "Fecha de creación").grid(row = 5, column = 0, padx = separacion)
        self.created_date_str = StringVar()
        self.created_date_str.set(" ")
        Entry(self.info_panel, textvariable = self.created_date_str, state = DISABLED).grid(row = 6, column = 0, padx = separacion)
        self.info_panel.pack()

        self.buttons_panel = Frame(self.side_panel)
        Button(self.buttons_panel, text = "Regresar", command = self.backDirectory, width = 20).grid(row = 0, column = 0, pady = sep_y * 2, padx = separacion)
        Button(self.buttons_panel, text = "Enviar", command = self.sendFileTo, width = 20).grid(row =  1, column = 0, pady = sep_y, padx = separacion)
        Button(self.buttons_panel, text = "Transferir", command = self.requestFileFrom, width = 20).grid(row =  2, column = 0, pady = sep_y, padx = separacion)
        Button(self.buttons_panel, text = "Eliminar", command = self.deleteDirectory, width = 20).grid(row =  3, column = 0, pady = sep_y, padx = separacion)
        self.buttons_panel.pack()

        self.side_panel.grid(row = 0, column = 3)
        #self.side_panel.pack(fill = 'both', side = RIGHT)

    def addTabs(self, pc, parent):
        print("añadiendo tabs")
        myTab = ScrollableFrame(self.tabsFrame)
        tab = FileExplorer(myTab.scrollable_frame, pc.tree, parent, pc.name)
        self.tabs.append(tab)
        tab.pack()
        self.tabsFrame.add(myTab, text = pc.name)

    def actualizarContactos(self):
        global username, socketclient
        print("actualizando contactos")
        onlineClients= socketclient.updateclients()
        time.sleep(0.5)
        connectUsers = []
        if onlineClients!=None:
            for user in onlineClients :
                if user != " " and user != username and user!="":
                    newpc=Computer(user, None)
                    self.computers.append(newpc)  #### se agregan los arboles de los clientes 
                    connectUsers.append(user)
                    self.addClient(user)
                    self.addTabs(newpc, self)
        print("Contactos actualizados: ")
        for pc in self.computers:
            print(pc.name)

    def initTabs(self, parent):
        for computer in self.computers:
            myTab = ScrollableFrame(self.tabsFrame)
            tab = FileExplorer(myTab.scrollable_frame, computer.tree, parent, computer.name)
            self.tabs.append(tab)
            tab.pack()
            self.tabsFrame.add(myTab, text = computer.name)
        self.actualizarContactos()

    def askmsg(self, titl, msg):
        return messagebox.askyesno(message=msg, title=titl)

    def sendFileTo(self):
        pass
    
    def requestFileFrom(self):
        destino = self.current_tab.name
        file_c = tkinter.filedialog.askopenfilename(initialdir = os.path.expanduser("~/"),title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
        file_name = os.path.basename(file_c)
        socketclient.sendRequestFile(file_c, destino)
    
    def reciveMessageFrom(self, msg):
        pass

    def on_closing(self):
        socketclient.disconect()
        self.parent.destroy()

    def addClient(self, clientname):
        global chatsLog
        if clientname not in users:
            chatsLog[clientname] = ""
        else:
            pass

    def backDirectory(self):
        if(self.current_tab != None):
            self.current_tab.backDirectory()
            self.name_str.set(" ")
            self.file_size_str.set(" ")
            self.created_date_str.set(" ")

    def deleteDirectory(self):
        pass

    def changeTab(self, event):
        global tabIndex
        tabIndex = event.widget.index("current")
        print("toy en la tab", tabIndex)
        self.current_tab = self.tabs[tabIndex]
        print(self.tabs[0])
    
    def popupmsg(self, error, msg):
        LARGE_FONT= ("Verdana", 12)
        NORM_FONT = ("Helvetica", 10)
        SMALL_FONT = ("Helvetica", 8)
        popup = Tk()
        popup.wm_title(error)
        label = ttk.Label(popup, text=msg, font=NORM_FONT)
        label.pack(side="top", fill="x", pady=10)
        B1 = ttk.Button(popup, text="Okay", command = popup.destroy)
        B1.pack()
        popup.mainloop()
    
    def modificateAttribs(self, file):
        if file != None:
            self.name_str.set(file.name)
            self.file_size_str.set(file.attribs['size'])
            self.created_date_str.set(file.attribs['created'])
        else :
            self.name_str.set(" ")
            self.file_size_str.set(" ")
            self.created_date_str.set(" ")


class FileExplorer(Frame):

    def __init__(self, parent, tree : FileTree, mainParent, nombre):
        super().__init__(parent)
        Frame.__init__(self, parent)
        self.parent = parent
        self.mainTree = tree
        self.current_tree = tree
        self.tree_trace = list()
        self.myFrame = self
        self.name = nombre
        self.explorerFrame()
        self.mainParent = mainParent
        _thread.start_new_thread(self.checkForChanges, tuple())
    
    def checkForChanges(self):
        print("iniciado")
        path_to_watch = self.current_tree.path
        before = dict([(f, None) for f in os.listdir(path_to_watch)])
        while True:
            time.sleep(5)
            after = dict([(f, None) for f in os.listdir(path_to_watch)])
            news = [f for f in after if not f in before]
            deleted = [f for f in before if not f in after]
            if len(before) != len(after):
                self.current_tree.updateTree(news, deleted)
                self.clearFrame()
                self.explorerFrame()
            before = after

    def clearFrame(self):
        for widget in self.myFrame.winfo_children():
            widget.destroy()
        #self.myFrame.grid_forget()
        #self.myFrame.pack_forget()
        
    def explorerFrame(self):
        #self.clearFrame()
        try:
            index = 0
            for directory in self.current_tree.directories:
                self.createImageButton(directory.name, True, self.myFrame, index)
                index += 1
            for file in self.current_tree.files:
                self.createImageButton(file.name, False, self.myFrame, index)
                index += 1
        except:
            pass
    def createImageButton(self, name : str, isDir :bool, parent : Tk, index : int):
        global fileImg, folderImg, audioImg, pdfImg, imgImg, txtImg, codeImg, exelImg, wordImg, poweImg, videoImg, zipImg
        _, extt = os.path.splitext(name)
        if extt in [".mp3", ".wav"]:
            photoImg = audioImg
        elif extt in [".pdf"]:
            print("ptooo")
            photoImg = pdfImg
        elif extt in [".png", ".jpg", ".jpeg", ".gif", ".bit"]:
            photoImg = imgImg
        elif extt in [".txt"]:
            photoImg = txtImg
        elif extt in [".c", ".cpp", ".java", ".go", ".js", ".py", ".cs", ".html"]:
            photoImg = codeImg
        elif extt in [".xlsx", ".xlsm", ".xlsb", ".xltx"]:
            photoImg = exelImg
        elif extt in [".doc", ".docx", ".docm", "dotx", ".dotm"]:
            photoImg = wordImg
        elif extt in [".avi", ".mp4", ".mov", ".m4v", ".mpg", ".mpge", ".swf"]:
            photoImg = videoImg
        elif extt in [".ppxt", ".ppx"]:
            photoImg = poweImg
        elif extt in [".zip", ".rar", ".7z", ".tar"]:
            photoImg = zipImg
        else :
            photoImg = fileImg if not isDir else folderImg
        if len(name) > 20:
            texto = name[0:14] + "..."
        else:
            texto = name
        btn = Button(master = parent, text = texto, width = 140, image = photoImg, compound = TOP, command = lambda : self.clickButton(name, isDir))
        btn.grid(row = index // MAX_COLUMNS, column = index % MAX_COLUMNS)
        btn.bind("<Button-3>",self.popupMenu)

    def clickButton(self, name, isDir):
        #print("Current tree: ", self.current_tree.name)
        if isDir:
            self.tree_trace.append(self.current_tree)
            self.mainParent.modificateAttribs(None)
            for direc in self.current_tree.directories:
                if name == direc.name:
                    self.current_tree = direc
                    break
            self.clearFrame()
            self.explorerFrame()
        else:
            file = self.current_tree.searchFile(name)
            if file != None:
                self.mainParent.modificateAttribs(file)
        #print("Current tree: ", self.current_tree.name)
    

    def backDirectory(self):
        self.current_tree = self.tree_trace.pop()
        self.last_tree = None
        self.clearFrame()
        self.explorerFrame()

    def popupMenu(self, event):
        print("Click deresho")

class ScrollableFrame(Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = Frame(canvas)   
        self.scrollable_frame.pack(fill = 'both')

        self.scrollable_frame.bind("<Configure>",lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        #self.width = self.winfo_screenwidth()
        print("Panel:" ,self.winfo_screenwidth())

