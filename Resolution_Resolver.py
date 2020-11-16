''' 
1. Resolution Resolver (Mreceived, Msent, ) {
   Let Pthis be the current peer
2. m = the latest message in Mreceived
3. Qsent = set of credentials Pthis requested from others
4. Qreceived = set of credentials others requested from Pthis
5. Qnew=∅
6. Dsent = set credentials Pthis sent to others
7. Dreceived = set of credentials Pthis received from others
8. Dnew=∅
9. if m is an offer of credential C then
   /* Calculate new credentials Dnew that Pthis will send to other parties */
10. Dunlocked = all credentials unlocked by C and other credentials in Dreceived
11. Dnew = Dunlocked ∩ Qreceived − Dsent
12. else if m is a request for credential C then if C is already unlocked then
13. Dnew ={C}
14. else
   /* Calculate new credentials Qnew( based on the policy) that Pthis will request
   from others */
   Drelevant = all relevant remote credentials for C # need to be requested form other
   Qnew = Drelevant − Dreceived − Qsent
   Return the list of messages M composed of credentials in Dnew and requests for credentials
   in Qnew
} 
'''

