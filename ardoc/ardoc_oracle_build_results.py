import re
import os, getopt
import sys, logging
import getpass
import platform
import cx_Oracle
from pprint import pprint
import datetime

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
try:
    optionslist, args = getopt.getopt(sys.argv[1:],':c',['complete'])
except getopt.error:
    logging.warning('''ardoc_oracle_build_results: Error: You tried to use an unknown option or the
          argument for an option that requires it was missing.''')
    sys.exit(0)

#for a in optionslist[:]:
#    if a[0] in ('-c','--complete'): opt_complete=1

logging.info("ardoc_oracle_build_results.py: START")
home=os.environ.get('HOME','')
nname=os.environ.get('ARDOC_NIGHTLY_NAME','')
arjid=os.environ.get('ARDOC_JOBID','')
t_epoch=os.environ.get('ARDOC_EPOCH','')
if arjid == "":
    logging.error("ardoc_oracle_build_results.py: Error: ARDOC_JOBID is not defined")
    sys.exit(1)
if t_epoch == "":
    logging.error("ardoc_oracle_build_results.py: Error: ARDOC_EPOCH is not defined")
    sys.exit(1)
if nname == "":
    logging.error("ardoc_oracle_build_results.py: Error: ARDOC_NIGHTLY_NAME is not defined")
    sys.exit(1)

oracle_schema=os.environ.get('ARDOC_ORACLE_SCHEMA','ATLAS_NICOS').strip()
parray=os.environ.get('ARDOC_PROJECT_ARRAY','UNDEF').strip()
paname=os.environ.get('ARDOC_PROJECT_NAME','UNDEF').strip()
if paname == "" : paname='UNDEF'
parray_a=re.split(r'\s+',parray)
lnumber=len(parray_a)
if lnumber == 0: parray_a=[]; parray_a.append(paname)
#
role=os.environ.get('ARDOC_NIGHTLY_ROLE','main')
if len(role) > 6: role=role[0:6]

warea=os.environ.get('ARDOC_WORK_AREA','')
if warea == "":
    logging.error("ardoc_oracle_build_results.py: Error: ARDOC_WORK_AREA is not defined")
    sys.exit(1)
if not os.path.exists(warea):
    logging.error("ardoc_oracle_build_results.py: Error: ARDOC_WORK_AREA: '%s' is not directory" % warea)
    sys.exit(1)
warea_dir=os.path.dirname(warea)
ardoc_webpage=os.environ.get('ARDOC_WEBPAGE','')
ardoc_project_relname=os.environ.get('ARDOC_PROJECT_RELNAME','')
link_base=ardoc_webpage+os.sep+'ARDOC_Log_'+ardoc_project_relname

logging.info("ardoc_oracle_build_results.py: JID :'%s'" % arjid)
jid=arjid

############    
cFN="/afs/cern.ch/atlas/software/dist/nightlies/cgumpert/TC/OW_crdntl"
lne=open(cFN,'r')
lne_res=lne.readline()
lne.close()
lnea=re.split(r'\s+',lne_res)          
accnt,pwf,clust=lnea[0:3]
connection = cx_Oracle.connect(accnt,pwf,clust)
logging.info("Oracle DB version: '%s'", connection.version)
connection.clientinfo = 'python 2.6 @ home'
connection.module = 'cx_Oracle ardoc_oracle_build_results.py'
connection.action = 'TestArdocJob'
cursor = connection.cursor()
try:
    connection.ping()
except cx_Oracle.DatabaseError as exception:
    error, = exception.args
    logging.info("Database connection error: '%s' '%s' '%s'", error.code, error.offset, error.message)
else:
    logging.info("Connection is alive!")

cursor.execute("ALTER SESSION SET current_schema = "+oracle_schema)
cmnd="""
select sys_context(\'USERENV\',\'SESSION_USER\') current_user,sys_context(\'USERENV\',\'SESSION_SCHEMA\') current_schema from dual"""
cursor.execute(cmnd)
result = cursor.fetchall()
logging.info("ardoc_oracle_build_results: session user,schema: '%s'",result[0])

