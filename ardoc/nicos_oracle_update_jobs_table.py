import re,os,sys
import getpass
import platform
import cx_Oracle
from pprint import pprint
import datetime
import getopt, traceback

#if len(sys.argv) < 2 :
#    print "nicos_oracle_update_jobs_table: Error: no options specified\n"
#    sys.exit(1)
#try:
#    optionslist, args = getopt.gnu_getopt(sys.argv[1:],'o:s:p:',['nochange'])
#except getopt.error:
#    print '''Error: You tried to use an unknown option or the
#                    argument for an option that requires it was missing.'''
#    sys.exit(1)
                        
#optStepName=""
#statusCode=""
#param=""

#for a in optionslist[:]:
#    if a[0] == '-o' and a[1] != '':
#      optStepName=a[1]
#    elif a[0] == '-s' and a[1] != '':
#      statusCode=a[1]
#    elif a[0] == '-p' and a[1] != '':  
#      param=a[1]
#    elif a[0] == '--nochange':
#      statusCode='nochange'      

#if optStepName == "":
#    print "nicos_oracle_update_jobs_table: Error: Step is not provided"
#    sys.exit(1)

nname=os.environ.get('NICOS_NIGHTLY_NAME','')
current_projname=os.environ.get('NICOS_PROJECT_NAME','')
parray=os.environ.get('NICOS_PROJECT_ARRAY','UNDEF').strip()
parray_a=re.split(r'\s+',parray)
lnumber=len(parray_a)
if lnumber == 0:
    print("nicos_oracle_update_jobs_table: Error: project array is empty")
    sys.exit(1)
first_project_name=parray_a[0]
#if current_projname == '' or current_projname != first_project_name:
#    print "nicos_oracle_update_jobs_table: Info: project ", current_projname, "is not the first ",first_project_name, " ===>SKIPPING"
#    sys.exit(2)
scrind=os.environ.get('NICOS_SCRATCH_INDICATOR','')
l_fullbuild=os.environ.get('NICOS_FULLBUILD_LABEL','')
l_fullunit=os.environ.get('NICOS_FULLUNIT_LABEL','')
l_fullintegr=os.environ.get('NICOS_FULLINTEGR_LABEL','')
l_longtests=os.environ.get('NICOS_LONGTESTS_LABEL','')
nprojb=os.environ.get('LEN_NICOS_PROJECT_ARRAY','')
nprojmax=os.environ.get('LEN_NICOS_PROJECT_ARRAY_MAX','')
print("nicos_oracle_update_jobs_table: Info: SCRATCH_INDICATOR ",scrind)
print("nicos_oracle_update_jobs_table: Info: FULLBUILD FULLUNIT FULLINTEGR LONGTESTS _LABELS  ",l_fullbuild, l_fullunit, l_fullintegr, l_longtests)
i_fullbuild=0; i_fullunit=0; i_fullintegr=0; i_longtests=0
if l_fullbuild == 'True': i_fullbuild=1
if l_fullunit == 'True': i_fullunit=1
if l_fullintegr == 'True': i_fullintegr=1
if l_longtests == 'True': i_longtests=1
print("nicos_oracle_update_jobs_table: Info: FULLBUILD FULLUNIT FULLINTEGR LONGTESTS CODES  ",i_fullbuild, i_fullunit, i_fullintegr, i_longtests)
print("nicos_oracle_update_jobs_table: Info: NPROJ NPROJMAX ",nprojb,nprojmax)

ci_results_dict=os.environ.get('CI_RESULTS_DICT','')
ciresults_dir=os.path.dirname(ci_results_dict)
key_results_dict=1
if ci_results_dict != "" and os.path.isfile(ci_results_dict) :
    base_crd=os.path.basename(ci_results_dict)
    dir_crd=os.path.dirname(ci_results_dict)
    base_crd_0=os.path.splitext(base_crd)[0]
    print("nicos_oracle_update_jobs_table: Info: base name of CI_RESULTS_DICT: ",base_crd_0)
    os.chdir(dir_crd)
    print("nicos_oracle_update_jobs_table: Info: CWD: ",os.getcwd())
    pm=[]
    try:
        pm = __import__(base_crd_0)
    except ImportError:
        traceback.print_exc()
        print("nicos_oracle_update_jobs_table: Error: in importing generated results dict", base_crd_0)
        key_results_dict=0
        pass
