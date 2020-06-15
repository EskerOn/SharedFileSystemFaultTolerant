import json

messageType = {
    'none' : 0,  
    'login' : 1,  
    'logout' : 2,
    'username' : 3,
    'info' : 4,
    'request' : 5,
    'error' : 6,
    'back' : 7,
    'update' : 8,
    'upsignal' : 9,
    'filesend' : 10
}

def decodeJSON(message):
    return json.loads(message.decode('utf-8'))
        
def encodeJSON(type, message = None, target = None):
    msg = {
        'type' : type,
        'content' : message,
        'target' : target, 
    }
    return bytes(json.dumps(msg), 'utf-8')
