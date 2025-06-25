import re
import os
import sys
import getpass
import platform
import cx_Oracle
from pprint import pprint
import datetime
import getopt

if len(sys.argv) < 2 :
    print("ardoc_oracle_jobstat: Error: no options specified\n")
    sys.exit(1)
try:
    optionslist, args = getopt.gnu_getopt(sys.argv[1:],'o:s:p:',['nochange'])
except getopt.error:
    print('''Error: You tried to use an unknown option or the
                    argument for an option that requires it was missing.''')
    sys.exit(1)
                        
#print ("Python version: " + platform.python_version())
#print ("cx_Oracle version: " + cx_Oracle.version)
#print ("Oracle client: " + str(cx_Oracle.clientversion()).replace(', ','.'))

optStepName=""
statusCode=""
param=""

for a in optionslist[:]:
    if a[0] == '-o' and a[1] != '':
      optStepName=a[1]
    elif a[0] == '-s' and a[1] != '':
      statusCode=a[1]
    elif a[0] == '-p' and a[1] != '':  
      param=a[1]
    elif a[0] == '--nochange':
      statusCode='nochange'      

if optStepName == "":
    print("ardoc_oracle_jobstat.py: Error: Step is not provided")
    sys.exit(1)

stepDict={'conf':'CONF','config':'CONF'}
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
stepDict.update({'cvkv':'CVKV', 'cvmfskv':'CVKV'})
stepDict.update({'q431':'Q431'})
stepDict.update({'q221':'Q221'})

stepDBN=""
if optStepName.lower() in stepDict:
    stepDBN=stepDict[optStepName.lower()]
else:
    print("ardoc_oracle_jobstat.py: Error: Unknown step provided:",optStepName)
    sys.exit(1)
print("ardoc_orackle_jobstat: option:",stepDBN," ,statusCode:",statusCode)

home=""
nname=""
if 'HOME' in os.environ : home=os.environ['HOME']
if 'ARDOC_NIGHTLY_NAME' in os.environ : nname=os.environ['ARDOC_NIGHTLY_NAME']
if nname == "":
    print("ardoc_oracle_interface_script.py: Error: ARDOC_NIGHTLY_NAME is not defined")  
    sys.exit(1)
oracle_schema=os.environ.get('ARDOC_ORACLE_SCHEMA','ATLAS_ARDOC').strip()    
parray=os.environ.get('ARDOC_PROJECT_ARRAY','')
paname=os.environ.get('ARDOC_PROJECT_NAME','')
parray_a=re.split(r'\s+',parray)
firstproj=1
lnumber=len(parray_a)
if lnumber > 1 and paname != "" :
    if parray_a[0] != paname:
        print("ardoc_oracle_jobstat.py: Info: current project", paname, " is not the first (",parray_a[0],"): limited db insertions")
        firstproj=0
#print "lnumber, firstproj",lnumber,firstproj,lnumber,optStepName        
relname=os.environ.get('ARDOC_PROJECT_RELNAME_COPY','')
reltype="NIT"
relstbb=os.environ.get('ARDOC_STABLE_RELEASE','')
if relstbb == 'yes': reltype="STB"
url2log=os.environ.get('ARDOC_WEBPAGE','')
#RELID NID NAME TYPE URL2LOG
ardoc_arch=os.environ.get('ARDOC_ARCH','')
arch_a=re.split(r'\-',ardoc_arch)
arch=arch_a[0]
osys=arch_a[1]
comp=arch_a[2]
opt=arch_a[3]
role=os.environ.get('ARDOC_NIGHTLY_ROLE','master')
if len(role) > 6: role=role[0:6]
cFN="/afs/cern.ch/atlas/software/dist/nightlies/cgumpert/TC/OW_crdntl"
lne=open(cFN,'r')
lne_res=lne.readline()
lne.close()
lnea=re.split(r'\s+',lne_res)          
accnt,pwf,clust=lnea[0:3]
#print "XXXX",accnt,pwf,clust
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
    print(("ardoc_oracle_jobstat.py: Database connection error: ", error.code, error.offset, error.message))
