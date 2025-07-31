import re
import os
import sys
import getpass,logging
import platform
import cx_Oracle
from pprint import pprint
import datetime
import smtplib

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
logging.info("ardoc_oracle_interface_script.py: Python version: " + platform.python_version())
logging.info("ardoc_oracle_interface_script.py: cx_Oracle version: " + cx_Oracle.version)
logging.info("ardoc_oracle_interface_script.py: Oracle client: " + str(cx_Oracle.clientversion()).replace(', ','.'))
home=""
nname=""
ngroup="N/A"
incrmode="N/A"
if 'HOME' in os.environ : home=os.environ['HOME']
if 'ARDOC_NIGHTLY_NAME' in os.environ : nname=os.environ['ARDOC_NIGHTLY_NAME']
if nname == "":
    logging.error("ardoc_oracle_interface_script.py: Error: ARDOC_NIGHTLY_NAME is not defined")  
    sys.exit(1)
oracle_schema=os.environ.get('ARDOC_ORACLE_SCHEMA','ATLAS_NICOS').strip()
if 'ARDOC_NIGHTLY_GROUP' in os.environ : ngroup=os.environ['ARDOC_NIGHTLY_GROUP']
if 'ARDOC_INC_BUILD' in os.environ : incrmode=os.environ['ARDOC_INC_BUILD']
ardoc_gen_config_area=os.environ.get('ARDOC_GEN_CONFIG_AREA','')
ardoc_arch=os.environ.get('ARDOC_ARCH','')
arch_a=re.split(r'\-',ardoc_arch)
arch=arch_a[0]
osys=arch_a[1]
comp=arch_a[2]
opt=arch_a[3]
role=os.environ.get('ARDOC_NIGHTLY_ROLE','main')
if len(role) > 6: role=role[0:6]
#
relname=os.environ.get('ARDOC_PROJECT_RELNAME','')
reltype="NIT"
tcrel='N/A'; tcrelbase='N/A'
nightly_group=os.environ.get('ARDOC_NIGHTLY_GROUP','N/A')
nightly_name=os.environ.get('ARDOC_NIGHTLY_NAME','N/A')
buildarea1=os.environ.get('ARDOC_RELHOME','')
buildarea=os.path.dirname(buildarea1)
#NO COPY AREA FOR NOW
copyarea = "N/A"
#copyarea1=os.environ.get('ARDOC_COPY_HOME','')
#copyarea=os.path.dirname(copyarea1)
if buildarea == "": buildarea = 'N/A'
#if copyarea == "": copyarea='N/A'
gitmrlink=os.environ.get('MR_GITLAB_LINK','')
# BUILD TOOL unconditional CMAKE for now
btool='CMAKE'
bvers=''
ts_now = datetime.datetime.now()
now_f=datetime.datetime.strftime(ts_now,'%Y-%m-%d %H:%M')
t_epoch=os.environ.get('ARDOC_EPOCH','')
ts=ts_now
if t_epoch != '':
   fdtt=float(t_epoch)
   ts=datetime.datetime.fromtimestamp(fdtt)
relnstamp=ts.strftime("%Y-%m-%dT%H%M")
logging.info("ardoc_oracle_interface_script.py: date: '%s' release name stamp: '%s'",ts,relnstamp)
#
ardoc_http=os.environ.get('ARDOC_HTTP','')
coma='bash -c \'(unset ARDOC_SUFFIX;ARDOC_PROJECT_NAME=\'PRJ\'; $ARDOC_HOME/ardoc_project_suffix_creator.py)\''
sff=os.popen(coma,'r')
ardoc_suffix=sff.readline()
#    print "SFF",ardoc_suffix
ardoc_webpage=ardoc_http+'/'+ngroup+'WebArea/ardoc_web_area'+ardoc_suffix
logging.info("ardoc_oracle_starter.py: ardoc_webpage: '%s'",ardoc_webpage)
ardoc_webarea=os.path.dirname(ardoc_webpage)
logging.info("ardoc_oracle_starter.py: ardoc_webarea: '%s'",ardoc_webarea)
ardoc_http_build=os.environ.get('ARDOC_HTTP_BUILD','')
logging.info("ardoc_oracle_starter.py: ardoc_http_build: '%s'",ardoc_http_build)
#
ntype="other"
#    ntype="patch"
#    ntype="full"
cFN="/afs/cern.ch/atlas/software/dist/nightlies/cgumpert/TC/OW_crdntl"
lne=open(cFN,'r')
lne_res=lne.readline()
lne.close()
lnea=re.split(r'\s+',lne_res)          
accnt,pwf,clust=lnea[0:3]
#print "XXXX",accnt,pwf,clust
connection = cx_Oracle.connect(accnt,pwf,clust)
logging.info("ardoc_oracle_interface_script.py: Oracle DB version: '%s'",connection.version)
#print ("ardoc_oracle_interface_script.py: Oracle client encoding: " + connection.encoding)
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
    logging.info("ardoc_oracle_interface_script.py: Database connection error: '%s' '%s' '%s'", error.code, error.offset, error.message)
