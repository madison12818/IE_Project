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
import json
import time
from Message import *
import socket
import multiprocessing
import threading
from queue import Queue, LifoQueue
#add dictionary of port locations so servers can find each other

##############################################################################
class Peer:
   def __init__(self, name, policyFileName, resourceFileName, port):
      #set a name to peer
      self.name = name

      #get policies from json
      with open(policyFileName) as json_file:
         self.policies = json.load(json_file)
      
      #get resources from json
      with open(resourceFileName) as json_file:
         self.resources = json.load(json_file)

      #set up client/server props
      try:
         self.fd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      except socket.error as err:
         'unable to create socket: {}'.format(err)

      self.udp_ip = '127.0.0.1'
      self.udp_port = port
      self.fd.bind((self.udp_ip,self.udp_port))
      
      #message queue
      self.messageQueue = Queue(128)

      #past message stacks
      self.mrecv = LifoQueue(128)
      self.msent = LifoQueue(128)

      self.printPolicies()
      self.printResources()

      #begin receiving messages in seperate thread
      recvThread = threading.Thread(target=self.recieveMessage, args=[])
      recvThread.start()

   def recieveMessage(self):
      while True:
         r = self.fd.recvfrom(1000)
         recievedMsg = str(r[0], "utf-8")
         print('{} recieved Message: {}'.format(self.name, recievedMsg))

   def sendMessage(self, message, port):
      self.fd.sendto(bytearray(message, "utf-8"), (self.udp_ip, port))
      print("msg sent {}".format(message))

   #print loaded policies
   def printPolicies(self):
      print("Policies:")
      for policy in self.policies:
         print("  {}: {}".format(policy, self.policies[policy]))

   #print loaded resources
   def printResources(self):
      print("Resources:")
      for resource in self.resources:
         print("  {}: {}".format(resource, self.resources[resource]))

   def resolutionResolver(self):
      message = self.mrecv.get()
      if message.resource not in self.resources:
         tosend = Message('error', message.resource, self.name, message.issuer)
         self.sendMessage(tosend, 6868)
      else:
         for policy in self.policies:
            if policy


   def participateInOAuth(self):
      while True:
         if not self.messageQueue.empty():
            message = self.messageQueue.get()
            self.processMessage(message)
         else:
            time.sleep(0.2) #may change this delay

   def processMessage(self, message):
      self.mrecv.put(message)
      if message.type == 'request':
         messageList = self.resolutionResolver()
         if messageList:
            for m in messageList:
               self.sendMessage(m, 6869)
               self.mrecv.put(m)
