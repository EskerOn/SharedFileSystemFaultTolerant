import json

messageType = {
    'none' : 0,  
    'login' : 1,  
    'logout' : 2,
    'username' : 3,
    'private' : 4,
    'public' : 5,
    'chatroom' : 6,
    'info' : 7,
    'request' : 8,
    'error' : 9,
    'back' : 10
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
