import re
import os
import sys
import getpass
import platform
import cx_Oracle
from pprint import pprint
import datetime
import smtplib
print(("ardoc_oracle_starter.py: Python version: " + platform.python_version()))
print(("ardoc_oracle_starter.py: cx_Oracle version: " + cx_Oracle.version))
print(("ardoc_oracle_starter.py: Oracle client: " + str(cx_Oracle.clientversion()).replace(', ','.')))
home=""
nname=""
ngroup="N/A"
valmode="N/A"
incrmode="N/A"
parray=""
if 'HOME' in os.environ : home=os.environ['HOME']
if 'ARDOC_NIGHTLY_NAME' in os.environ : nname=os.environ['ARDOC_NIGHTLY_NAME']
if nname == "":
    print("ardoc_oracle_starter.py: Error: ARDOC_NIGHTLY_NAME is not defined")  
    sys.exit(1)
oracle_schema=os.environ.get('ARDOC_ORACLE_SCHEMA','ATLAS_NICOS').strip()
if 'ARDOC_NIGHTLY_GROUP' in os.environ : ngroup=os.environ['ARDOC_NIGHTLY_GROUP']
if 'ARDOC_VAL_MODE' in os.environ : valmode=os.environ['ARDOC_VAL_MODE']
if 'ARDOC_INC_BUILD' in os.environ : incrmode=os.environ['ARDOC_INC_BUILD']
if 'ARDOC_PROJECT_ARRAY' in os.environ : parray=os.environ['ARDOC_PROJECT_ARRAY']
scratch_indicator=os.environ.get('ARDOC_SCRATCH_INDICATOR','').strip()
target_branch=os.environ.get('ARDOC_TARGET_BRANCH','UNKNOWN').strip()
print("ardoc_oracle_starter.py: Info: TARGET BRANCH: ",target_branch)
ardoc_gen_config_area=os.environ.get('ARDOC_GEN_CONFIG_AREA','')
ardoc_arch=os.environ.get('ARDOC_ARCH','')
arch_a=re.split(r'\-',ardoc_arch)
arch=arch_a[0]
osys=arch_a[1]
comp=arch_a[2]
opt=arch_a[3]
role=os.environ.get('ARDOC_NIGHTLY_ROLE','master')
if len(role) > 6: role=role[0:6]
#
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
if buildarea == "": buildarea = 'N/A'
if copyarea == "": copyarea='N/A'
cmakevers=os.environ.get('CMAKE_VERSION','')
gitmrlink=os.environ.get('MR_GITLAB_LINK','')
gitmrhash=os.environ.get('MR_GITHASH','')
btool='CMAKE'
bvers=cmakevers
hostnam=os.uname()[1]
hostnam_b=re.split(r'\.',hostnam)[0]
hostnam_n=re.sub('[^0-9]','',hostnam_b)
hostnam_nn=hostnam_n.lstrip('0')
ts_now = datetime.datetime.now()
now_f=datetime.datetime.strftime(ts_now,'%Y-%m-%d %H:%M')
t_epoch=os.environ.get('ARDOC_EPOCH','')
ts=ts_now
if t_epoch != '':
   fdtt=float(t_epoch)
   ts=datetime.datetime.fromtimestamp(fdtt)
relnstamp=ts.strftime("%Y-%m-%dT%H%M")
print("ardoc_oracle_starter.py: date: ",ts," release name stamp: ",relnstamp)
#
ardoc_http=os.environ.get('ARDOC_HTTP','')
coma='bash -c \'(unset ARDOC_SUFFIX;ARDOC_PROJECT_NAME=\'PRJ\'; python3 $ARDOC_HOME/ardoc_project_suffix_creator.py)\''
sff=os.popen(coma,'r')
ardoc_suffix=sff.readline()
#    print "SFF",ardoc_suffix
ardoc_webpage=ardoc_http+'/'+ngroup+'WebArea/ardoc_web_area'+ardoc_suffix
print("ardoc_oracle_starter.py: ardoc_webpage: ",ardoc_webpage)
#
valmode_d={ 'doubleyes' : 'dbl', 'none' : 'non', 'no' : 'non' }
valmode_s=valmode_d.get(valmode,valmode)
if len(valmode_s) > 3: valmode_s=valmode_s[0:3]
ntype="other"
lnumber=len(re.split(r'\s+',parray))
if lnumber == 1:
    ntype="patch"
