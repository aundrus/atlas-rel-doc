import re
import os,getopt
import sys
import getpass,logging
import platform
import cx_Oracle
from pprint import pprint
import datetime

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
try:
    optionslist, args = getopt.getopt(sys.argv[1:],':c',['complete'])
except getopt.error:
    logging.warning('''ardoc_oracle_test_results: Error: You tried to use an unknown option or the
    argument for an option that requires it was missing.''')
    sys.exit(0)

#for a in optionslist[:]:
#    if a[0] in ('-c','--complete'): opt_complete=1

logging.error("ardoc_oracle_test_results.py: START")
home=os.environ.get('HOME','')
nname=os.environ.get('ARDOC_NIGHTLY_NAME','')
arjid=os.environ.get('ARDOC_JOBID','')
t_epoch=os.environ.get('ARDOC_EPOCH','')
if arjid == "":
    logging.info("ardoc_oracle_test_results.py: Error: ARDOC_JOBID is not defined")
    sys.exit(1)
if t_epoch == "":
    logging.info("ardoc_oracle_test_results.py: Error: ARDOC_EPOCH is not defined")
    sys.exit(1)
if nname == "":
    logging.info("ardoc_oracle_test_results: Error: ARDOC_NIGHTLY_NAME is not defined")
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
    logging.error("ardoc_oracle_build_results.py: Error: ARDOC_WORK_AREA: '%s' is not directory",warea)
    sys.exit(1)
warea_dir=os.path.dirname(warea)
ardoc_webpage=os.environ.get('ARDOC_WEBPAGE','')
ardoc_project_relname=os.environ.get('ARDOC_PROJECT_RELNAME','')
link_base=ardoc_webpage+os.sep+'ARDOC_TestLog_'+ardoc_project_relname

logging.info("ardoc_oracle_test_results.py: JID : '%s'",arjid)
jid=arjid

pfilegen=os.environ.get('ARDOC_TEST_DBFILE','')
if pfilegen == "":
    logging.error("ardoc_oracle_test_results.py: Error: ARDOC_TEST_DBFILE is not defined")
    sys.exit(1)
pfilegen_base=os.path.basename(pfilegen)
ardoc_testlog=os.environ.get('ARDOC_TESTLOG','')
if ardoc_testlog == "":
    logging.error("ardoc_oracle_test_results.py: Error: ARDOC_TESTLOG is not defined")
    sys.exit(1)
ardoc_test_logdir=os.path.dirname(ardoc_testlog)
#
lines_db=[]
try:
    mf=open(pfilegen)
    lines_db = mf.readlines()
    mf.close()
except:
    lines_db=[]

ar_fname=[]
ar_tname=[]
ar_ttname_new=[]
ar_sname=[]
ar_cont=[]
ar_mngrs=[]
item=-1
for x in lines_db:
    item=item+1
    line1=x.strip()
    if len(re.sub(r'\s+','',line1)) == 0 : continue
    fil=re.split(r'\s+',line1)
    tttname=fil[0]
    tname=re.split(r'\.',x)[0]
    tttname_new=fil[1]
    ttname_new=re.split(r'\.',tttname_new)[0]
    ttname_new_trnc_a=re.split('__',ttname_new)
#    print "TTNAME_NEW", ttname_new
#    print "TTNAME_NEW_TRNC_A",ttname_new_trnc_a
    if (item < 5 ):
        pprint(ttname_new_trnc_a)
    if len(ttname_new_trnc_a) > 1 :
        if len(ttname_new_trnc_a) > 3 :
            ttname_new_trnc_a.pop()
        ttname_new_trnc='__'.join(ttname_new_trnc_a[1:])
    else:
        ttname_new_trnc=ttname_new
#    print "TTNAME_NEW_TRNC",ttname_new_trnc
    tdir=fil[2]
    tdir_new=fil[3]
    tsui=fil[4]
    tlimit=int(fil[5])
    tcont=fil[6].strip('/')
    taut=''.join(fil[7:])
    tname_1=re.sub(tname,'',ttname_new_trnc,1)
