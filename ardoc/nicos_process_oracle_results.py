import os,getopt,sys,re,glob
import os.path, shutil
import datetime
from pprint import pprint
from socket import gethostname
import smtplib

nicos_home=os.environ.get('NICOS_HOME','')
nicos_log=os.environ.get('NICOS_LOG','')
nicos_testlog=os.environ.get('NICOS_TESTLOG','')
hname=gethostname()
nicos_suffix=os.environ.get('NICOS_SUFFIX','')
nicos_nightly_name=os.environ.get('NICOS_NIGHTLY_NAME','')
nicos_project_relname_copy=os.environ.get('NICOS_PROJECT_RELNAME_COPY','')
nicos_arch=os.environ.get('NICOS_ARCH','')
nicos_relhome=os.environ.get('NICOS_RELHOME','')
nicos_copy_home=os.environ.get('NICOS_COPY_HOME','')

if nicos_home == "" :
   print("nicos_process_oracle_results.py: Error: NICOS_HOME is not defined")
   sys.exit(1)
if nicos_suffix == "" :
   print("nicos_process_oracle_results.py: Error: NICOS_SUFFIX is not defined")
   sys.exit(1)

#a_dir=[ os.path.dirname(nicos_log), os.path.dirname(nicos_testlog) ]
a_dir=[ os.path.dirname(nicos_log) ]
dict_err={}

for v_dir in a_dir:
  if v_dir != "" :  
    if not os.path.exists(v_dir): continue
  for ifile in os.listdir(v_dir):
    if ifile.endswith('.logora'):
      print("nicos_process_oracle_results.py: processing ",ifile)  
      coma='bash -c \'('+nicos_home+os.sep+'nicos_oracle_errortester.pl'+' '+v_dir+os.sep+ifile+')\''
#      print "COMA",coma
      sff=os.popen(coma,'r')
      strng=sff.readline().strip()
#      print "String",strng
      if strng != "":
        if strng not in dict_err:
          dict_err[strng]=[ifile]
        else:
          dict_err[strng].append(ifile)

list_errors=''
for k,v in dict_err.items():
    list_errors=list_errors+"----------------------\n" 
    print("nicos_process_oracle_results.py: Error signature ",k, "found in")
    print(v)          
    list_errors=list_errors+'Error signature \"'+k+'\" found in \n'
    for it in v :
      list_errors=list_errors+it+"\n"

if list_errors != "" :
  
  subj = "NICOS: ORACLE problems in "+nicos_nightly_name+" "+nicos_project_relname_copy+" "+nicos_arch
  sender = 'atnight@mail.cern.ch'
  receivers = ['undrus@bnl.gov']
  details = "Release local area: " + nicos_relhome + "\n"
  details = details + "Release AFS area: " + nicos_copy_home
  message = """From: Atlas Nightlybuild <atnight@mail.cern.ch>
To: undrus@bnl.gov
Subject: %s

===========================================================
Oracle problem occured in %s nightly job
on machine %s
%s
%s===========================================================
""" % (subj,nicos_suffix,hname,details,list_errors)
# MAIL DISABLED
#  print "MMMM ",message
##  try:
##     smtpObj = smtplib.SMTP('localhost')
##     smtpObj.sendmail(sender, receivers, message)         
##     print "nicos_process_oracle_results.py: SENDING MESSAGE TO ",receivers
##  except:
##     print "nicos_process_oracle_results.py: Error: unable to send email"
##     sys.exit(1)
