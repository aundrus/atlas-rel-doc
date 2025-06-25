# to set env run
# export ARDOC_HOME=/afs/cern.ch/atlas/software/dist/ci/git_ci/ardoc_doc_builder_CI01_dev_V2/ardoc_doc_builder
# source $ARDOC_HOME/ARDOC_oracle_setup.sh
import logging, fnmatch, glob, random, re
import os
import sys
import getpass
import platform
import cx_Oracle
from pprint import pprint
import datetime
#logging.basicConfig(format='%(asctime)s %(levelname)-10s %(message)s', datefmt='%H:%M:%S', level='DEBUG')
#level has to be set as logging.DEBUG 
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
#logging.basicConfig(format='%(asctime)s %(levelname)-10s %(message)s', datefmt='%H:%M:%S',level=logging.DEBUG)
#print ("Python version: " + platform.python_version())
#print ("cx_Oracle version: " + cx_Oracle.version)
#print ("Oracle client: " + str(cx_Oracle.clientversion()).replace(', ','.'))
home=""
if 'HOME' in os.environ : home=os.environ['HOME']
oracle_schema=os.environ.get('ARDOC_ORACLE_SCHEMA','ATLAS_ARDOC').strip()
projects=['Athena','AthSimulation']
branches=['23.0','main']
ts_now = datetime.datetime.now()
ts=ts_now
tsminus90days=ts_now-datetime.timedelta(days=90)
tdminus90days=tsminus90days.date()
tsminus30days=ts_now-datetime.timedelta(days=30)
tdminus30days=tsminus30days.date()
tsminus14days=ts_now-datetime.timedelta(days=14)
tdminus14days=tsminus14days.date()
tsminus7days=ts_now-datetime.timedelta(days=7)
tdminus7days=tsminus7days.date()
tsminus1days=ts_now-datetime.timedelta(days=1)
tdminus1days=tsminus1days.date()
jidminus90days=int(tdminus90days.strftime("%Y%m%d"))*10000000
jidminus30days=int(tdminus30days.strftime("%Y%m%d"))*10000000
jidminus14days=int(tdminus14days.strftime("%Y%m%d"))*10000000
jidminus7days=int(tdminus7days.strftime("%Y%m%d"))*10000000
jidminus1days=int(tdminus1days.strftime("%Y%m%d"))*10000000 
jidminus0days=int(ts_now.strftime("%Y%m%d"))*10000000

cFN="/afs/cern.ch/atlas/software/dist/nightlies/cgumpert/TC/OW_crdntl"
lne=open(cFN,'r')
lne_res=lne.readline()
lne.close()
lnea=re.split(r'\s+',lne_res)          
accnt,pwf,clust=lnea[0:3]
#print "XXXX",accnt,pwf,clust
#
connection = cx_Oracle.connect(accnt,pwf,clust)
#print ("Oracle DB version: " + connection.version)
#print ("Oracle client encoding: " + connection.encoding)
cursor = connection.cursor()
cursor.execute('select sysdate from dual')
try:
    connection.ping()
except cx_Oracle.DatabaseError as exception:
    error, = exception.args
    logging.info("ardoc_select_domain_for_training.py: Database connection error: '%s' '%s' '%s'" % (error.code, error.offset, error.message))
else:
    logging.info("ardoc_select_domain_for_training.py: Connection is alive!")
cursor.execute("ALTER SESSION SET current_schema = "+oracle_schema)    

i1=0
l_days=[]; l_branch=[];  l_project=[]; l_ldomaindb=[]
l_domainset=[];
for project_select in projects:
    for branch_select in branches:
        i_jid=0
        days=[90,30,14,7,1,0]
#        days=[0]
        for jid_select in [jidminus90days, jidminus30days, jidminus14days, jidminus7days, jidminus1days, jidminus0days]:
#        for jid_select in [jidminus0days]:
            l_days.append(days[i_jid])
            l_branch.append(branch_select)
            l_project.append(project_select) 
            i1+=1; i_jid+=1
            gitbr1=branch_select
            gitbr2='none'
            logging.info("ardoc_list_training: Info: PROJECT, BRANCH, START_JID selected: '%s'***'%s'***'%s'" % (project_select,branch_select,jid_select))
            if gitbr1 == 'main':
                gitbr2='master'
                logging.info("ardoc_list_training: Info: additionally BRANCH '%s' is selected" % (gitbr2)) 
            cmnd="""
SELECT did,dcont,projname,tdstamp,to_char(jid) FROM DOMAINS natural join TDOMRESULTS natural join PROJECTS \
natural join jobs \
where jid > :jid and (updflag is NULL or updflag = 0) and projname = :projname \
and ( gitbr = :gitbr1 or gitbr = :gitbr2 ) order by tdstamp desc"""
            logging.info("ardoc_select_domain_for_training.py: cmnd: '%s' '%s'" % (cmnd,{'jid':jid_select,'gitbr1':gitbr1,'gitbr2':gitbr2,'projname':project_select}))
            cursor.execute(cmnd,{'jid':jid_select,'gitbr1':gitbr1,'gitbr2':gitbr2,'projname':project_select})
            result=cursor.fetchall()
            lresult=len(result)
            i9=0
            domaindb_set=set()
            for row in result:
                i9+=1
                did9=row[0]
                cont9=row[1]
                proj9=row[2]
                tsta9=row[3]
                jid9=row[4]
#                print(jid9,cont9)
                domaindb_set.add(cont9) 
            ldomaindb=len(domaindb_set)
#            print(domaindb_set)
            logging.info("ardoc_list_training: Info: number of domains probed: %s, total N tests %s" % (ldomaindb, lresult))
            l_domainset.append(domaindb_set) 
            l_ldomaindb.append(ldomaindb)
cursor.close()
connection.commit()
connection.close()
s_mainAthena_30=set(); s_main23_30=set()
for i in range(0,i1):
    logging.info("ardoc_list_training: %s * %s * %s * %s --- %s " % (str(i),l_project[i], l_branch[i], str(l_days[i]), l_ldomaindb[i]))
    if l_days[i] == 30 and l_branch[i] == 'main' and l_project[i] == 'Athena' : s_mainAthena_30=l_domainset[i]
    if l_days[i] == 30 and l_branch[i] == '23.0' and l_project[i] == 'Athena' : s_main23_30=l_domainset[i]

#print(list(s_mainAthena_30))
#print("==================")
#print(list(s_main23_30))
print("------------------")
print((list(s_main23_30-s_mainAthena_30)))