else:
    print("ardoc_oracle_jobstat.py: Connection is alive!")
cursor.execute("ALTER SESSION SET current_schema = "+oracle_schema)
cmnd="""
select nid from nightlies where nname = :nname"""
#print "CMND", cmnd
cursor.execute(cmnd,{'nname' : nname})
result = cursor.fetchall()
#pprint(result)
if len(result) < 1: print("ardoc_oracle_jobstat.py: absent nightly name: ",nname); sys.exit(1)   
row=result[-1]
nightly_id=row[0]
ts = datetime.datetime.now()
relid_j=""
ts_j=""
ts_1=ts
if firstproj == 0:
    ts_1=ts - datetime.timedelta(days=2)
else:
    if ( optStepName == 'conf' or  optStepName == 'config' ) and role == 'master' :
      ts_1=ts - datetime.timedelta(minutes=30)
    else:
      ts_1=ts - datetime.timedelta(days=1)  
#print 'ardoc_oracle_jobstat.py: timestamps',ts,ts_1    
cmnd="""
SELECT RELID,reltstamp FROM RELEASES WHERE nid = :nightly_id and name = :relname and reltstamp > :t_val order by reltstamp""" 
#print "CMND", cmnd
cursor.execute(cmnd,{ 'nightly_id' : nightly_id, 'relname' : relname, 't_val' : ts_1 })
result = cursor.fetchall()
lresult=len(result)
#print "FFF",lresult
relid_j=""
ts_j=""
#if firstproj == 1 and  role == 'master':
#    for row in result:
#        print row
#        if row[1] == ts:
#            print "ardoc_oracle_jobstat.py: relid found:",row[0],' XX ',row[1], ts
#            relid_j=row[0]; ts_j=row[1]
#            break
#else:
if lresult > 0:
        for row in result:
            print("ardoc_oracle_jobstat.py: RELEASES row:",row)
        rowmax=result[-1]
        ts_2=ts - datetime.timedelta(days=2)
        if rowmax[1] > ts_2:
            print("ardoc_oracle_jobstat.py: relid found:",rowmax[0],' XX ',rowmax[1],' > ', ts_2)
            relid_j=rowmax[0]; ts_j=rowmax[1]
#
if relid_j == "":
      print("ardoc_oracle_jobstat.py: Error: relid for jobs table not found")
      sys.exit(1)
#print "TSJ",ts_j
#print "SSS",ts_j.year,ts_j.month,ts_j.day
#print "SSA",ts_j.date()
tdd_j=ts_j.date()
#print tdd_j.strftime("%Y%m%d"), nightly_id
jid_base=int(tdd_j.strftime("%Y%m%d"))*10000000+int(nightly_id)*1000
jid_max=int(tdd_j.strftime("%Y%m%d"))*10000000+int(nightly_id)*1000+999
jid=int(tdd_j.strftime("%Y%m%d"))*10000000+int(nightly_id)*1000+1
print("ardoc_oracle_jobstat.py: MASTER jid candidate", jid)
####
if firstproj != 1 or  role != 'master':
    ts_j=ts
#
role_up=role.upper()
relid_jj=""
cmnd="""
SELECT JID,RELID,tstamp FROM JOBS WHERE nid = :nightly_id and JID > :jid_base and JID <= :jid_max and OS = :osys and COMP = :comp and ARCH = :arch and OPT = :opt and ROLE = :role order by tstamp"""
cursor.execute(cmnd,{'nightly_id' : nightly_id, 'jid_base' : jid_base, 'jid_max' : jid_max, 'osys' : osys, 'comp' : comp, 'arch' : arch, 'opt' : opt, 'role' : role_up})
result = cursor.fetchall()
print("ardoc_oracle_jobstat.py: DB command", cmnd)
#cursor.execute(cmnd)
lresult=len(result)
if lresult > 0:
  for row in result:
    print('ardoc_oracle_jobstat.py: result JID,RELID', row)
  rowmax=result[-1]
  jid = rowmax[0]
  relid_jj = rowmax[1] 