btt_dict={}; ttt_dict={}; jt_dict={}
if key_results_dict == 1:
    try: btt_dict=pm.BuildTotalTime
    except: btt_dict={}
    try: ttt_dict=pm.IntTestsTotalTime
    except: ttt_dict={}
    try: jt_dict=pm.JobTime
    except: jt_dict={}
    try: utt_dict=pm.UnitTestsTotalTime
    except: utt_dict={}
print("nicos_oracle_update_jobs_table: Info: build time dict: ",btt_dict)
print("nicos_oracle_update_jobs_table: Info: unit time dict: ",utt_dict)
print("nicos_oracle_update_jobs_table: Info: int time dict: ",ttt_dict) 
print("nicos_oracle_update_jobs_table: Info: job time dict: ",jt_dict)
bjj=''; ejj=''; bbj=''; ebj=''; bij=''; eij=''; buj=''; euj=''
bjj_epoch=jt_dict.get('Start','')
if bjj_epoch != '' : bjj=datetime.datetime.fromtimestamp(float(bjj_epoch))
ejj_epoch=jt_dict.get('End','')
if ejj_epoch != '' : ejj=datetime.datetime.fromtimestamp(float(ejj_epoch))
bbj_epoch=btt_dict.get('Start','')
if bbj_epoch != '' : bbj=datetime.datetime.fromtimestamp(float(bbj_epoch))
ebj_epoch=btt_dict.get('End','')
if ebj_epoch != '' : ebj=datetime.datetime.fromtimestamp(float(ebj_epoch))
bij_epoch=ttt_dict.get('Start','')
if bij_epoch != '' : bij=datetime.datetime.fromtimestamp(float(bij_epoch))
eij_epoch=ttt_dict.get('End','')
if eij_epoch != '' : eij=datetime.datetime.fromtimestamp(float(eij_epoch))
buj_epoch=utt_dict.get('Start','')
if buj_epoch != '' : buj=datetime.datetime.fromtimestamp(float(buj_epoch))
euj_epoch=utt_dict.get('End','')
if euj_epoch != '' : euj=datetime.datetime.fromtimestamp(float(euj_epoch))
print("nicos_oracle_update_jobs_table: Info: build times: ",bbj," # ",ebj)
print("nicos_oracle_update_jobs_table: Info: unit times: ",buj," # ",euj)
print("nicos_oracle_update_jobs_table: Info: int times: ",bij," # ",eij)
print("nicos_oracle_update_jobs_table: Info: job times: ",bjj," # ",ejj)

warea=os.environ.get('NICOS_WORK_AREA','')
if warea == "":
    print("nicos_oracle_update_jobs_table: Error: NICOS_WORK_AREA is not defined")
    sys.exit(1)
if not os.path.exists(warea):
    print("nicos_oracle_update_jobs_table: Error: NICOS_WORK_AREA:",warea," is not directory")
    sys.exit(1)
warea_dir=os.path.dirname(warea)
fjid=warea+os.sep+'jid_identificator'
if ( not os.path.isfile(fjid) ):
    print("nicos_oracle_update_jobs_table: Error: file with jid does not exist:",fjid)
    sys.exit(1)

os.chdir(warea)
print("nicos_oracle_update_jobs_table: Info: CWD: ",os.getcwd())
mf=open(fjid)
jid=mf.readline().strip()
mf.close()

if jid == '':
    print("nicos_update_jobs_table: Error: empty jid from",fjid)
    sys.exit(1)

print("nicos_update_jobs_table: JID read:",jid,"from:",fjid)

