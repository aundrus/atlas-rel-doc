import re
import os
import sys
import getpass
import platform
import cx_Oracle
from pprint import pprint
import datetime
print("ardoc_oracle_tags.py: START")
print(("Python version: " + platform.python_version()))
print(("cx_Oracle version: " + cx_Oracle.version))
print(("Oracle client: " + str(cx_Oracle.clientversion()).replace(', ','.')))
home=""
nname=""
if 'HOME' in os.environ : home=os.environ['HOME']
if 'ARDOC_NIGHTLY_NAME' in os.environ : nname=os.environ['ARDOC_NIGHTLY_NAME']
if nname == "":
    print("ardoc_oracle_tags.py: Error: ARDOC_NIGHTLY_NAME is not defined")  
    sys.exit(1)
oracle_schema=os.environ.get('ARDOC_ORACLE_SCHEMA','ATLAS_ARDOC').strip()
domain_map={}
domain_map['^Control/.*$']='Core'
domain_map['^Event/.*$']='Core'
paname=os.environ.get('ARDOC_PROJECT_NAME','UNDEF').strip()
if paname == "" : paname='UNDEF'
parray=os.environ.get('ARDOC_PROJECT_ARRAY',paname).strip()
parray_a=re.split(r'\s+',parray)
lnumber=len(parray_a)
#=== THIS SCRIPT IS NOW RUN FOR EACH PROJECT SEPARATELY TO PROPERLY MERGE NEW PACKAGES IN
#if lnumber > 1 :
#    if parray_a[-1] != paname:
#        print "ardoc_oracle_tags.py: Info: current project", paname, " is not the last (",parray_a[-1],")"
#        print "ardoc_oracle_tags.py: Info: no db insertions"
#        sys.exit(0)
#if lnumber == 0:
#    parray_a=(); parray_a[0]=paname
#=== SET PROJECT ARRAY TO THE CURRENT PROJECT (SINGLE ITEM)
parray_a=[]; parray_a.append(paname)

role=os.environ.get('ARDOC_NIGHTLY_ROLE','master')
if len(role) > 6: role=role[0:6]
if role != "master":
        print("ardoc_oracle_tags.py: Info: job role is",role," : no db insertions")
        sys.exit(1)
relname=os.environ.get('ARDOC_PROJECT_RELNAME_COPY','')
reltype="NIT"
relstbb=os.environ.get('ARDOC_STABLE_RELEASE','')
if relstbb == 'yes': reltype="STB"
tcrel=os.environ.get('ARDOC_ATLAS_RELEASE','')
tcrelbase=os.environ.get('ARDOC_ATLAS_ALT_RELEASE','')
pfilegen=os.environ.get('ARDOC_DBFILE_GEN','')
if pfilegen == "":
    print("ardoc_oracle_tags.py: Error: ARDOC_DBFILE_GEN is not defined")
    sys.exit(1)
pfilegen_res=pfilegen+'_res'
if not os.path.isfile(pfilegen_res):
    print("ardoc_oracle_tags.py: Error: tag file",pfilegen_res,"does not exist")
    sys.exit(1)
pfilegen_res_base=os.path.basename(pfilegen_res)
warea=os.environ.get('ARDOC_WORK_AREA','')
if warea == "":
    print("ardoc_oracle_tags.py: Error: ARDOC_WORK_AREA is not defined")
    sys.exit(1)
if not os.path.exists(warea):
    print("ardoc_oracle_tags.py: Error: ARDOC_WORK_AREA:",warea," is not directory")
    sys.exit(1)
warea_dir=os.path.dirname(warea)
############    
cFN="/afs/cern.ch/atlas/software/dist/nightlies/cgumpert/TC/OW_crdntl"
lne=open(cFN,'r')
lne_res=lne.readline()
lne.close()
lnea=re.split(r'\s+',lne_res)          
accnt,pwf,clust=lnea[0:3]
connection = cx_Oracle.connect(accnt,pwf,clust)
print(("Oracle DB version: " + connection.version))
print(("Oracle client encoding: " + connection.encoding))
connection.clientinfo = 'python 2.6 @ home'
connection.module = 'cx_Oracle test_ARDOC.py'
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
for p_item in parray_a:
    p_item_s=p_item.strip()
    print("ardoc_oracle_tags.py: Info: updating projects if current project is new: ", p_item_s)
    cmnd="""
merge into projects a USING ( select max(projid)+1 as new_projid from projects ) b
ON ( projname = :p_item_s )
WHEN NOT MATCHED THEN insert values
( b.new_projid
, :p_item_s)""" 
#    print "CMND", cmnd
    cursor.execute(cmnd, {'p_item_s' : p_item_s})
    cursor.execute('SELECT * FROM PROJECTS')
    result = cursor.fetchall()
#    pprint(result)
cursor.close()
connection.commit()
connection.close()
#
connection = cx_Oracle.connect(accnt,pwf,clust)
print(("Oracle DB version: " + connection.version))
print(("Oracle client encoding: " + connection.encoding))
connection.clientinfo = 'python 2.6 @ home'
connection.module = 'cx_Oracle test_ARDOC.py'
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
#
cmnd="""
select projid from projects where projname = :paname order by projid
""" 
cursor.execute(cmnd,{'paname' : paname})
result = cursor.fetchall()
if len(result) == 0:
        print("ardoc_oracle_tags.py: Error: absent project:",paname)
        sys.exit(1)