elif  lnumber > 9:
    ntype="full"
cFN="/afs/cern.ch/atlas/software/dist/nightlies/cgumpert/TC/OW_crdntl"
lne=open(cFN,'r')
lne_res=lne.readline()
lne.close()
lnea=re.split(r'\s+',lne_res)          
accnt,pwf,clust=lnea[0:3]
#print "XXXX",accnt,pwf,clust
connection = cx_Oracle.connect(accnt,pwf,clust)
print(("ardoc_oracle_starter.py: Oracle DB version: " + connection.version))
#print ("ardoc_oracle_starter.py: Oracle client encoding: " + connection.encoding)
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
    print(("ardoc_oracle_starter.py: Database connection error: ", error.code, error.offset, error.message))
else:
    print("ardoc_oracle_starter.py: Connection is alive!")
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
dict_p={'nname' : nname,'ngroup' :ngroup,'ntype' : ntype,'valmode_s' : valmode_s,'incrmode_trim' : incrmode_trim,'stat' : 0, 'btype' : '', 'sttime' : ts_now, 'stuser' : ''} 
#print "CMND", cmnd, " dict ",dict_p 
cursor.prepare(cmnd)
cursor.setinputsizes(sttime=cx_Oracle.TIMESTAMP)
cursor.execute(None, dict_p)
connection.commit()
cmnd="""
SELECT nid,nname,ngroup,ntype,val,incr,stat,stuser FROM NIGHTLIES where nname = :nname"""
cursor.execute(cmnd,{'nname' : nname})
result = cursor.fetchall()
if len(result) < 1: print("ardoc_oracle_starter.py: absent nightly name: ",nname); sys.exit(1)
for row in result:
    print("ardoc_oracle_starter.py:",row)
row=result[-1]
nightly_id=row[0]
statn=row[6]
stusern=row[7]
relnmaster=""
if stusern == None : stusern="N/A"  
#
if role == 'master':
    mail_body="===============================================================\n"
    mail_body=mail_body+"ARDOC restarted jobs for the nightly branch "+nname+"\n"
    mail_body=mail_body+"through on-demand interface at "+now_f+"\n"
    mail_body=mail_body+"at request of: "+stusern+"(CERN user name)\n"
    mail_body=mail_body+"===============================================================\n"
    if statn == 1 or statn == 3:
        subj = "ARDOC restarted "+nname+" nightly"
        sender = 'atnight@mail.cern.ch'
        receivers = ['undrus@bnl.gov']
        if stusern != "" and stusern.lower() != "none" and stusern.lower() != "n/a":
           receivers.append(stusern+'@mail.cern.ch')
        mail_body=mail_body+"This mail is sent to "+", ".join(receivers)+"\n"
        mail_body=mail_body+"===============================================================\n"
        message = """From: Atlas Nightlybuild <atnight@mail.cern.ch>
To: %s
Subject: %s
%s
""" % (", ".join(receivers), subj,mail_body)
        try:
            smtpObj = smtplib.SMTP('localhost')
            smtpObj.sendmail(sender, receivers, message)
            print("ardoc_oracle_starter.py: SENDING MESSAGE TO ",receivers)
            print("--->",message)
        except:
            print("ardoc_oracle_starter.py: Warning: unable to send email")

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
    dict_p={'nightly_id' : nightly_id,'relname' : relname,'reltype' : reltype,'tcrel' : tcrel,'tcrelbase' : tcrelbase, 'ardoc_webpage' : ardoc_webpage, 't_val' : ts, 'validation' : validation, 'relnstamp' : relnstamp, 'gitmrlink' : gitmrlink, 'relnmaster' : relnmaster}
    print("CMND", cmnd, " dict ",dict_p)
    cursor.prepare(cmnd)
    cursor.setinputsizes(t_val=cx_Oracle.TIMESTAMP)
    cursor.execute(None, dict_p)
    print('ardoc_oracle_starter.py: bindvars ', cursor.bindvars)
ts_1=ts
if role != 'master':
    ts_1=ts - datetime.timedelta(days=2)
