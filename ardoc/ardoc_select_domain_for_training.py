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
warea=""
nname=""
if 'HOME' in os.environ : home=os.environ['HOME']
oracle_schema=os.environ.get('ARDOC_ORACLE_SCHEMA','ATLAS_ARDOC').strip()
source_dir=os.environ.get('SOURCE_DIR','')
if 'PROJECT' not in os.environ : logging.warning("ardoc_select_domain_for_training: Warning: PROJECT is not defined in env, assuming Athena")
proj_select=os.environ.get('PROJECT','Athena')
build_dir=os.environ.get('BUILD_DIR','')
target_branch=os.environ.get('gitlabTargetBranch','')
build_proj_dir=build_dir+os.sep+proj_select+os.sep+'build'+os.sep+proj_select
logging.info("ardoc_select_domain_for_training: Info: PROJECT selected: '%s'" % (proj_select))

if source_dir == "":
    logging.critical("ardoc_select_domain_for_training: Error: SOURCE_DIR is not defined")
    sys.exit(1)
if not os.path.isdir(source_dir):
    logging.critical("ardoc_select_domain_for_training: Error: SOURCE_DIR '%s' does not exist" % (source_dir))
    sys.exit(1)
if target_branch == "":
    logging.critical("ardoc_select_domain_for_training: Error: target_branch is not defined")
    sys.exit(1)
logging.info("ardoc_select_domain_for_training: Info: gitlab target branch: '%s'" % (target_branch))

ts_now = datetime.datetime.now()
ts=ts_now
tsminus14days=ts_now-datetime.timedelta(days=12)
tdminus14days=tsminus14days.date()
#print tdd_j.strftime("%Y%m%d"), nightly_id                                                                                   
jidminus14days=int(tdminus14days.strftime("%Y%m%d"))*10000000
#jidminus14days=int(202306010000000)  
build_areas_flag=True
try:
    os.chdir(build_proj_dir)
except Exception as e:
    logging.critical("ardoc_select_domain_for_training: error when chdir to build dir '%s': '%s'" % (build_proj_dir, e))
    build_areas_flag=False
build_areas_array=[]
if build_areas_flag:
    for item in os.listdir('.'):
        if re.match('^\..*$', item): continue
        if os.path.isdir(item):
            for item1 in os.listdir(item):
                if re.match('^\..*$', item1): continue
                item9 = os.path.join(item, item1)
                if os.path.isdir(item9):
                    build_areas_array.append(item9)
len_build_areas_array=len(build_areas_array)
try:
    os.chdir(source_dir)
except Exception as e:
    logging.critical("ardoc_select_domain_for_training: error when chdir to source dir '%s': '%s'" % (source_dir, e))
domain_array_source=[]
domain_array_reduced=[]
for item in os.listdir('.'):
    if re.match('^\..*$', item): continue
    if os.path.isdir(item):
       file_found=False 
       for item1 in os.listdir(item):
         item9 = os.path.join(item, item1)
         if os.path.isfile(item9):
           logging.warning("ardoc_select_domain_for_training: Warning: skipping area '%s' as it contains file '%s'" % (item,item9))  
           file_found=True
           break
       if not file_found:
         for item1 in os.listdir(item):
           item9 = os.path.join(item, item1)
           if os.path.isdir(item9):
             CM_array=[]
             for dpath8, dirs8, files8 in os.walk(item9): 
               for filename in fnmatch.filter(files8, 'CMakeLists.txt'):
                 CM_found=os.path.join(dpath8, filename) 
                 CM_array.append(CM_found)                
                 break
               if len(CM_array) > 0: break
             if len(CM_array) == 0:
               logging.warning("ardoc_select_domain_for_training: Warning: skipping area '%s' as it does not contain CMakeLists" % (item9))
               continue
             else:
#               logging.info("ardoc_select_domain_for_training: area '%s' contains CMakeLists, e.g. " % (CM_array[0]))
               domain_array_source.append(item9)
               if len_build_areas_array != 0:
                   if item9 in build_areas_array:
                       domain_array_reduced.append(item9)
logging.info("ardoc_select_domain_for_training: resulting source domain array: '%s'" % (domain_array_source))
logging.info("ardoc_select_domain_for_training: length of the source domain array: '%s'" % (len(domain_array_source)))
logging.info("=========================")
logging.info("ardoc_select_domain_for_training: resulting domain array from build area: '%s'" % (build_areas_array))
logging.info("ardoc_select_domain_for_training: length of the domain array from build area: '%s'" % (len_build_areas_array))
logging.info("=========================")
logging.info("ardoc_select_domain_for_training: resulting reduced domain array: '%s'" % (domain_array_reduced))
logging.info("ardoc_select_domain_for_training: length of the reduced domain array: '%s'" % (len(domain_array_reduced)))
logging.info("=========================")
domain_array=domain_array_source
if proj_select != "Athena" :
    domain_array=domain_array_reduced
    logging.info("ardoc_select_domain_for_training: using reduced domain array for project '%s'" % (proj_select))