cmnd="""select projid from projects where projname = :paname order by projid"""
cursor.execute(cmnd, {'paname' : paname })
result = cursor.fetchall()
if len(result) == 0:
    logging.error("ardoc_oracle_build_results.py: Error: absent project: '%s'" % paname)
    sys.exit(1)
rowmax=result[-1]
projid_current=rowmax[0]

cmnd="""select relid,nid from jobs where jid = :jid"""
cursor.execute(cmnd, {'jid' : jid })
result = cursor.fetchall()
if len(result) == 0:
    logging.error("ardoc_oracle_build_results.py: Error: absent jid in jobs table: '%s'" % jid)
    sys.exit(1)
rowmax=result[-1]
relid_current=rowmax[0]
nid_current=rowmax[1]

logging.info("ardoc_oracle_build_results.py: projid,nid,relid '%s' '%s' '%s'" % (projid_current,nid_current,relid_current))

cmnd="""select relid,nid from cstat where jid = :jid and projid = :projid_c"""
cursor.execute(cmnd, {'jid' : jid, 'projid_c' : projid_current })
result = cursor.fetchall()
ts_j = datetime.datetime.now()

if len(result) > 0:
    logging.info("ardoc_oracle_build_results.py: Info: CSTAT has already a record for jid,projid: '%s' '%s'",jid,projid_current)
    logging.info("ardoc_oracle_build_results.py: Info: update CSTAT: completion status on '%s'",ts_j) 
    cmnd="""
update CSTAT set enddatecs = :t_val, cstat = :cstat where
jid = :jid and projid = :projid_c"""
    cursor.prepare(cmnd)
    cursor.setinputsizes(t_val=cx_Oracle.TIMESTAMP)
    cursor.execute(None, {'projid_c' : projid_current, 'jid' : jid ,'cstat' : 2,'t_val':ts_j})
else: # if len(result) > 0:
    logging.info("ardoc_oracle_build_results.py: Info: creating CSTAT entry (stat completed) for projid,jid,relid,nid: '%s' '%s' '%s' '%s'",projid_current,jid,relid_current,nid_current)
    cmnd="""
    insert into CSTAT (projid,jid,relid,nid,begdatecs,enddatecs,cstat,npack,ncompl,pccompl,npb,ner,pcpb,pcer) values
( :projid_c
  , :jid
  , :relid_c
  , :nid_c
  , :t_val
  , :t_val
  , :cstat
  , :npack
  , :ncompl, :pccompl, :npb, :ner, :pcpb, :pcer
)"""
    dict_p={ 'projid_c' : projid_current, 'jid' : jid , 'relid_c' : relid_current, 'nid_c': nid_current, 't_val' : ts_j, 'cstat' : 2, 'npack' : 0, 'ncompl' : 0, 'pccompl' : 0, 'npb' : 0, 'ner' : 0, 'pcpb' : 0, 'pcer' : 0 }
    logging.info("ardoc_oracle_build_results.py: '%s' '%s'", cmnd, dict_p)
    cursor.prepare(cmnd)
    cursor.setinputsizes(t_val=cx_Oracle.TIMESTAMP)
    cursor.execute(None, dict_p)
#
# CHECK TSTAT and create entry if absent 
# (so that results are displayed when only compilations completed)
#
cmnd="""select relid,nid from tstat where jid = :jid and projid = :projid_c"""
cursor.execute(cmnd, {'jid' : jid, 'projid_c' : projid_current })
result_t = cursor.fetchall()
if len(result_t) > 0:
    logging.info("ardoc_oracle_build_results.py: Info: TSTAT has already a record for jid,projid: '%s' '%s'",jid,projid_current)
