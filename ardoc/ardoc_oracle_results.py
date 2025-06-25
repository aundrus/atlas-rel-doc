import re
import os,getopt,pickle
import sys
import getpass
import platform
import cx_Oracle
from pprint import pprint
import datetime
try:
    optionslist, args = getopt.getopt(sys.argv[1:],':c',['complete'])
except getopt.error:
    print('''ardoc_oracle_results: Error: You tried to use an unknown option or the
    argument for an option that requires it was missing.''')
    sys.exit(0)

opt_complete=0
for a in optionslist[:]:
    if a[0] in ('-c','--complete'): opt_complete=1

print("ardoc_oracle_results.py: START, stage: ",opt_complete)
print(("Python version: " + platform.python_version()))
print(("cx_Oracle version: " + cx_Oracle.version))
print(("Oracle client: " + str(cx_Oracle.clientversion()).replace(', ','.')))
home=""
nname=""
if 'HOME' in os.environ : home=os.environ['HOME']
if 'ARDOC_NIGHTLY_NAME' in os.environ : nname=os.environ['ARDOC_NIGHTLY_NAME']
if nname == "":
    print("ardoc_oracle_results.py: Error: ARDOC_NIGHTLY_NAME is not defined")  
    sys.exit(1)
oracle_schema=os.environ.get('ARDOC_ORACLE_SCHEMA','ATLAS_ARDOC').strip()
parray=os.environ.get('ARDOC_PROJECT_ARRAY','UNDEF').strip()
parray_s=os.environ.get('ARDOC_PROJECT_ARRAY_S','UNDEF').strip()
paname=os.environ.get('ARDOC_PROJECT_NAME','UNDEF').strip()
if paname == "" : paname='UNDEF'
parray_a=re.split(r'\s+',parray)
parray_sa=re.split(r'\s+',parray_s)
lnumber=len(parray_a)
if lnumber == 0:
    parray_a=[]; parray_a.append(paname)
    parray_sa=[]; parray_sa.append(paname)
role=os.environ.get('ARDOC_NIGHTLY_ROLE','master')
if len(role) > 6: role=role[0:6]
relname=os.environ.get('ARDOC_PROJECT_RELNAME_COPY','')
reltype="NIT"
relstbb=os.environ.get('ARDOC_STABLE_RELEASE','')
if relstbb == 'yes': reltype="STB"
tcrel=os.environ.get('ARDOC_ATLAS_RELEASE','')
tcrelbase=os.environ.get('ARDOC_ATLAS_ALT_RELEASE','')
pfilegen=os.environ.get('ARDOC_TEST_DBFILE_GEN','')
if pfilegen == "":
    print("ardoc_oracle_results.py: Error: ARDOC_TEST_DBFILE_GEN is not defined")
    sys.exit(1)
pfilegen_base=os.path.basename(pfilegen)
warea=os.environ.get('ARDOC_WORK_AREA','')
if warea == "":
    print("ardoc_oracle_results.py: Error: ARDOC_WORK_AREA is not defined")
    sys.exit(1)
if not os.path.exists(warea):
    print("ardoc_oracle_results.py: Error: ARDOC_WORK_AREA:",warea," is not directory")
    sys.exit(1)
ardoc_inttests_dir=os.environ.get('ARDOC_INTTESTS_DIR','')
atn_workdir=os.environ.get('ATN_WORKDIR','old')
warea_dir=os.path.dirname(warea)
ardoc_webpage=os.environ.get('ARDOC_WEBPAGE','')
ardoc_web_home=os.environ.get('ARDOC_WEB_HOME','')
ardoc_project_relname_copy=os.environ.get('ARDOC_PROJECT_RELNAME_COPY','')
link_base=ardoc_webpage+os.sep+'ARDOC_TestLog_'+ardoc_project_relname_copy
ctest_tailor_file=os.environ.get('ARDOC_CTEST_TAILOR_LIST','')
gitlabTB=os.environ.get('gitlabTargetBranch','')
print("ardoc_oracle_results.py: Info: gitlabTargetBranch:",gitlabTB)

fjid=warea+os.sep+'jid_identificator'
fjid_p=warea+os.sep+'jid_identificator_' + paname
if ( not os.path.isfile(fjid) ):
    print("ardoc_oracle_results.py: Error: file with jid does not exist:",fjid) 
    sys.exit(1)

