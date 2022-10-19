#!/usr/bin/python
import pexpect, re, os
import calendar
import time
import config
import my_classes
import logging
from datetime import datetime
import signal
import sys

#-----------------------------------------------------------------------------------------------------------
# Author: Ahmed benhida
#
# For reference, below some output from show commands I am parsing
# Total Sessions            73         73      73       73         73      73
# 503 Service Unavail     4559       4559    4559        0          0       0
#'408 Request Timeout        0         17      15        0          0       0'
# atcpd01         No      0.0%         No
#
#        tuco: v3, Standby, health=100, max silence=1050    // show health
#4       Thread 0 (atcpd01) usage is at 80 percent, over minor threshold of 75 percent   // display alarlms
#
#
#
#  *** More show commands will be aded .....
#

#-----------------------------------------------------------------------------------------------------------

def keyboardInterruptHandler(signal, frame):
    print("KeyboardInterrupt (you hit ^c).. Cleaning up...")
    exit(0)

#-----------------------------------------------------------------------
# n = how many matches in there
# pMatch = string to match
# p = pattern combination of [string,number,..]
#
# Example, to match following line: 
#  Total Sessions              0       0       0          0       0       0
#  These are the parameters values:
#  pMatch = "  Total Sessions"
#  p = '(\s+)(\d+)'
#  n = 6 (matchesi of strings and numbers)
#-----------------------------------------------------------------------

def build_pattern(pMatch,n,p):
    pat =''
    for i in range(1,n):
        pat += p
    pattern = "{0}{1}".format(pMatch,pat)
    return re.compile(pattern)

def createLogfile(file):
   print ("file:", file)
   fh= open(file,"w+")
   print("fh:", fh)
   return fh

