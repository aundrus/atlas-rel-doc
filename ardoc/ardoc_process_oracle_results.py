import os,getopt,sys,re,glob
import os.path, shutil
import datetime
from pprint import pprint
from socket import gethostname
import smtplib

ardoc_home=os.environ.get('ARDOC_HOME','')
ardoc_log=os.environ.get('ARDOC_LOG','')
ardoc_testlog=os.environ.get('ARDOC_TESTLOG','')
hname=gethostname()
ardoc_suffix=os.environ.get('ARDOC_SUFFIX','')
ardoc_nightly_name=os.environ.get('ARDOC_NIGHTLY_NAME','')
ardoc_project_relname_copy=os.environ.get('ARDOC_PROJECT_RELNAME_COPY','')
ardoc_arch=os.environ.get('ARDOC_ARCH','')
ardoc_relhome=os.environ.get('ARDOC_RELHOME','')
ardoc_copy_home=os.environ.get('ARDOC_COPY_HOME','')

if ardoc_home == "" :
   print("ardoc_process_oracle_results.py: Error: ARDOC_HOME is not defined")
   sys.exit(1)
if ardoc_suffix == "" :
   print("ardoc_process_oracle_results.py: Error: ARDOC_SUFFIX is not defined")
   sys.exit(1)

#a_dir=[ os.path.dirname(ardoc_log), os.path.dirname(ardoc_testlog) ]
a_dir=[ os.path.dirname(ardoc_log) ]
dict_err={}

for v_dir in a_dir:
  if v_dir != "" :  
    if not os.path.exists(v_dir): continue
  for ifile in os.listdir(v_dir):
    if ifile.endswith('.logora'):
      print("ardoc_process_oracle_results.py: processing ",ifile)  
      coma='bash -c \'(python3 '+ardoc_home+os.sep+'ardoc_oracle_errortester.py'+' '+v_dir+os.sep+ifile+')\''
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
    print("ardoc_process_oracle_results.py: Error signature ",k, "found in")
    print(v)          
    list_errors=list_errors+'Error signature "'+k+'" found in \n'
    for it in v :
      list_errors=list_errors+it+"\n"

if list_errors != "" :
  
  subj = "ARDOC: ORACLE problems in "+ardoc_nightly_name+" "+ardoc_project_relname_copy+" "+ardoc_arch
  sender = 'atnight@mail.cern.ch'
  receivers = ['undrus@bnl.gov']
  details = "Release local area: " + ardoc_relhome + "\n"
  details = details + "Release AFS area: " + ardoc_copy_home
  message = """From: Atlas Nightlybuild <atnight@mail.cern.ch>
To: undrus@bnl.gov
Subject: %s

===========================================================
Oracle problem occured in %s nightly job
on machine %s
%s
%s===========================================================
""" % (subj,ardoc_suffix,hname,details,list_errors)
# MAIL DISABLED
#  print "MMMM ",message
##  try:
##     smtpObj = smtplib.SMTP('localhost')
##     smtpObj.sendmail(sender, receivers, message)         
##     print "ardoc_process_oracle_results.py: SENDING MESSAGE TO ",receivers
##  except:
##     print "ardoc_process_oracle_results.py: Error: unable to send email"