#  if firstproj == 1: jid += 1
  if firstproj == 1 and  role != 'master': ts_j=rowmax[2]
print("ardoc_oracle_jobstat.py: jid relid ts: ",jid,relid_j,relid_jj,ts_j," ROLE ",role_up) 
if relid_jj == "" or relid_j != relid_jj:
    print("ardoc_oracle_jobstat.py: Error: relid from jobs table differs from releases table",relid_jj," xx ",relid_j) 
#

hostnam=os.uname()[1]
prcid=os.getpid()
usid=os.getuid()
parid=os.getppid() 
#print "PPPPP", prcid, parid, usid
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

### FOR BUILD step: try to read build times from dictionary
key_results_dict=0
ci_results_dict=os.environ.get('CI_RESULTS_DICT','')
ciresults_dir=os.path.dirname(ci_results_dict)
keystart="Start;"+paname
keyend="End;"+paname
if ci_results_dict != "" and os.path.isfile(ci_results_dict) : key_results_dict=1
if key_results_dict == 1:
     base_crd=os.path.basename(ci_results_dict)
     base_crd_0=os.path.splitext(base_crd)[0]
     print("ardoc_oracle_jobstat_test:BASE_CRD_0 ",base_crd_0)
     pm=[]
     try:
        pm = __import__(base_crd_0)
     except ImportError:
        print("ardoc_oracle_jobstat_test: Error: in importing generated results dict", base_crd_0)
        key_results_dict=0
        pass

print("ardoc_oracle_jobstat_test: Info: KEY_RESULTS_DICT ", key_results_dict)      

#tstart92=""
#tend92=""
if key_results_dict == 1:
    dictS={}; dictE={}
    try: pm.BuildTime
    except: pm.BuildTime={}
    BuildTimeS=pm.BuildTime.get(keystart,'0.'); BuildTimeE=pm.BuildTime.get(keyend,'0.')
    dictS['B']=float(BuildTimeS); dictE['B']=float(BuildTimeE)
    try: pm.COTime
    except: pm.COTime={}
    if firstproj == 1:
        COTimeS=pm.COTime.get('Start','0.');COTimeE=pm.COTime.get('End','0.')
    else:
        COTimeS='0.';COTimeE='0.'
    dictS['CO']=float(COTimeS); dictE['CO']=float(COTimeE)
    try: pm.ExternalsTime
    except: pm.ExternalsTime={}
    ExternalsTimeS=pm.ExternalsTime.get(keystart,'0.'); ExternalsTimeE=pm.ExternalsTime.get(keyend,'0.')
    dictS['EXT']=float(ExternalsTimeS); dictE['EXT']=float(ExternalsTimeE)
    try: pm.ConfigTime
    except: pm.ConfigTime={}
    ConfigTimeS=pm.ConfigTime.get(keystart,'0.'); ConfigTimeE=pm.ConfigTime.get(keyend,'0.')
    dictS['CONF']=float(ConfigTimeS); dictE['CONF']=float(ConfigTimeE)
    try: pm.UnitTestsTime
    except: pm.UnitTestsTime={}
    UnitTestsTimeS=pm.UnitTestsTime.get(keystart,'0.'); UnitTestsTimeE=pm.UnitTestsTime.get(keyend,'0.')
    dictS['Q']=float(UnitTestsTimeS); dictE['Q']=float(UnitTestsTimeE)
    try: pm.Q221TestTime
    except: pm.Q221TestTime={}
    Q221TestTimeS=pm.Q221TestTime.get(keystart,'0.'); Q221TestTimeE=pm.Q221TestTime.get(keyend,'0.')
    dictS['Q221']=float(Q221TestTimeS); dictE['Q221']=float(Q221TestTimeE)
    try: pm.Q431TestTime
    except: pm.Q431TestTime={}
    Q431TestTimeS=pm.Q431TestTime.get(keystart,'0.'); Q431TestTimeE=pm.Q431TestTime.get(keyend,'0.')
    dictS['Q431']=float(Q431TestTimeS); dictE['Q431']=float(Q431TestTimeE)
    try: pm.IntTestsTime
    except: pm.IntTestsTime={}
    IntTestsTimeS=pm.IntTestsTime.get(keystart,'0.'); IntTestsTimeE=pm.IntTestsTime.get(keyend,'0.')
    arrIS=[]; dictS['I'] = 0.0; dictE['I'] = 0.0
    if IntTestsTimeS != '0.' : arrIS.append(float(IntTestsTimeS))