mf=open(fjid)
jid=mf.readline().strip()
mf.close()

if jid == '':
    print("ardoc_oracle_results.py: Error: empty jid from",fjid)
    sys.exit(1)

print("ardoc_oracle_results.py: JID read:",jid,"from:",fjid)

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
    if (item < 5 ):
        pprint(ttname_new_trnc_a)
    if len(ttname_new_trnc_a) > 1 :
        if len(ttname_new_trnc_a) > 3 :
            ttname_new_trnc_a.pop()
        ttname_new_trnc='__'.join(ttname_new_trnc_a[1:])
    else:
        ttname_new_trnc=ttname_new
    tdir=fil[2]
    tdir_new=fil[3]
    tsui=fil[4]
    tlimit=int(fil[5])
    tcont=fil[6].strip('/')
    taut=''.join(fil[7:])
    tname_1=re.sub(tname,'',ttname_new_trnc,1)
    tname_final=re.sub('__','',tname_1,1)
    if (item < 5 ):
       print('ardoc_oracle_results.py (first 5): test #',item+1,'fname:',tname,'tname:',tname_final,'dir',tdir,'dir_new',tdir_new,'sui',tsui,'tlimit',tlimit,'cont',tcont,'aut',taut)
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
print(("Oracle DB version: " + connection.version))
connection.clientinfo = 'python 2.6 @ home'
connection.module = 'cx_Oracle ardoc_oracle_results.py'
connection.action = 'TestArdocJob'
cursor = connection.cursor()
try:
    connection.ping()
except cx_Oracle.DatabaseError as exception:
    error, = exception.args
    print(("Database connection error: ", error.code, error.offset, error.message))
else:
    print("Connection is alive!")

cursor.execute("ALTER SESSION SET current_schema = "+oracle_schema)
cmnd="""
select sys_context(\'USERENV\',\'SESSION_USER\') current_user,sys_context(\'USERENV\',\'SESSION_SCHEMA\') current_schema from dual"""
cursor.execute(cmnd)
result = cursor.fetchall()
print('ardoc_oracle_results: session user,schema:',result[0])

cmnd="""select projid from projects where projname = :paname order by projid"""
cursor.execute(cmnd, {'paname' : paname })
result = cursor.fetchall()
if len(result) == 0:
    print("ardoc_oracle_results.py: Error: absent project:",paname)
    sys.exit(1)
rowmax=result[-1]
projid_current=rowmax[0]

cmnd="""select relid,nid from jobs where jid = :jid"""
cursor.execute(cmnd, {'jid' : jid })
result = cursor.fetchall()
if len(result) == 0:
    print("ardoc_oracle_results.py: Error: absent jid in jobs table:",jid)
    sys.exit(1)
rowmax=result[-1]
relid_current=rowmax[0]
nid_current=rowmax[1]

print("ardoc_oracle_results.py: projid,nid,relid",projid_current,nid_current,relid_current)

cmnd="""select relid,nid from tstat where jid = :jid and projid = :projid_c"""
cursor.execute(cmnd, {'jid' : jid, 'projid_c' : projid_current })
result = cursor.fetchall()
ts_j = datetime.datetime.now()
if len(result) > 0:
   print("ardoc_oracle_results.py: Warning: TSTAT has already a record for jid,projid:",jid,projid_current)
#   print "ardoc_oracle_results.py: EXIT"
#   sys.exit(0)
else:
    cmnd="""
insert into TSTAT (projid,jid,relid,nid,begdatets,tstat,ntests,ncompl,pccompl,npb,ner,pcpb,pcer,nto,pcto) values
( :projid_c
  , :jid
  , :relid_c
  , :nid_c
  , :t_val
  , :tstat
  , :n_tests
  , :ncompl, :pccompl, :npb, :ner, :pcpb, :pcer, :nto, :pcto
)"""
    dict_p={ 'projid_c' : projid_current, 'jid' : jid , 'relid_c' : relid_current, 'nid_c': nid_current, 't_val' : ts_j, 'tstat' : 0, 'n_tests' : n_tests, 'ncompl' : 0, 'pccompl' : 0, 'npb' : 0, 'ner' : 0, 'pcpb' : 0, 'pcer' : 0, 'nto' : 0, 'pcto' : 0 }
    print("ardoc_oracle_results.py:", cmnd, "dict", dict_p)
    cursor.prepare(cmnd)
    cursor.setinputsizes(t_val=cx_Oracle.TIMESTAMP)
    cursor.execute(None, dict_p)

