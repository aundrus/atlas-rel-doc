import re
import os
import sys
import getpass
import platform
import cx_Oracle
from pprint import pprint
import datetime
import smtplib,logging,socket
import pickle

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
#print ("Python version: " + platform.python_version())
#print ("cx_Oracle version: " + cx_Oracle.version)
#print ("Oracle client: " + str(cx_Oracle.clientversion()).replace(', ','.'))
hostname1=socket.gethostname(); hostname=re.split(r'\.',hostname1)[0]
home=""
nname=""; paname=""; nicos_arch=""
mr_id=""; mr_iid=""; ci_results_file=""
if 'HOME' in os.environ : home=os.environ['HOME']
oracle_schema=os.environ.get('NICOS_ORACLE_SCHEMA','ATLAS_NICOS').strip()
nicos_gen_config_area=os.environ.get('NICOS_GEN_CONFIG_AREA','')
projn=os.environ.get('NICOS_PROJECT_NAME','')
nicos_home=os.environ.get('NICOS_HOME','')
local_work_area=''
if nicos_home != '':
    local_work_area_base=os.path.basename(nicos_home)
    if local_work_area_base == '':
        local_work_area_1=os.path.dirname(nicos_home)
        local_work_area=os.path.dirname(local_work_area_1) 
    else:
        local_work_area=os.path.dirname(nicos_home)
nightly_name=os.environ.get('NICOS_NIGHTLY_NAME','N/A')
nicos_project_relname=os.environ.get('NICOS_PROJECT_RELNAME','N/A')
nicos_arch=os.environ.get('NICOS_ARCH','')
mr_id=os.environ.get('gitlabMergeRequestId','')
mr_iid=os.environ.get('gitlabMergeRequestIid','')
mr_tbr=os.environ.get('gitlabTargetBranch','')
ts_now = datetime.datetime.now()
t_epoch=os.environ.get('NICOS_EPOCH','')
ci_results_file=os.environ.get('CI_RESULTS_DICT','') 
if projn == "":
    logging.warn("nicos_oracle_domains_updater.py: Error: PROJECT NAME is not defined")
    sys.exit(1)
if nicos_arch == "":
    logging.warn("nicos_oracle_domains_updater.py: Error: ARCHITECTURE (\"NICOS_ARCH\" var) is not defined")
    sys.exit(1)
if mr_id == "" :
    logging.warn("nicos_oracle_domains_updater.py: Error: gitlabMergeRequestId is not defined")
    sys.exit(1)
if mr_iid == "" :
    logging.warn("nicos_oracle_domains_updater.py: Error: gitlabMergeRequestIid is not defined")
    sys.exit(1)
if mr_tbr == "" :
    logging.warn("nicos_oracle_domains_updater.py: Error: gitlabTargetBranch is not defined")
    sys.exit(1)
if ci_results_file == "" :
    logging.warn("nicos_oracle_domains_updater.py: Error: CI RESULTS file (\"CI_RESULTS_DICT\" var) is not defined")
    sys.exit(1)
if projn != 'Athena' and projn != 'AthSimulation':
    logging.info("nicos_oracle_domains_updater.py: RUNS FOR Athena and AthSimulation projects only")
    sys.exit(1)

ci_results_dir=os.path.dirname(ci_results_file)
ctest_dict_file=ci_results_dir+os.sep+'ctestlist'+projn+'_'+mr_id+'.pkl'
afdomainlist_file=ci_results_dir+os.sep+'afdomainlist'+projn+'_'+mr_id
if os.path.isfile(ctest_dict_file) :
   logging.info("nicos_oracle_domains_updater.py: using ctest results pickle file '%s'" % (ctest_dict_file))
else:
   logging.warn("nicos_oracle_domains_updater.py: Error: ctest results pickle file '%s' does not exist" % (ctest_dict_file))
   sys.exit(1)
if os.path.isfile(afdomainlist_file) :
   logging.info("nicos_oracle_domains_updater.py: using affected domain list from '%s'" % (afdomainlist_file))
else:
   logging.warn("nicos_oracle_domains_updater.py: Error: affected domain list file '%s' does not exist" % (afdomainlist_file))   
   sys.exit(1)