#    print "TNAME",tname
#    print "TNAME_1",tname_1
    tname_final=re.sub('__','',tname_1,1)
#    print "TNAME_FINAL",tname_final
#    sys.exit(1)
    if (item < 5 ):
       logging.info("ardoc_oracle_test_results.py (first 5): test #'%s' fname: '%s' tname_final: '%s' dir: '%s' dir_new: '%s' sui: '%s' tlimit: '%s' cont: '%s' aut '%s'",item+1,tname,tname_final,tdir,tdir_new,tsui,tlimit,tcont,taut)
    ar_fname.append(tname)
    ar_ttname_new.append(ttname_new)
    ar_tname.append(tname_final)
    ar_cont.append(tcont)
    ar_mngrs.append(taut)
    ar_sname.append(tsui)
n_tests=item+1

############    
cFN="/afs/cern.ch/atlas/software/dist/nightlies/cgumpert/TC/OW_crdntl"
lne=open(cFN,'r')
lne_res=lne.readline()
lne.close()
lnea=re.split(r'\s+',lne_res)          
accnt,pwf,clust=lnea[0:3]
connection = cx_Oracle.connect(accnt,pwf,clust)
logging.info("Oracle DB version: '%s'",connection.version)
connection.clientinfo = 'python 2.6 @ home'
connection.module = 'cx_Oracle ardoc_oracle_test_results.py'
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
logging.info("ardoc_oracle_test_results: session user,schema: '%s'",result[0])

cmnd="""select projid from projects where projname = :paname order by projid"""
cursor.execute(cmnd, {'paname' : paname })
result = cursor.fetchall()
if len(result) == 0:
    logging.error("ardoc_oracle_test_results.py: Error: absent project: '%s'",paname)
    sys.exit(1)
rowmax=result[-1]
projid_current=rowmax[0]

cmnd="""select relid,nid from jobs where jid = :jid"""
cursor.execute(cmnd, {'jid' : jid })
result = cursor.fetchall()
if len(result) == 0:
    logging.error("ardoc_oracle_test_results.py: Error: absent jid in jobs table: '%s'",jid)
    sys.exit(1)
rowmax=result[-1]
relid_current=rowmax[0]
nid_current=rowmax[1]

logging.info("ardoc_oracle_test_results.py: projid,nid,relid '%s' '%s' '%s'",projid_current,nid_current,relid_current)

cmnd="""select relid,nid from tstat where jid = :jid and projid = :projid_c"""
cursor.execute(cmnd, {'jid' : jid, 'projid_c' : projid_current })
result = cursor.fetchall()
ts_j = datetime.datetime.now()
if len(result) > 0:
   logging.info("ardoc_oracle_test_results.py: Info: TSTAT has already a record for jid,projid: '%s' '%s'",jid,projid_current)
   logging.info("ardoc_oracle_test_results.py: Info: update TSTAT: completion status on '%s'",ts_j)
   cmnd=""" 
update TSTAT set enddatets = :t_val, tstat = :tstat where
jid = :jid and projid = :projid_c"""
   cursor.prepare(cmnd)
   cursor.setinputsizes(t_val=cx_Oracle.TIMESTAMP)
   cursor.execute(None, {'projid_c' : projid_current, 'jid' : jid ,'tstat' : 2,'t_val':ts_j})
