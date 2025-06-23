#!/usr/bin/env python2
import sys
import re
import os, shutil, logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

testdir=[]
testfile=[]
def lister(currdir):
    for file in os.listdir(currdir):
      path = os.path.join(currdir, file)
      if os.path.isdir(path):
          for file1 in os.listdir(path):
#              path_tot=os.path.join(path, file1)
              if re.match('^CMakeLists.txt$', file1):
                  path1=path.replace(searchdirsep,'')
                  if path1.strip() != '':
                      testdir.append(path1)
#                  testfile.append(file1)
          lister(path)
if 'ARDOC_SOURCEHOME' in os.environ :
    sourcehome=os.environ['ARDOC_SOURCEHOME']
else :
    logging.error("ardoc_package_test_lists: Error: ARDOC_SOURCEHOME is not defined")
    sys.exit(1)
if 'ARDOC_RELHOME' in os.environ :
    relhome=os.environ['ARDOC_RELHOME']
else :
    logging.error("ardoc_package_test_lists: Error: ARDOC_RELHOME is not defined")
    sys.exit(1)
if 'ARDOC_ARCH' in os.environ :
    arch=os.environ['ARDOC_ARCH']
else :
    logging.error("ardoc_package_test_lists: Error: ARDOC_ARCH is not defined")
    sys.exit(1)
if 'ARDOC_DBFILE' in os.environ :
    dbfile=os.environ['ARDOC_DBFILE']
else :
    logging.error("ardoc_package_test_lists: Error: ARDOC_DBFILE is not defined")
    sys.exit(1)

searchdir=sourcehome
if not os.path.exists(searchdir): 
    logging.error("ardoc_package_test_lists: Error: search dir '%s' does not exist",searchdir)
    sys.exit(1)
#cmakelogdir=relhome+os.sep+'build.'+arch+os.sep+'BuildLogs'
cmakelogdir=relhome+os.sep+'BuildLogs'
if not os.path.exists(cmakelogdir):
    logging.error("ardoc_package_test_lists: Error: cmake log dir '%s' does not exist",cmakelogdir)
    sys.exit(1)

searchdirsep=searchdir+os.sep
lister(searchdir)
#print 'SSS :', testdir

dict_pack={}
for ddd in testdir:
    base=os.path.basename(ddd)
    dirn=os.path.dirname(ddd).strip()
    dict_pack[base]=dirn
pathdbfileres=dbfile
dbfileres=open(pathdbfileres, 'w')
for k,v in dict_pack.items():
    blogfile=cmakelogdir+os.sep+k+'.log' 
    vplusk=v+os.sep+k
    if len(re.sub(r'\s+','',v)) == 0 : vplusk=k
    if os.path.exists(blogfile):
       logging.info("ardoc_package_test_lists: found package and container '%s' '%s' and log '%s'",k,v,blogfile)
       dbfileres.write(vplusk+'  '+k+' nomail@cern.ch\n')
    else:
       logging.info("ardoc_package_test_lists: found package and container '%s' '%s' but NO LOGFILE '%s'",k,v,blogfile)
dbfileres.close()

logging.info("ardoc_package_test_lists: =====TEST FILES PROCESSING")
if 'ARDOC_TEST_DBFILE' in os.environ :
    testdbfile=os.environ['ARDOC_TEST_DBFILE']
else :
    logging.error("ardoc_package_test_lists: Error: ARDOC_TEST_DBFILE is not defined")
    sys.exit(1)
testlogdir=relhome+os.sep+'TestLogs'
if not os.path.exists(testlogdir):
    logging.warning("ardoc_package_test_lists: Warning: test log dir '%s' does not exist",testlogdir)
    sys.exit(0)
if 'ARDOC_TESTLOG' in os.environ :
    dirardoctestlog=os.path.dirname(os.environ['ARDOC_TESTLOG'])
    dirardoctestlog_tmp=dirardoctestlog+'_tmp'
