from Peer import *

def main():
    print("Client:")
    client = Peer('client', 'Client_Policy.json', 'Client_Resource.json', 6868)
    print("\n")

    initialMsg = Message("request", "C1", 6868, 6869)
    client.sendMessage(initialMsg, 6869)

if __name__ == "__main__":
    main()