output_list_read=[]
allowed_tests=[]
excluded_tests=[]
actually_excluded_tests=[]
if ctest_tailor_file == "" :
    print("ardoc_oracle_results.py: Warning: ctest_tailor_file is not defined")
else:
    if not os.path.isfile(ctest_tailor_file):
        print("ardoc_oracle_results.py: Warning: ctest_tailor_file does not exist: ", ctest_tailor_file)
    else:
        print("ardoc_oracle_results.py: Warning: ctest_tailor_file found: ", ctest_tailor_file)
        with open(ctest_tailor_file, 'rb') as fp:
            objs = []
            while True:
                try:
                    o = pickle.load(fp)
                except EOFError:
                    break
                objs.append(o)
            lenobjs=len(objs)
            print("ardoc_oracle_results.py: Info: number of objects read from ctest_tailor_file: ", str(lenobjs))
            if lenobjs >= 2 :
                allowed_tests=objs[1]
            if lenobjs >= 3 :
                excluded_tests=objs[2] 
            if lenobjs >= 4 :
                actually_excluded_tests=objs[3]

allowed_tests_mod=[re.sub(r'(.*)_ctest',r'\1-test',i9) for i9 in allowed_tests]
excluded_tests_mod=[re.sub(r'(.*)_ctest',r'\1-test',i9) for i9 in excluded_tests]
actually_excluded_tests_mod=[re.sub(r'(.*)_ctest',r'\1-test',i9) for i9 in actually_excluded_tests]
i9=0
for it9 in allowed_tests :
    i9+=1
    print("ardoc_oracle_results.py: Info: from ctest_tailor_file: test allowed: ", str(i9), it9) 
i9=0
for it9 in excluded_tests :
    i9+=1
    print("ardoc_oracle_results.py: Info: from ctest_tailor_file: test excluded: ", str(i9), it9)
i9=0
for it9 in actually_excluded_tests :
    i9+=1
    print("ardoc_oracle_results.py: Info: from ctest_tailor_file: test actually excluded: ", str(i9), it9)
i9=0
for it9 in excluded_tests_mod :
    i9+=1
    print("ardoc_oracle_results.py: Info: from ctest_tailor_file: test excluded (mod): ", str(i9), it9)
i9=0
for it9 in actually_excluded_tests_mod :
    i9+=1
    print("ardoc_oracle_results.py: Info: from ctest_tailor_file: test actually excluded (mod): ", str(i9), it9)
         
if opt_complete == 0:
    cmnd="""
delete from testresults where jid = :jid and projid = :projid_c"""
    print("ardoc_oracle_results.py: cleaning: ", cmnd) 
    cursor.execute(cmnd, { 'projid_c' : projid_current, 'jid' : jid })

item=-1
for fname in ar_fname:
    item=item+1
    tname=ar_tname[item]
    ttname_new=ar_ttname_new[item]
    tcont=ar_cont[item].strip('/')
    tcont_sub=re.sub('/','_',tcont)
    taut=ar_mngrs[item]
    tsui=ar_sname[item]
    tcombin=fname+'#'+tname
    tcombin_link='<a href=\"'+link_base+os.sep+tcont_sub+'_'+ttname_new+'.html\">'+tcombin+'</a>'
    if tcont.find('/')+1: 
       cmnd="""select pid,contname||'/'||pname from packages where (contname||'/'||pname)= :tcont"""
    else:
       cmnd="""select pid,contname||'/'||pname from packages where pname= :tcont""" 
    print('CMND',cmnd)
    cursor.execute(cmnd, { 'tcont' : tcont })
    result = cursor.fetchall()
    pid_current="0"
    if len(result) > 0:
       rowmax=result[-1]
       pid_current=rowmax[0]
    print("PPPP",pid_current)

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
      print("ardoc_oracle_results.py: Warning: no insertion for pid=",pid_current)   
