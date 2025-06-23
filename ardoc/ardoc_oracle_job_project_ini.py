import re
import os
import sys
import getpass, logging
import platform
import cx_Oracle
from pprint import pprint
import datetime

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
home=os.environ.get('HOME','')
warea=os.environ.get('ARDOC_WORK_AREA','')
nname=os.environ.get('ARDOC_NIGHTLY_NAME','')
arjid=os.environ.get('ARDOC_JOBID','')
t_epoch=os.environ.get('ARDOC_EPOCH','')
if arjid == "":
    logging.error("ardoc_oracle_job_project_ini.py: Error: ARDOC_JOBID is not defined")
    sys.exit(1)
if t_epoch == "":
    logging.error("ardoc_oracle_job_project_ini.py: Error: ARDOC_EPOCH is not defined")
    sys.exit(1)
if nname == "":
    logging.error("ardoc_oracle_job_project_ini.py: Error: ARDOC_NIGHTLY_NAME is not defined")  
    sys.exit(1)
logging.info("ardoc_oracle_job_project_ini.py: use jid: '%s'",arjid)
oracle_schema=os.environ.get('ARDOC_ORACLE_SCHEMA','ATLAS_NICOS').strip()
ardoc_gen_config_area=os.environ.get('ARDOC_GEN_CONFIG_AREA','')
parray=os.environ.get('ARDOC_PROJECT_ARRAY','')
paname=os.environ.get('ARDOC_PROJECT_NAME','')
parray_a=re.split(r'\s+',parray)
firstproj=1
lastproj=1
lnumber=len(parray_a)
if lnumber > 1 and paname != "" :
    lastproj=0
    if parray_a[0] != paname:
        logging.info("ardoc_oracle_job_project_ini.py: Info: current project '%s' is not the first ('%s')",paname,parray_a[0])
        firstproj=0
    if parray_a[-1] == paname:
        lastproj=1
relname=os.environ.get('ARDOC_PROJECT_RELNAME','')
reltype="NIT"
tcrel="N/A"; tcrelbase="N/A"
validation=os.environ.get('ARDOC_VAL_MODE','')
nightly_group=os.environ.get('ARDOC_NIGHTLY_GROUP','N/A')
nightly_name=os.environ.get('ARDOC_NIGHTLY_NAME','N/A')

fdtt=float(t_epoch)
ts=datetime.datetime.fromtimestamp(fdtt)
relnstamp=ts.strftime("%Y-%m-%dT%H%M")

ardoc_arch=os.environ.get('ARDOC_ARCH','')
arch_a=re.split(r'\-',ardoc_arch)
arch=arch_a[0];osys=arch_a[1];comp=arch_a[2];opt=arch_a[3]
role=os.environ.get('ARDOC_NIGHTLY_ROLE','main')
if len(role) > 6: role=role[0:6]
ardoc_suffix=os.environ.get('ARDOC_SUFFIX','')
ardoc_webpage=os.environ.get('ARDOC_WEBPAGE','')
ardoc_webarea=os.path.dirname(ardoc_webpage)
ardoc_http_build=os.environ.get('ARDOC_HTTP_BUILD','')

cFN="/afs/cern.ch/atlas/software/dist/nightlies/cgumpert/TC/OW_crdntl"
lne=open(cFN,'r')
lne_res=lne.readline()
lne.close()
lnea=re.split(r'\s+',lne_res)          
accnt,pwf,clust=lnea[0:3]
#print "XXXX",accnt,pwf,clust
#
logging.info("ardoc_oracle_job_project_ini.py: jid retrieved from file: '%s'",arjid)    
connection = cx_Oracle.connect(accnt,pwf,clust)
#print ("Oracle DB version: " + connection.version)
#print ("Oracle client encoding: " + connection.encoding)
connection.clientinfo = 'python 2.6 @ home'
connection.module = 'cx_Oracle test_ARDOC.py'
connection.action = 'TestArdocJob'
cursor = connection.cursor()
cursor.execute('select sysdate from dual')
try:
    connection.ping()
except cx_Oracle.DatabaseError as exception:
    error, = exception.args
    logging.warning("ardoc_oracle_job_project_ini.py: Database connection error: '%s' '%s' '%s'", error.code, error.offset, error.message)
else:
    logging.info("ardoc_oracle_job_project_ini.py: Connection is alive!")
cursor.execute("ALTER SESSION SET current_schema = "+oracle_schema)    