lines_afd=[]
try:
    mf=open(afdomainlist_file)
    lines_afd = mf.readlines()
    mf.close()
except:
    lines_afd=[]
affected_domains=[]
for x in lines_afd:
    line1=x.strip()
    if len(re.sub(r'\s+','',line1)) == 0 : continue
    affected_domains.append(line1)
len_affected_domains=len(affected_domains)
logging.info("nicos_oracle_domains_updater.py: affected domains: '%s'" % (affected_domains))
ts=ts_now
tsminus30days=ts_now-datetime.timedelta(days=30)
tdminus30days=tsminus30days.date()
jidminus30days=int(tdminus30days.strftime("%Y%m%d"))*10000000
year_and_day=ts_now.strftime("%Y_%j")
if t_epoch != '':
    fdtt=float(t_epoch)
    ts=datetime.datetime.fromtimestamp(fdtt)
relnstamp=ts.strftime("%Y-%m-%dT%H%M")
#RELID NID NAME TYPE TCREL TCRELBASE URL2LOG
arch_a=re.split(r'\-',nicos_arch)
arch=arch_a[0]
osys=arch_a[1]
comp=arch_a[2]
opt=arch_a[3]
#
cFN="/afs/cern.ch/atlas/software/dist/nightlies/cgumpert/TC/OW_crdntl"
lne=open(cFN,'r')
lne_res=lne.readline()
lne.close()
lnea=re.split(r'\s+',lne_res)          
accnt,pwf,clust=lnea[0:3]
#print "XXXX",accnt,pwf,clust
#
jid_res=''
fjid=nicos_gen_config_area+os.sep+'jobid.txt'
if os.path.isfile(fjid) :
    f=open(fjid, 'r')
    jid_res=f.readline()
    f.close()
if jid_res == '':
    logging.warn("nicos_oracle_domains_updater.py: Error: JOB ID could not be retrieved")
    sys.exit(1)
logging.info("nicos_oracle_domains_updater.py: jid retrieved from file: '%s'" % (jid_res))

#output_list_read=[]
#allowed_tests=[]
#excluded_tests=[]
#with open(ctest_dict_file, 'rb') as fp:
#    objs = []
#    while True:
#        try:
#            o = pickle.load(fp)
#        except EOFError:
#            break
#        objs.append(o)
#    lenobjs=len(objs)
#    logging.info("nicos_oracle_domains_updater.py: number of objects read from pickle file '%s'", str(lenobjs))
#    if lenobjs >= 1 :
#        output_list_read=objs[0]
#    if lenobjs >= 2 :
#        allowed_tests=objs[1]
#    if lenobjs >= 3 :
#        excluded_tests=objs[2]
#i9=0
#for item in allowed_tests :
#    i9+=1
#    logging.info("nicos_oracle_domains_updater.py: test allowed: '%s' '%s'" % (str(i9),item))
#i9=0
#for item in excluded_tests :
#    i9+=1
#    logging.info("nicos_oracle_domains_updater.py: test excluded: '%s' '%s'" % (str(i9),item))
#
#logging.info("nicos_oracle_domains_updater.py: output_list: '%s'" % (output_list_read))

connection = cx_Oracle.connect(accnt,pwf,clust)
#print ("Oracle DB version: " + connection.version)
#print ("Oracle client encoding: " + connection.encoding)
connection.clientinfo = 'python 2.6 @ home'
connection.module = 'cx_Oracle test_NICOS.py'
connection.action = 'TestNicosJob'
cursor = connection.cursor()
cursor.execute('select sysdate from dual')
try:
    connection.ping()
except cx_Oracle.DatabaseError as exception:
    error, = exception.args
    logging.warn("nicos_oracle_domains_updater.py: Database connection error: %s %s %s" % ( error.code, error.offset, error.message))
else:
    logging.warn("nicos_oracle_domains_updater.py: Connection is alive!")
cursor.execute("ALTER SESSION SET current_schema = "+oracle_schema)    

