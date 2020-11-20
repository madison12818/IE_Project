from Peer import *

def main():
    print("Resource Server:")
    rs = Peer('rs','RS_Policy.json', 'RS_Resource.json', 6869)
    print("\n")

if __name__ == "__main__":
    main()