else: # if len(result) > 0
    cmnd="""
insert into TSTAT (projid,jid,relid,nid,begdatets,enddatets,tstat,ntests,ncompl,pccompl,npb,ner,pcpb,pcer,nto,pcto) values
( :projid_c
  , :jid
  , :relid_c
  , :nid_c
  , :t_val
  , :t_val 
  , :tstat
  , :n_tests
  , :ncompl, :pccompl, :npb, :ner, :pcpb, :pcer, :nto, :pcto
)"""
    dict_p={ 'projid_c' : projid_current, 'jid' : jid , 'relid_c' : relid_current, 'nid_c': nid_current, 't_val' : ts_j, 'tstat' : 0, 'n_tests' : n_tests, 'ncompl' : 0, 'pccompl' : 0, 'npb' : 0, 'ner' : 0, 'pcpb' : 0, 'pcer' : 0 , 'nto' : 0, 'pcto' : 0 }
    logging.info("ardoc_oracle_test_results.py: '%s' dict '%s'",cmnd,dict_p)
    cursor.prepare(cmnd)
    cursor.setinputsizes(t_val=cx_Oracle.TIMESTAMP)
    cursor.execute(None, dict_p)
#
#  CLEANUP AND FILL TESTRESULTS
#

cmnd="""
delete from testresults where jid = :jid and projid = :projid_c"""
logging.info("ardoc_oracle_test_results.py: cleaning: '%s'", cmnd) 
cursor.execute(cmnd, { 'projid_c' : projid_current, 'jid' : jid })

item=-1
for fname in ar_fname:
    item=item+1
    tname=ar_tname[item]
    ttname_new=ar_ttname_new[item]
    tcont=ar_cont[item].strip('/')
#    print "LLLLLLLLLLLLL ",tname,tcont
    tcont_sub=re.sub('/','_',tcont)
    taut=ar_mngrs[item]
    tsui=ar_sname[item]
    tcombin=fname+'#'+tname
    tcombin_link='<a href=\"'+link_base+os.sep+tcont_sub+'_'+ttname_new+'.html\">'+tcombin+'</a>'
    if tcont.find('/')+1: 
       cmnd="""select pid,contname||'/'||pname from packages where (contname||'/'||pname)= :tcont"""
    else:
       cmnd="""select pid,contname||'/'||pname from packages where pname= :tcont""" 
#    logging.info("ardoc_oracle_test_results: CMND '%s' cont '%s'",cmnd,tcont)
    cursor.execute(cmnd, { 'tcont' : tcont })
    result = cursor.fetchall()
    pid_current="0"
    if len(result) > 0:
       rowmax=result[-1]
       pid_current=rowmax[0]
#    logging.info("ardoc_oracle_test_results: project id '%s'",pid_current)

    if pid_current != '0': 
      cmnd="""
merge into tests a USING ( select max(tid)+1 as new_tid from tests ) b ON ( a.name = :tcombin and pid = :pid_c )
WHEN NOT MATCHED THEN insert (a.tid,a.pid,a.name,a.type,a.fname,a.tname) values
( b.new_tid
  , :pid_c
  , :tcombin
  , :type
  , :fname
  , :tname
  )""" 
      dict_p = { 'tcombin' : tcombin, 'pid_c' : pid_current, 'type' : 'INT' ,'fname' : fname,'tname' : tname}    
#    print 'CMND',cmnd 
      cursor.execute(cmnd,dict_p)
    else:
      logging.info("ardoc_oracle_test_results.py: WARNING: no insertion for pid='%s'",pid_current)   
#
    cmnd="""
select tid from tests where
name = :tcombin and
pid = :pid_c""" 
#    print cmnd
    cursor.execute(cmnd, {'tcombin' : tcombin, 'pid_c' : pid_current})
    result = cursor.fetchall()
    tid_current=0
    if len(result) > 0:
        rowmax=result[-1]
        tid_current=rowmax[0]
    else:
        logging.error("ardoc_oracle_test_results.py: Error: absent test in tests table: '%s' pid='%s'",tcombin,pid_current)
        #sys.exit(1)
        continue