logging.info("nicos_oracle_domains_updater.py: reading test results from DB")
cmnd="""
SELECT res,projname,name,pname,contname,to_char(tstamp, 'RR/MM/DD HH24:MI'), \
tname,excess from TESTRESULTS natural join JOBSTAT natural join PROJECTS natural join PACKAGES \
where jid = :jid_res and projname = :projn"""
logging.info("nicos_oracle_domains_updater.py: cmnd: '%s' '%s'" % (cmnd,{'jid_res':jid_res,'projn':projn}))
cursor.execute(cmnd,{'jid_res':jid_res,'projn':projn})
result=cursor.fetchall()
lresult=len(result)
i8=0
dict_results={}
npbs=0
for row in result:
    i8+=1
    res8=row[0]
    if res8 > 0: npbs+=1 
    name8=row[2]
    pname8=row[3]
    cname8=row[4]
    t8=row[5]
    fname8=row[6]
    exc8=row[7]
    if re.match('^CITest.*',fname8) and not re.match('^CITest_SystemCheck.*',fname8): dict_results[fname8]=res8   
    if i8 > (lresult - 5): logging.info("=== '%s' * '%s' = '%s' '%s' '%s' = '%s' '%s'" % (res8, exc8, name8, pname8, cname8, fname8, t8)) 
if lresult <= 1:
    logging.warn("nicos_oracle_domains_updater.py: Warning: number of tests performed is less than 2, exiting")

dict_domain_results={}
for afd9 in affected_domains:
    logging.info("nicos_oracle_domains_updater.py: checking DB info for domain '%s'" % (afd9)) 
    cmnd="""
SELECT dname,dcont,dres,fname,projname,tdstamp,updflag,to_char(j.jid) FROM DOMAINS d inner join \
 ( TESTS t inner join \
 ( JOBS j inner join \
 ( PROJECTS p inner join TDOMRESULTS td on p.projid = td.projid ) \
 on td.jid = j.jid and td.relid = j.relid ) \
 on t.tid = td.tid ) \
 on d.did = td.did \
 where j.jid > :jid and projname = :projn and dcont = :dcont and gitbr = :gitbr order by tdstamp asc"""
#    cmnd=""" 
#SELECT dname,dcont,dres,fname,projname,tdstamp,updflag,to_char(jid) \
#FROM DOMAINS natural join TDOMRESULTS natural join PROJECTS \
#natural join jobs natural join tests \
#where jid > :jid and projname = :projn \
#and gitbr = :gitbr and dcont = :dcont order by tdstamp asc"""
    logging.info("nicos_oracle_domains_updater.py: cmnd: '%s' '%s'" % (cmnd,{'jid':jidminus30days,'gitbr':mr_tbr,'projn':projn,'dcont':afd9}))
    cursor.execute(cmnd,{'jid':jidminus30days,'gitbr':mr_tbr,'projn':projn,'dcont':afd9})
    result=cursor.fetchall()
    lresult=len(result)
    i9=0
    dict_per_domain_results={}
    for row in result:
       i9+=1
       dname9=row[0]
       cont9=row[1]
       dres9=row[2]
       fname9=row[3]
       proj9=row[4]
       tsta9=row[5]
       updflag9=row[6]
       jid9=row[7]
       if i9 > (lresult - 5): logging.info("=== '%s' * '%s' * '%s' = '%s' = '%s' = '%s' = '%s'" % (dname9,cont9,dres9,fname9,proj9,updflag9,tsta9))
       if re.match('^CITest.*',fname9) and not re.match('^CITest_SystemCheck.*',fname9) : dict_per_domain_results[fname9]=dres9
#    logging.info("nicos_oracle_domains_updater: total N tests %s" % (lresult))
    logging.info("nicos_oracle_domains_updater: results stored for domain %s : %s" % (afd9,dict_per_domain_results))
    l_dict_per_domain_results=len(dict_per_domain_results)
    if l_dict_per_domain_results <= 1:
        logging.warn("nicos_oracle_domains_updater.py: Warning: number results stored for domain %s is less than 2" % (afd9))
    for k,v in list(dict_per_domain_results.items()):
        if k in dict_domain_results:
            if dict_domain_results[k] < v: 
                logging.info("nicos_oracle_domains_updater.py: updating combined domain results from %s to %s" % (dict_domain_results[k], v)) 
                dict_domain_results[k]=v
        else:
            dict_domain_results[k]=v
cursor.close()
connection.commit()
connection.close()
logging.info("nicos_oracle_domains_updater.py: combined domain results %s" % (dict_domain_results))

