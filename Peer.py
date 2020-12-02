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
from collections import deque
#add dictionary of port locations so servers can find eachother
resourceLookup = dict()
resourceLookup['C1'] = 6869
resourceLookup['C2'] = 6870
resourceLookup['C3'] = 6871
resourceLookup['C4'] = 6868
##############################################################################
class Peer():
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
      
      #incoming message queue
      self.messageQueue = deque()

      #messages sent
      self.MSent = deque()

      #messages recieved
      self.MRecieved = deque()

      self.printPolicies()
      self.printResources()

      #begin receiving messages in seperate thread
      recvThread = threading.Thread(target=self.recieveMessage, args=[])
      recvThread.start()

      #begin participateInOAuth in seperate thread
      OAuthThread = threading.Thread(target=self.participateInOAuth, args=[])
      OAuthThread.start()

   def recieveMessage(self):
      while True:
         r = self.fd.recvfrom(1000)
         recievedMsg = str(r[0], "utf-8")

         #convert the received msg from a str to a Message obj
         recievedMsg = json.loads(recievedMsg)
         recievedMsg = Message(**recievedMsg)
         print('{} recieved: Message[messageType:{}, resource:{}, issuer:{}, subject:{}]'.format(self.name, recievedMsg.messageType, recievedMsg.resource, recievedMsg.issuer, recievedMsg.subject))
         #add the message to the incoming message queue
         self.messageQueue.appendleft(recievedMsg)

   def sendMessage(self, message, port):
      #convert the recieved Message obj to a json string
      jsonMsg = json.dumps(message.__dict__) 

      #send the json string
      self.fd.sendto(bytearray(jsonMsg, "utf-8"), (self.udp_ip, port))
      print('{} sent: Message[messageType:{}, resource:{}, issuer:{}, subject:{}]'.format(self.name, message.messageType, message.resource, message.issuer, message.subject))

   def participateInOAuth(self):
      while True:
         if self.messageQueue:
            #queue not empty, do work
            msg = self.messageQueue.pop()
            self.processMessage(msg)
         else:
            #empty queue, sleep for a little
            time.sleep(10)

   def processMessage(self, m):
      self.MRecieved.appendleft(m)
      if m.messageType == 'offer':
         self.resources[m.resource] = True
      msgs = self.resolutionResolver(self.MRecieved, self.MSent)
      for msg in msgs:
         self.MSent.appendleft(msg)
         self.sendMessage(msg, msg.subject)

   def resolutionResolver(self, MReceived, MSent):
      print('\n====Resolution Resolver====')

      #latest message received
      m = MReceived[0]
      print("latest message: Message[messageType:{}, resource:{}, issuer:{}, subject:{}]".format(m.messageType, m.resource, m.issuer, m.subject))

      #set of credentials pthis requested from others
      Qsent = set()
      for msg in MSent:
         if msg.messageType == 'request':
            Qsent.add(msg.resource)
      print("Peer has requested: {}".format(Qsent))

      #set of credentials others requested from pthis
      Qrecieved = set()
      for msg in MReceived:
         if msg.messageType == 'request':
            Qrecieved.add(msg.resource)
      print("Other peers have requested: {}".format(Qrecieved))

      #set of credentials pthis sent to others
      Dsent = set()
      for msg in MSent:
         if msg.messageType == 'offer':
            Dsent.add(msg.resource)
      print("Peer has offered: {}".format(Dsent))

      #set of credentials pthis recieved from others
      Drecieved = set()
      for msg in MReceived:
         if msg.messageType == 'offer':
            Drecieved.add(msg.resource)
      print("Other peers have offered: {}".format(Drecieved))

      #if incoming msg resource not in self.policies
         #check if resource is in resourceLookup
            #if it is send message to location resource is located
         #else send error and quit
      if m.resource not in self.policies:
         messages = list()
         if m.resource in resourceLookup:
            m.issuer = self.udp_port
            m.subject = resourceLookup[m.resource]
            messages.append(m)
            return messages
         else:
            print("Resource {} can't be found".format(m.resource))
            return messages
         

      #Calculate new credentials Dnew that Pthis will send to other parties  

      #isUnlocked is True if all credentials required for a resource have been received    
      isUnlocked = True
      for policy in self.policies[m.resource]:
         print("--policyCheck:{}".format(policy))
         #if the policy is true, resource is available
         if policy == 'True':
            break
         #if this peer hasn't recieved any credentials, then resource not available
         if Drecieved == set():
            isUnlocked = False
            break
         #if every credential in policies has been received, then resource is unlocked, otherwise keep resource unavailable
         if policy not in Drecieved:
            isUnlocked = False

      print("isUnlocked:{}".format(isUnlocked))

      #credentials to offer 
      Dnew = set()

      #credentials to request
      Qnew = set()

      if m.messageType == 'offer':
         Dunlocked = Drecieved

         if isUnlocked:
            Dunlocked.add(m.resource)

         Dnew = Dunlocked & (Qrecieved - Dsent)
      elif m.messageType == 'request' and isUnlocked:
         Dnew.add(m.resource)
      else:
         Drelevant = set(self.policies[m.resource])
         Qnew = Drelevant - Drecieved - Qsent
      
      print("Credentials to be offered: {}".format(Dnew))
      print("Credentials to be requested: {}".format(Qnew))

      messages = list()
      for credential in Dnew:
         sendTo = m.issuer
         messages.append(Message('offer', credential, self.udp_port, sendTo))
      
      for credential in Qnew:
         sendTo = 6868 if self.name != 'client' else resourceLookup[m.resource]
         messages.append(Message('request', credential, self.udp_port, sendTo))

      print("===End of resolution algo===")
      return messages

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

