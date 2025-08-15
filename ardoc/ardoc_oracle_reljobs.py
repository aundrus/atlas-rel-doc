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
if 'ARDOC_WORK_AREA' in os.environ : warea=os.environ['ARDOC_WORK_AREA']
if 'ARDOC_NIGHTLY_NAME' in os.environ : nname=os.environ['ARDOC_NIGHTLY_NAME']
if nname == "":
    print("ardoc_oracle_reljobs.py: Error: ARDOC_NIGHTLY_NAME is not defined")  
    sys.exit(1)
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
        print("ardoc_oracle_reljobs.py: Info: current project", paname, " is not the first (",parray_a[0],")")
        print("ardoc_oracle_reljobs.py: Info: limited db insertions")
        firstproj=0
    if parray_a[-1] == paname:
        lastproj=1
target_branch=os.environ.get('ARDOC_TARGET_BRANCH','UNKNOWN').strip()
print("ardoc_oracle_reljobs.py: Info: TARGET BRANCH: ",target_branch)
relname=os.environ.get('ARDOC_PROJECT_RELNAME_COPY','')
reltype="NIT"
relstbb=os.environ.get('ARDOC_STABLE_RELEASE','')
if relstbb == 'yes': reltype="STB"
tcrel=os.environ.get('ARDOC_ATLAS_RELEASE','')
tcrelbase=os.environ.get('ARDOC_ATLAS_ALT_RELEASE','')
validation=os.environ.get('ARDOC_VAL_MODE','')
nightly_group=os.environ.get('ARDOC_NIGHTLY_GROUP','N/A')
nightly_name=os.environ.get('ARDOC_NIGHTLY_NAME','N/A')
buildarea1=os.environ.get('ARDOC_PROJECT_HOME','')
buildarea=os.path.dirname(buildarea1)
copyarea1=os.environ.get('ARDOC_COPY_HOME','')
copyarea=os.path.dirname(copyarea1)
if buildarea == "" : buildarea='N/A'
if copyarea == "" : copyarea='N/A'
cmakevers=os.environ.get('CMAKE_VERSION','')
btool='CMAKE'
bvers=cmakevers
url2log=os.environ.get('ARDOC_WEBPAGE','')
ts_now = datetime.datetime.now()
t_epoch=os.environ.get('ARDOC_EPOCH','')
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
role=os.environ.get('ARDOC_NIGHTLY_ROLE','master')
if len(role) > 6: role=role[0:6]
ardoc_kitb=os.environ.get('ARDOC_KIT_TOOL','void')
ardoc_cvmfs=os.environ.get('ARDOC_CVMFS_TOOL','void')
ardoc_webpage=os.environ.get('ARDOC_WEBPAGE','')
ardoc_webarea=os.path.dirname(ardoc_webpage)
ardoc_http_build=os.environ.get('ARDOC_HTTP_BUILD','')
ardoc_suffix=os.environ.get('ARDOC_SUFFIX','')
gitmrlink=os.environ.get('MR_GITLAB_LINK','')
gitmrhash=os.environ.get('MR_GITHASH','')
kitb = (0,1)[ardoc_kitb.lower().strip() != 'no' and ardoc_kitb.lower().strip() != 'void' ]
#print "KBBBB",ardoc_kitb.lower().strip(),kitb
cvmfs = (0,1)[ardoc_cvmfs.lower().strip() == 'yes']
#coma='bash -c \'if [ -f $ARDOC_WORK_AREA/ardoc_errorhandler_gen ]; then source $ARDOC_WORK_AREA/ardoc_errorhandler_gen >/dev/null 2>&1; echo \"${ARDOC_MAIL};${ARDOC_MAIL_INT_TESTS};${ARDOC_MAIL_QA_TESTS}\"; fi\''
#sff=os.popen(coma,'r')
#sff_res=sff.readline()
#sff_a=re.split(r'\;',sff_res)
#mailc = (0,1)[sff_a[0].lower().strip() == 'yes']
#maili = (0,1)[sff_a[1].lower().strip() == 'yes']
#mailq = (0,1)[sff_a[2].lower().strip() == 'yes']
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
print("ardoc_oracle_reljobs.py: jid retrieved from file: ",jid_res)    
####if role == 'master'
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
    print(("ardoc_oracle_reljobs.py: Database connection error: ", error.code, error.offset, error.message))
else:
    print("ardoc_oracle_reljobs.py: Connection is alive!")
