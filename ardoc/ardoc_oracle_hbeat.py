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
    optionslist, args = getopt.getopt(sys.argv[1:],':eko',['end','killed','overtime'])
except getopt.error:
    print('''ardoc_oracle_hbeat.py: Error: You tried to use an unknown option or the
          argument for an option that requires it was missing.''')
    sys.exit(0)

opt_stat="NONE"
for a in optionslist[:]:
    if a[0] in ('-e','--end'): opt_stat="OKEND"
    elif a[0] in ('-k','--killed'): opt_stat="KILLED"
    elif a[0] in ('-o','--overtime'): opt_stat="OVRTIM"

home=""
nname=""
if 'HOME' in os.environ : home=os.environ['HOME']
if 'ARDOC_NIGHTLY_NAME' in os.environ : nname=os.environ['ARDOC_NIGHTLY_NAME']
if nname == "":
    print("ardoc_oracle_hbeat.py: Error: ARDOC_NIGHTLY_NAME is not defined")  
    sys.exit(1)
oracle_schema=os.environ.get('ARDOC_ORACLE_SCHEMA','ATLAS_NICOS').strip()
paname=os.environ.get('ARDOC_PROJECT_NAME','')
#
warea=os.environ.get('ARDOC_GEN_CONFIG_AREA','')
if warea == "":
    print("ardoc_oracle_hbeat.py: Error: ARDOC_WORK_AREA is not defined")
    sys.exit(1)
if not os.path.exists(warea):
    print("ardoc_oracle_hbeat.py: Error: ARDOC_WORK_AREA:",warea," is not directory")
    sys.exit(1)
warea_dir=os.path.dirname(warea)
fjid=warea+os.sep+'jobid.txt'
if ( not os.path.isfile(fjid) ):
    print("ardoc_oracle_hbeat.py: Error: file with jid does not exist:",fjid)
    sys.exit(1)
mf=open(fjid)
jid=mf.readline().strip()
mf.close()
if jid == '':
    print("ardoc_oracle_hbeat.py: Error: empty jid from",fjid)
    sys.exit(1)
print("ardoc_oracle_hbeat.py: JID read:",jid,"from:",fjid)
#
ts_j = datetime.datetime.now()
#
cFN="/afs/cern.ch/atlas/software/dist/nightlies/cgumpert/TC/OW_crdntl"
lne=open(cFN,'r')
lne_res=lne.readline()
lne.close()
lnea=re.split(r'\s+',lne_res)          
accnt,pwf,clust=lnea[0:3]
#print "XXXX",accnt,pwf,clust
connection = cx_Oracle.connect(accnt,pwf,clust)
#print ("Oracle DB version: " + connection.version)
#print ("Oracle client encoding: " + connection.encoding)
connection.clientinfo = 'python 2.6 @ home'
connection.module = 'cx_Oracle test_ARDOC.py'
connection.action = 'TestArdocJob'
cursor = connection.cursor()
try:
    connection.ping()
except cx_Oracle.DatabaseError as exception:
    error, = exception.args
    print(("ardoc_oracle_hbeat.py: Database connection error: ", error.code, error.offset, error.message))
#else:
#    print "ardoc_oracle_hbeat.py: Connection is alive!"
cursor.execute("ALTER SESSION SET current_schema = "+oracle_schema)    

cmnd="""select projid from projects where projname = :paname order by projid"""
cursor.execute(cmnd,{'paname' : paname})
result = cursor.fetchall()
if len(result) == 0:
            print("ardoc_oracle_hbeat.py: Error: absent project:",paname)
            sys.exit(1)
rowmax=result[-1]
projid_current=rowmax[0]
#
print("ardoc_oracle_hbeat.py: updating for jid",jid,", proj",projid_current,", date",ts_j,", status:",opt_stat)
if opt_stat == 'NONE':
    cmnd="""
update jobstat set HBEAT = :t_val, STAT = 'ALIVE'
where 
jid = :jid and projid = :projid_c
"""
    print("ardoc_oracle_hbeat.py: HBEAT UPDATE: ALIVE")
    cursor.prepare(cmnd)
    cursor.setinputsizes(t_val=cx_Oracle.TIMESTAMP)
    cursor.execute(None, {'jid' : jid, 'projid_c' : projid_current, 't_val':ts_j})
elif opt_stat == 'KILLED':
    cmnd="""
update jobstat set HBEAT = :t_val, STAT = 'KILLED', REQ = 'COMPL'
where
jid = :jid
"""
    cursor.prepare(cmnd)
    cursor.setinputsizes(t_val=cx_Oracle.TIMESTAMP)
    cursor.execute(None, {'jid' : jid, 't_val':ts_j})
else:
    cmnd="""
update jobstat set HBEAT = :t_val, STAT = :opt_stat
where
jid = :jid and projid = :projid_c and stat != 'KILLED'
"""   
    print("CMND HBEAT",cmnd,opt_stat)
    cursor.prepare(cmnd)
    cursor.setinputsizes(t_val=cx_Oracle.TIMESTAMP)
    cursor.execute(None, {'jid' : jid, 'projid_c' : projid_current, 'opt_stat' : opt_stat, 't_val':ts_j})

cursor.close()
connection.commit()
connection.close()
