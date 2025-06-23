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
if len(sys.argv) < 2 :
    logging.error("ardoc_oracle_jobstat: Error: no options specified")
    sys.exit(1)
try:
    optionslist, args = getopt.gnu_getopt(sys.argv[1:],'o:s:p:',['nochange','err=','suc='])
except getopt.error:
    logging.error('''Error: You tried to use an unknown option or the
                    argument for an option that requires it was missing.''')
    sys.exit(1)
                        
#print ("Python version: " + platform.python_version())
#print ("cx_Oracle version: " + cx_Oracle.version)
#print ("Oracle client: " + str(cx_Oracle.clientversion()).replace(', ','.'))

optStepName=""
statusCode=""
nerr="N/A"
nsuc="N/A"
for a in optionslist[:]:
    if a[0] == '-o' and a[1] != '':
      optStepName=a[1]
    elif a[0] == '-s' and a[1] != '':
      statusCode=a[1]
    elif a[0] == '--nochange':
      statusCode='nochange'      
    elif a[0] == '--err' and a[1] != '':
      nerr=a[1]
    elif a[0] == '--suc' and a[1] != '':
      nsuc=a[1]
if optStepName == "":
    logging.error("ardoc_oracle_jobstat.py: Error: Step is not provided")
    sys.exit(1)

logging.info("ardoc_oracle_jobstat.py: Info: N errors and successes: '%s' '%s'",nerr,nsuc)
stepDict={'conf':'CONF','config':'CONF','CONFIG':'CONF'}
stepDict.update({'co':'CO','checkout':'CO'})
stepDict.update({'tc':'TC','tagcollector':'TC','toolinit':'TC'})
stepDict.update({'set':'SET','setup':'SET','projectconf':'SET'})
stepDict.update({'cb':'CB','configbuild':'CB'})
stepDict.update({'b':'B','build':'B'})
stepDict.update({'ib':'IB','installbuild':'IB'})
stepDict.update({'q':'Q','qa':'Q'})
stepDict.update({'i':'I','int':'I','inttest':'I','inttests':'I'})
stepDict.update({'doc':'DOC','err':'DOC'})
stepDict.update({'afs':'AFS','copy':'AFS','copyb':'AFS'})
stepDict.update({'copyt':'AFST','COPYT':'AFST'})
stepDict.update({'rpm':'RPM'})
stepDict.update({'kit':'KIT','kitinst':'KITINST'})
stepDict.update({'cv':'CV', 'cvmfs':'CV'})
stepDict.update({'cvkv':'CVKV'})
stepDict.update({'art':'LA', 'lart':'LA', 'la':'LA'})

stepDBN=""
if optStepName.lower() in stepDict:
    stepDBN=stepDict[optStepName.lower()]
else:
    logging.error("ardoc_oracle_jobstat.py: Error: Unknown step provided: '%s'",optStepName)
    sys.exit(1)
logging.info("ardoc_orackle_jobstat: option: '%s',statusCode: '%s'",stepDBN,statusCode)

home=os.environ.get('HOME','')
nname=os.environ.get('ARDOC_NIGHTLY_NAME','')
arjid=os.environ.get('ARDOC_JOBID','')
t_epoch=os.environ.get('ARDOC_EPOCH','')
if arjid == "":
    logging.error("ardoc_oracle_jobstat.py: Error: ARDOC_JOBID is not defined")
    sys.exit(1)
if t_epoch == "":
    logging.error("ardoc_oracle_jobstat.py: Error: ARDOC_EPOCH is not defined")
    sys.exit(1)
if nname == "":
    logging.error("ardoc_oracle_jobstat.py: Error: ARDOC_NIGHTLY_NAME is not defined")
    sys.exit(1)

oracle_schema=os.environ.get('ARDOC_ORACLE_SCHEMA','ATLAS_NICOS').strip()    
parray=os.environ.get('ARDOC_PROJECT_ARRAY','')
paname=os.environ.get('ARDOC_PROJECT_NAME','')
parray_a=re.split(r'\s+',parray)
firstproj=1
# if the project is the first in sequence then firstproj=1
lnumber=len(parray_a)
if lnumber > 1 and paname != "" :
    if parray_a[0] != paname:
        logging.info("ardoc_oracle_jobstat.py: Info: current project '%s' is not the first ('%s'): limited db insertions",paname,parray_a[0])
        firstproj=0
#print "lnumber, firstproj",lnumber,firstproj,lnumber,optStepName        
relname=os.environ.get('ARDOC_PROJECT_RELNAME','')
ardoc_arch=os.environ.get('ARDOC_ARCH','')
arch_a=re.split(r'\-',ardoc_arch)
arch=arch_a[0]; osys=arch_a[1]; comp=arch_a[2]; opt=arch_a[3]
role=os.environ.get('ARDOC_NIGHTLY_ROLE','main')
if len(role) > 6: role=role[0:6]
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
cursor.execute('select sysdate from dual')
# Autocommit -- read/write attribute.
# By default autocommit is off (0).
# connection.autocommit
try:
    connection.ping()
