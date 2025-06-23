#!/usr/bin/env python2
import sys
import re,time,datetime
import string
import os, shutil

today = datetime.datetime.now()
today_f=datetime.datetime.strftime(today,'%Y-%m-%d %H:%M:%S')
ardoc_project_name=os.environ.get('ARDOC_PROJECT_NAME','')
ardoc_home=os.environ.get('ARDOC_HOME','')
ardoc_testlog=os.environ.get('ARDOC_TESTLOG','')
ardoc_relhome=os.environ.get('ARDOC_RELHOME','')
testdb=os.environ.get('ARDOC_TEST_DBFILE','')
if ardoc_home == '':
    print("ardoc_testdb_generator: Error: ARDOC_HOME is not defined")
    sys.exit(1)
if ardoc_testlog == '':
    print("ardoc_testdb_generator: Error: ARDOC_TESTLOG is not defined")
    sys.exit(1)
if ardoc_relhome == '':
    print("ardoc_testdb_generator: Error: ARDOC_RELHOME is not defined")
    sys.exit(1)
if testdb == '':
    print("ardoc_testdb_generator: Error: ARDOC_TEST_DBFILE is not defined")
    sys.exit(1)
testlogdir=os.path.dirname(ardoc_testlog)

print("ardoc_testdb_generator: Info: starting . . . ",today_f)
if not os.path.exists(testdb):
    print("ardoc_testdb_generator: Warning: test db file ",testdb," does not exist yet, creating empty one")
    dbfileres=open(testdb, 'w')
    dbfileres.write("")
    dbfileres.close()
else:
    print("ardoc_testdb_generator: Info: test db file found: ",testdb)

configtestlog=ardoc_relhome+os.sep+'TestLogs'+os.sep+'citest.config'
if not os.path.exists(configtestlog):
    print("ardoc_testdb_generator: Warning: ci test list ",configtestlog," does not exist")
    print("ardoc_testdb_generator: Info: information about ci tests is not available")
    sys.exit(0)
else:
    print("ardoc_testdb_generator: Info: ci test list found: ",configtestlog)

lines_db=[]
try:
    mf=open(configtestlog)
    lines_db = mf.readlines()
    mf.close()
except:
    lines_db=[]

dbfileres=open(testdb, 'a')
for x in lines_db:
    line1=x.strip()
    if len(re.sub(r'\s+','',line1)) == 0 : continue
    fill=re.split(r':',line1)
    testname1=fill[0].strip()
#    testname=re.sub(r'\s+','-',testname1)
    testname=re.split(r'\s+',testname1)[0]
    testpath='' 
    if len(fill) <= 1 : continue  
    testpath=(':'.join(fill[1:])).strip()
    timestamppath=re.sub(r'test.log',r'timestamp.log',testpath,1)
    exitcodepath=re.sub(r'test.log',r'exitcode.log',testpath,1)
    if ardoc_project_name != '' :
        if not re.match('^.*/'+ardoc_project_name+'/.*$',testpath) : continue
    xmlf=testname+'.xml'
    testname_ext="__"+testname+"__"+testname+'__m.sh'
    testprior="Release"
    testdir=testprior+'Tests/test/' 
    gen_testdir='N/A'
    suite='CI'
    testtime='100'
    container=testprior+'Tests'
    addr='nomail@cern.ch'  
    linew=xmlf+' '+testname_ext+' '+testdir+' '+gen_testdir+' '+suite+' '+testtime+' '+container+' '+addr
    print("ardoc_testdb_generator: Info: writing: ",linew )
    dbfileres.write(linew+'\n')
    if os.path.isfile(testpath):
        copypath=testlogdir+os.sep+container+'___'+testname+'__'+testname+'__m.loglog'
        print("ardoc_testdb_generator: Info: copying: ",testpath, copypath)
        shutil.copy2(testpath, copypath)
        if re.search('unit-test',testname,re.IGNORECASE):
            print("ardoc_testdb_generator: modifying file", copypath)
#            os.system(ardoc_home+os.sep+'unit_test_log_processor.pl '+copypath)
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


                                      
