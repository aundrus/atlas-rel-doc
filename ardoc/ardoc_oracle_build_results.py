import re
import os, getopt
import sys
import getpass
import platform
import cx_Oracle
from pprint import pprint
import datetime

try:
    optionslist, args = getopt.getopt(sys.argv[1:],':c',['complete'])
except getopt.error:
    print('''ardoc_oracle_build_results: Error: You tried to use an unknown option or the
          argument for an option that requires it was missing.''')
    sys.exit(0)


opt_complete=0
for a in optionslist[:]:
    if a[0] in ('-c','--complete'): opt_complete=1

print("ardoc_oracle_build_results.py: START, stage: ",opt_complete)
print(("Python version: " + platform.python_version()))
print(("cx_Oracle version: " + cx_Oracle.version))
print(("Oracle client: " + str(cx_Oracle.clientversion()).replace(', ','.')))
home=""
nname=""
if 'HOME' in os.environ : home=os.environ['HOME']
if 'ARDOC_NIGHTLY_NAME' in os.environ : nname=os.environ['ARDOC_NIGHTLY_NAME']
if nname == "":
    print("ardoc_oracle_build_results.py: Error: ARDOC_NIGHTLY_NAME is not defined")  
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
    parray_a=(); parray_a[0]=paname
    parray_sa=(); parray_sa[0]=paname
role=os.environ.get('ARDOC_NIGHTLY_ROLE','master')
if len(role) > 6: role=role[0:6]
reltype="NIT"
relstbb=os.environ.get('ARDOC_STABLE_RELEASE','')
if relstbb == 'yes': reltype="STB"
ciresults=os.environ.get('CI_RESULTS_DICT','')
ciresults_dir=os.path.dirname(ciresults)
tcrel=os.environ.get('ARDOC_ATLAS_RELEASE','')
tcrelbase=os.environ.get('ARDOC_ATLAS_ALT_RELEASE','')
warea=os.environ.get('ARDOC_WORK_AREA','')
if warea == "":
    print("ardoc_oracle_build_results.py: Error: ARDOC_WORK_AREA is not defined")
    sys.exit(1)
if not os.path.exists(warea):
    print("ardoc_oracle_build_results.py: Error: ARDOC_WORK_AREA:",warea," is not directory")
    sys.exit(1)
warea_dir=os.path.dirname(warea)
ardoc_webpage=os.environ.get('ARDOC_WEBPAGE','')
ardoc_project_relname_copy=os.environ.get('ARDOC_PROJECT_RELNAME_COPY','')
link_base=ardoc_webpage+os.sep+'ARDOC_Log_'+ardoc_project_relname_copy

fjid=warea+os.sep+'jid_identificator'
fjid_p=warea+os.sep+'jid_identificator_' + paname
if ( not os.path.isfile(fjid) ):
    print("ardoc_oracle_build_results.py: Error: file with jid does not exist:",fjid) 
    sys.exit(1)

mf=open(fjid)
jid=mf.readline().strip()
mf.close()

if jid == '':
    print("ardoc_oracle_build_results.py: Error: empty jid from",fjid)
    sys.exit(1)

print("ardoc_oracle_build_results.py: JID read:",jid,"from:",fjid)

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
connection.module = 'cx_Oracle ardoc_oracle_build_results.py'
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
print('ardoc_oracle_build_results: session user,schema:',result[0])

cmnd="""select projid from projects where projname = :paname order by projid"""
cursor.execute(cmnd, {'paname' : paname })
result = cursor.fetchall()
if len(result) == 0:
    print("ardoc_oracle_reljobs.py: Error: absent project:",paname)
    sys.exit(1)
rowmax=result[-1]
projid_current=rowmax[0]

cmnd="""select relid,nid from jobs where jid = :jid"""
cursor.execute(cmnd, {'jid' : jid })
result = cursor.fetchall()
if len(result) == 0:
    print("ardoc_oracle_build_results.py: Error: absent jid in jobs table:",jid)
    sys.exit(1)
rowmax=result[-1]
relid_current=rowmax[0]
nid_current=rowmax[1]

print("ardoc_oracle_build_results.py: projid,nid,relid",projid_current,nid_current,relid_current)

cmnd="""select relid,nid from cstat where jid = :jid and projid = :projid_c"""
cursor.execute(cmnd, {'jid' : jid, 'projid_c' : projid_current })
result = cursor.fetchall()
ts_j = datetime.datetime.now()

if opt_complete == 0:
  if len(result) > 0:
    print("ardoc_oracle_build_results.py: Warning: CSTAT has already a record for jid,projid:",jid,projid_current)
#    print "ardoc_oracle_build_results.py: EXIT"
#    sys.exit(0)
  else:
    cmnd="""
insert into CSTAT (projid,jid,relid,nid,begdatecs,cstat,npack,ncompl,pccompl,npb,ner,pcpb,pcer) values
( :projid_c
  , :jid
  , :relid_c
  , :nid_c
  , :t_val
  , :cstat
  , :npack
  , :ncompl, :pccompl, :npb, :ner, :pcpb, :pcer
)"""
    dict_p={ 'projid_c' : projid_current, 'jid' : jid , 'relid_c' : relid_current, 'nid_c': nid_current, 't_val' : ts_j, 'cstat' : 0, 'npack' : 0, 'ncompl' : 0, 'pccompl' : 0, 'npb' : 0, 'ner' : 0, 'pcpb' : 0, 'pcer' : 0 }
    print("ardoc_oracle_reljobs.py:", cmnd, dict_p)
    cursor.prepare(cmnd)
    cursor.setinputsizes(t_val=cx_Oracle.TIMESTAMP)
    cursor.execute(None, dict_p)