else:
    logging.info("ardoc_select_domain_for_training: using full (source) domain array for project '%s'" % (proj_select)) 
#
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
connection.clientinfo = 'python 2.6 @ home'
connection.module = 'cx_Oracle test_ARDOC.py'
connection.action = 'TestArdocJob'
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

domaindb_set=set()
cmnd="""
SELECT did,dcont,projname,tdstamp FROM DOMAINS natural join TDOMRESULTS natural join PROJECTS \
natural join jobs \
where jid > :jid and (updflag is NULL or updflag = 0) and gitbr = :gitbr order by tdstamp desc"""
logging.info("ardoc_select_domain_for_training.py: cmnd: '%s' '%s'" % (cmnd,{'jid' : jidminus14days, 'gitbr' : target_branch}))
cursor.execute(cmnd,{'jid' : jidminus14days, 'gitbr' : target_branch})
result = cursor.fetchall()
cursor.close()
connection.commit()
connection.close()
if len(result) < 1:  logging.critical("ardoc_select_domain_for_training.py: Error: failure to get domains from db"); sys.exit(1)
i9=0
for row in result:
    i9+=1
    did9=row[0]
    cont9=row[1]
    proj9=row[2]
    tsta9=row[3]
    if i9 < 4:
        logging.info("ardoc_select_domain_for_training.py: DB ROW: '%s' '%s' '%s' '%s'" % (did9, cont9, proj9, tsta9)) 
#    print "===DB ROW ",did9,cont9,proj9,tsta9
    if proj9 == proj_select:
        domaindb_set.add(cont9)
domaindb_list=list(domaindb_set)
unlisted_domains=list(set(domain_array)-domaindb_set)
check_diff=list(set(domain_array)-set(unlisted_domains))
logging.info("ardoc_select_domain_for_training.py: list of domains from db: '%s'" % (domaindb_list)) 
logging.info("ardoc_select_domain_for_training.py: domains not listed in db: '%s'" % (unlisted_domains))
#logging.info("ardoc_select_domain_for_training.py: check: domains with unlisted domains subtracted listed: '%s'" % (check_diff))
if len(unlisted_domains) < 1 :
    logging.info("ardoc_select_domain_for_training.py: Warning: all domains are listed, selecting oldest domain")
    i9=0; i90=0; i91=0; i92=0 
    domaindb_dict={}
    domaindb_order_dict={}
    for row in result:
        i9+=1
        did9=row[0]
        cont9=row[1]
        proj9=row[2]
        tsta9=row[3]
        if not cont9 in domain_array:
            i90+=1
            if i90 < 4: logging.info("ardoc_select_domain_for_training.py: item skipped - not found in build area '%s'" % (cont9))
            continue
        if cont9 not in domaindb_dict:
            domaindb_dict[cont9]=tsta9
            i91+=1
            domaindb_order_dict[cont9]=i91
            if i91 < 4: logging.info("ardoc_select_domain_for_training.py: item selected for domain_dict '%s', '%s'" % (cont9,tsta9))
        else:
            i92+=1
            tsta9_exist=domaindb_dict[cont9]
            if i92 < 4: logging.info("ardoc_select_domain_for_training.py: item '%s', '%s' already in domain_dict with '%s'" % (cont9,tsta9,tsta9_exist))
    d_keys=list(domaindb_order_dict.keys())
    d_values=list(domaindb_order_dict.values())
    val_index=d_values.index(i91)
    oldest_domain=d_keys[val_index]
    logging.info("ardoc_select_domain_for_training.py: domaindb_dict: '%s'" % (domaindb_dict))
    logging.info("ardoc_select_domain_for_training.py: domaindb_order_dict: '%s'" % (domaindb_order_dict))
    logging.info("ardoc_select_domain_for_training.py: index of domain with oldest results: '%s'- '%s'" % (val_index,oldest_domain))
    print(oldest_domain)
else:
    random_domain=random.choice(unlisted_domains)
    logging.info("ardoc_select_domain_for_training.py: random domain choice: '%s' out of %s unlisted items" % (random_domain,len(unlisted_domains)))
    print(random_domain)

