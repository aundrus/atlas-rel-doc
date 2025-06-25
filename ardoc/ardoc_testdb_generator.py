import sys
import re,time,datetime
import os, shutil

today = datetime.datetime.now()
today_f=datetime.datetime.strftime(today,'%Y-%m-%d %H:%M:%S')
if 'ARDOC_TESTLOG' in os.environ :
    testlog=os.environ['ARDOC_TESTLOG']
    testlogdir=os.path.dirname(testlog)
else :
    print("ardoc_testdb_generator: Error: ARDOC_TESTLOG is not defined")
    sys.exit(1)
if 'ARDOC_HOME' in os.environ :
    ardoc_home=os.environ['ARDOC_HOME']
else :
    print("ardoc_testdb_generator: Error: ARDOC_HOME is not defined")
    sys.exit(1)

print("ardoc_testdb_generator: Info: starting . . . ",today_f)

if 'ARDOC_TEST_DBFILE_GEN' in os.environ :
    testdb_gen=os.environ['ARDOC_TEST_DBFILE_GEN']
else :
    print("ardoc_testdb_generator: Error: ARDOC_TEST_DBFILE_GEN is not defined")
    sys.exit(1)
dbfileres=open(testdb_gen, 'w')
dbfileres.write("")
dbfileres.close()
if 'MR_PATH_TO_CONFTESTLOG' in os.environ :
    configtestlog=os.environ['MR_PATH_TO_CONFTESTLOG']
else :
    print("ardoc_testdb_generator: Warning: MR_PATH_TO_CONFTESTLOG is not defined")
    sys.exit(0)
ardoc_project_name=os.environ.get('ARDOC_PROJECT_NAME','')

if not os.path.isfile(configtestlog):
    print("ardoc_testdb_generator: Warning: CONF TEST LOG",configtestlog, "does not exist")
lines_db=[]
try:
    mf=open(configtestlog)
    lines_db = mf.readlines()
    mf.close()
except:
    lines_db=[]

dbfileres=open(testdb_gen, 'w')
for x in lines_db:
    line1=x.strip()
    if len(re.sub(r'\s+','',line1)) == 0 : continue
    fill=re.split(r':',line1)
    testname1=fill[0].strip()
    testname=re.sub(r'\s+','-',testname1) 
    testpath='' 
    if len(fill) <= 1 : continue 
    testpath_iii=':'.join(fill[1:]) 
    testpath=testpath_iii.strip()
    timestamppath=re.sub(r'test.log',r'timestamp.log',testpath,1)
    exitcodepath=re.sub(r'test.log',r'exitcode.log',testpath,1)
    if ardoc_project_name != '' :
        if not re.match('^.*/'+ardoc_project_name+'/.*$',testpath) : continue
    xmlf=testname+'.xml'
    testname_ext="__"+testname+"__"+testname+'__m.sh'
    testprior="Release"
    if 'SOURCE_DIR' in os.environ:
      source_dir=os.environ['SOURCE_DIR']
      optional_dir=source_dir+os.sep+'OptionalTests'
      print("ardoc_testdb_generator: Info: optional test dir : ",optional_dir) 
      if os.path.isdir(optional_dir):
        print("ardoc_testdb_generator: Info: optional test dir : ",optional_dir)
        if not re.match('.*required.*$',testname):
          if re.match('HelloWorld.*$',testname): testprior="Optional"
          if re.match('Trigger_MT.*$',testname): testprior="Optional"
          if re.match('Tier0Tests.*$',testname): testprior="Optional" 
          if re.match('SimulationTier.*$',testname): testprior="Optional"
          if re.match('Overlay.*$',testname): testprior="Optional"
          if re.match('.*optional.*$',testname): testprior="Optional" 
        print("ardoc_testdb_generator: Info: optional test dir exists, test name ",testname,", priority ",testprior) 
    testdir=testprior+'Tests/test/' 
    gen_testdir='N/A'
    suite='CI'
    testtime='100'
    container=testprior+'Tests'
    addr='nomail@cern.ch'  
    linew=xmlf+' '+testname_ext+' '+testdir+' '+gen_testdir+' '+suite+' '+testtime+' '+container+' '+addr
    print("ardoc_testdb_generator: Info: writing: ",linew) 
    dbfileres.write(linew+'\n')
    if os.path.isfile(testpath):
        copypath=testlogdir+os.sep+container+'___'+testname+'__'+testname+'__m.loglog'
        print("ardoc_testdb_generator: Info: copying: ",testpath, copypath)
        shutil.copy2(testpath, copypath)
        if re.search('unit-test',testname,re.IGNORECASE):
            print("ardoc_testdb_generator: modifying file", copypath)
            os.system(ardoc_home+os.sep+'unit_test_log_processor.pl '+copypath)
    else:
        print("ardoc_testdb_generator: Warning: test log does not exist: ",testpath) 
    if os.path.isfile(timestamppath):
        copypath=testlogdir+os.sep+container+'___'+testname+'__'+testname+'__m.timestamp'
        print("ardoc_testdb_generator: Info: copying timestamp: ",timestamppath, copypath)
        shutil.copy2(timestamppath, copypath)
    else:
        print("ardoc_testdb_generator: Warning: timestamp does not exist: ",timestamppath)
    if os.path.isfile(exitcodepath):
        copypath=testlogdir+os.sep+container+'___'+testname+'__'+testname+'__m.exitcode'
        print("ardoc_testdb_generator: Info: copying exitcode: ",exitcodepath, copypath)
        shutil.copy2(exitcodepath, copypath)
    else:
        print("ardoc_testdb_generator: Warning: exitcode does not exist: ",exitcodepath)
dbfileres.close()
    
sys.exit(0)


                                      
