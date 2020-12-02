
#ex: message(request, C2, RS,     client)
#    message(request, C2, client, AS1   )
#    message(offer,   C2, issuer, client)

class Message:
    def __init__(self, messageType, resource, issuer, subject):
        self.messageType = messageType
        self.resource = resource
        self.issuer = issuer
        self.subject = subject

def MessageDecoder(obj):
    if '__type__' in obj and obj['__type__'] == 'Message':
        return Message(obj['messageType'], obj['resource'], obj['issuer'], obj['subject'])