cursor.execute("ALTER SESSION SET current_schema = "+oracle_schema)    
# Cancel long running transaction
#  connection.cancel()
# commit transaction
#  connection.commit()
# rollback transaction
#  connection.rollback()
#cmnd="""
#select nid from nightlies where regexp_like(nname,'MIG') order by nid"""  % locals()
cmnd="""
select nid from nightlies where nname = :nname"""
print("ardoc_oracle_reljobs: ",cmnd)
cursor.execute(cmnd,{'nname' : nname})
result = cursor.fetchall()
pprint(result)
#print "(name, type_code, display_size, internal_size, precision, scale, null_ok)"
#pprint(cursor.description)
if len(result) < 1: print("ardoc_oracle_reljobs.py: absent nightly name: ",nname); sys.exit(1)   
#for row in result:
#    print row
row=result[-1]
nightly_id=row[0]
relid_j=""
ts_j=""
relnmaster=""
print('ardoc_oracle_reljobs.py: TS',ts," release name stamp: ",relnstamp)

if role == 'master' and jid_res == '' :
    if firstproj == 1:
      cmnd="""
insert into releases (RELID,NID,NAME,TYPE,TCREL,TCRELBASE,URL2LOG,RELTSTAMP,VALIDATION,RELNSTAMP,GITMRLINK,RELNMASTER) 
values ( ( select max(a.relid)+1 from releases a), :nightly_id
, :relname
, :reltype
, :tcrel
, :tcrelbase
, :url2log
, :t_val
, :validation
, :relnstamp
, :gitmrlink
, :relnmaster )"""
      dict_p={'nightly_id' : nightly_id,'relname' : relname,'reltype' : reltype,'tcrel' : tcrel,'tcrelbase' : tcrelbase, 'url2log' : url2log, 't_val' : ts, 'validation' : validation, 'relnstamp' : relnstamp, 'gitmrlink' : gitmrlink, 'relnmaster' : relnmaster}
      print("CMND", cmnd, dict_p)
      cursor.prepare(cmnd)
      cursor.setinputsizes(t_val=cx_Oracle.TIMESTAMP)
      cursor.execute(None, dict_p)

ts_1=ts
if jid_res != '' :
    ts_1=ts - datetime.timedelta(minutes=100)
if firstproj == 0 or role != 'master':
    ts_1=ts - datetime.timedelta(days=2)
print('ardoc_oracle_reljobs.py: tstamps:',ts,ts_1)
cmnd="""
SELECT RELID,reltstamp FROM RELEASES WHERE nid = :nightly_id and name = :relname and reltstamp > :t_val order by reltstamp"""
print("CMND", cmnd, {'t_val' : ts_1,'nightly_id' : nightly_id,'relname' : relname})
cursor.execute(cmnd, {'t_val' : ts_1,'nightly_id' : nightly_id,'relname' : relname})
result = cursor.fetchall()
lresult=len(result)
    #lOut = cursor.var(cx_Oracle.TIMESTAMP)
    #cursor.execute("BEGIN :out := :t_val; END;",{'out' : lOut, 't_val' : ts})  
    #print lOut
print("FFF",lresult)
relid_j=""
ts_j=""
if firstproj == 1 and  role == 'master':
    for row in result:
#        print "AAAA1",row[1]
#        print ts
        if row[1] == ts:
            print("ardoc_oracle_reljobs.py: relid found:",row[0],' XX ',row[1], ts)
            relid_j=row[0]; ts_j=row[1]
            break
else:
    if lresult > 0:
        rowmax=result[-1]
#        for row in result:
#            print row
        ts_2=ts - datetime.timedelta(days=2)
        if rowmax[1] > ts_2:
            print("ardoc_oracle_reljobs.py: relid found:",rowmax[0],' XX ',rowmax[1],' > ', ts_2)
            relid_j=rowmax[0]; ts_j=rowmax[1]
#
if relid_j == "":
      print("ardoc_oracle_reljobs.py: Error: relid for jobs table not found")
      sys.exit(1)
#print "TSJ",ts_j
#print "SSS",ts_j.year,ts_j.month,ts_j.day
#print "SSA",ts_j.date()
tdd_j=ts_j.date()
#print tdd_j.strftime("%Y%m%d"), nightly_id
if jid_res == '' :
    jid_base=int(tdd_j.strftime("%Y%m%d"))*10000000+int(nightly_id)*1000
    jid_max=int(tdd_j.strftime("%Y%m%d"))*10000000+int(nightly_id)*1000+999
    jid=int(tdd_j.strftime("%Y%m%d"))*10000000+int(nightly_id)*1000
    print("ardoc_oracle_reljobs.py: MASTER jid candidate (base):", jid)