inconsistency_list=[]
for k,v in list(dict_results.items()):
    if k in dict_domain_results:
        domain_res=dict_domain_results[k]

        if v > domain_res:
            logging.warn("nicos_oracle_domains_updater.py: Issue: test '%s' result '%s' domain result '%s'" % (k,v,domain_res))
            inconsistency_list.append('test:'+k+',result:'+str(v)+',dbdata:'+str(domain_res))
        else:
            logging.info("nicos_oracle_domains_updater.py: test '%s' result '%s' domane result '%s'" % (k,v,domain_res)) 
    else:
        logging.warn("nicos_oracle_domains_updater.py: Warning: no result stored for test '%s' ('%s')" % (k,v))
len_inconsistency_list=len(inconsistency_list)
cumulative_data_file="/afs/cern.ch/atlas/software/dist/ci/log_domcheck/domcheck_"+year_and_day
if npbs > 0:
    logging.info("nicos_oracle_domains_updater.py: findings are forwarded to %s", cumulative_data_file)
    file_handle=open(cumulative_data_file, 'a')
    file_handle.write('#\n')
    data_line=nicos_project_relname+"#project:"+projn+"#target:"+mr_tbr+"#issues:"+str(npbs)+"#inconsistencies:"+str(len_inconsistency_list)
    file_handle.write(data_line+'\n') 
    if len_inconsistency_list > 0:
        data_line=nicos_project_relname+"#project:"+projn+"#target:"+mr_tbr+"#hostname:"+hostname+"#jid:"+jid_res  
        file_handle.write(data_line+'\n')
        data_line=nicos_project_relname+"#project:"+projn+"#target:"+mr_tbr+"#n_domains:"+str(len_affected_domains)+"#domnames:"+' '.join(affected_domains)
        file_handle.write(data_line+'\n')
        for item76 in inconsistency_list:
            file_handle.write(nicos_project_relname+"#project:"+projn+"#target:"+mr_tbr+"#inconsistency:"+item76+'\n')
    file_handle.close() 
if len_inconsistency_list > 0:
    mail_body="CI reports inconsistency in tests sensitivities\n"
    mail_body=mail_body+"time stamp "+relnstamp+"\n"
    mail_body=mail_body+"hostname,job id "+hostname+' '+jid_res+"\n"
    mail_body=mail_body+"nightly name "+nightly_name+"\n"
    mail_body=mail_body+"local work area, MR name "+local_work_area+' '+nicos_project_relname+"\n"
    mail_body=mail_body+"project, target branch "+projn+' '+mr_tbr+"\n"
    mail_body=mail_body+"id, iid "+mr_id+' '+mr_iid+"\n"
    mail_body=mail_body+"affected domains "+' '.join(affected_domains)+"\n"
    mail_body=mail_body+"========INCONSISTENCIES:========\n"
    for item76 in inconsistency_list:
        mail_body=mail_body+item76+"\n"
    logging.info("nicos_oracle_domains_updater.py: sending email notification--->")
    logging.info("'%s'" % (mail_body))
    subj = "CI testing: domain issue on "+hostname
    sender = 'atlasbot@mail.cern.ch'
    receivers = ['undrus@bnl.gov']
    message = """From: ATLAS Robot <atlasbot@mail.cern.ch>
To: %s
Subject: %s

%s
""" % (", ".join(receivers),subj,mail_body)
    try:
        smtpObj = smtplib.SMTP('localhost')
        smtpObj.sendmail(sender, receivers, message)
        logging.info("nicos_oracle_domains_updater.py: SENDING MESSAGE TO '%s'",receivers)
    except:
        logging.error("ardoc_send_mail.py: Warning: unable to send email")

# update domain results the number of affected domais <= max_len_affected_domains
max_len_affected_domains=3
if len_inconsistency_list > 0 and len_affected_domains <= max_len_affected_domains:
  connection = cx_Oracle.connect(accnt,pwf,clust)
  connection.clientinfo = 'python 2.6 @ home'
  connection.module = 'cx_Oracle test_NICOS.py'
  connection.action = 'TestNicosJob'
  cursor = connection.cursor()
  cursor.execute('select sysdate from dual')
  try:
      connection.ping()
  except cx_Oracle.DatabaseError as exception:
      error, = exception.args
      logging.warn("nicos_oracle_domains_updater.py: Database connection #2 error: %s %s %s" % ( error.code, error.offset, error.message))
  else:
      logging.warn("nicos_oracle_domains_updater.py: Connection #2 is alive!")
  cursor.execute("ALTER SESSION SET current_schema = "+oracle_schema)