except cx_Oracle.DatabaseError as exception:
    error, = exception.args
    logging.error("ardoc_oracle_jobstat.py: Database connection error: '%s' '%s' '%s'", error.code, error.offset, error.message)
else:
    logging.info("ardoc_oracle_jobstat.py: Connection is alive!")
cursor.execute("ALTER SESSION SET current_schema = "+oracle_schema)
cmnd="""
select nid from nightlies where nname = :nname"""
cursor.execute(cmnd,{'nname' : nname})
result = cursor.fetchall()
if len(result) < 1: logging.error("ardoc_oracle_jobstat.py: absent nightly name: '%s'",nname); sys.exit(1)   
row=result[-1]
nightly_id=row[0]
ts = datetime.datetime.now()
relid_j=""
ts_j=""
ts_1=ts
if firstproj == 0:
    ts_1=ts - datetime.timedelta(days=2)
else:
    if ( optStepName == 'conf' or  optStepName == 'config' ):
#      ts_1=ts - datetime.timedelta(minutes=30)
# FOR JENKINS BUILD LOG PUBLICATION ALLOW TIME WINDOW 12 hours 
      ts_1=ts - datetime.timedelta(minutes=1720) 
    else:
      ts_1=ts - datetime.timedelta(days=1)  
logging.info("ardoc_oracle_jobstat.py: timestamps '%s' '%s'",ts,ts_1)    

# FIND RELID as RELID of latest release with given nid and relname, with reltstamp > ts_1 (12 - 48 hours from now)  
cmnd="""
SELECT RELID,reltstamp FROM RELEASES WHERE nid = :nightly_id and name = :relname and reltstamp > :t_val order by reltstamp""" 
logging.info("CMND '%s'", cmnd)
cursor.execute(cmnd,{ 'nightly_id' : nightly_id, 'relname' : relname, 't_val' : ts_1 })
result = cursor.fetchall()
lresult=len(result)
logging.info("ardoc_oracle_jobstat.py: result length '%s'",lresult)
relid_j=""
ts_j=""
if lresult > 0:
        for row in result:
            logging.info("ardoc_oracle_jobstat.py: RELEASES row: '%s'",row)
        rowmax=result[-1]
        logging.info("ardoc_oracle_jobstat.py: relid found: '%s' XX '%s'",rowmax[0],rowmax[1])
        relid_j=rowmax[0]; ts_j=rowmax[1]
#
if relid_j == "":
      logging.error("ardoc_oracle_jobstat.py: Error: relid for jobs table not found")
      sys.exit(1)
#print "TSJ",ts_j
#print "SSS",ts_j.year,ts_j.month,ts_j.day
#print "SSA",ts_j.date()
#tdd_j=ts_j.date()
#print tdd_j.strftime("%Y%m%d"), nightly_id

relid_jj=""
# GET JOB info from jobs for jid, verification of jobs and releases entries match
cmnd="""
SELECT JID,RELID,tstamp FROM JOBS WHERE nid = :nightly_id and JID = :jid and OS = :osys and COMP = :comp and ARCH = :arch and OPT = :opt order by tstamp"""
cursor.execute(cmnd,{'nightly_id' : nightly_id, 'jid' : arjid, 'osys' : osys, 'comp' : comp, 'arch' : arch, 'opt' : opt})
result = cursor.fetchall()
logging.info("ardoc_oracle_jobstat.py: DB command '%s'", cmnd)
lresult=len(result)
if lresult > 0:
  for row in result:
    logging.info("ardoc_oracle_jobstat.py: result JID,RELID '%s'", row)
  rowmax=result[-1]
  jid = rowmax[0]
  relid_jj = rowmax[1] 
logging.info("ardoc_oracle_jobstat.py: query result: jid relid ts: '%s' '%s' '%s'",jid,relid_j,relid_jj)
if relid_jj == "" or relid_j != relid_jj:
    logging.info("ardoc_oracle_jobstat.py: Error: relid from jobs table differs from releases table '%s' xx '%s'",relid_jj,relid_j) 
#

cmnd="""select projid from projects where projname = :paname order by projid"""
cursor.execute(cmnd,{'paname' : paname })
result = cursor.fetchall()
# ADDING PROJECT IF ABSENT
if len(result) == 0:
    logging.info("ardoc_oracle_jobstat.py: Info: absent project: '%s'",paname)
    logging.info("ardoc_oracle_jobstat.py: Info: adding project: '%s'",paname)
    p_item_s=paname.strip()
    cmnd7="""
merge into projects a USING ( select max(projid)+1 as new_projid from projects ) b
ON ( projname = :p_item_s )
WHEN NOT MATCHED THEN insert values
( b.new_projid
, :p_item_s)"""
    logging.info("ardoc_oracle_jobstat.py:CMND '%s' '%s'", cmnd7,p_item_s)
    cursor.execute(cmnd7, {'p_item_s' : p_item_s})
    cursor.execute(cmnd,{'paname' : paname })
    result = cursor.fetchall()        
