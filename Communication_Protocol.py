'''

Participate In OAuth () {
  while willing to participate do
    if the incoming message queue is empty then
      Wait a short period of time for new messages
    if there is a new message in the incoming message queue then
      Choose such a message m and remove it from the queue
      Record m’s receipt time as the current time
      ProcessMessage(m)}
/* message handler */

ProcessMessage (m) {
/* Mreceived and Msent store received and sent messages respectively */
Mreceived = Mreceived ∪ {m}
If m is an offer, add m to the local knowledge base L ( resources_vault)
Apply the resolution resolver algorithm with parameters Mreceived, Msent, and L,
which returns a list of messages M
/* send the messages to their intended recipients */
  if M is not empty then
     for every message k in M do
        Send k to its specified recipient
        Record k’s sending time as the current time
        Msent = Msent ∪ {k}
}

'''