#    logging.info("ardoc_oracle_test_results.py: TID found: '%s'",tid_current)  
#
    cmnd="""
      insert into testresults (JID
      ,NID,RELID,TID,PID,PROJID,CODE
      ,TYPE,NAME,NAMELN,FNAME,TNAME,SNAME
      ,ECODE,RES,WDIRLN,MNGRS,TSTAMP,TORDER) values
      (:jid
      , :nid_c
      , :relid_c
      , :tid_c
      , :pid_c
      , :projid_c
      , :code
      , :type
      , :tcombin
      , :tcombin_link
      , :fname
      , :tname
      , :tsui
      , :ecode 
      , :res 
      , :wdirln
      , :mngrs
      , :t_val
      , :t_order
      )""" 
    dict_p={'jid' : jid, 'nid_c' : nid_current, 'relid_c' : relid_current, 'tid_c' : tid_current, 'pid_c' : pid_current, 'projid_c' : projid_current,'code' : 0, 'type' : 'INT', 'tcombin': tcombin, 'tcombin_link' : tcombin_link, 'fname' : fname, 'tname' : tname, 'tsui' : tsui, 'ecode' : 0, 'res' : '-1','wdirln' : 'N/A', 'mngrs' : taut,'t_val' : ts_j, 't_order' : 0 }
    if ( item < 5 ):
        logging.info("ardoc_oracle_test_results.py:CMNDA(5 items) '%s' tval '%s'",cmnd,ts_j)
    cursor.prepare(cmnd)
    cursor.setinputsizes(t_val=cx_Oracle.TIMESTAMP)
    cursor.execute(None, dict_p)

########
logging.info("ardoc_oracle_test_results.py: processing all tests results")
fprepage=warea+os.sep+'ardoc_testprepage'
lines_db=[]
try:
    mf=open(fprepage)
    lines_db = mf.readlines()
    mf.close()
except:
    lines_db=[]
item=-1
nprblm=0
nerr=0
nto=0
list_dict=[]
for x in lines_db:
    item=item+1
    line1=x.strip()
    if len(re.sub(r'\s+','',line1)) == 0 : continue
    fil9=re.split(r' """',line1)
    fil=re.split(r'\s+',fil9[0])
    tname=fil[0]
    tsui=fil[1]
    file_html=fil[2]
    tprob=fil[3]
    tecode=fil[4]
    tresult=0
    if tecode == '10': #timeout
        tresult=10
#        nprblm=nprblm+1
#        nerr=nerr+1
        nto=nto+1
    else:  #no timeout    
        if tprob == "0.5" :
            tresult=1
            nprblm=nprblm+1
        elif tprob == "1" :
            tresult=2
            nprblm=nprblm+1
        elif tprob == "2" :
            tresult=3
            nprblm=nprblm+1
            nerr=nerr+1
    tdir=fil[5]
    tname_base=fil[6]
    addresses=';'.join(fil[7:])
    pttrns=fil9[2]
#       print "TNAME ",tname
    ttname_new_trnc_a=re.split('__',tname)
    ttname_new_trnc_aa=re.split('___',tname)
#       print "TNAME_AA ",ttname_new_trnc_aa
    if len(ttname_new_trnc_aa) > 1 :
        ttname_new_trnc_aa.pop(0)
#        print "TNAME_AA ",ttname_new_trnc_aa
        ttname_new_trnc_j1='___'.join(ttname_new_trnc_aa)
        ttname_new_trnc_a=re.split('__',ttname_new_trnc_j1)
        ttname_new_trnc_a.insert(0,'')
    ttname_new_trnc=tname
    if len(ttname_new_trnc_a) > 1 :
        if len(ttname_new_trnc_a) > 3 :
            ttname_new_trnc_a.pop()
            ttname_new_trnc='__'.join(ttname_new_trnc_a[1:])
    else:
        ttname_new_trnc=tname
#    print "TNAME_A ",ttname_new_trnc_a
#    print "TNAME_AA ",ttname_new_trnc_aa
#    print "TNAME_TRNC",ttname_new_trnc 
    tname_final=re.sub('__','#',ttname_new_trnc,1)
    test_name_low=re.split('#',tname_final)[0].lower() 
    logging.info("ardoc_oracle_test_results: final test info '%s' (db name '%s'),S '%s' H '%s' R '%s' E '%s' 'D '%s' B '%s' A '%s' P '%s'",tname,tname_final,tsui,file_html,tresult,tecode,tdir,tname_base,addresses,pttrns)