else:
    logging.info("ardoc_oracle_interface_script.py: Connection is alive!")
cursor.execute("ALTER SESSION SET current_schema = "+oracle_schema)
# Cancel long running transaction
#  connection.cancel()
# commit transaction
#  connection.commit()
# rollback transaction
#  connection.rollback()
incrmode_trim = (incrmode[:3]) if len(incrmode) > 3 else incrmode
cmnd="""
merge into nightlies a USING ( select max(nid)+1 as new_nid from nightlies ) b
ON ( nname = :nname )
WHEN NOT MATCHED THEN insert values
( b.new_nid, :nname
, :ngroup
, :ntype
, :valmode_s
, :incrmode_trim, :stat, :btype, :sttime, :stuser )"""
dict_p={'nname' : nname,'ngroup' :ngroup,'ntype' : ntype,'valmode_s' : 'N/A','incrmode_trim' : incrmode_trim,'stat' : 0, 'btype' : '', 'sttime' : ts_now, 'stuser' : ''} 
#print "CMND NN", cmnd, " dict ",dict_p 
cursor.prepare(cmnd)
cursor.setinputsizes(sttime=cx_Oracle.TIMESTAMP)
cursor.execute(None, dict_p)
connection.commit()
cmnd="""
SELECT nid,nname,ngroup,ntype,val,incr,stat,stuser FROM NIGHTLIES where nname = :nname"""
cursor.execute(cmnd,{'nname' : nname})
result = cursor.fetchall()
if len(result) < 1: logging.error("ardoc_oracle_starter.py: absent nightly name: '%s'",nname); sys.exit(1)
for row in result:
    logging.info("ardoc_oracle_interface_script.py: '%s'",row)
row=result[-1]
nightly_id=row[0]
statn=row[6]
stusern=row[7]
relnmaster=""
if stusern == None : stusern="N/A"  
#
cmnd="""
insert into releases (RELID,NID,NAME,TYPE,TCREL,TCRELBASE,URL2LOG,RELTSTAMP,VALIDATION,RELNSTAMP,GITMRLINK,RELNMASTER) 
values ( (select max(a.relid)+1 from releases a), :nightly_id
, :relname
, :reltype
, :tcrel
, :tcrelbase
, :ardoc_webpage
, :t_val
, :validation
, :relnstamp
, :gitmrlink
, :relnmaster )"""
dict_p={'nightly_id' : nightly_id,'relname' : relname,'reltype' : reltype,'tcrel' : tcrel,'tcrelbase' : tcrelbase, 'ardoc_webpage' : ardoc_webpage, 't_val' : ts_now, 'validation' : '', 'relnstamp' : relnstamp, 'gitmrlink' : gitmrlink, 'relnmaster' : relnmaster}
logging.info("CMND  '%s' dict  '%s'",cmnd,dict_p)
cursor.prepare(cmnd)
cursor.setinputsizes(t_val=cx_Oracle.TIMESTAMP)
cursor.execute(None, dict_p)
logging.info("ardoc_oracle_starter.py: bindvars  '%s'", cursor.bindvars)
#
ts_1=ts - datetime.timedelta(days=1)
# FOR NOW ROLE is not taken into account
logging.info("ardoc_oracle_starter.py: tstamps: '%s' '%s' '%s'",ts,ts_1,role)
cmnd="""
SELECT RELID,reltstamp FROM RELEASES WHERE nid = :nightly_id and name = :relname and reltstamp >= :t_val order by reltstamp desc"""
logging.info("CMND '%s', t_val:  '%s' nightly_id: '%s' relname '%s'",cmnd,ts_1,nightly_id,relname)
cursor.execute(cmnd, {'t_val' : ts_1,'nightly_id' : nightly_id,'relname' : relname})
result = cursor.fetchall()
pprint(result)
lresult=len(result)
relid_j=""
ts_j=""
# DOUBLE CHECK RELEASE ENTRY
for row in result:
#    if row[1] == ts:
        logging.info("ardoc_oracle_starter.py: relid found: '%s' XX '%s' '%s'",row[0],row[1], ts)
        relid_j=row[0]; ts_j=row[1]
        break
if relid_j == "":            
    logging.error("ardoc_oracle_starter.py: Error: relid for jobs table not found")
    sys.exit(1)