#   CLEANUP ARDOC_TESTLOG with preservation of ardoc_ files (imporant when this scripts runs several times pere job) 
    if os.path.exists(dirardoctestlog_tmp): shutil.rmtree(dirardoctestlog_tmp)
#    print "shutil.move:",dirardoctestlog,dirardoctestlog_tmp
    shutil.move(dirardoctestlog,dirardoctestlog_tmp)
    os.mkdir(dirardoctestlog)
#    print "os.listdir: ",dirardoctestlog
#    os.listdir(dirardoctestlog)
    for ddd in os.listdir(dirardoctestlog_tmp):
#        print "CC  ",ddd
        path_ddd=dirardoctestlog_tmp+os.sep+ddd 
        if os.path.isfile(path_ddd):
          if re.search('ardoc_',ddd,re.IGNORECASE):
            ddd_new=ddd+'_prev'
            path_ddd_new=dirardoctestlog+os.sep+ddd_new 
#            print "shutil.copy2: ",path_ddd,path_ddd_new
            shutil.copy2(path_ddd,path_ddd_new)
else:
    dirardoctestlog=testlogdir
#   ARDOC_TESTLOG is requiered for test handling    
#   NO CLEANUP when testlogdir is in the release area
    logging.error("ardoc_package_test_lists: Error: ARDOC_TESTLOG is not defined")
    logging.warning("ardoc_package_test_lists: Warning: test lists will not be created")
    sys.exit(1)    

searchdirsep=searchdir+os.sep
lister(searchdir)
#print 'SSS :', testdir
dict_pack={}
for ddd in testdir:
    base=os.path.basename(ddd)
    dirn=os.path.dirname(ddd).strip()
    dict_pack[base]=dirn
pathtestdbfileres=testdbfile+'_res'
pathtestdbfilenores=testdbfile
testdbfileres=open(pathtestdbfileres, 'w')
testdbfilenores=open(pathtestdbfilenores, 'w')
for k,v in dict_pack.items():
    blogfile=testlogdir+os.sep+k+'.log'
    exitcodefile=testlogdir+os.sep+k+'.exitcode'
    if os.path.exists(blogfile):
       logging.info("ardoc_package_test_lists: found package and container '%s' '%s' and test log '%s'",k,v,blogfile)
       vplusk=v+os.sep+k
       if len(re.sub(r'\s+','',v)) == 0 : vplusk=k
       vplusk_mod=re.sub('/', '_', vplusk)
#COPY TEST logfiles to the dirarea of ARDOC_TESTLOG 
       ardoclogfile=dirardoctestlog+os.sep+vplusk_mod+'___'+k+'Conf__'+k+'Test__m.loglog'
       ardocexitcodefile=dirardoctestlog+os.sep+vplusk_mod+'___'+k+'Conf__'+k+'Test__m.exitcode'
       logging.info("ardoc_package_test_lists: copy '%s' -> '%s' AND '%s' -> '%s'",blogfile,ardoclogfile,exitcodefile,ardocexitcodefile)
       shutil.copy2(blogfile,ardoclogfile)
       if os.path.isfile(exitcodefile) : shutil.copy2(exitcodefile,ardocexitcodefile)
#       testdbfileres.write(vplusk+'  '+k+' nomail@cern.ch\n')
       tttname=k+"Conf.xml"
       tttname_new="__"+k+"Conf__"+k+"Test__m.sh"
       tdir=vplusk+os.sep+"test"+os.sep
       tdir_new="ARDOC_area"
       tsui="unit_tests"
       tlimit="2"
       tcont=vplusk+os.sep
       taut="nomail@cern.ch"
       testdbfileres.write(vplusk+'  '+k+' nomail@cern.ch\n')
       testdbfilenores.write(tttname+" "+tttname_new+" "+tdir+" "+tdir_new+" "+tsui+" "+tlimit+" "+tcont+" "+taut+'\n')
    else:
       logging.info("ardoc_package_test_lists: found package and container '%s' '%s' but NO TEST LOGFILE '%s'",k,v,blogfile)
testdbfileres.close()
testdbfilenores.close()

sys.exit(0)


                                      