else:
    jid=jid_res
    jid_base=(int(jid)/1000)*1000
    jid_max=jid_base+999
    print("ardoc_oracle_reljobs.py: jid from file:",jid,jid_base)
####
if firstproj != 1 or role != 'master':
    ts_j=ts_now
#
role_up=role.upper()
relid_jj=""
#cmnd="""
#SELECT JID,RELID,tstamp FROM JOBS WHERE nid = '%(nightly_id)s' and JID > '%(jid_base)s' and JID <= '%(jid_max)s' and OS = '%(osys)s' and COMP = '%(comp)s' and ARCH = '%(arch)s' and OPT = '%(opt)s' and ROLE = '%(role_up)s' order by tstamp""" % locals()
cmnd="""
SELECT JID,RELID,tstamp FROM JOBS WHERE nid = :nightly_id and JID > :jid_base and JID <= :jid_max order by tstamp"""
cursor.execute(cmnd,{'nightly_id' : nightly_id,'jid_base' : jid_base,'jid_max' : jid_max})
result = cursor.fetchall()
#print cmnd
lresult=len(result)
if lresult > 0:
  for row in result:
    print('ardoc_oracle_reljobs.py: JID,RELID', row)
  rowmax=result[-1]
  jid = rowmax[0]
  relid_jj = rowmax[1]
#  if firstproj == 1 and  role != 'master': ts_j=rowmax[2]

if firstproj == 1 and jid_res == '':
    jid += 1
    relid_jj=relid_j 
print("ardoc_oracle_reljobs.py: max jid:",jid," for relid:",relid_j,relid_jj," current ts:",ts_j," ROLE ",role_up) 
if relid_jj == "" or relid_j != relid_jj:
    print("ardoc_oracle_reljobs.py: Warning: relid from jobs table differs from releases table",relid_j," xx ",relid_jj) 
#
if firstproj == 1:
  if jid_res == '':  
    cmnd="""
insert into jobs (jid,nid,relid,arch,os,comp,opt,role,kitb,cvmfs,tstamp,webarea,webbuild,btool,bvers,buildarea,copyarea,gitbr,githash) values
( :jid
, :nightly_id
, :relid_j
, :arch
, :osys
, :comp
, :opt, :role, :kitb
, :cvmfs
, :t_val, :ardoc_webarea, :ardoc_http_build, :btool, :bvers, :buildarea, :copyarea, :target_branch, :gitmrhash)"""
    dict_p={'jid':jid,'nightly_id':nightly_id,'relid_j':relid_j,'arch':arch,'osys':osys,'comp':comp,'opt':opt,'role':role_up,'kitb':kitb,'cvmfs':cvmfs,'t_val':ts_j,'ardoc_webarea':ardoc_webarea,'ardoc_http_build':ardoc_http_build, 'btool' : btool, 'bvers' : bvers, 'buildarea' : buildarea, 'copyarea' : copyarea, 'target_branch' : target_branch, 'gitmrhash' : gitmrhash}
    print("CMNDJ", cmnd,dict_p)
    cursor.prepare(cmnd)
    cursor.setinputsizes(t_val=cx_Oracle.TIMESTAMP)
    cursor.execute(None, dict_p)
  else:
    cmnd="""
update jobs set kitb = :kitb
,cvmfs = :cvmfs
,webarea = :ardoc_webarea
,webbuild = :ardoc_http_build
,buildarea = :buildarea 
,copyarea = :copyarea
,gitbr = :target_branch where 
jid = :jid"""
    dict_p={'jid':jid_res,'kitb':kitb,'cvmfs':cvmfs,'ardoc_webarea':ardoc_webarea,'ardoc_http_build':ardoc_http_build,'buildarea':buildarea,'copyarea':copyarea,'target_branch':target_branch}
    print("CMNDJU", cmnd,dict_p)
    cursor.execute(cmnd,dict_p)
cmnd="""
select jid,nid,relid,arch,os,comp,opt,role,kitb,cvmfs,tstamp from jobs where nid = :nightly_id and relid = :relid_j and OS = :osys and COMP = :comp and ARCH = :arch and OPT = :opt and ROLE = :role order by tstamp"""
cursor.execute(cmnd,{'nightly_id':nightly_id,'relid_j':relid_j,'osys':osys,'comp':comp,'arch':arch,'opt':opt,'role':role_up})
result = cursor.fetchall()
for row in result:
        print(row)
