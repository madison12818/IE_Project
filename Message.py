

class Message:
    def __init__(self, messageType, resource, issuer, subject, originalRequester=0):
        self.messageType = messageType
        self.resource = resource
        self.issuer = issuer
        self.subject = subject
        self.originalRequester = originalRequester

