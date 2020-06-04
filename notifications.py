import os
from plyer import notification
import threading

ICON_PATH = os.getcwd() + "\\favicon.ico"

class Notitfication():
    def __init__(self, title, content):
        self.title = title
        self.content = content
        myThread = threading.Thread(target=self.showNotification)
        myThread.start()
        myThread.join()

    def showNotification(self):
        notification.notify(
            title = self.title,
            message = self.content,
            app_icon = ICON_PATH,
            timeout = 3.5
        )   