def processOutput(output,k,history):
   breach = 0
   logStr = ""
   msg = ''
   if k == "cpu":
      msg +='**** Breach - from cpu ..'
      for l in output.split('\r\n'):
          if re.search(r'(Total load)(.*):(.*)',l):
              r = re.search(r'(Total load)(.*):(.*)',l)
              cpuLd = int(r.group(3).strip().strip('%'))
              logStr +=' Total CPU Load: '+str(cpuLd)+'%'              

          #CPU 00 load  :     0%
          cpu=0
          if re.search(r'(CPU )(.*):(.*)',l):
             r = re.search(r'(CPU)(.*):(.*)',l)
             cpu = int(r.group(3).strip().strip('%'))
             logStr +=' CPU'+r.group(2).strip()+': '+str(cpu)+'%'
             if (cpu >= config.cpuMax):
                #Ahmed temporarily ignoring CPU as it spikes
                #breach = 1;  msg += '*** '+str(cpu)+'%'
                print ('breach'+'%  .......................................................................................> Breach:'+str(cpu)+'%')
                breach = 0;  msg += str(cpu)+'%  .......................................................................................> Breach:'+str(cpu)+'%'
      return [breach, logStr,msg]

   if k == "sess":
      msg +='**** Breach - from sess ..'
      reg = build_pattern('Total Sessions',6,'(\s+)(\d+)')
      pattern = re.compile(reg)
      for line in output.split('\r\n'):
          #print ('l:',line)
          match = pattern.search(line)
          if  match: 
             logStr +=' Tot Active Sess:'+match.group(2)
      return [breach,logStr,msg]
             
   if k == "ha":
      msg +='**** Breach - from HA ..'
      haState = ''
      for l in output.split('\r\n'):
          if re.search(r'(State)(.*)',l):
             r = re.search(r'(State)(.*)',l)
             logStr +=' HA State: '+r.group(2).strip()
             haState = r.group(2).strip()
             if haState != 'Active':
                logStr +=', wrong Primary state: '+ haState
                breach = 1; msg += '*** HA related alarm:'
          if re.search(r'(.*): v3, Standby, health=100, max silence=(.*)',l):
             r = re.search(r'((.*): v3, Standby, health=100, max silence=(.*))',l)
             logStr +=', Secondary: '+ r.group(2)+' Health= 100'
          if re.search(r'(.*):(\d+):(\d+).(\d+):(.*)',l):
             #r = re.search(r'(.*):(\d+):(\d+).(\d+):(.*)',l)
             logStr +=', HA Alarm: '+l
      return [breach,logStr,msg]

   if k == "mem":
      msg +='**** Breach - from mem ..'
      msg = ''
      for l in output.split('\r\n'):
          if re.search(r'(Total Memory:)(.*)',l):
             r = re.search(r'(Total Memory:)(.*)',l)
             logStr +=' Tot Mem: '+r.group(2).strip()
          if re.search(r'(System Usage:)(.*)',l):
             r = re.search(r'(System Usage:)(.*)',l)
             logStr +=', Mem Sys Usage: '+r.group(2).strip()
          if re.search(r'(Percent Free:)(.*)',l):
             r = re.search(r'(Percent Free:)(.*)',l)
             fmem = int(r.group(2).strip().strip(' %'))
             logStr +=', Mem free: '+str(fmem)+'%'
             if (fmem <= config.fmemMin):
                 breach = 1
                 msg += '*** Free Mem breach:'+str(fmem)
      return [breach,logStr,msg]

   if k == "sipdInv":
      msg +='**** Breach - from SIP INVITE  ..'
      reg503 = build_pattern('503 Service Unavail',6,'(\s+)(\d+)')
      pattern503 = re.compile(reg503)

      reg408 = build_pattern('408 Request Timeout',6,'(\s+)(\d+)')
      pattern408 = re.compile(reg408)

      regTout = build_pattern('Transaction Timeouts',6,'(\s+)(\d+)')
      patternTout = re.compile(regTout)
      msg = ''
      for line in output.split('\r\n'):
          #print ('lne xx:',line)
          match = pattern503.search(line)
          if  match:
             logStr +=' Tot 503 (SRVR): '+match.group(4)+', CLIENT: '+match.group(10)
             b503 = int(match.group(4))+int(match.group(10))
             if b503 > config.max503:
                breach = 1; msg += '**** Breach - 503 snd/rcv:'+str(b503) 
          match = pattern408.search(line)
          if  match:
             logStr +=' Tot 408 (SRVR): '+match.group(4)
             b408 = int(match.group(4))+int(match.group(10))
             if b408 > config.max408:
                breach = 1; msg += '**** Breach - 408 snd/rcv:'+str(b408)
          match = patternTout.search(line)
          if  match:
             logStr +=' Req Time Out (SRVR): '+match.group(4)+', (CLIENT): '+match.group(10)
             bReqTo = int(match.group(4)) + int(match.group(10))
             if (bReqTo > config.maxReqTo):
                breach = 1; msg += '**** Breach - Req T.O. snd/rcv:'+str(bReqTo) 
      return [breach,logStr,msg]
   
   if k == "secSrtp":
      msg +='**** Breach - from Security SRTP ..'
      srtpses = build_pattern('   ',2,'(\s+)(\d+)')
      patternSrtpses = re.compile(srtpses)

      msg = ''
      for line in output.split('\r\n'):
          match = patternSrtpses.search(line)
          if  match:
             logStr +=' SRTP ses: '+match.group(2)
      return [breach,logStr,msg] 

   if k == "msrp":
      msg +='**** Breach - from msrp ..'
      msrpses = build_pattern('Total Active Sessions:',2,'(\s+)(\d+)')
      patternMsrpses = re.compile(msrpses)

      msg = ''
      for line in output.split('\r\n'):
          match = patternMsrpses.search(line)
          if  match:
             logStr +='\n Max MSRP Active Sess: '+match.group(2)
      return [breach,logStr,msg]      

   if k == "recSess":
      msg +='**** Breach - from recSess ..'
      medSes = build_pattern('Rec Sessions',3,'(\s+)(\d+)')
      patternMedSes = re.compile(medSes)

      medStrm = build_pattern('Media Streams',3,'(\s+)(\d+)')  # should be n stream * medSes
      patternMedStrm = re.compile(medStrm)

      msg = ''
      for line in output.split('\r\n'):
          #print ('lne xx:',line)
          match = patternMedSes.search(line)
          if  match:
             logStr +=' REC sess: '+match.group(4)

          match = patternMedStrm.search(line)
          if  match:
             logStr +=', Med Strm: '+match.group(4)
      return [breach,logStr,msg] 

   if k == "regis":
      msg +='**** Breach - from registrations ..'
      patToCompile = build_pattern('User Entries',6,'(\s+)(\d+)')
      patternMatched = re.compile(patToCompile)
      msg = ''
      for line in output.split('\r\n'):
          #print ('lne xx:',line)
          match = patternMatched.search(line)
          if  match:
             logStr +='\n Reistrations: '+match.group(2)
      return [breach,logStr,msg]
      
   if k == "common":
      msg +='**** Breach - from com mon ..'
      patToCompile = build_pattern('([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3}):\d+',3,'(\s+)(\d+)')
      patternMatched = re.compile(patToCompile)
      patToCompile2 = build_pattern('Socket Message Dropped',3,'(\s+)(\d+)')
      patternMatched2 = re.compile(patToCompile2)
      msg = ''
      for line in output.split('\r\n'):
          match = patternMatched.search(line)
          match2 = patternMatched2.search(line)
          if  match:
             logStr +='\n Com State:'+match.group(2)
          if  match2:
             logStr +=' Socket Msg Drop : '+match2.group(3)
      return [breach,logStr,msg]         

   if k == "procOver":
      msg +='**** Breach - from process oveload ..'
      regAtcpd = build_pattern('    atcpd01',4,'(\s+)(\S+)')
      patternAtcpd = re.compile(regAtcpd)

      regmbcd01 = build_pattern('    mbcd01',4,'(\s+)(\S+)')
      patternmbcd01 = re.compile(regmbcd01)

      regsipd01 = build_pattern('    sipd01',4,'(\s+)(\S+)')
      patternsipd01 = re.compile(regsipd01)
      msg = ''
      for line in output.split('\r\n'):
          #print ('l atcpd:',line)
          match = patternAtcpd.search(line)
          if  match:
             logStr +='\n atcpd01: '+match.group(4)
             atcpd01 = float(match.group(4).strip().strip(' %'))
             if (atcpd01 >= config.maxAtcpd01):
                 # changed Breach value so it does not exit
                 print ('breach'+'ATCPD >='+str(config.maxAtcpd01)+'.......................................................................................>ATCPD  Breach:'+str(atcpd01))
                 breach = 0; msg += '**** Breach - atcpd01:'+str(atcpd01)
 
          match = patternmbcd01.search(line)
          if  match:
             logStr +=', mbcd01: '+match.group(4).strip()
             mbcd01 = float(match.group(4).strip().strip(' %'))
             if (mbcd01 >= config.maxMbcd01):
                 print ('breach'+'MBCD >='+str(config.maxMbcd01)+'%  .......................................................................................>MBCD  Breach:'+str(mbcd01))
                 # changed Breach value so it does not exit
                 breach = 0; msg += '**** Breach - mbcd01:'+str(mbcd01)
          match = patternsipd01.search(line)
          if  match:
             logStr +=', sipd01: '+match.group(4).strip()
             sipd01 = float(match.group(4).strip().strip(' %'))
             if (sipd01 >= config.maxSipd01):
                 breach = 1; msg += '**** Breach - sipd01:'+str(sipd01)
      return [breach,logStr,msg]
   #I should not be coming here
   #return   temprarily disabling this
   return [breach,logStr]
    