# getting nightly ID
cmnd="""
select nid from nightlies where nname = :nname"""
#print "ardoc_oracle_job_project_ini: ",cmnd
cursor.execute(cmnd,{'nname' : nname})
result = cursor.fetchall()
pprint(result)
if len(result) < 1: logging.error("ardoc_oracle_job_project_ini.py: absent nightly name: '%s'",nname); sys.exit(1)   
row=result[-1]
nightly_id=row[0]

relid_j=""
ts_j=""
relnmaster=""
logging.info("ardoc_oracle_job_project_ini.py: TS '%s' release name stamp: '%s'",ts,relnstamp)

#FIND RELID
cmnd="""
SELECT RELID,reltstamp FROM RELEASES WHERE nid = :nightly_id and name = :relname and relnstamp = :relnstamp order by reltstamp desc"""
logging.info("CMND '%s' relnstamp '%s' nightly_id: '%s' relname: '%s'",cmnd,relnstamp,nightly_id,relname)
cursor.execute(cmnd, {'relnstamp' : relnstamp,'nightly_id' : nightly_id,'relname' : relname})
result = cursor.fetchall()
lresult=len(result)
relid_j=""
ts_j=""
for row in result:
#    if row[1] == ts:
        logging.info("ardoc_oracle_job_project_ini.py: relid found: '%s' X '%s' X '%s'",row[0],row[1], ts)
        relid_j=row[0]; ts_j=row[1]
        break
if relid_j == "":
      logging.error("ardoc_oracle_job_project_ini.py: Error: relid for jobs table not found")
      sys.exit(1)
#print "TSJ",ts_j
#print "SSS",ts_j.year,ts_j.month,ts_j.day
#print "SSA",ts_j.date()
#tdd_j=ts_j.date()
#print tdd_j.strftime("%Y%m%d"), nightly_id
relid_jj=""

#=======CHECK PROJECTS TABLE=======
cmnd="""
merge into projects a USING ( select max(projid)+1 as new_projid from projects ) b ON ( projname = :paname )
WHEN NOT MATCHED THEN insert values
( 1, :paname) where b.new_projid is NULL"""
cursor.execute(cmnd,{'paname':paname})

cmnd="""select projid from projects where projname = :paname order by projid"""
cursor.execute(cmnd,{'paname':paname})
result = cursor.fetchall()
if len(result) == 0:
            logging.error("ardoc_oracle_job_project_ini.py: Error: absent project:",paname)
            sys.exit(1)
rowmax=result[-1]
projid_current=rowmax[0]

#
if warea != "" :
  fjid=warea+os.sep+'jid_identificator'
  fjid_p=warea+os.sep+'jid_identificator_' + paname
  f=open(fjid, 'w')
  f.write(str(arjid))
  f.close()
  f=open(fjid_p, 'w')
  f.write(str(arjid))
  f.close()
#
cmnd="""select begdate from jobstat where JID = :jid
and NID = :nightly_id
and RELID = :relid_j
and PROJID = :projid_c
"""
cursor.execute(cmnd,{'jid':arjid,'nightly_id':nightly_id,'relid_j':relid_j,'projid_c':projid_current})
result = cursor.fetchall()
if len(result) > 0:
           logging.error("ardoc_oracle_job_project_ini.py: Error: attempt to add existing jobstat row: arjid,nid,relid,projid '%s' '%s' '%s' '%s'",arjid,nightly_id,relid_j,projid_current)
           sys.exit(1)
#
procid='100000'
hostnam=os.uname()[1]
cmnd="""
insert into jobstat (jid,nid,relid,projid,lastpj,begdate,bconf,hname,processid,hbeat,req,stat,suff) values
( :jid
  , :nightly_id
  , :relid_j
  , :projid_c
  , :lastpj 
  , :t_val
  , :t_val
  , :hostnam
  , :procid
  , :t_val
  , :req
  , :stat
  , :ardoc_suffix
)"""
dict_p={'jid':arjid,'nightly_id':nightly_id,'relid_j':relid_j,'projid_c':projid_current,'lastpj':lastproj,'hostnam':hostnam,'procid':procid,'req':'NONE','stat':'START','t_val':ts_j,'ardoc_suffix':ardoc_suffix}
logging.info("ardoc_oracle_job_project_ini.py: '%s' '%s'", cmnd, dict_p)
cursor.prepare(cmnd)
cursor.setinputsizes(t_val=cx_Oracle.TIMESTAMP)
cursor.execute(None, dict_p)

cursor.close()
connection.commit()
connection.close()
