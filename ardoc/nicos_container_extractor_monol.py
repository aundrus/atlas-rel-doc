import sys
import re
import os
#dname=sys.argv[1]
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
if 'NICOS_SOURCEHOME' in os.environ :
    sourcehome=os.environ['NICOS_SOURCEHOME']
else :
    print("nicos_container_extractor: Error: NICOS_SOURCEHOME is not defined")
    sys.exit(1)
if 'NICOS_RELHOME' in os.environ :
    relhome=os.environ['NICOS_RELHOME']
else :
    print("nicos_container_extractor: Error: NICOS_RELHOME is not defined")
    sys.exit(1)
if 'NICOS_ARCH' in os.environ :
    arch=os.environ['NICOS_ARCH']
else :
    print("nicos_container_extractor: Error: NICOS_ARCH is not defined")
    sys.exit(1)
if 'NICOS_DBFILE' in os.environ :
    dbfile=os.environ['NICOS_DBFILE']
else :
    print("nicos_container_extractor: Error: NICOS_DBFILE is not defined")
    sys.exit(1)

#searchdir=relhome+os.sep+'aogt8'
searchdir=sourcehome
if not os.path.exists(searchdir): 
    print(("nicos_container_extractor: Error: search dir "+searchdir+" does not exist"))
    sys.exit(1)
#cmakelogdir=relhome+os.sep+'build.'+arch+os.sep+'BuildLogs'
cmakelogdir=relhome+os.sep+'BuildLogs'
if not os.path.exists(cmakelogdir):
    print(("nicos_container_extractor: Error: cmake log dir "+cmakelogdir+" does not exist"))
    sys.exit(1)

searchdirsep=searchdir+os.sep
lister(searchdir)
#print 'SSS :', testdir

dict_pack={}
for ddd in testdir:
    base=os.path.basename(ddd)
    dirn=os.path.dirname(ddd).strip()
    dict_pack[base]=dirn
pathdbfileres=dbfile+'_gen_res'
dbfileres=open(pathdbfileres, 'w')
for k,v in list(dict_pack.items()):
    blogfile=cmakelogdir+os.sep+k+'.log' 
    if os.path.exists(blogfile):
       print(("nicos_container_extractor: found package and container ",k,v," and log ",blogfile))
       dbfileres.write(v+os.sep+k+'  '+k+' nomail@cern.ch\n')
    else:
       print(("nicos_container_extractor: found package and container ",k,v," but NO  LOGFILE"))
dbfileres.close()
    
sys.exit(0)


                                      
