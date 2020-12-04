from Peer import *

def main():
    print("Client:")
    client = Peer('client', 'Client_Policy.json', 'Client_Resource.json', 6868)
    print("\n")

    initialMsg = Message(messageType="request", resource="C1", issuer=6868, subject=6869, originalRequester=6868)
    client.sendMessage(initialMsg, 6869)

if __name__ == "__main__":
    main()