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
    optionslist, args = getopt.getopt(sys.argv[1:],'n:',['nightly='])
except getopt.error:
    logging.error('''ardoc_oracle_latest_ntag.py: Error: You tried to use an unknown option or the argument for an option that requires it was missing.''')
    sys.exit(0)

nname="NONE"
for a in optionslist[:]:
    if a[0] in ('-n','--nightly') and a[1] != '': nname=a[1]

home=""
if 'HOME' in os.environ : home=os.environ['HOME']
if nname == "NONE":
    logging.error("ardoc_oracle_latest_ntag.py: Error: NIGHTLY NAME is not defined")  
    sys.exit(1)
oracle_schema=os.environ.get('ARDOC_ORACLE_SCHEMA','ATLAS_NICOS').strip()
ts_j = datetime.datetime.now()
cFN="/afs/cern.ch/atlas/software/dist/nightlies/cgumpert/TC/OR_crdntl"
lne=open(cFN,'r')
lne_res=lne.readline()
lne.close()
lnea=re.split(r'\s+',lne_res)          
accnt,pwf,clust=lnea[0:3]
connection = cx_Oracle.connect(accnt,pwf,clust)
connection.clientinfo = 'python 2.6 @ home'
connection.module = 'cx_Oracle ardoc_oracle_latest_ntag.py'
connection.action = 'night status handling'
cursor = connection.cursor()
try:
    connection.ping()
except cx_Oracle.DatabaseError as exception:
    error, = exception.args
    logging.error("ardoc_oracle_latest_ntag.py: Database connection error: '%s' '%s' '%s'", error.code, error.offset, error.message)
#else:
#    print "ardoc_oracle_hbeat.py: Connection is alive!"
cursor.execute("ALTER SESSION SET current_schema = "+oracle_schema)    

cmnd="""select nid from nightlies where nname = :nname"""
cursor.execute(cmnd,{'nname' : nname})
result = cursor.fetchall()
if len(result) == 0:
            logging.error("ardoc_oracle_latest_ntag.py: Info: this nightly branch do not exist: '%s'",nname)
            sys.exit(2)
if len(result) > 1:
            logging.error("ardoc_oracle_latest_ntag.py: Error: multiple rows for this nightly branch do exist: '%s'",nname)
            sys.exit(1)
nid=result[0][0]
logging.warn("ardoc_oracle_latest_ntag.py: nightly '%s' has id '%s'",nname,nid)

cmnd="""select relnstamp from releases where nid = :nid and reltstamp > SYSDATE - 23/24 order by reltstamp desc"""
cursor.execute(cmnd,{'nid' : nid})
result = cursor.fetchall()
lresult=len(result)
if len(result) == 0:
    logging.error("ardoc_oracle_latest_ntag.py: Info: recent releases for the nightly branch do not exist: '%s'",nname)
    sys.exit(2)
latest_relnstamp=result[0][0]
logging.warn("ardoc_oracle_latest_ntag.py: nightly '%s' has the lastest release '%s'",nname,latest_relnstamp)
print(latest_relnstamp)
cursor.close()
connection.close()