#
  iter=0
  for afd9 in affected_domains:
    cmnd="""
SELECT did,dname,dcont FROM DOMAINS where dcont = :dcont"""
    cursor.execute(cmnd,{'dcont':afd9})
    result=cursor.fetchall()
    if len(result) < 1: logging.error("nicos_oracle_domains_updater.py: absent domain container name: ",afd9); sys.exit(1)
    row=result[-1]
    domid8=row[0]
    logging.info("--------") 
    logging.info("nicos_oracle_domains_updater.py: updating DB for domain '%s' - '%s'" % (domid8,afd9))
    for x in inconsistency_list:
        line=x.strip()
        line_a=re.split(r',',line) 
        if line_a >= 3:
            testn5=(re.split(r':',line_a[0]))[-1] 
            rest5=(re.split(r':',line_a[1]))[-1]
            domrest5=(re.split(r':',line_a[2]))[-1]
            logging.info("nicos_oracle_domains_updater.py: test: %s, result: %s, result for domain %s" % (testn5,rest5,domrest5))
            cmnd="""
SELECT res,projname,name,pname,contname,tname,excess,nid,relid,tid,pid,projid from TESTRESULTS
natural join JOBSTAT natural join PROJECTS natural join PACKAGES where
jid = :jid_res and projname = :projn and fname = :testn5"""
            logging.info("nicos_oracle_domains_updater.py: cmnd: '%s' '%s'" % (cmnd,{'jid_res':jid_res,'projn':projn,'testn5':testn5}))
            cursor.execute(cmnd,{'jid_res':jid_res,'projn':projn,'testn5':testn5})
            result=cursor.fetchall()
            if len(result) != 1: logging.error("nicos_oracle_domains_updater.py: incorrect length of results: ",len(result)); sys.exit(1)
            row=result[-1]
            res8=row[0]
            name8=row[2]
            pname8=row[3]
            fname8=row[5]
            exc8=row[6]
            nid8=row[7]
            relid8=row[8]
            tid8=row[9]
            pid8=row[10] 
            projid8=row[11]
            logging.info("--- '%s' * '%s' * '%s' * '%s' * '%s' *** '%s' '%s' '%s' '%s' '%s'" % (res8,name8,pname8,fname8,exc8,nid8,relid8,tid8,pid8,projid8)) 
#
            iter+=1
            if iter == 1:
                cmnd="""delete from tdomresults where jid = :jid and projid = :projid"""
                logging.info("nicos_oracle_domains_updater.py: cleaning: '%s' '%s'" % (cmnd, { 'projid' : projid8, 'jid' : jid_res }))
                cursor.execute(cmnd, { 'projid' : projid8, 'jid' : jid_res }) 
                logging.info("nicos_oracle_domains_updater.py: tdomresults deleted rows count %s",cursor.rowcount)
#                                                                                                                            
#           updflag should be set for 1 when the result is from a regular (not calibration) CI job
            updflag=1
            cmnd="""
insert into tdomresults
(jid,nid,relid,did,tid,pid,projid,dres,tdstamp,updflag)
values (
:jid,:nid,:relid,:did,:tid,:pid,:projid,:dres,:tdstamp,:updflag
)"""
            dict_p={'jid':jid_res,'nid':nid8,'relid':relid8,'did':domid8,'tid':tid8,'pid':pid8,'projid':projid8,'dres':res8, 'tdstamp' : ts_now,'updflag' : updflag}
            logging.info("nicos_oracle_domains_updater.py: cmnd: '%s' '%s'" % (cmnd,dict_p))
            cursor.prepare(cmnd)
            cursor.setinputsizes(tdstamp=cx_Oracle.TIMESTAMP)
            cursor.execute(None, dict_p)
            
  cursor.close()
  connection.commit()
  connection.close()
