import re
class BuildRgexPatterns:

   # let's say my line to parse is: sessions  10  200 15
   #
   # The parameters values will look like:
   #     pMatch =  sessions
   #     n = 3   // 3 values to build the pattern for
   def __init__(self,pMatch,n,p):
      pat =''
      for i in range(1,n):
          pat += p 
      self.pattern = "{0}{1}".format(pMatch,pat)


   # for every type of to match return its corresponding pattern
   def get_regex_pattern(self):
       return re.compile(self.pattern)

   @staticmethod
   def search_output(obj, output, msg, nthValue):
       msg, logStr, breach = '', '', 0
       for line in output.split('\r\n'):
           match = obj.search(line)
           print ('--> groups:{0}, g2:{1},g4:{2}, g6:{3}'.format(match.groups(),match.group(2),match.group(4),match.group(6) ))
           if  match:
              logStr += msg+match.group(nthValue)
       return [breach,logStr,msg]


# recSess <-- "sh rec"
# These objects will be reusable, same output will be pulled again and again
siprec_medSes = BuildRgexPatterns('Rec Sessions',4,'(\s+)(\d+)')
tot_sess      = BuildRgexPatterns('Total Sessions',6,'(\s+)(\d+)')
reg503        = BuildRgexPatterns('503 Service Unavail',6,'(\s+)(\d+)')
reg408        = BuildRgexPatterns('408 Request Timeout',6,'(\s+)(\d+)')
srtpses       = BuildRgexPatterns('   ',2,'(\s+)(\d+)')
msrpses       = BuildRgexPatterns('Total Active Sessions:',2,'(\s+)(\d+)')
medStrm       = BuildRgexPatterns('Media Streams',3,'(\s+)(\d+)')


# ../.. all your objects here


# here need to get show cmd output to pass
#....>
# each mach is one group, 100= group(2), 20= group(4), 40= group(6)
output = "Rec Sessions     100 20 40\n"

# now search the output for this pattern, see if you find a match
# and return the nth value (bec there could be many)
value = siprec_medSes.search_output(siprec_medSes.get_regex_pattern(), output,"REC sess: ",2)
print ('result 1:',value)

#vvalue = siprec_medSes.search_output(siprec_medSes.get_regex_pattern(), output,"REC sess: ",2)
#print ('result 2:',value)

#value = siprec_medSes.search_output(siprec_medSes.get_regex_pattern(), output,"REC sess: ",3)
#print ('result 3:',value)


alue = siprec_medSes.search_output(siprec_medSes.get_regex_pattern(), output,"REC sess: ",4)
print ('result 4:',value)


# check if the values is abouve some threshold, setup alarm by building
# a message to display


# log the value to the log file




