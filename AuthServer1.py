from Peer import *

def main():
    print("Auth Server 1:")
    as1 = Peer('as1', 'AS1_Policy.json', 'AS1_Resource.json', 6870)
    print("\n")

if __name__ == "__main__":
    main()