oracle_schema=os.environ.get('NICOS_ORACLE_SCHEMA','ATLAS_NICOS').strip()    
cFN="/afs/cern.ch/atlas/software/dist/nightlies/cgumpert/TC/OW_crdntl"
lne=open(cFN,'r')
lne_res=lne.readline()
lne.close()
lnea=re.split(r'\s+',lne_res)          
accnt,pwf,clust=lnea[0:3]
connection = cx_Oracle.connect(accnt,pwf,clust)
connection.clientinfo = 'python 2.6 @ home'
connection.module = 'cx_Oracle test_NICOS.py'
connection.action = 'TestNicosJob'
cursor = connection.cursor()
try:
    connection.ping()
except cx_Oracle.DatabaseError as exception:
    error, = exception.args
    print(("nicos_oracle_update_jobs_table: Database connection error: ", error.code, error.offset, error.message))
else:
    print("nicos_oracle_update_jobs_table: Connection is alive!")
cursor.execute("ALTER SESSION SET current_schema = "+oracle_schema)

cmnd="""select relid,nid from jobs where jid = :jid"""
cursor.execute(cmnd, {'jid' : jid })
result = cursor.fetchall()
if len(result) == 0:
    print("nicos_oracle_update_jobs_table: Error: absent jid in jobs table:",jid)
    sys.exit(1)
rowmax=result[-1]
relid_current=rowmax[0]
nid_current=rowmax[1]
print("nicos_oracle_update_jobs_table.py: nid,relid ",nid_current,relid_current)

cmnd="""select ntests,projname,npb,ner,nto from tstat natural join projects where jid = :jid""" 
cursor.execute(cmnd, {'jid' : jid })
result = cursor.fetchall()
lresult=len(result)
ntests=0; ntestspb=0; ntestser=0;  nteststo=0;
if lresult > 0:
    for row in result:
         ntests_p=row[0]
         name_p=row[1]
         ntests_pb=row[2]
         ntests_er=row[3]
         ntests_to=row[4]
         print("nicos_oracle_update_jobs_table.py: ntests, project name ",ntests_p,name_p)
         ntests += int(ntests_p)
         ntestspb += int(ntests_pb)
         ntestser += int(ntests_er)
         nteststo += int(ntests_to)
print("nicos_oracle_update_jobs_table.py: total number of tests",ntests,ntestspb,ntestser,nteststo)

cmnd="""
update jobs set lblfullb = :lblfullb
, lblfunit = :lblfunit
, lblfint = :lblfint
, lbllongt = :lbllongt
, nprojb = :nprojb
, nprojmax = :nprojmax
, bjj = :bjj
, ejj = :ejj
, bbj = :bbj
, ebj = :ebj
, buj = :buj
, euj = :euj 
, bij = :bij
, eij = :eij 
, erntst = :erntst
, pbntst = :pbntst 
, tontst = :tontst
, ntst = :ntst where
jid = :jid"""
dict_p={'jid':jid,'lblfullb':i_fullbuild,'lblfunit':i_fullunit,'lblfint':i_fullintegr,'lbllongt':i_longtests,'nprojb':nprojb,'nprojmax':nprojmax,'bjj':bjj,'ejj':ejj,'bbj':bbj,'ebj':ebj,'buj':buj,'euj':euj,'bij':bij,'eij':eij, 'ntst':ntests, 'erntst':ntestser, 'pbntst':ntestspb, 'tontst':nteststo }
print("nicos_oracle_update_jobs_table.py: Oracle command", cmnd," # ",dict_p)
cursor.prepare(cmnd)
cursor.setinputsizes(bjj=cx_Oracle.TIMESTAMP);cursor.setinputsizes(ejj=cx_Oracle.TIMESTAMP);
cursor.setinputsizes(bbj=cx_Oracle.TIMESTAMP);cursor.setinputsizes(ebj=cx_Oracle.TIMESTAMP);
cursor.setinputsizes(buj=cx_Oracle.TIMESTAMP);cursor.setinputsizes(euj=cx_Oracle.TIMESTAMP);
cursor.setinputsizes(bij=cx_Oracle.TIMESTAMP);cursor.setinputsizes(eij=cx_Oracle.TIMESTAMP);
cursor.execute(None, dict_p)

cursor.close()
connection.commit()
connection.close()
