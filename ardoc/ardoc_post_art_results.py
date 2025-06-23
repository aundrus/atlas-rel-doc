import re,os,sys,json
import getpass
import platform
import cx_Oracle
from pprint import pprint
import datetime
import getopt,glob,logging
import subprocess

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
#try:
#    optionslist, args = getopt.getopt(sys.argv[1:],'n:gs:',['nightly=','get','set=','short'])
#except getopt.error:
#    print >> sys.stderr,'''ardoc_post_art_results.py: Error: You tried to use an unknown option or the argument for an option that requires it was missing.'''
#    sys.exit(0)

home=os.environ.get('HOME','')
ardoc_home=os.environ.get('ARDOC_HOME','')
if ardoc_home == '':
    logging.error("ardoc_post_art_results.py: Error: ARDOC_HOME is not defined")
    sys.exit(1)
oracle_schema=os.environ.get('ARDOC_ORACLE_SCHEMA','ATLAS_NICOS').strip()

art_logdir="/afs/cern.ch/atlas/software/dist/gitwww/GITWebArea/nightlies"
ts_j=datetime.datetime.now()
ts_2=ts_j - datetime.timedelta(days=2)
cFN="/afs/cern.ch/atlas/software/dist/nightlies/cgumpert/TC/OR_crdntl"
lne=open(cFN,'r')
lne_res=lne.readline()
lne.close()
lnea=re.split(r'\s+',lne_res)          
accnt,pwf,clust=lnea[0:3]
connection = cx_Oracle.connect(accnt,pwf,clust)
connection.clientinfo = 'python 2.6 @ home'
connection.module = 'cx_Oracle ardoc_post_art_results.py'
connection.action = 'night status handling'
cursor = connection.cursor()
try:
    connection.ping()
except cx_Oracle.DatabaseError as exception:
    error, = exception.args
    logging.error("ardoc_post_art_results.py: Database connection error: '%s' '%s' '%s'", error.code, error.offset, error.message)
cursor.execute("ALTER SESSION SET current_schema = "+oracle_schema)    

cmnd="""
select n.nname, a.name, a.reltstamp, platf.pl, p.projname, j.projid, to_char(j.jid), j.ela, j.sla
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
    logging.error("ardoc_post_art_results.py: Error: query for recent nightlies returned empty result")
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
      logging.info("ardoc_post_art_results.py: Warning: bypassing non-standard nightly name: '%s'",k)
      continue
    branch=arrk[0]
    project=arrk[1]
    platform='_'.join(arrk[2:])
    logging.info("ardoc_post_art_results.py: Info:  '%s' '%s' '%s' '%s' '%s' '%s'=='%s'=='%s'",branch,project,platform,v[0],v[1],v[2],v[3],v[4])
    path_to_js=art_logdir+os.sep+branch+os.sep+str(v[0])+os.sep+project+os.sep+platform+os.sep+project+os.sep+'index.js'
    logging.info("ardoc_post_art_results.py: Info: path to ART js: ")
    logging.info(">>>>>> '%s'",path_to_js)
#    list_paths=glob.glob(path_to_js)
#    if len(list_paths) > 0:
    if os.path.isfile(path_to_js):
      logging.info("ardoc_post_art_results.py: Info: ART JS FOUND")
      a0={}
      with open(path_to_js,'r') as f987:
          t987=''.join([x.strip() for x in f987])
#          pprint(t987)
          arr987=re.split(',',t987)
          sign=0
          nerr='N/A'; nsuc='N/A'; nwar='N/A'
          for line in arr987:
              line1=re.sub('\s','',line)
              if re.match('^art:.*$', line1): sign=1 
#              print "L", line1, sign
              if sign == 1 and re.match('e:',line1): nerr=re.sub('e:','',line1)
              if sign == 1 and re.match('s:',line1): nsuc=re.sub('s:','',line1)
              if sign == 1 and re.match('w:',line1): nwar=re.sub('w:','',line1)
              nerr=re.sub('}','',nerr); nsuc=re.sub('}','',nsuc); nwar=re.sub('}','',nwar)
              if sign == 1 and re.search('}', line1): break
              if nerr != 'N/A' and nsuc != 'N/A' and nwar != 'N/A': break
          logging.info("ardoc_post_art_results.py: Info: N errors, successes, warnings: '%s' '%s' '%s'",nerr,nsuc,nwar)  

#          if v[3] == None or v[3] == '':
          if '1' == '1':
              logging.info("ardoc_post_art_results.py: Info: ART INFO MISSING in DB, adding") 
              env_coma={'ARDOC_HOME' : ardoc_home}
              coma=ardoc_home+os.sep+'ardoc_post_status_new_withwarn --jid '+v[2]+' --relstamp '+v[0]+ ' -n '+k+' --arch '+platform+' --param la --phase e status 0 --err '+nerr+' --suc '+nsuc+' --war '+nwar+' --notimeoutcontrol'
      
              logging.info("ardoc_post_art_results.py: Info: command to run via subprocess:")
              logging.info(">>>>>> '%s'",coma)
              subp = subprocess.Popen(coma, stdout = subprocess.PIPE, shell=True, env=env_coma)
              stdout,stderr = subp.communicate()
              if subp.returncode != 0:
                logging.error("ardoc_post_art_results.py: Error: subprocess return code is: '%s'", subp.returncode)
              if stderr!=None:
                logging.error("ardoc_post_art_results.py: Error: subprocess stderr")
                logging.error("'%s'",stderr)
                sys.exit(1)
              if stdout!=None:
                logging.info("ardoc_post_art_results.py: Info: subprocess stdout")
                logging.info("'%s'",stdout)
#          else:
#             print "ardoc_post_art_results.py: Info: ART INFO is in DB : date:",v[3],", status",v[4]        
    else:
      logging.info("ardoc_post_art_results.py: Info: ART JS IS NOT YET") 
    logging.info("------")
