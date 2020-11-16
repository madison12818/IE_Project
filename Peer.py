'''

Peer class has the following components:
1. Resource data structure (L) : a JSON format file: { “C1”: “discount 20%”
                                                       “C2”: “Credit Score 780”
                                                       “C3”: “Alex.kent.edu”,
                                                       “C4”: “ID81023456”
                                                     }
2. Policy data structure: a JSON format file { “C1”:[[“C2”, “C3”],
                                               “C2”: [True],
                                               “C3”: [“C4”],
                                               “C4”: “TRUE”
                                             }

3. send a message method: call the message class and create a message to other peers
4. Receive a message method:
5. Resolution Resolver: an algorithm that will be invoked when a message m is received. It extracts the
   requested credential (C) from the message, check the policy and send new messages to request all the item
   in the policy from different parties. See the example in Resolution_Resolver.py

'''
