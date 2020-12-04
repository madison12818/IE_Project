'''

To run:
   1. open 4 terminal windows
   2. run ResourceServer.py, AuthServer1.py, AuthServer2.py, Client.py in the seperate terminal windows
         -example command: Python3 ResourceServer.py
   3. Make sure the last file ran is always Client.py since it will initiate the first message (if the other files are not running the message sent won't reach them)

'''
import json
import time
from Message import *
import socket
import multiprocessing
import threading
from collections import deque
#dictionary of port locations so servers can find eachother
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
      #latest message received
      m = MReceived[0]

      #set of credentials pthis requested from others
      Qsent = set()
      for msg in MSent:
         if msg.messageType == 'request':
            Qsent.add(msg.resource)

      #set of credentials others requested from pthis
      Qrecieved = set()
      for msg in MReceived:
         if msg.messageType == 'request':
            Qrecieved.add(msg.resource)

      #set of credentials pthis sent to others
      Dsent = set()
      for msg in MSent:
         if msg.messageType == 'offer':
            Dsent.add(msg.resource)

      #set of credentials pthis recieved from others
      Drecieved = set()
      for msg in MReceived:
         if msg.messageType == 'offer':
            Drecieved.add(msg.resource)

      #if incoming msg resource not in self.policies and isnt an offer
         #check if resource is in resourceLookup
            #if it is send message to where resource is located
         #else send error and quit
      #if incoming msg resource not in self.policies and is an offer and is not originalRequester
         #then find message that originally requested m.resource and use it's originalRequester to send offer to originalRequester
      if m.resource not in self.policies and m.messageType != 'offer':
         if m.resource in resourceLookup:
            m.issuer = self.udp_port
            m.subject = resourceLookup[m.resource]
            return [m]
         else:
            print("Resource {} can't be found".format(m.resource))
            return
      elif m.resource not in self.policies and m.messageType == 'offer' and self.udp_port != m.originalRequester:
         for msg in MReceived:
            if msg.resource == m.resource and msg.messageType == 'request':
               m.issuer = self.udp_port
               m.subject = msg.originalRequester
               return [m]

      #isUnlocked is True if all credentials required for a resource have been received    
      isUnlocked = True
      if m.resource in self.policies:
         for policy in self.policies[m.resource]:
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
      else:
         for policy in self.policies:
            if not all(item in Drecieved for item in self.policies[policy]):
               isUnlocked = False

      #credentials to offer 
      Dnew = set()

      #credentials to request
      Qnew = set()

      #Calculate new credentials Dnew that Pthis will send to other parties 
      if m.messageType == 'offer':
         Dunlocked = Drecieved
         if isUnlocked:
            for resource in self.policies:
               if m.resource in self.policies[resource]:
                  Dunlocked.add(resource)
                  break
         Dnew = Dunlocked & (Qrecieved - Dsent)
      elif m.messageType == 'request' and isUnlocked:
         Dnew.add(m.resource)
      else:
         Drelevant = set(self.policies[m.resource])
         Qnew = Drelevant - Drecieved - Qsent

      messages = list()
      for credential in Dnew:
         sendTo = m.issuer
         messages.append(Message('offer', credential, self.udp_port, sendTo, m.originalRequester))
      
      for credential in Qnew:
         sendTo = 6868 if self.name != 'client' else resourceLookup[m.resource]
         messages.append(Message('request', credential, self.udp_port, sendTo, self.udp_port))

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