#    if Q221TestTimeS != '0.' : arrIS.append(float(Q221TestTimeS))
#    if Q431TestTimeS != '0.' : arrIS.append(float(Q431TestTimeS))
    arrIE=[]
    if IntTestsTimeE != '0.' : arrIE.append(float(IntTestsTimeE))
#    if Q221TestTimeE != '0.' : arrIE.append(float(Q221TestTimeE))
#    if Q431TestTimeE != '0.' : arrIE.append(float(Q431TestTimeE))
    if len(arrIS) != 0: dictS['I']=min(arrIS)
    if len(arrIE) != 0: dictE['I']=min(arrIE) 
    for k92,v92 in list(dictS.items()):
        print('ardoc_oracle_jobstat.py: Info: START: ', k92, v92) 
    for k92,v92 in list(dictE.items()):
        print('ardoc_oracle_jobstat.py: Info:  END : ', k92, v92)
#    if BuildTime.has_key(keystart):
#         start92=BuildTime[keystart]
#         print "ardoc_oracle_jobstat_test: Info: value keystart ", start92
#         fstart92=float(start92)
#         tstart92=datetime.datetime.fromtimestamp(fstart92)
#         print "ardoc_oracle_jobstat_test: Info: value keystart ", tstart92
#    else:
#         print "ardoc_oracle_jobstat_test: Info: no value keystart "
#         for k92,v92 in BuildTime.items():
#             print k92, v92 
#    if BuildTime.has_key(keyend):
#         end92=BuildTime[keyend]
#         print "ardoc_oracle_jobstat_test: Info: value keyend ", end92
#         fend92=float(end92)
#         tend92=datetime.datetime.fromtimestamp(fend92)
#         print "ardoc_oracle_jobstat_test: Info: value keyend ", tend92
### END FOR BUILD step: try to read build times from dictionary 

cmnd="""select projid from projects where projname = :paname order by projid"""
cursor.execute(cmnd,{'paname' : paname })
result = cursor.fetchall()
if len(result) == 0:
            print("ardoc_oracle_jobstat.py: Error: absent project:",paname)
            sys.exit(1)
rowmax=result[-1]
projid_current=rowmax[0]
#
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
     print("ardoc_oracle_jobstat.py: Error: attempt to update non-existing jobstat row: jid,nid,relid,projid",jid,nightly_id,relid_j,projid_current)
     sys.exit(1)

rowmax=result[-1]
relname_sel=rowmax[0]
projname_sel=rowmax[1]
begdate_sel=rowmax[2]
nname_sel=rowmax[3]

print("ardoc_oracle_jobstat.py: updating for nightly",nname_sel,", release",relname_sel,", proj",projname_sel,", begdate",begdate_sel,"***(",lresult,")***")

arrStep=[ stepDBN ]
arrCode=[ statusCode ]
if stepDBN == 'B' : 
    print("ardoc_oracle_jobstat.py: step B")
    arrStep=[ 'B', 'CO', 'EXT', 'CONF', 'Q', 'I', 'Q431', 'Q221' ]
    if statusCode == "" :
        arrCode=[ statusCode, '', '', '', '', '' , '', '' ]
    else:
        arrCode=[ statusCode, '0', '0', '0', '0', '0' , '0', '0' ]