if len(result) == 0:
    logging.error("ardoc_oracle_jobstat.py: Error: project is absent and could not be added: '%s'",paname) 
    sys.exit(1)
rowmax=result[-1]
projid_current=rowmax[0]
#
#GETTING JOBSTAT INFO
cmnd="""select r.name,p.projname,j.begdate,n.nname from jobstat j
INNER JOIN projects p on p.projid=j.projid
INNER JOIN nightlies n on n.nid=j.nid
INNER JOIN releases r on r.relid=j.relid
where j.relid=:relid_j
and j.jid=:jid
and j.nid = :nightly_id
and j.projid = :projid_c order by JID
""" 
cursor.execute(cmnd, {'relid_j': relid_j, 'jid' : jid, 'nightly_id' : nightly_id, 'projid_c' : projid_current })
result = cursor.fetchall()
if len(result) == 0:
     logging.error("ardoc_oracle_jobstat.py: Error: attempt to update non-existing jobstat row: jid,nid,relid,projid '%s' '%s' '%s' '%s'",jid,nightly_id,relid_j,projid_current)
     sys.exit(1)

rowmax=result[-1]
relname_sel=rowmax[0]
projname_sel=rowmax[1]
begdate_sel=rowmax[2]
nname_sel=rowmax[3]

#UPDATING JOBSTAT
logging.info("ardoc_oracle_jobstat.py: updating for nightly '%s', release '%s', proj '%s', begdate '%s' ***('%s')***",nname_sel,relname_sel,projname_sel,begdate_sel,lresult)
errors_successes=""
if stepDBN == 'LA': errors_successes=" , ER"+stepDBN+" = :nerr , SU"+stepDBN+" = :nsuc" 
logging.info("ardoc_oracle_jobstat.py: error and success data: '%s' '%s'",nerr,nsuc)

procid='100000'
cmnd0="update jobstat j set E"+stepDBN+" = NULL , S"+stepDBN+" = NULL"
cmnd1="update jobstat j set B"+stepDBN+" = :t_val"
cmnd2="update jobstat j set E"+stepDBN+" = :t_val , S"+stepDBN+" = :statusCode" + errors_successes
cmnd3="update jobstat j set E"+stepDBN+" = :t_val"
cmnd9="""
where j.relid=:relid_j
and j.jid=:jid
and j.nid = :nightly_id
and j.projid = :projid_c
"""

cmnd00=cmnd0+cmnd9
ts_inp=ts
if statusCode == "":
#   end date and status become NULL, begin date updated
    cmnd=cmnd1+cmnd9
    cursor.execute(cmnd00, {'relid_j': relid_j, 'jid' : jid, 'nightly_id' : nightly_id, 'projid_c' : projid_current })
    cursor.prepare(cmnd)
    cursor.setinputsizes(t_val=cx_Oracle.TIMESTAMP)
    cursor.execute(None, {'relid_j': relid_j, 'jid' : jid, 'nightly_id' : nightly_id, 'projid_c' : projid_current, 't_val':ts_inp})
else:    
    if statusCode == "nochange":
#       no status code update, end date updated 
        cmnd=cmnd3+cmnd9
        cursor.prepare(cmnd)
        cursor.setinputsizes(t_val=cx_Oracle.TIMESTAMP)
        cursor.execute(None, {'relid_j': relid_j, 'jid' : jid, 'nightly_id' : nightly_id, 'projid_c' : projid_current, 't_val':ts_inp})
    else: 
#       status code AND end date updated
        cmnd=cmnd2+cmnd9
        cursor.prepare(cmnd)
        cursor.setinputsizes(t_val=cx_Oracle.TIMESTAMP)
        if stepDBN == 'LA':
          cursor.execute(None, {'relid_j': relid_j, 'jid' : jid, 'nightly_id' : nightly_id, 'projid_c' : projid_current, 't_val':ts_inp, 'statusCode' : statusCode, 'nerr' : nerr, 'nsuc' : nsuc})
        else:
          cursor.execute(None, {'relid_j': relid_j, 'jid' : jid, 'nightly_id' : nightly_id, 'projid_c' : projid_current, 't_val':ts_inp, 'statusCode' : statusCode})

logging.info("ardoc_oracle_jobstat.py: updating '%s' code: '%s' tval: '%s' jid,projid: '%s' '%s'",stepDBN,statusCode,ts,jid,projid_current)

cursor.close()
connection.commit()
connection.close()