else: # if len(result_t) > 0:
    logging.info("ardoc_oracle_build_results.py: Info: creating TSTAT entry (stat completed) for projid,jid,relid,nid: '%s' '%s' '%s' '%s'",projid_current,jid,relid_current,nid_current)
    cmnd="""
insert into TSTAT (projid,jid,relid,nid,begdatets,tstat,ntests,ncompl,pccompl,npb,ner,pcpb,pcer,nto,pcto) values
( :projid_c
  , :jid
  , :relid_c
  , :nid_c
  , :t_val
  , :tstat
  , :n_tests
  , :ncompl, :pccompl, :npb, :ner, :pcpb, :pcer, :nto, :pcto)"""
    dict_p={ 'projid_c' : projid_current, 'jid' : jid , 'relid_c' : relid_current, 'nid_c': nid_current, 't_val' : ts_j, 'tstat' : 0, 'n_tests' : 0, 'ncompl' : 0, 'pccompl' : 0, 'npb' : 0, 'ner' : 0, 'pcpb' : 0, 'pcer' : 0 ,'nto' : 0, 'pcto' : 0}
    logging.info("ardoc_oracle_build_results.py: completion: '%s' '%s'", cmnd, dict_p)
    cursor.prepare(cmnd)
    cursor.setinputsizes(t_val=cx_Oracle.TIMESTAMP)
    cursor.execute(None, dict_p)

#    
#  CLEANUP AND FILL COMPRESULTS              
#
cmnd="""
delete from compresults where jid = :jid and projid = :projid_c"""
logging.info("ardoc_oracle_build_results.py: cleaning: '%s'", cmnd)
cursor.execute(cmnd, { 'projid_c' : projid_current, 'jid' : jid })
  
fprepage=warea+os.sep+'ardoc_prepage'
lines_db=[]
try:
    mf=open(fprepage)
    lines_db = mf.readlines()
    mf.close()
except:
    lines_db=[]
order_db=[]
forder=warea+os.sep+'ardoc_comporder'
try:
    mf=open(forder)
    order_db = mf.readlines()
    mf.close()
except:
    order_db=[]
item=-1
nprblm=0
nerr=0
list_dict_pp=[]
for x in lines_db:
      item=item+1
      line1=x.strip()
      if len(re.sub(r'\s+','',line1)) == 0 : continue
      fil9=re.split(r' """',line1)
      fil=re.split(r'\s+',fil9[0])
      package=fil[0]
      container=fil[1]
      c_order=0
      if container == 'N/A': container='/'
      for ior, jor in enumerate(order_db):
          line15=jor.strip()
          if len(re.sub(r'\s+','',line15)) == 0 : continue 
          arr15=re.split(r'\s+',line15)
          arr_con='/'
          if len(arr15) > 2 : arr_con=arr15[2] 
#          logging.info "OOOOOOOOO", arr15[0], "++", arr_con, "++", ior 
          if arr15[0] == package and arr_con == container:
               logging.info("ardoc_oracle_build_results.py: Build order '%s' for '%s' / '%s'",ior,arr_con,arr15[0])
               c_order=ior+1
               break
      recent_logfiles=fil[2]
      problems=fil[3]
      if problems != '0' : nprblm=nprblm+1
      if problems == '2' : nerr=nerr+1
      cresult=0
      if problems == "0.5" : cresult=1
      elif problems == "1" : cresult=2
      elif problems == "2" : cresult=3
      qaproblems=fil[4]
      uproblems=fil[5]
      addresses=';'.join(fil[6:])
      pttrns='N/A'
      if len(fil9): pttrns=fil9[2]
      pid_current=0
      cmnd="""select pid from packages where pname = :package and contname = :container"""