else: # opt_complete != 0
  if len(result) > 0:
    cmnd="""
update CSTAT set enddatecs = :t_val, cstat = :cstat where
jid = :jid and projid = :projid_c"""
    print("ardoc_oracle_reljobs.py: completion:", cmnd, "t_val", ts_j)
    cursor.prepare(cmnd)
    cursor.setinputsizes(t_val=cx_Oracle.TIMESTAMP)
    cursor.execute(None, {'projid_c' : projid_current, 'jid' : jid ,'cstat' : 2,'t_val':ts_j})
  else: # if len(result) > 0:
    print("ardoc_oracle_build_results.py: Warning: CSTAT does not have a record for jid,projid:",jid,projid_current)
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
    dict_p={ 'projid_c' : projid_current, 'jid' : jid , 'relid_c' : relid_currnnt, 'nid_c': nid_current, 't_val' : ts_j, 'cstat' : 2, 'npack' : 0, 'ncompl' : 0, 'pccompl' : 0, 'npb' : 0, 'ner' : 0, 'pcpb' : 0, 'pcer' : 0 }
    print("ardoc_oracle_reljobs.py: completion:", cmnd, dict_p)
    cursor.prepare(cmnd)
    cursor.setinputsizes(t_val=cx_Oracle.TIMESTAMP)
    cursor.execute(None, dict_p)
#    
#  CONTINUATION FOR COMPLETION STAGE: OFFSET 2 DIGITS              
#
  cmnd="""
  delete from compresults where jid = :jid and projid = :projid_c"""
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
  list_dict=[]
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
#          print "OOOOOOOOO", arr15[0], "++", arr_con, "++", ior 
          if arr15[0] == package and arr_con == container:
               print("ardoc_oracle_build_results.py: Build order", ior, "for", arr_con, "/",arr15[0])
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
#      print cmnd
      cursor.execute(cmnd, {'package' : package, 'container' : container})
      result = cursor.fetchall()
      if len(result) > 0:
          rowmax=result[-1]
          pid_current=rowmax[0]
      print("ardoc_oracle_build_results.py: ",item,'p,cont:',package,container,'log:',recent_logfiles,'pbs:',cresult,qaproblems,uproblems,'adds:',addresses,'pttrns:',pttrns,'pid:',pid_current)
      recent_logfiles_link='<a href=\"'+link_base+os.sep+recent_logfiles+'\">'+package+'</a>'
#      print 'LINK:',recent_logfiles_link
      if pid_current != '0':
        dict={'jid':jid,'nid':nid_current,'relid':relid_current,'pid':pid_current,'projid':projid_current,'link':recent_logfiles_link,'cres':cresult,'addr':addresses,'pttrns':pttrns,'t_val':ts_j, 't_z' : 0, 'c_order' : c_order }
      else:
        print("ardoc_oracle_build_results.py: WARNING: no insertion for pid=",pid_current,package,container)   
      list_dict.append(dict)
#      cmnd="""insert into compresults (JID,NID,RELID,PID,PROJID,CODE,
#      NAMELN,ECODE,RES,MNGRS,TSTAMP,ERRID,ERRTEXT) values
#      ('%(jid)s'
#      , '%(nid_current)s'
#      , '%(relid_current)s'
#      , '%(pid_current)s'
#      , '%(projid_current)s'
#      , '0'
#      , '%(recent_logfiles_link)s'
#      , '0'
#      , '%(cresult)s'
#      , '%(addresses)s'
#      , :t_val
#      , '0'
#      , '%(pttrns)s')""" % locals()
#      if item < 4:   print 'ardoc_oracle_build_results.py: command for compresults insert',cmnd
#      cursor.prepare(cmnd)
#      cursor.setinputsizes(t_val=cx_Oracle.TIMESTAMP)
#      cursor.execute(None, {'t_val':ts_j})
  print("ardoc_oracle_build_results: INFO: first 4 members of dict for compresults insertion:") 
  pprint(list_dict[0:4])
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
  print("ardoc_oracle_build_results: INFO: end of dict for compresults insertion:")
#  print 'FFFF',cmnd
  cursor.prepare(cmnd)
  cursor.setinputsizes(t_val=cx_Oracle.TIMESTAMP)
  cursor.executemany(None,list_dict)

#  cursor.close()
#  connection.commit()
#  cursor = connection.cursor()
#  cursor.execute("ALTER SESSION SET current_schema = "+oracle_schema)
#
#  CONTINUATION FOR COMPLETION STAGE: OFFSET 2 DIGITS
#
  npack=item+1
  pcpb=-1.0
  pcerr=-1.0
  if npack > 0:
      pcpb=100.*nprblm/npack
      pcerr=100.*nerr/npack
  print('ardoc_oracle_build_results.py: Info: N packages, % problems, % errors',npack,pcpb,pcerr)   
  if ciresults_dir != '':
    if os.path.isdir(ciresults_dir):
       gitlabMergeRequestId=os.environ.get('gitlabMergeRequestId','99999')
       filecproblems=ciresults_dir+os.sep+'cproblems'+paname+'_'+gitlabMergeRequestId 
       print('ardoc_oracle_build_results.py: wrting into '+filecproblems+' '+str(nprblm)+' '+str(nerr))
       f=open(filecproblems, 'w')
       f.write(str(nprblm)+' '+str(nerr)+'\n')
       f.close()
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
  print('ardoc_oracle_build_results.py: Command:',cmnd,dict_p)
  cursor.execute(cmnd,dict_p)

cursor.close()
connection.commit()
connection.close()