#
    if opt_complete != 1:
      cmnd="""
      select tid from tests where
      name = :tcombin and
      pid = :pid_c
      """ 
#      print cmnd
      cursor.execute(cmnd, {'tcombin' : tcombin, 'pid_c' : pid_current})
      result = cursor.fetchall()
      tid_current=0
      if len(result) > 0:
        rowmax=result[-1]
        tid_current=rowmax[0]
      else:
        print("ardoc_oracle_results.py: Error: absent test in tests table:",tcombin," pid=",pid_current)
        #sys.exit(1)
        continue
      excess_flag=0
      if tname in excluded_tests_mod and (gitlabTB == 'master' or gitlabTB == 'main' or gitlabTB == '23.0'): excess_flag=1
      if tname in actually_excluded_tests_mod: excess_flag=2
      if tname == "CITest_SystemCheck-test" and gitlabTB == '23.0' : excess_flag=2
      print("ardoc_oracle_results.py: TID, tname, excess_flag:",tid_current,tname,excess_flag)  
#
      cmnd="""
      insert into testresults (JID
      ,NID,RELID,TID,PID,PROJID,CODE
      ,TYPE,NAME,NAMELN,FNAME,TNAME,SNAME
      ,ECODE,RES,WDIRLN,MNGRS,TSTAMP,TORDER,EXCESS) values
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
      , :excess
      )""" 
      dict_p={'jid' : jid, 'nid_c' : nid_current, 'relid_c' : relid_current, 'tid_c' : tid_current, 'pid_c' : pid_current, 'projid_c' : projid_current,'code' : 0, 'type' : 'INT', 'tcombin': tcombin, 'tcombin_link' : tcombin_link, 'fname' : fname, 'tname' : tname, 'tsui' : tsui, 'ecode' : 0, 'res' : '-1','wdirln' : 'N/A', 'mngrs' : taut,'t_val' : ts_j, 't_order' : 0, 'excess' : excess_flag}
      if ( item < 5 ):
        print("ardoc_oracle_results.py:CMNDA(5 items)", cmnd, "tval", ts_j)
        print("ardoc_oracle_results.py:CMNDA dict", dict_p)  
      cursor.prepare(cmnd)
      cursor.setinputsizes(t_val=cx_Oracle.TIMESTAMP)
      cursor.execute(None, dict_p)

if opt_complete == 1:
    print("ardoc_oracle_results.py: processing all tests results")
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
#           nprblm=nprblm+1
#           nerr=nerr+1
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
       ttime_beg=str(fil[7])
       ttime_end=str(fil[8])
       tbeg92=''
       if ttime_beg != '' and ttime_beg != '0.0' and ttime_beg != 'N/A':
          if ttime_beg.isdigit(): ttime_beg=str(float(ttime_beg))
          ttime_beg_f=float(ttime_beg)
          if re.match("^\d+?\.\d+?$", ttime_beg):
              tbeg92=datetime.datetime.fromtimestamp(ttime_beg_f)
          else:
              print("ardoc_oracle_results: Warning: test begin epoch time is not float: ",ttime_beg,ttime_beg_f)
       tend92=''
       if ttime_end != '' and ttime_end != '0.0' and ttime_end != 'N/A': 
          if ttime_end.isdigit(): ttime_end=str(float(ttime_end))
          ttime_end_f=float(ttime_end)
          if re.match("^\d+?\.\d+?$", ttime_end):
              tend92=datetime.datetime.fromtimestamp(ttime_end_f)
          else:
              print("ardoc_oracle_results: Warning: test end epoch time is not float: ",ttime_end,ttime_end_f) 
       addresses=';'.join(fil[9:])
       pttrns=fil9[2]
       tname_rplc=tname.replace('___','###')
       tname_rplc_a=re.split('__',tname_rplc)
       tname_rplc_1=''
       if len(tname_rplc_a) == 1: tname_rplc_1=tname_rplc_a[0]
       else: tname_rplc_1=tname_rplc_a[1]
       excess_flag=0
       if tname_rplc_1 in excluded_tests_mod and (gitlabTB == 'master' or gitlabTB == 'main' or gitlabTB == '23.0'): excess_flag=1
       if tname_rplc_1 in actually_excluded_tests_mod: excess_flag=2
       if tname_rplc_1 == "CITest_SystemCheck-test" and gitlabTB == '23.0' : excess_flag=1
       print("ardoc_oracle_results: final test info",tname_rplc_1,'*',tname,"S",tsui,'H',file_html,'R',tresult,'E',tecode,'D',tdir,'B',tname_base,'T',ttime_beg,ttime_end,'A',addresses,'P',pttrns,'EXC',excess_flag) 
       print("ardoc_oracle_results: test start and end stamps: ",tbeg92,' # ',tend92)
       ttname_new_trnc_a=re.split('__',tname_base)
       ttname_new_trnc=tname_base
       if len(ttname_new_trnc_a) > 1 :
           if len(ttname_new_trnc_a) > 3 :
               ttname_new_trnc_a.pop()
               ttname_new_trnc='__'.join(ttname_new_trnc_a[1:])
           else:
               ttname_new_trnc=tname_base
       tname_final=re.sub('__','#',ttname_new_trnc,1)
       test_name_low=re.split('#',tname_final)[0].lower()
       test_suite_low=tsui.lower()

       work_dir=''
       if atn_workdir == "new" :
           work_dir=test_suite_low+'_work'+os.sep+test_name_low+'_work'
       else:
           if re.match('^trig.*$',test_name_low) or test_suite_low == '' :
               work_dir=test_name_low+'_work'
           else:
               work_dir=test_name_low+'_'+test_suite_low+'_work'
       test_warea_link=ardoc_web_home+os.sep+ardoc_project_relname_copy+os.sep+ardoc_inttests_dir+os.sep+work_dir
       cmnd011="update testresults set code = :code, tstamp = :t_val, ecode = :ecode, res = :res, wdirln = :wdirln, errtext = :errtext, excess = :excess"
       cmnd012=""
       cmnd013=" where jid = :jid and projid = :projid_c and name = :tname_final"                                                                                         
