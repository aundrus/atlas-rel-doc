import os,getopt,sys,re
import socket
from pprint import pprint
import datetime
import smtplib

###########
#### MAIN
###########                             
home=os.environ.get('HOME','')
ardoc_nightly_name=os.environ.get('ARDOC_NIGHTLY_NAME','UNKNOWN')
ardoc_arch=os.environ.get('ARDOC_ARCH','UNKNOWN')
UID=os.getuid()
hostname1=socket.gethostname(); hostname=re.split(r'\.',hostname1)[0]
ts_j = datetime.datetime.now()
ts_jf = datetime.datetime.strftime(ts_j,'%Y-%m-%d %H:%M')

try:
  optionslist, args = getopt.getopt(sys.argv[1:],'l:m:',['level=','message='])
except getopt.error:
  print('''Error: You tried to use an unknown option or the                     
                 argument for an option that requires it was missing.''')            
  sys.exit(2)

if len(optionslist) == 0:
  print('''Error: ardoc_send_mail.py requires coomand line options  
                 Try "ardoc_send_mail.py -h" for more information.''')
  sys.exit(2) 
level='NONE'
message='NONE'
for a in optionslist[:]:
  if ( a[0] == '--level' or a[0] == '-l' ) and a[1] != '':
    level=a[1]
  if ( a[0] == '--message' or a[0] == '-m' ) and a[1] != '':
    message=a[1] 

mail_body="ARDOC reports "+level+" ORACLE problems\n" 
mail_body=mail_body+"message "+message+"\n"
mail_body=mail_body+"hostname "+hostname+"\n"
mail_body=mail_body+"nightly name "+ardoc_nightly_name+"\n"
mail_body=mail_body+"platform "+ardoc_arch+"\n"
mail_body=mail_body+"date "+ts_jf+"\n"
mailing=True
if mailing:
          subj = "ARDOC: "+level+" ORACLE problems on "+hostname
          sender = 'atnight@mail.cern.ch'
          receivers = ['undrus@bnl.gov']
          message = """From: Atlas Nightlybuild <atnight@mail.cern.ch>
To: %s                                                                                                                         
Subject: %s 

%s
""" % (", ".join(receivers), subj,mail_body)
          try:
            smtpObj = smtplib.SMTP('localhost')
            smtpObj.sendmail(sender, receivers, message)
            print("ardoc_send_mail.py: SENDING MESSAGE TO ",receivers)
            print("--->",message)
          except:
            print("ardoc_send_mail.py: Warning: unable to send email")
            sys.exit(1)