def getTimestamp():
   return calendar.timegm(time.gmtime())

def readInput(msg, msgTitle):
    inp=""
    print ('\n*************  '+msgTitle+'  *************\n\n')
    return input("\n"+msg)

def sshToBoxAndCollectOutput(cmdDict, fh, host):
   cmd = '/usr/bin/ssh admin@'+host
   child = pexpect.spawn(cmd)
   child.expect('password:', timeout=120)
   child.sendline('Abcd1234')
   child.expect ('# ')

   # starting the whole test at t0
   start = datetime.now()
   stopRun = 0
   hisDic = {}
   round =1 
   signal.signal(signal.SIGINT, keyboardInterruptHandler)

   # keep running these commands at interval t
   while (config.testDur > 0):
      # collect all these commands in list
      history =[]
      lst =[]
      for k in cmdDict:
         child.sendline (cmdDict[k])
         child.expect ('# ')
         output = child.before.join(child.after)
         fh.write(output)                     # save this to a file
         lst = processOutput(output,k,history)
         history.append(lst[1])               # always apped to history list

         if lst[0] == 1:                      # 1= error encountered
            stopRun = 1                       # flag this - encountered error in this lap
            break

      hisDic[round] = history
      elapsed = ((datetime.now() - start).seconds)
      l = '-'*30+' ROUND: '+str(round)+', '+str(elapsed)+' sec, '+str(elapsed/60)+' min '+'-'*30 
      #print ('-'*30+' ROUND: '+str(round)+', '+str(elapsed)+' sec, '+str(elapsed/60)+' min '+'-'*30 )
      print (l)
      fh.write('\n'+l+'\n')
      round += 1
      printhistory(hisDic,1)                   # to delete line  - print history last 2 records

      if stopRun == 1:
         #print ('Breach ?:'+lst[1]+'lst2:'+lst[2])            # lst[2] contains 'breach' message
         printhistory(hisDic,config.printLast) # print history last 2 records
         return

      elapsed = (datetime.now() - start).seconds
      time.sleep(config.sleepIntv)

      config.testDur -= elapsed 
      #print ('********> left from config.testDur:'+str(config.testDur))
      #print child.after
      #logging.error('--------------- Run Round:'+str(round))

   # how log the whole test took, +sleep period extra is ok
   print (" Test took overall time of:"+ str((datetime.now() - start).seconds))

   