print('ardoc_oracle_starter.py: tstamps:',ts,ts_1,role)
cmnd="""
SELECT RELID,reltstamp FROM RELEASES WHERE nid = :nightly_id and name = :relname and reltstamp > :t_val order by reltstamp"""
print("CMND", cmnd, {'t_val' : ts_1,'nightly_id' : nightly_id,'relname' : relname})
cursor.execute(cmnd, {'t_val' : ts_1,'nightly_id' : nightly_id,'relname' : relname})
result = cursor.fetchall()
pprint(result)
lresult=len(result)
relid_j=""
ts_j=""
if role == 'master':
    for row in result:
        if row[1] == ts:
            print("ardoc_oracle_starter.py: relid found:",row[0],' XX ',row[1], ts)
            relid_j=row[0]; ts_j=row[1]
            break
else:
    if lresult > 0:
        rowmax=result[-1]
        ts_2=ts - datetime.timedelta(days=2)
        if rowmax[1] > ts_2:
            print("ardoc_oracle_starter.py: relid found:",rowmax[0],' XX ',rowmax[1],' > ', ts_2)
            relid_j=rowmax[0]; ts_j=rowmax[1]
if relid_j == "":            
    print("ardoc_oracle_starter.py: Error: relid for jobs table not found")
    sys.exit(1)
#    
tdd_j=ts_j.date()
#print tdd_j.strftime("%Y%m%d"), nightly_id
jid_base=int(tdd_j.strftime("%Y%m%d"))*10000000+int(nightly_id)*1000
jid_max=int(tdd_j.strftime("%Y%m%d"))*10000000+int(nightly_id)*1000+999
jid=int(tdd_j.strftime("%Y%m%d"))*10000000+int(nightly_id)*1000
print("ardoc_oracle_starter.py: MASTER jid candidate (base)", jid)
####
if role != 'master':
    ts_j=ts
#
role_up=role.upper()
relid_jj=""
cmnd="""
SELECT JID,RELID,tstamp FROM JOBS WHERE nid = :nightly_id and JID > :jid_base and JID <= :jid_max and tstamp is not null order by tstamp"""
cursor.execute(cmnd,{'nightly_id' : nightly_id,'jid_base' : jid_base,'jid_max' : jid_max})
result = cursor.fetchall()
#print cmnd
rowmax_max=jid
lresult=len(result)
if lresult > 0:
    for row in result:
        print('ardoc_oracle_starter.py: JID,RELID', row, jid)
        if row[0] > rowmax_max:
          rowmax_max = row[0] 
#    rowmax=result[-1]
    jid = rowmax_max
    print('ardoc_oracle_starter.py: MAX_JID',jid) 
#    relid_jj = rowmax[1]
jid += 1
relid_jj=relid_j
print("ardoc_oracle_starter.py: max jid:",jid," for relid:",relid_j,relid_jj," current ts:",ts_j," ROLE ",role_up)
#
cmnd="""
insert into jobs (jid,nid,relid,arch,os,comp,opt,role,kitb,cvmfs,tstamp,btool,bvers,buildarea,copyarea,gitbr,hid,fromscratch,githash) values
( :jid
, :nightly_id
, :relid_j
, :arch
, :osys
, :comp
, :opt, :role_up
, :z, :z
, :t_val, :btool, :bvers, :buildarea, :copyarea, :target_branch, :hid, :fromscratch, :gitmrhash)"""
dict_p={'jid' : jid,'nightly_id' : nightly_id,'relid_j' : relid_j,'arch' : arch,'osys' : osys,'comp' : comp,'opt' : opt,'role_up' : role_up,'t_val' : ts_j,'z' : 0, 'btool' : btool, 'bvers' : bvers, 'buildarea' : buildarea, 'copyarea' : copyarea, 'target_branch' : target_branch, 'hid' : hostnam_nn, 'fromscratch' : scratch_indicator, 'gitmrhash' : gitmrhash}
print("CMNDJ", cmnd,' dict ',dict_p)
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
        print("ardoc_oracle_starter.py: job id for jobstat insertion identified:",jid)
    else:
        print("ardoc_oracle_starter.py: Error: absent job for relid:",relid_j)
        sys.exit(1)

if ardoc_gen_config_area == '':
    print("ardoc_oracle_starter.py: Error: absent ardoc_gen_config_area")
    sys.exit(1)
fjid=ardoc_gen_config_area+os.sep+'jobid.txt'
f=open(fjid, 'w')
f.write(str(jid))
f.close()
fepoch=ardoc_gen_config_area+os.sep+'jobepoch.txt'
f=open(fepoch, 'w')
f.write(str(t_epoch))
f.close()

print('ardoc_oracle_starter.py: bindvars ', cursor.bindvars)
cursor.close()
connection.commit()
connection.close()
