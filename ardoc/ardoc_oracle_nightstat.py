import re
import os
import sys
import getpass
import platform
import cx_Oracle
from pprint import pprint
import datetime
import getopt

try:
    optionslist, args = getopt.getopt(sys.argv[1:],'n:gs:',['nightly=','get','set=','short'])
except getopt.error:
    sys.stderr.write('''ardoc_oracle_nightstat.py: Error: You tried to use an unknown option or the argument for an option that requires it was missing.\n''')
    sys.exit(0)

nname="NONE"
opt_stat="get"
stat_user=""
set_stat='0'
do_commit=False
shortprint=False
for a in optionslist[:]:
    if a[0] in ('-n','--nightly') and a[1] != '': nname=a[1]
    elif a[0] in ('-g','--get'): opt_stat="get"
    elif a[0] in ('-s','--set'): 
       opt_stat="set"
       if a[1] != '': set_stat=a[1]
    elif a[0] in ('-u','--user'):
       stat_user=""
       if a[1] != '': stat_user=a[1]  
    elif a[0] in ('--short'): shortprint=True
home=""
if 'HOME' in os.environ : home=os.environ['HOME']
if nname == "NONE":
    sys.stderr.write("ardoc_oracle_nightstat.py: Error: ARDOC NIGHTLY NAME is not defined\n")  
    sys.exit(1)
oracle_schema=os.environ.get('ARDOC_ORACLE_SCHEMA','ATLAS_ARDOC').strip()
ts_j = datetime.datetime.now()
cFN="/afs/cern.ch/atlas/software/dist/nightlies/cgumpert/TC/OR_crdntl"
if opt_stat == "set": cFN="/afs/cern.ch/atlas/software/dist/nightlies/cgumpert/TC/OW_crdntl"
lne=open(cFN,'r')
lne_res=lne.readline()
lne.close()
lnea=re.split(r'\s+',lne_res)          
accnt,pwf,clust=lnea[0:3]
connection = cx_Oracle.connect(accnt,pwf,clust)
connection.clientinfo = 'python 2.6 @ home'
connection.module = 'cx_Oracle ardoc_oracle_nightstat.py'
connection.action = 'night status handling'
cursor = connection.cursor()
try:
    connection.ping()
except cx_Oracle.DatabaseError as exception:
    error, = exception.args
    sys.stderr.write("ardoc_oracle_nightstat.py: Database connection error: " + str(error.code) + " " + str(error.offset) + " " + str(error.message) + "\n")
#else:
#    print "ardoc_oracle_hbeat.py: Connection is alive!"
cursor.execute("ALTER SESSION SET current_schema = "+oracle_schema)    

cmnd="""select stat, btype, stuser from nightlies where nname = :nname"""
cursor.execute(cmnd,{'nname' : nname})
result = cursor.fetchall()
if len(result) == 0:
            sys.stderr.write("ardoc_oracle_nightstat.py: Info: this nightly branch do not exist: " + str(nname) + "\n")
            sys.exit(2)
if len(result) > 1:
            sys.stderr.write("ardoc_oracle_nightstat.py: Error: multiple rows for this nightly branch do exist:" + str(nname) + "\n")
            sys.exit(1)
stat,btype,requestor=result[0]
if requestor == None : requestor=""
#
if shortprint : 
  if opt_stat == 'get' : print(stat)
else:
  print("ardoc_oracle_nightstat.py: nightly",nname," has type",btype,", status",stat)
if opt_stat == 'set' :
  if set_stat == '0' or set_stat == '1' or set_stat == '3': 
    if set_stat == '3': stat_user=requestor
    cmnd="""update nightlies set stat = :stat, sttime = :sttime, stuser = :stuser where nname = :nname"""
    if shortprint : 
      print(set_stat)
    else:
      print("ardoc_oracle_nightstat: ",cmnd,' nightly name: ',nname,' new stat: ',set_stat,'requestor (parameter stuser):',stat_user)  
    int_stat=int(set_stat)
    dict_p={ 'stat' : int_stat, 'sttime' : ts_j, 'nname' : nname, 'stuser' : stat_user } 
    cursor.prepare(cmnd)
    cursor.setinputsizes(sttime=cx_Oracle.TIMESTAMP)
    cursor.execute(None, dict_p)
    do_commit='True'
  else:
    if shortprint : 
      print("99")
    else: 
      print("ardoc_oracle_nightstat.py: Warning: this stat value is not allowed and will not be set: ",set_stat) 
cursor.close()
if do_commit: connection.commit()
connection.close()
