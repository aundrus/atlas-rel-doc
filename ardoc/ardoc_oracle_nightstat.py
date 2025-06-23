import re
import os
import sys
import getpass
import platform
import cx_Oracle
from pprint import pprint
import datetime
import getopt,logging

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
try:
    optionslist, args = getopt.getopt(sys.argv[1:],'n:gs:',['nightly=','get','set=','short'])
except getopt.error:
    logging.error('''ardoc_oracle_nightstat.py: Error: You tried to use an unknown option or the argument for an option that requires it was missing.''')
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
    logging.error("ardoc_oracle_nightstat.py: Error: ARDOC NIGHTLY NAME is not defined")  
    sys.exit(1)
oracle_schema=os.environ.get('ARDOC_ORACLE_SCHEMA','ATLAS_NICOS').strip()
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
    logging.error("ardoc_oracle_nightstat.py: Database connection error: '%s' '%s' '%s'", error.code, error.offset, error.message)
#else:
#    print "ardoc_oracle_hbeat.py: Connection is alive!"
cursor.execute("ALTER SESSION SET current_schema = "+oracle_schema)    

cmnd="""select stat, btype, stuser from nightlies where nname = :nname"""
cursor.execute(cmnd,{'nname' : nname})
result = cursor.fetchall()
if len(result) == 0:
            logging.error("ardoc_oracle_nightstat.py: Info: this nightly branch do not exist: '%s'",nname)
            sys.exit(2)
if len(result) > 1:
            logging.error("ardoc_oracle_nightstat.py: Error: multiple rows for this nightly branch do exist: '%s'",nname)
            sys.exit(1)
stat,btype,requestor=result[0]
if requestor == None : requestor=""
#
if shortprint : 
  if opt_stat == 'get' : print(stat)
else:
  logging.info("ardoc_oracle_nightstat.py: nightly '%s' has type '%s', status '%s'",nname,btype,stat)
if opt_stat == 'set' :
  if set_stat == '0' or set_stat == '1' or set_stat == '3': 
    if set_stat == '3': stat_user=requestor
    cmnd="""update nightlies set stat = :stat, sttime = :sttime, stuser = :stuser where nname = :nname"""
    if shortprint : 
      logging.info("ardoc_oracle_nightstat: setting status: '%s'",set_stat)
    else:
      logging.info("ardoc_oracle_nightstat: '%s' nightly name: '%s' new stat: '%s' requestor (parameter stuser): '%s'",cmnd,nname,set_stat,stat_user)  
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
      logging.info("ardoc_oracle_nightstat.py: Warning: this stat value is not allowed and will not be set: '%s'",set_stat) 
cursor.close()
if do_commit: connection.commit()
connection.close()
