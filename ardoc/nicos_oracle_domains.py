import re
import os
import sys
import getpass
import platform
import cx_Oracle
from pprint import pprint
import datetime
#print ("Python version: " + platform.python_version())
#print ("cx_Oracle version: " + cx_Oracle.version)
#print ("Oracle client: " + str(cx_Oracle.clientversion()).replace(', ','.'))
home=""
warea=""
nname=""
if 'HOME' in os.environ : home=os.environ['HOME']
oracle_schema=os.environ.get('ARDOC_ORACLE_SCHEMA','ATLAS_ARDOC').strip()
ardoc_gen_config_area=os.environ.get('ARDOC_GEN_CONFIG_AREA','')
parray=os.environ.get('ARDOC_PROJECT_ARRAY','')
paname=os.environ.get('ARDOC_PROJECT_NAME','')
parray_a=re.split(r'\s+',parray)
nightly_name=os.environ.get('ARDOC_NIGHTLY_NAME','N/A')
ts_now = datetime.datetime.now()
t_epoch=os.environ.get('ARDOC_EPOCH','')
training_domain=os.environ.get('MR_TRAINING_DOMAIN','').strip()
training_domain_name=re.sub('/','___',training_domain)
training_gittagbase=os.environ.get('MR_TRAINING_GITTAGBASE','').strip()

if training_domain == "":
    print("ardoc_oracle_domains.py: Error: MR_TRAINING_DOMAIN is not defined")
    sys.exit(1)
ts=ts_now
if t_epoch != '':
    fdtt=float(t_epoch)
    ts=datetime.datetime.fromtimestamp(fdtt)
relnstamp=ts.strftime("%Y-%m-%dT%H%M")
#RELID NID NAME TYPE TCREL TCRELBASE URL2LOG
ardoc_arch=os.environ.get('ARDOC_ARCH','')
arch_a=re.split(r'\-',ardoc_arch)
arch=arch_a[0]
osys=arch_a[1]
comp=arch_a[2]
opt=arch_a[3]
#
cFN="/afs/cern.ch/atlas/software/dist/nightlies/cgumpert/TC/OW_crdntl"
lne=open(cFN,'r')
lne_res=lne.readline()
lne.close()
lnea=re.split(r'\s+',lne_res)          
accnt,pwf,clust=lnea[0:3]
#print "XXXX",accnt,pwf,clust
#
jid_res=''
fjid=ardoc_gen_config_area+os.sep+'jobid.txt'
if os.path.isfile(fjid) :
    f=open(fjid, 'r')
    jid_res=f.readline()
    f.close()
if jid_res == '':
    print("ardoc_oracle_domains.py: Error: JOB ID could not be retrieved")
    sys.exit(1)
print("ardoc_oracle_domains.py: jid retrieved from file: ",jid_res)    
connection = cx_Oracle.connect(accnt,pwf,clust)
#print ("Oracle DB version: " + connection.version)
#print ("Oracle client encoding: " + connection.encoding)
connection.clientinfo = 'python 2.6 @ home'
connection.module = 'cx_Oracle test_ARDOC.py'
connection.action = 'TestNicosJob'
cursor = connection.cursor()
cursor.execute('select sysdate from dual')
try:
    connection.ping()
except cx_Oracle.DatabaseError as exception:
    error, = exception.args
    print(("ardoc_oracle_domains.py: Database connection error: ", error.code, error.offset, error.message))
else:
    print("ardoc_oracle_domains.py: Connection is alive!")
cursor.execute("ALTER SESSION SET current_schema = "+oracle_schema)    

cmnd="""
merge into domains a USING ( select max(did)+1 as new_did from domains ) b   
ON ( dcont = :dcont )
WHEN NOT MATCHED THEN insert values
( b.new_did, :dname, :dcont )"""
dict_p={'dname' : training_domain_name, 'dcont' : training_domain} 
print("CMND", cmnd, " dict ",dict_p) 
cursor.execute(cmnd, dict_p)

cmnd="""
SELECT did,dname,dcont FROM DOMAINS where dcont = :dcont"""
cursor.execute(cmnd,{'dcont' : training_domain})
result = cursor.fetchall()
if len(result) < 1: print("ardoc_oracle_domains.py: absent domain container name: ",training_domain); sys.exit(1)
row=result[-1]
domid=row[0]
print('ardoc_oracle_domains.py: TS',ts_now," relnstamp: ",relnstamp, " jid: ",jid_res, "dom: ",training_domain,domid)
cmnd="""
select res,projname,name,nameln,pname,contname,to_char(tstamp, 'RR/MM/DD HH24:MI'), 
fname, nid, relid, tid, pid,  
projid from testresults natural join jobstat natural join projects natural join packages where jid = :jid"""
cursor.execute(cmnd,{'jid' : jid_res})
result = cursor.fetchall()

lresult=len(result)
print("FFF",lresult)
iter=0
for row in result:
    iter+=1
    rescode=row[0]
    proj9=row[1]
    name9=row[2]
    nmln9=row[3]
    pack9=row[4]
    cont9=row[5]
    tsta9=row[6]
    fnam9=row[7]
    nid9=row[8]
    relid9=row[9]
    tid9=row[10]
    pid9=row[11]
    projid9=row[12]
    print("===PROJ ",proj9, "TEST ",name9,nmln9,fnam9)
    print("---------> RES ",rescode, "TIME ",tsta9)
    print(":::::::::> NID,RELID,TID,PID,PROJID",nid9,relid9,tid9,pid9,projid9)
    print("+++++++++> PACK ", pack9, " CONT", cont9)
    
    if jid_res == "" or projid9 == "":
        print("ardoc_oracle_domains.py: Warning: JID =${jid_res}= or PROJID =${projid9}= empty, skipping tdomresults inserts")
        continue
    if iter == 1: 
        cmnd="""
delete from tdomresults where jid = :jid and projid = :projid"""
        print("ardoc_oracle_domains.py: cleaning: ", cmnd, { 'projid' : projid9, 'jid' : jid_res })
        cursor.execute(cmnd, { 'projid' : projid9, 'jid' : jid_res })
#
        cmnd="""update jobs set did = :did, gittagbase = :training_gittagbase where jid = :jid"""
        dict_p={ 'did' : domid, 'training_gittagbase' : training_gittagbase, 'jid' : jid_res }
        print("ardoc_oracle_domains.py: Oracle command", cmnd," # ",dict_p)
        cursor.execute(cmnd, dict_p)
#   updflag should be set for 1 when the result is from a regular (not calibration) CI job
    updflag=0
    cmnd="""
insert into tdomresults
(jid,nid,relid,did,tid,pid,projid,dres,tdstamp,updflag)
values (
:jid,:nid,:relid,:did,:tid,:pid,:projid,:dres,:tdstamp,:updflag
)"""  
    dict_p={'jid' : jid_res,'nid' : nid9,'relid' : relid9,'did' : domid,'tid' : tid9,'pid' : pid9,'projid' : projid9,'dres' : rescode, 'tdstamp' : ts_now,'updflag' : updflag}
    print("CMND", cmnd,'\n',dict_p)
    cursor.prepare(cmnd)
    cursor.setinputsizes(tdstamp=cx_Oracle.TIMESTAMP)
    cursor.execute(None, dict_p)    

cursor.close()
connection.commit()
connection.close()