rowmax=result[-1]
projid_current=rowmax[0]
cmnd="""
select releases.relid,releases.nid,nightlies.nname,releases.type from releases,nightlies
where releases.nid = nightlies.nid
and nightlies.nname = :nname
and releases.name = :relname and releases.type = :reltype
order by relid""" 
cursor.execute(cmnd,{'nname' : nname, 'relname' : relname, 'reltype' : reltype})
result = cursor.fetchall()
if len(result) == 0:
    print("ardoc_oracle_tags.py: Error: absent combination: n_name,relname,reltype:",nname,relname,reltype)
    sys.exit(1)
rowmax=result[-1]
relid_current=rowmax[0]
nid_current=rowmax[1]
print("ardoc_oracle_tags.py: RELID,NID,PROJID:",relid_current,nid_current,projid_current)
#
cursor.close()
connection.commit()
connection.close()

it1=0
for p_item in parray_a:
    print("ardoc_oracle_tags.py: Info: updating packages and tags for project", p_item)
    connection = cx_Oracle.connect(accnt,pwf,clust)
    connection.clientinfo = 'python 2.6 @ home'
    connection.module = 'cx_Oracle test_ARDOC.py'
    connection.action = 'TestArdocJob'
    cursor = connection.cursor()
    try:
        connection.ping()
    except cx_Oracle.DatabaseError as exception:
        error, = exception.args
        print(("ardoc_oracle_tags.py: Next database connection error: ", error.code, error.offset, error.message))
    else:
        print("ardoc_oracle_tags.py: Next connection is alive!")
    cursor.execute("ALTER SESSION SET current_schema = "+oracle_schema)    
    p_item_s=p_item.strip()
    cmnd="""
select projid from projects where projname = :p_item_s order by projid
""" 
    cursor.execute(cmnd, {'p_item_s' : p_item_s})
    result = cursor.fetchall()
    if len(result) == 0:
        print("ardoc_oracle_tags.py: Error: absent project:",p_item_s)
        projid_current='N/A'
    else:    
        rowmax=result[-1]
        projid_current=rowmax[0]
    it1 += 1
    coma='bash -c \'(ARDOC_PROJECT_NAME='+p_item_s+'; python3 $ARDOC_HOME/ardoc_project_suffix_creator.py)\''
    print("ardoc_oracle_tags.py: COMA",coma)
    sff=os.popen(coma,'r')
    sff_res=sff.readline()
#    print "SFF",sff_res 
    warea_i=warea_dir+os.sep+'ardoc_work_area'+sff_res
#    print "WA",warea_i
    file_i=warea_i+os.sep+pfilegen_res_base
    print("ardoc_oracle_tags.py: FILE_I",file_i)
    lines_db=[] 
    if os.path.exists(file_i):
        try:
            mf=open(file_i)
            lines_db = mf.readlines()
            mf.close()
        except:
            lines_db=[]
    sign_Gaudi=0
    sign_GAUDIRelease=0
    lines_db.append('GAUDIRelease GAUDIRelease-GAUDI-00-00-00 nobody@cern.ch')
    len_db=len(lines_db)
    i_db=0
#    print lines_db;
    for line in lines_db:
        i_db += 1
        line11=line.strip()
        line1=line11.replace('\n','')
        if len(re.sub(r'\s+','',line1)) == 0 : continue
        fil=re.split(r'\s+',line1)
        package=os.path.basename(fil[0])
        if package == 'Gaudi': sign_Gaudi=1
#        print "SSS",package,i_db,len_db,sign_Gaudi,sign_GAUDIRelease 
        if i_db == len_db and (sign_Gaudi == 0 or sign_GAUDIRelease == 1): break
        if package == 'GAUDIRelease': sign_GAUDIRelease=1
        cont=os.path.dirname(fil[0])
        if cont == "": cont="/"
        tag1=fil[1]
        domain='Other'
        for k,v in list(domain_map.items()):
            if re.match(k,cont) : domain=v 
#        print "SSS",package,cont,tag1
        cmnd="""
merge into packages a USING ( select max(pid)+1 as new_pid from packages ) b
ON ( pname = :package and contname = :cont  )
WHEN NOT MATCHED THEN insert values
( b.new_pid
, :package, :cont)""" 
#        print "CMND", cmnd
        cursor.execute(cmnd, {'package' : package, 'cont' : cont})
        cmnd="""select pid,pname,contname from packages where pname = :package and contname = :cont""" 
        cursor.execute(cmnd, {'package' : package, 'cont' : cont})
        result = cursor.fetchall()
        pprint(result)
        rowmax=result[-1]
        pid_current=rowmax[0]
        print("ardoc_oracle_tags.py: RELID,NID,PID,PROJID,DOMAIN:",relid_current,nid_current,pid_current,projid_current,domain)
        cmnd="""
merge into tags a USING ( select max(tagid)+1 as new_tagid from tags ) b
ON ( relid = :relid_c
and nid = :nid_c
and pid = :pid_c
and projid = :projid_c )
WHEN MATCHED THEN update
set TAGNAME = :tag1 where
relid = :relid_c and
nid = :nid_c and
pid = :pid_c and
projid = :projid_c
WHEN NOT MATCHED THEN insert values
( :relid_c, :nid_c, :pid_c,
b.new_tagid, :tag1, :projid_c, :domain 
)"""
        dict_p={'relid_c' : relid_current, 'nid_c' : nid_current, 'pid_c' : pid_current, 'projid_c' : projid_current, 'tag1' : tag1, 'domain' : domain}
#        print "CMND", cmnd, dict_p
        cursor.execute(cmnd,dict_p)
#        cmnd="""select tagid,tagname from tags where
#relid = '%(relid_current)s' and
#nid = '%(nid_current)s' and
#pid = '%(pid_current)s'and
#projid = '%(projid_current)s'
#""" % locals()
#        cursor.execute(cmnd)
#        result = cursor.fetchall()
#        pprint(result)
    cursor.close()
    connection.commit()
    connection.close()
