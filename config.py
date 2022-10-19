# CAPACITY VNF
# Only using below variables so far

# Only using below variables so far
testDur = 1536000             # for how long I should keep collecting show output in secs
sleepIntv  = 7          # sleep time between run a bunch of show commands
cpuMax    = 90          # report a MAX cpu reached  85 - 87
fmemMin   = 10          # minimum free memory, below this report
max503    = 0           # minimum 503's to consider a test failed
maxReqTo  = 0           # minimum acceptable request timeout
max408    = 1000000000       # minimum acceptable 408 -- basically ignoring timeouts
maxAtcpd01= 86          # max ATCPD (stop at 77 , max 80
maxSipd01 = 86
maxMbcd01 = 77          # 77 above 80 you start to see failures

printLast = 3           # when error found print last ..

# DUT IP, if not entered here you will be prompte to enter it at runtime
#host = "10.196.75.43"     # ovm3 
#host = "10.196.75.42"     # ovm2
#host = '10.196.133.123'    # 3900 - stark
#host = "10.196.133.113"   # 1100 Pullock 
host = "10.196.133.126"   # 6350 tortuga
host = "10.196.133.125"   # 6350 tuco
#standby = "10.196.133.125"   # 6350 tuco

#testname ="4836_Max_Registrations_limits_TLS."
#testname ="4836_Max_Registrations_limits_TCP."
#testname ="Bomer_4844_Max.SRTP.SRTP.Sessions."
#testname ="Bomer_4844_Max.SRTP.RTP.Sessions.21k."
#testname = '4611_Access.with.authentication_no.refresh.CPS.1.5k.'
#testname ='4621_Access.UDP.TLS_no.refreshi.CPS.1200.'
testname ='5246_Access.with.Encryption.CPS.1200.'
#testname ='4696_Max.MSRP.B2BUA.Sessions1.TCP.Chat.M00_M01.'
#testname = '4696_Max.MSRP.TLS.B2BUA.Sessions.TLS.Chat.M00-M02.IPv4_M01_M03.IPv6_listen-port0.'
#testname = '4696.Max.MSRP.TLS.B2BUA.Sessions.TLS.Chat.M00_M02.IPv4.M01_M03.IPv6.'
#testname ="Bomer_4632_Peering_QoS_Accounting."
#testname ="4695_Max.MSRP.B2BUA.Sessions_TCP.Chat.M02_M03"
#testname = "4696_Max.MSRP.B2BUA.Sessions.TCP.Chat.M00_M02_IPv4.M01_M03_IPv6"
#testname ="4695_Max.MSRP.B2BUA.Sessions_TCP.Chat.M00_M01"
#testname="4266_Max_CPS_with_EOM_OCOM_HA"
#testname = "4696_Max.MSRP.TLS.B2BUA.Sessions.TLS.Chat.M00_M02.IPv4.M01_M03.IPv6"    to redo with first gz, use tls also

imageVersion="TCZ0.0.0 Cycle 88"

# Where to put the logs
Capalogdir = 'capalogs/'
Perflogdir = 'perflogs/'

# Autohome, where scripts directory is 
autohome='~/automation'



#-----------------------------------------
# Notes
#-----------------------------------------
# PERFORMANCE VNF
# 10 to 15 minutes test duration, CH 10 sec