#   in path to exitfile the test_name_low directory should be removed. The reason for it is not clear, under investigation
    test_exitfile=ardoc_test_logdir+os.sep+test_name_low+os.sep+tname+'.exitcode'
    exit_code="-1"
    if ( not os.path.isfile(test_exitfile) ):
        logging.info("ardoc_oracle_test_results.py: INFO: file with test exit code does not exist: '%s'",test_exitfile)
    else:
        mf=open(test_exitfile)
        exit_code=mf.readline().strip()
        mf.close()
    logging.info("ardoc_oracle_test_results: test_exitfile: '%s' exit code '%s'",test_exitfile,exit_code)

    cmnd="""select tid,name,tstamp from testresults where jid = :jid and projid = :projid_c and name = :tname_final"""
    cursor.execute(cmnd,{'projid_c' : projid_current, 'jid' : jid, 'tname_final' : tname_final})
#    print "LLLLLL ",cmnd,projid_current,jid,tname_final
    result = cursor.fetchall()
    tid_current=0
    if len(result) > 0:
        rowmax=result[-1]
        tid_current=rowmax[0]
    else:
        logging.error("ardoc_oracle_test_results.py: Error: absent test in testresults table: '%s'",tname_final)
#        sys.exit(1)                                                                                 

    logging.info("ardoc_oracle_test_results.py: Info: test found in testresults table: '%s' '%s' TID '%s'",tname_final,test_name_low,tid_current)
    cmnd="""                                                                                         
update testresults set                                                                           
code = :code, tstamp = :t_val, ecode = :ecode, res = :res, wdirln = :wdirln, errtext = :errtext where
jid = :jid and                                                                                   
projid = :projid_c and                                                                           
name = :tname_final"""
    dict_p={'code' : 2, 't_val' : ts_j, 'ecode' : exit_code, 'res' : tresult, 'wdirln' : 'N/A', 'errtext' : pttrns, 'projid_c' : projid_current, 'jid' : jid, 'tname_final' : tname_final}
    logging.info("ardoc_oracle_test_results.py: testresults update dict '%s'", dict_p)
    cursor.prepare(cmnd)
    cursor.setinputsizes(t_val=cx_Oracle.TIMESTAMP)
    cursor.execute(None, dict_p)

ntest=item+1
pcpb=-1.0
pcerr=-1.0
pcto=-1.0
if ntest > 0:
    pcpb=100.*nprblm/ntest
    pcerr=100.*nerr/ntest
    pcto=100.*nto/ntest
logging.info("ardoc_oracle_test_results.py: Info: N tests,prb,err %% problems, %% errors '%s' '%s' '%s' '%s' '%s' '%s' '%s",ntest,nprblm,nerr,nto,pcpb,pcerr,pcto)
cmnd="""
update TSTAT set tstat = :tstat
, ntests = :ntest
, ncompl = :ntest
, pccompl = :pccompl
, npb = :npb
, pcpb = :pcpb
, ner= :ner
, pcer = :pcer
, nto= :nto
, pcto = :pcto
, enddatets = :t_val
where
jid = :jid and projid = :projid_c"""
dict_p={ 'tstat' : 2, 'ntest' : ntest, 'pccompl' : 100.00, 'npb' : nprblm, 'ner' : nerr, 'pcpb' : pcpb, 'pcer' : pcerr, 'nto' : nto, 'pcto' : pcto, 'jid' : jid, 'projid_c' : projid_current, 't_val' : ts_j }
logging.info("ardoc_oracle_test_results.py: Command:  '%s' '%s' dict '%s'",cmnd,cmnd,dict_p)
cursor.prepare(cmnd)
cursor.setinputsizes(t_val=cx_Oracle.TIMESTAMP)
cursor.execute(None,dict_p)
 
cursor.close()
connection.commit()
connection.close()