def printhistory(hisDic, last):
    print ('-'*87)
    print ('------ printing last '+str(last)+' History records if available --------')
    lng = len(hisDic)
    dif = lng - last
    n = last
    if dif <= 0:
        last = lng
    # print last n of lng
    while last > 0:
        # ??? need to further parse this list
        for i in hisDic[lng]:
            if i:
               print( i)
        lng -= 1
        last -=1
 
def main ():
   stby = sys.argv[1:]
   print ('stby:'+str(stby))
   fileDir = os.path.dirname(os.path.realpath('__file__'))
   ts = getTimestamp() 

   alarmLogs = str(ts)+'.cErrors'
   logging.basicConfig(filename=alarmLogs, pathname=fileDir+config.Capalogdir)

   # Read DUT/host IP, if not provided in config.py file
   host = config.host
   #if config.host == "none":
   # I could verify the validity of the IP Address here .. later on
   if stby == ['stby']:
      host = readInput('Enter STBY IP address or press enter to accept ('+config.standby+'):', 'STBY IP ADDRESS INPUT')
      if host == '':
         host = config.standby
   else:
      host = readInput('Enter host IP address or press enter to accept ('+config.host+'):', 'HOST IP ADDRESS INPUT')
      if host == '':
         host = config.host
   # Read extra 'show commands' to consider when running the test
   testcase = readInput('1. TLS, 2. Xcode, 3. SRTP, 4. Siprec, 5. HA, 6 common, 7. acct, 8. Registr., 9. MSRP:', 'Test checcks (1 2 3 ..):') 
   
   # you could overwrite testcase to whatever you want to avoid typing it
   #testcase = 1 2 3
   allshows = my_classes.Showcommands()

   for t in testcase:
       if t.isdigit():
          if int(t) == 1:
             allshows.addcmd("tlsSess", "sh security tls stats")
          if int(t) == 2:
             allshows.addcmd("xcod", "sh xcode xlist")
          if int(t) == 3:
             allshows.addcmd("secSrtp", "sh security srtp sessions")
          if int(t) == 4:
             allshows.addcmd("recSess", "sh rec")
          if int(t) == 5:
             allshows.addcmd("ha", "Sh health")
          if int(t) == 6:
             allshows.addcmd("common", "sh comm-monitor")
          if int(t) == 7:
             allshows.addcmd("acct", "sh accounting")
          if int(t) == 8:
             allshows.addcmd("regis", "sh registration")
             allshows.addcmd("sipdRegis", "sh sipd register")
          if int(t) == 9:
             allshows.addcmd("msrp", "sh msrp")





   #print (allshows.shows)

   logfilename = config.testname+str(ts)+'.clog'
   if stby == ['stby']:
       logfilename = config.testname+str(ts)+'.stby.clog'

   logfile = os.path.join(fileDir, config.Capalogdir+logfilename)
   print ('logfile:'+logfile)
   fh = open(config.Capalogdir+logfilename, "a+")
   sshToBoxAndCollectOutput(allshows.shows, fh, host)

if __name__== "__main__":
   main()
