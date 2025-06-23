import re,os,sys
import getpass
import platform
import cx_Oracle
from pprint import pprint
import datetime
import getopt,glob,logging
import subprocess

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
try:
    optionslist, args = getopt.getopt(sys.argv[1:],'n:gs:',['nightly=','get','set=','short'])
except getopt.error:
    logging.error('''ardoc_post_cvmfsclient_status.py: Error: You tried to use an unknown option or the argument for an option that requires it was missing.''')
    sys.exit(0)

home=os.environ.get('HOME','')
ardoc_home=os.environ.get('ARDOC_HOME','')
if ardoc_home == '':
    logging.error("ardoc_post_cvmfsclient_status.py: Error: ARDOC_HOME is not defined")
    sys.exit(1)
cvmfs_install_root="/cvmfs/atlas-nightlies.cern.ch/repo/sw"
oracle_schema=os.environ.get('ARDOC_ORACLE_SCHEMA','ATLAS_NICOS').strip()
ts_j = datetime.datetime.now()
ts_2 = ts_j - datetime.timedelta(days=2)
cFN="/afs/cern.ch/atlas/software/dist/nightlies/cgumpert/TC/OR_crdntl"
lne=open(cFN,'r')
lne_res=lne.readline()
lne.close()
lnea=re.split(r'\s+',lne_res)          
accnt,pwf,clust=lnea[0:3]
connection = cx_Oracle.connect(accnt,pwf,clust)
connection.clientinfo = 'python 2.6 @ home'
connection.module = 'cx_Oracle ardoc_post_cvmfsclient_status.py'
connection.action = 'night status handling'
cursor = connection.cursor()
try:
    connection.ping()
except cx_Oracle.DatabaseError as exception:
    error, = exception.args
    logging.error("ardoc_post_cvmfsclient_status.py: Database connection error: '%s' '%s' '%s'", error.code, error.offset, error.message)
cursor.execute("ALTER SESSION SET current_schema = "+oracle_schema)    

cmnd="""
select n.nname, a.name, a.reltstamp, platf.pl, p.projname, j.projid, to_char(j.jid), j.ecvkv, j.scvkv
from nightlies n inner join                                    
( releases  a  inner join                                     
( jobstat j inner join projects p on j.projid = p.projid ) 
on a.nid=j.nid and a.relid=j.relid )                               
on n.nid=a.nid,                                                           
(select arch||'-'||os||'-'||comp||'-'||opt as pl, jid from jobs ) platf 
where
j.jid BETWEEN to_number(to_char(SYSDATE-4, 'YYYYMMDD'))*10000000
AND to_number(to_char(SYSDATE, 'YYYYMMDD')+1)*10000000                        
AND j.jid = platf.jid
AND a.reltstamp > :t_val 
AND n.nname not like 'MR%-CI%'
AND j.begdate between sysdate-4 and sysdate 
AND j.eb is not NULL 
order by j.eb asc
"""
cursor.execute(cmnd,{'t_val' : ts_2})
result = cursor.fetchall()
connection.close()
if len(result) == 0:
    logging.error("ardoc_post_cvmfsclient_status.py: Error: query for recent nightlies returned empty result")
    sys.exit(1)
#for row in result:
#    pprint(row)
dict_n={}
for row in result:
#    dict_n[row[0]+':'+row[3]+':'+row[4]]=row[1]
    dict_n[row[0]]=[row[1],row[5],row[6],row[7],row[8]]
for k,v in dict_n.items():
    arrk=re.split('_',k)
    if len(arrk) < 3:
      logging.info("ardoc_post_cvmfsclient_status.py: Warning: bypassing non-standard nightly name: '%s'",k)
      continue
    branch=arrk[0]
    project=arrk[1]
    platform='_'.join(arrk[2:])
    logging.info("ardoc_post_art_results.py: Info:  '%s' '%s' '%s' '%s' '%s' '%s'=='%s'=='%s'",branch,project,platform,v[0],v[1],v[2],v[3],v[4])
    path_to_releasedata=cvmfs_install_root+os.sep+branch+os.sep+str(v[0])+os.sep+project+os.sep+'*'+os.sep+'InstallArea'+os.sep+platform+os.sep+'ReleaseData'
    logging.info("ardoc_post_cvmfsclient_status.py: Info: path to ReleaseData: ")
    logging.info(">>>>>> '%s'",path_to_releasedata) 
    path_to_releasedata1=cvmfs_install_root+os.sep+branch+'_'+project+'_'+platform+os.sep+str(v[0])+os.sep+project+os.sep+'*'+os.sep+'InstallArea'+os.sep+platform+os.sep+'ReleaseData'
    logging.info("ardoc_post_cvmfsclient_status.py: Info: path1 to ReleaseData: ")
    logging.info(">>>>>> '%s'",path_to_releasedata1)
    list_paths=[]
    list_paths=glob.glob(path_to_releasedata)
    list_paths1=[]
    list_paths1=glob.glob(path_to_releasedata1)
#    pprint(list_paths)
    if len(list_paths) > 0 or len(list_paths1):
      logging.info("ardoc_post_cvmfsclient_status.py: Info: CVMFS INSTALLATION FOUND '%s' '%s'",len(list_paths),len(list_paths1))
      if v[3] == None or v[3] == '':
        logging.info("ardoc_post_cvmfsclient_status.py: Info: CVMFS CLIENT INFO MISSING in DB, adding")
        env_coma={'ARDOC_HOME' : ardoc_home}
        coma=ardoc_home+os.sep+'ardoc_post_status --jid '+v[2]+' --relstamp '+v[0]+ ' -n '+k+' --arch '+platform+' --param cvkv --phase e status 0 --notimeoutcontrol'
        logging.info("ardoc_post_cvmfsclient_status.py: Info: command to run via subprocess:")
        logging.info(">>>>>> '%s'",coma)
        subp = subprocess.Popen(coma, stdout = subprocess.PIPE, shell=True, env=env_coma)
        stdout,stderr = subp.communicate()
        if subp.returncode != 0:
          logging.info("ardoc_post_cvmfsclient_status.py: Error: subprocess return code is: '%s'", subp.returncode)
        if stderr!=None:
          logging.error("ardoc_post_cvmfsclient_status.py: Error: subprocess stderr")
          logging.error("'%s'")
          sys.exit(1)
        if stdout!=None:
          logging.info("ardoc_post_cvmfsclient_status.py: Info: subprocess stdout")
          logging.info("'%s'")
      else:
        logging.info("ardoc_post_cvmfsclient_status.py: Info: CVMFS CLIENT is in DB : date: '%s', status '%s'",v[3],v[4])        
    else:
      logging.info("ardoc_post_cvmfsclient_status.py: Info: CVMFS INSTALLATION NOT YET DONE") 
    logging.info("------")