######EXIT CODE HARDWIRED TO ZERO       
       dict_p={'code' : 2, 't_val' : ts_j, 'ecode' : 0, 'res' : tresult, 'wdirln' : test_warea_link, 'errtext' : pttrns, 'projid_c' : projid_current, 'jid' : jid, 'tname_final' : tname_final, 'excess' : excess_flag}
       if tbeg92 != '':
           cmnd012=cmnd012+', BEGDATET = :tbeg92'
           dict_p['tbeg92']=tbeg92
       if tend92 != '':
           cmnd012=cmnd012+', ENDDATET = :tend92'
           dict_p['tend92']=tend92
       cmnd=cmnd011+cmnd012+cmnd013
       print("ardoc_oracle_results.py:", cmnd, "dict", dict_p)
       cursor.prepare(cmnd)
       cursor.setinputsizes(t_val=cx_Oracle.TIMESTAMP)
       if tbeg92 != '': cursor.setinputsizes(tbeg92=cx_Oracle.TIMESTAMP)
       if tend92 != '': cursor.setinputsizes(tend92=cx_Oracle.TIMESTAMP)
       cursor.execute(None, dict_p)

    ntest=item+1
    pcpb=-1.0
    pcerr=-1.0
    pcto=-1.0
    if ntest > 0:
        pcpb=100.*nprblm/ntest
        pcerr=100.*nerr/ntest
        pcto=100.*nto/ntest
    print('ardoc_oracle_results.py: Info: N tests,prb,err % problems, % errors',ntest,nprblm,nerr,nto,pcpb,pcerr,pcto)
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
    , pcto= :pcto
    , enddatets = :t_val
    where
    jid = :jid and projid = :projid_c
    """
    dict_p={ 'tstat' : 2, 'ntest' : ntest, 'pccompl' : 100.00, 'npb' : nprblm, 'ner' : nerr, 'pcpb' : pcpb, 'pcer' : pcerr, 'nto' : nto, 'pcto' : pcto, 'jid' : jid, 'projid_c' : projid_current, 't_val' : ts_j }
    print('ardoc_oracle_results.py: Command:',cmnd,cmnd,"dict",dict_p)
    cursor.prepare(cmnd)
    cursor.setinputsizes(t_val=cx_Oracle.TIMESTAMP)
    cursor.execute(None,dict_p)
 
cursor.close()
connection.commit()
connection.close()


