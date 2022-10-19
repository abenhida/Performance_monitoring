# this class initially contains the common 'show commands' needed to be collected
# and based on the test case the user will be entering additional 'show commands' relevant to his test
#
class Showcommands:
     # common 'show commands'
     shows = {
           "cpu": "sh platform cpu-load",
           "mem": "sh memo usage",
           "sess": "sh sessions",
           "procOver": "sho processes overload",
           "sipdInv": "sh sipd invite",
           "sipdRate": "show sipd rate",
           "vers":    "sh version"
     }
     def addcmd(self,k,v):
         self.shows[k] = v

     def results(self,k,v):
         self.collectedResults[k] = v