#      logging.info cmnd
      cursor.execute(cmnd, {'package' : package, 'container' : container})
      result = cursor.fetchall()
      if len(result) == 0:
          logging.info("ardoc_oracle_build_results.py: new package,container: '%s' '%s' to be added to db", package, container)  
          cmnd="""
merge into packages a USING ( select max(pid)+1 as new_pid from packages ) b
ON ( pname = :package and contname = :cont  )
WHEN NOT MATCHED THEN insert values
( b.new_pid
, :package, :cont)"""
          logging.info("ardoc_oracle_build_results.py: oracle command '%s' '%s' '%s'", cmnd, package, container)
          cursor.execute(cmnd, {'package' : package, 'cont' : container})
          cmnd="""select pid from packages where pname = :package and contname = :container"""
          cursor.execute(cmnd, {'package' : package, 'container' : container})
          result = cursor.fetchall()
      if len(result) > 0:
          rowmax=result[-1]
          pid_current=rowmax[0]
      logging.info("ardoc_oracle_build_results.py: '%s' p,cont: '%s' '%s' log: '%s' pbs: '%s' '%s' '%s' adds: '%s' pttrns: '%s' pid: '%s'",item,package,container,recent_logfiles,cresult,qaproblems,uproblems,addresses,pttrns,pid_current)
      recent_logfiles_link='<a href=\"'+link_base+os.sep+recent_logfiles+'\">'+package+'</a>'
#      logging.info 'LINK:',recent_logfiles_link
      if pid_current != '0':
        dict_pp={'jid':jid,'nid':nid_current,'relid':relid_current,'pid':pid_current,'projid':projid_current,'link':recent_logfiles_link,'cres':cresult,'addr':addresses,'pttrns':pttrns,'t_val':ts_j, 't_z' : 0, 'c_order' : c_order }
      else:
        logging.info("ardoc_oracle_build_results.py: WARNING: no insertion for pid='%s' '%s' '%s'",pid_current,package,container)   
      list_dict_pp.append(dict_pp)
logging.info("ardoc_oracle_build_results: INFO: first 4 members of dict for compresults insertion:") 
pprint(list_dict_pp[0:4])
logging.info("ardoc_oracle_build_results: INFO: end of dict for compresults insertion:")
cmnd="""insert into compresults (JID,NID,RELID,PID,PROJID,CODE,
  NAMELN,ECODE,RES,MNGRS,TSTAMP,ERRID,ERRTEXT,CORDER) values
  (:jid
   , :nid
   , :relid
   , :pid
   , :projid
   , :t_z
   , :link
   , :t_z
   , :cres
   , :addr
   , :t_val
   , :t_z
   , :pttrns
   , :c_order)"""
logging.info("ardoc_oracle_build_results: INFO: oracle query: '%s'",cmnd)
cursor.prepare(cmnd)
cursor.setinputsizes(t_val=cx_Oracle.TIMESTAMP)
cursor.executemany(None,list_dict_pp)

npack=item+1
pcpb=-1.0
pcerr=-1.0
if npack > 0:
    pcpb=100.*nprblm/npack
    pcerr=100.*nerr/npack
logging.info("ardoc_oracle_build_results.py: Info: update CSTAT: N packages, %% problems, %% errors '%s' '%s' '%s'",npack,pcpb,pcerr)    
cmnd="""
  update CSTAT set cstat = :cstat
  , npack = :npack
  , ncompl = :npack
  , pccompl = :pccompl
  , npb = :npb
  , pcpb = :pcpb
  , ner= :ner
  , pcer = :pcer
  where
  jid = :jid and projid = :projid_c
  """
dict_p={ 'cstat' : 2, 'npack' : npack, 'pccompl' : 100.00, 'npb' : nprblm, 'ner' : nerr, 'pcpb' : pcpb, 'pcer' : pcerr, 'jid' : jid, 'projid_c' : projid_current }
logging.info("ardoc_oracle_build_results.py: Command: '%s' '%s'",cmnd,dict_p)
cursor.execute(cmnd,dict_p)

cursor.close()
connection.commit()
connection.close()


