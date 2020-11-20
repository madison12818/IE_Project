from Peer import *

def main():
    print("Auth Server 2:")
    as2 = Peer('as2', 'AS2_Policy.json', 'AS2_Resource.json', 6871)
    print("\n")

if __name__ == "__main__":
    main()