#    
#tdd_j=ts_j.date()
#JOBID defined from ARDOC_EPOCH
tdd_j=ts
#print tdd_j.strftime("%Y%m%d"), nightly_id
jid_base=int(tdd_j.strftime("%Y%m%d"))*10000000+int(nightly_id)*1000
jid_max=int(tdd_j.strftime("%Y%m%d"))*10000000+int(nightly_id)*1000+999
jid=int(tdd_j.strftime("%Y%m%d"))*10000000+int(nightly_id)*1000
logging.info("ardoc_oracle_starter.py: MASTER jid candidate (base) '%s'", jid)
####
# SEARCH FOR MAX JID, IF ANY
####
role_up=role.upper()
cmnd="""
SELECT JID,RELID,tstamp FROM JOBS WHERE nid = :nightly_id and JID > :jid_base and JID <= :jid_max and tstamp is not null order by tstamp"""
cursor.execute(cmnd,{'nightly_id' : nightly_id,'jid_base' : jid_base,'jid_max' : jid_max})
result = cursor.fetchall()
#print cmnd
rowmax_max=jid
lresult=len(result)
if lresult > 0:
    for row in result:
        logging.info("ardoc_oracle_starter.py: JID,RELID '%s' '%s'", row, jid)
        if row[0] > rowmax_max:
          rowmax_max = row[0] 
#    rowmax=result[-1]
    jid = rowmax_max
    logging.info("ardoc_oracle_starter.py: MAX_JID '%s'",jid) 
# INCREMENT JID FOR A NEW JOB
jid += 1
logging.info("ardoc_oracle_starter.py: incremented max jid: '%s' for relid: '%s' current ts: '%s' ROLE: '%s'",jid,relid_j,ts_j,role_up)
#
cmnd="""
insert into jobs (jid,nid,relid,arch,os,comp,opt,role,kitb,cvmfs,tstamp,webarea,webbuild,btool,bvers,buildarea,copyarea) values
( :jid
, :nightly_id
, :relid_j
, :arch
, :osys
, :comp
, :opt, :role_up
, :z, :z
, :t_val, :ardoc_webarea, :ardoc_http_build, :btool, :bvers, :buildarea, :copyarea)"""
dict_p={'jid' : jid,'nightly_id' : nightly_id,'relid_j' : relid_j,'arch' : arch,'osys' : osys,'comp' : comp,'opt' : opt,'role_up' : role_up,'t_val' : ts_j, 'ardoc_webarea' : ardoc_webarea, 'ardoc_http_build' : ardoc_http_build, 'z' : 0, 'btool' : btool, 'bvers' : bvers, 'buildarea' : buildarea, 'copyarea' : copyarea}
logging.info("CMNDJ '%s' dict '%s'",cmnd,dict_p)
cursor.prepare(cmnd)
cursor.setinputsizes(t_val=cx_Oracle.TIMESTAMP)
cursor.execute(None, dict_p)

cmnd="""
select jid,nid,relid,arch,os,comp,opt,role,kitb,cvmfs,tstamp from jobs where nid = :nightly_id and relid = :relid_j and OS = :osys and COMP = :comp and ARCH = :arch and OPT = :opt and ROLE = :role_up order by tstamp"""
cursor.execute(cmnd,{'nightly_id' : nightly_id,'relid_j' : relid_j,'arch' : arch,'osys' : osys,'comp' : comp,'opt' : opt,'role_up' : role_up})
result = cursor.fetchall()
for row in result:
    print(row)
    rowmax=result[-1]
    lresult=len(result)
    if lresult > 0:
        jid = rowmax[0]
        logging.info("ardoc_oracle_starter.py: job id for jobstat insertion identified: '%s'",jid)
    else:
        logging.error("ardoc_oracle_starter.py: Error: absent job for relid: '%s'",relid_j)
        sys.exit(1)

if ardoc_gen_config_area == '':
    logging.error("ardoc_oracle_starter.py: Error: absent ardoc_gen_config_area")
    sys.exit(1)
fjid=ardoc_gen_config_area+os.sep+'jobid.txt'
f=open(fjid, 'w')
f.write(str(jid))
f.close()
fepoch=ardoc_gen_config_area+os.sep+'jobepoch.txt'
f=open(fepoch, 'w')
f.write(str(t_epoch))
f.close()
logging.info("ardoc_oracle_starter.py: wrote jobid to '%s'"+fjid)
logging.info("ardoc_oracle_starter.py: wrote jobepoch to '%s'"+fepoch)

logging.info("ardoc_oracle_starter.py: bindvars '%s'", cursor.bindvars)
cursor.close()
connection.commit()
connection.close()