rowmax=result[-1]
lresult=len(result)
if lresult > 0:
    jid = rowmax[0]
    print("ardoc_oracle_reljobs.py: job id for jobstat insertion identified:",jid)
else:
    print("ardoc_oracle_reljobs.py: Error: absent job for relid:",relid_j)
    sys.exit(1)
hostnam=os.uname()[1]
prcid=os.getpid()
usid=os.getuid()
parid=os.getppid() 
#print "ardoc_oracle_reljobs.py: PID,PPID,USERID", prcid, parid, usid
command = 'ps -w -u ' + str(usid) + ' -o pgid,pid,ppid,args'
#print "COM", command
global psraw
psraw = os.popen(command).readlines()
def pnid(parid8, N=1):
    while N > 0:
        for ps in psraw[1:]:
            splps=ps.split()
            ppid9=splps[2]
            pid9=splps[1]
            arg9=splps[3]
#            print "LLLLL", parid8, pid9, ppid9, arg9 
            if int(pid9) == int(parid8) :
                parid8=ppid9
#                print "66666", ppid9, arg9 
                break
        else:
            raise RuntimeError("can't locate PPid line")
        N -= 1
    return int(parid8)    
pnid(parid,1)
##command = "ps eo pid,pgid,ppid"
##psraw = os.popen(command).readlines()
##psList = []
##for ps in psraw[1:]: # 1: gets rid of header
##    psList.append(map(int,ps.split()))
##pgid = 0
## find the pgid of the spawned subprocess:
##for ps in psList:
##    if int(self.p.pid) in ps:
##          pgid = ps[1]
##          break
##if pgid == 0:
##   print >>sys.stderr, "Something screwed up trying to find pids. fudge."
##   return
# get a list of all pids in the pgid except the group owner:
##for ps in psList:
##    if pgid in ps and pgid != ps[0]:  # check [0] so we don't kill ourselves
##         killList.append(ps[0])
# don't do anything if we didn't find anything:
##if len(killList) <= 0:
##   return
# kill the bastards:
##command = "kill %s" % string.join(map(str,killList[:-1]),' ')
##print "killing subprocesses with '%s'" % command
##os.system(command)

#=======ONLY NEEDED FOR THE CASE OF EMPTY TABLE=======
cmnd="""
merge into projects a USING ( select max(projid)+1 as new_projid from projects ) b ON ( projname = :paname )
WHEN NOT MATCHED THEN insert values
( 1, :paname) where b.new_projid is NULL"""
cursor.execute(cmnd,{'paname':paname})

cmnd="""
merge into projects a USING ( select max(projid)+1 as new_projid from projects ) b ON ( projname = :paname )
WHEN NOT MATCHED THEN insert values
( b.new_projid, :paname)"""
cursor.execute(cmnd,{'paname':paname})

cmnd="""select projid from projects where projname = :paname order by projid"""
cursor.execute(cmnd,{'paname':paname})
result = cursor.fetchall()
if len(result) == 0:
            print("ardoc_oracle_reljobs.py: Error: absent project:",paname)
            sys.exit(1)
rowmax=result[-1]
projid_current=rowmax[0]

#
if warea != "" :
  fjid=warea+os.sep+'jid_identificator'
  fjid_p=warea+os.sep+'jid_identificator_' + paname
  f=open(fjid, 'w')
  f.write(str(jid))
  f.close()
  f=open(fjid_p, 'w')
  f.write(str(jid))
  f.close()
#
cmnd="""select begdate from jobstat where JID = :jid
and NID = :nightly_id
and RELID = :relid_j
and PROJID = :projid_c
"""
cursor.execute(cmnd,{'jid':jid,'nightly_id':nightly_id,'relid_j':relid_j,'projid_c':projid_current})
result = cursor.fetchall()
if len(result) > 0:
           print("ardoc_oracle_reljobs.py: Error: attempt to add existing jobstat row: jid,nid,relid,projid",jid,nightly_id,relid_j,projid_current)
           sys.exit(1)
#
procid='100000'
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
dict_p={'jid':jid,'nightly_id':nightly_id,'relid_j':relid_j,'projid_c':projid_current,'lastpj':lastproj,'hostnam':hostnam,'procid':procid,'req':'NONE','stat':'START','t_val':ts_j,'ardoc_suffix':ardoc_suffix}
print("ardoc_oracle_reljobs.py:", cmnd, dict_p)
cursor.prepare(cmnd)
cursor.setinputsizes(t_val=cx_Oracle.TIMESTAMP)
cursor.execute(None, dict_p)

cursor.close()
connection.commit()
connection.close()
