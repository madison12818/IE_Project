from Peer import *

def main():
    print("Client:")
    client = Peer('client', 'Client_Policy.json', 'Client_Resource.json', 6868)
    print("\n")

    initialMsg = Message("request", "C1", "client", "rs")
    jsonMsg = json.dumps(initialMsg.__dict__) 
    client.sendMessage(jsonMsg, 6869)

if __name__ == "__main__":
    main()