print("ardoc_oracle_jobstat.py: ", arrStep)
i=0
for step in arrStep:
    fstart92=dictS.get(arrStep[i],'')
    tstart92=''
    if fstart92 != '' and fstart92 != '0.0': tstart92=datetime.datetime.fromtimestamp(fstart92)
    fend92=dictE.get(arrStep[i],'')
    tend92=''
    if fend92 != '' and fend92 != '0.0': tend92=datetime.datetime.fromtimestamp(fend92)
    code=arrCode[i]
    print("ardoc_oracle_jobstat.py: starting update step: ", step, fstart92, tstart92, " ** ", fend92, tend92, " *CODE*",code,"*")
    i=i+1
    procid='100000'
    cmnd0="update jobstat j set E"+step+" = NULL , S"+step+" = NULL"
    cmnd1="update jobstat j set B"+step+" = :t_val"
    cmnd10="update jobstat j set B"+step+" = NULL"
    cmnd2="update jobstat j set E"+step+" = :t_val , S"+step+" = :code"
    cmnd3="update jobstat j set E"+step+" = :t_val"
    cmnd9="""
where j.relid=:relid_j
and j.jid=:jid
and j.nid = :nightly_id
and j.projid = :projid_c
"""

    cmnd00=cmnd0+cmnd9
    ts_inp=ts
    if code == "" :
        cmnd=cmnd1+cmnd9
        cmnd100=cmnd10+cmnd9
#        ts_inp92=ts_inp
        ts_inp92="NULL"
        if tstart92 != "" :
          print("ardoc_oracle_jobstat_test.py: Info: taking start time from results file:",tstart92, "--- was ",ts_inp)
          ts_inp92=tstart92
        else:
          print("ardoc_oracle_jobstat_test.py: Warning: no start time retrieved from results file, using ",ts_inp92)
        print("ardoc_oracle_jobstat.py: command ",cmnd00)
        print("ardoc_oracle_jobstat.py: parameters ",relid_j,jid,nightly_id,projid_current)
        cursor.execute(cmnd00, {'relid_j': relid_j, 'jid' : jid, 'nightly_id' : nightly_id, 'projid_c' : projid_current })
        if ts_inp92 != "NULL":
          cursor.prepare(cmnd)
          cursor.setinputsizes(t_val=cx_Oracle.TIMESTAMP) 
          cursor.execute(None, {'relid_j': relid_j, 'jid' : jid, 'nightly_id' : nightly_id, 'projid_c' : projid_current, 't_val':ts_inp92})
        else:
          print("ardoc_oracle_jobstat.py: command ",cmnd100)
          cursor.execute(cmnd100, {'relid_j': relid_j, 'jid' : jid, 'nightly_id' : nightly_id, 'projid_c' : projid_current })          
    else:    
#        ts_inp92=ts_inp
        ts_inp92="NULL"
        if tend92 != "" :
          print("ardoc_oracle_jobstat_test.py: Info: taking end time from results file:",tend92, "--- was ",ts_inp)
          ts_inp92=tend92
        else:
          print("ardoc_oracle_jobstat_test.py: Warning: no end time retrieved from results file, using ",ts_inp92)
        if code == "nochange":
            cmnd=cmnd3+cmnd9
            if ts_inp92 != "NULL":
              cursor.prepare(cmnd)
              cursor.setinputsizes(t_val=cx_Oracle.TIMESTAMP)
              cursor.execute(None, {'relid_j': relid_j, 'jid' : jid, 'nightly_id' : nightly_id, 'projid_c' : projid_current, 't_val':ts_inp92})
        else: 
            cmnd=cmnd2+cmnd9
            print("ardoc_oracle_jobstat.py: command ",cmnd)
            print("ardoc_oracle_jobstat.py: parameters ",relid_j,jid,nightly_id,projid_current,ts_inp92,code) 
            if ts_inp92 != "NULL": 
              cursor.prepare(cmnd)
              cursor.setinputsizes(t_val=cx_Oracle.TIMESTAMP)
              cursor.execute(None, {'relid_j': relid_j, 'jid' : jid, 'nightly_id' : nightly_id, 'projid_c' : projid_current, 't_val':ts_inp92, 'code' : code})

    print("ardoc_oracle_jobstat.py: finishing update step: ", step, "code:",code,"tval:", ts,"jid,projid:",jid,projid_current)

cursor.close()
connection.commit()
connection.close()
