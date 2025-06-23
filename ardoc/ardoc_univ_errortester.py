import re, sys, os, shutil
from pprint import pprint
import getopt, logging

def help_message():
    ''' help_message function '''
    logging.warning('''ardoc_univ_errortester.py :

            Options: -h, --help             --> displays this help message
                     -f, --file <filename>  --> file name to analyze for errors
                     -o, --option <option>  --> type of logfile (e.g. externals, config)''')
    sys.exit(0)

def write_header(fhandle,logtypedesc):
    section="""<html>
<style>
body {
  color: black;
  link: navy;
  vlink: maroon;
  alink: tomato;
  background: floralwhite;
  font-family: 'Lucida Console', 'Courier New', Courier, monospace;
  font-size: 10pt;
}
td.aid {
  background: #6600CC;
  color: orangered;
  text-align: center;
}
td.ttl {
  color: #6600CC;
  text-align: center;
}
.prblm {background-color: orange;}
#hdr0 {
  font-family: Verdana, Arial, Helvetica, sans-serif;
  font-size: 14pt;
}
#hdr {
background-color: #FFCCFF;
  font-family:'Times New Roman',Garamond, Georgia, serif;
  font-size: 14pt;
}
#hdr1 {
background-color: #CFECEC;
  font-family: Verdana, Arial, Helvetica, sans-serif;
  font-size: 10pt;
}
#end {
background-color: #CFECEC;
  font-family: Verdana, Arial, Helvetica, sans-serif; 
  font-size: 10pt;
}
</style>

<head><title>
%s logfile
</title>
</head>

<body class=body marginwidth=\"0\" marginheight=\"0\" topmargin=\"0\" leftmargin=\"0\">
""" % logtypedesc
    fhandle.write(section)

def write_footer(fhandle):
    section="""<div id="end">END OF LOGFILE</div>
</body></html>
"""
    fhandle.write(section)

def write_page_header(fhandle):
    table="""<DIV id=hdr0>
<table bordercolor=\"#6600CC\" border=10 cellpadding=5 cellspacing=0 width=\"100%%\">
<tr><td class=aid width=20%% align=center valign=baseline>
<H1>ARDOC</H1>
</td>
<td class=ttl>
<EM><B><BIG>%s logfile</BIG></EM></B>
</td></tr>
<tr><td class=aid>
version %s
</td>
""" % (optionD, ARDOC_VERSION)

    error_statement=""
    lenRLN=len(recordLineNumber)
    lenCD=len(counterDesc)
    if lenRLN == 0:
        error_statement_top="""<td class=ttl><EM><B>No problems found</EM></B>
</td></tr></table>                                                                                                       </DIV>
"""
    else:
        err='';wrn='';mwrn=''
        for lpb in recordLevel:
            if lpb == 0: err="Error"
            if lpb == 1: wrn="Warning"
            if lpb == 2: mwrn="Minor Warning" 
        estring=err+","+wrn+","+mwrn
        estring=estring.strip(',')
        estring=re.sub(r',+',',',estring)
        error_statement_top="""<td class=ttl><EM><B>Problem(s) of type(s) %s found</EM></B>
</td></tr></table>
</DIV>                                                                                                                   
""" % estring
    error_statement="<DIV id=hdr>\n"
    icn=-1
    for lnpb in recordLineNumber:
        icn+=1
        pb_string=recordString[icn]
        pb_level=recordLevel[icn]
        if pb_level >=0 and pb_level < lenCD:
            pb_desc=counterDesc[pb_level]
        else:
            pb_desc="problem"
        pbitem="&nbsp;<BR>&nbsp;&nbsp;&nbsp;&nbsp;<a href=\"#pb%s\">%s pattern <B>\"%s\"</B> found in line %s</a>\n" % (lnpb,pb_desc,pb_string,lnpb)
        error_statement+=pbitem
    error_statement+="&nbsp;<BR>&nbsp;&nbsp;&nbsp;&nbsp;<a href=\"#end\">Link to the last line</A> <BR>\n"
    error_statement+="&nbsp;<BR>\n"
    error_statement+="</B></DIV>\n"
    fhandle.write(table)
    fhandle.write(error_statement_top)
    fhandle.write(error_statement)

def write_truncation_statement(fhandle,line_N1,line_N2): 
    message="""<DIV ID=hdr>................................................................
.....LINES TRUNCATED BETWEEN #%s and #%s .....
................................................................
</DIV>
""" % (line_N1,line_N2)
    fhandle.write(message) 

def write_line(fhandle):
    x=re.sub('<','&lt;',x1); x=re.sub('>','&gt;',x)
    safe_string = x.encode('utf-8', errors='replace').decode('utf-8')
    if iline in recordLineNumber:
        safe_string = """<div id=\"pb%s\" class=\"prblm\">%s</div>\n""" % (iline, safe_string)
    fhandle.write(safe_string)

ARDOC_HOME=os.environ.get('ARDOC_HOME','')
ARDOC_WORK_AREA=os.environ.get('ARDOC_WORK_AREA','')
ARDOC_LOGDIR=os.environ.get('ARDOC_LOGDIR','')
ARDOC_WEBDIR=os.environ.get('ARDOC_WEBDIR','')
ARDOC_WEB_HOME=os.environ.get('ARDOC_WEB_HOME','')
ARDOC_PROJECT_RELNAME=os.environ.get('ARDOC_PROJECT_RELNAME','')
ARDOC_VERSION=os.environ.get('ARDOC_VERSION','python3')
#ARDOC_LOGDIR=os.path.dirname(ARDOC_LOG)
#ARDOC_LOGDIRBASE=os.path.basename(ARDOC_LOGDIR)

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

try:
    optionslist, args = getopt.getopt(sys.argv[1:],'hf:o:',['file=','help','option='])
except getopt.error:
    logging.warning('''Error: You tried to use an unknown option or the
                        argument for an option that requires it was missing.
                        Try ardoc_univ_errortester.py for more information.''')
    sys.exit(2)

if len(optionslist) == 0:
    logging.warning('''Error: ardoc_univ_errortester.py requires command line options
                        Try "nicos_ps_handler.py -h" for more information.''')
    sys.exit(2)

option=""
filename=""
for a in optionslist[:]:
  if a[0] == '-h' or a[0] == '--help' :
    help_message()
  if ( a[0] == '--file' or a[0] == '-f' ) and a[1] != '':
    filename=a[1]
  if ( a[0] == '--option' or a[0] == '-o' ) and a[1] != '':
    option=a[1]
if option == "":
    logging.error("ardoc_univ_errortester.py: Error: option is not provided")
    sys.exit(1)
if filename == "":
    logging.error("ardoc_univ_errortester.py: Error: filename is not provided")
    sys.exit(1)                                     
if ( not os.path.isfile(filename) ):
    logging.error("ardoc_univ_errortester.py: Error: file does not exist %s" % filename)
    sys.exit(1)
#maxRecords is the maximum number of error, warning, minor warning trigger level
#Once maxRecords is reached further search for particular category is discontinued
#Once maxRecords is reached for errors then all searches are stopped
maxRecords=5
#maxLines is approximate maximum number of lines written in html version of a log file (other lines are truncated)
#Sections with problem triggers are always written ( 20 lines above, 20 lines below)
#Last (maxLines - topmaxLines) lines are also written
maxLines=1000
topmaxLines=maxLines-150

optionDict={'conf':'CB','config':'CB','configbuild':'CB','cb':'CB'}
optionDict.update({'ext':'EX','ex':'EX','externals':'EX'})
optionDict.update({'co':'CO','checkout':'CO','clone':'CO'})
optionDict.update({'im':'IM','image':'IM'})
optionDict.update({'cp':'CPACK','cpack':'CPACK'})
#
optionDesc={'cb':'cmake configuration', 'ex':'externals build'}
optionDesc.update({'co':'code checkout', 'im':'image build', 'cpack':'cpack'})
optionV=""; optionD=""
if option.lower() in optionDict:
    optionV=optionDict[option.lower()].lower()
    optionD=optionDesc.get(optionV,'build step '+optionV)
else:
    logging.error("ardoc_univ_errortester.py: Error: Unknown step provided: '%s'" % option)
    sys.exit(1)
logging.warning("ardoc_univ_errortester.py: option: '%s' - '%s'",optionV,optionD)
# Larger size limits for external htmls generation
if optionV == 'ex':
    maxRecords=9
    maxLines=100000
    topmaxLines=maxLines-150
#
successList=[]
successList.append({'string':'.*\s.*','ignore':['None'],'correlator':['None'],'logtype':['ALL']})
#
errorList=[]
errorList.append({'string':'can not','ignore':['ERRORS: 0'],'correlator':['None'],'logtype':['ALL'],'flags':0})
errorList.append({'string':'permission denied','ignore':['None'],'correlator':['None'],'logtype':['ALL'],'flags':re.IGNORECASE})
errorList.append({'string':'Disk quota exceeded','ignore':['None'],'correlator':['None'],'logtype':['ALL'],'flags':re.IGNORECASE})
errorList.append({'string':'traceback \(most recent','ignore':['None'],'correlator':['None'],'logtype':['ALL'],'flags':re.IGNORECASE})
errorList.append({'string':'CMake Error','ignore':['None'],'correlator':['None'],'logtype':['CB','EX','CPACK'],'flags':0})
errorList.append({'string':'cmake: command not found','ignore':['None'],'correlator':['None'],'logtype':['CB','EX','CPACK'],'flags':re.IGNORECASE})
errorList.append({'string':': error:','ignore':['collect2'],'correlator':['None'],'logtype':['CB','CPACK'],'flags':0})
errorList.append({'string':': error:','ignore':['collect2', 'maybe-uninitialized'],'correlator':['None'],'logtype':['EX'],'flags':0})
errorList.append({'string':'No rule to make target','ignore':['None'],'correlator':['None'],'logtype':['EX','CPACK'],'flags':0})
errorList.append({'string':'no makefile found','ignore':['None'],'correlator':['make:'],'logtype':['EX'],'flags':re.IGNORECASE})
errorList.append({'string':'Target.*not\sremade\sbecause\sof\serrors.*','ignore':['None'],'correlator':['None'],'logtype':['EX'],'flags':0})
errorList.append({'string':'ardoc_copy: problem','ignore':['None'],'correlator':['None'],'logtype':['CB','IM'],'flags':re.IGNORECASE})
#
errorList.append({'string':'Error: ','ignore':['None'],'correlator':['None'],'logtype':['CB','IM'],'flags':0})
# The next pattern is specifically for Ninja builds
errorList.append({'string':'^FAILED:','ignore':['None'],'correlator':['None'],'logtype':['EX'],'flags':0})
#
warningList=[]
warningList.append({'string':'package not found','ignore':['None'],'correlator':['None'],'logtype':['ALL'],'flags':re.IGNORECASE})
warningList.append({'string':'logfile not found','ignore':['None'],'correlator':['None'],'logtype':['ALL'],'flags':re.IGNORECASE})
warningList.append({'string':'Warning:.*logfile.*not\savailable','ignore':['None'],'correlator':['None'],'logtype':['ALL'],'flags':re.IGNORECASE})
warningList.append({'string':'CMake Warning','ignore':['None'],'correlator':['None'],'logtype':['CB','EX','CPACK'],'flags':0})
warningList.append({'string':'Call Stack','ignore':['None'],'correlator':['None'],'logtype':['CPACK'],'flags':0})
warningList.append({'string':'CMake Deprecation Warning','ignore':['None'],'correlator':['None'],'logtype':['CB','EX'],'flags':0})
warningList.append({'string':'> Warning:','ignore':['None'],'correlator':['None'],'logtype':['CB','EX','CPACK'],'flags':0})
minorWarningList=[]
minorWarningList.append({'string':'Warning: the last line','ignore':['checking for'],'correlator':['None'],'logtype':['ALL'],'flags':0})
minorWarningList.append({'string':'Could.*NOT.*find','ignore':['None'],'correlator':['missing:'],'logtype':['CB','EX','CPACK'],'flags':0})
#minorWarningList.append({'string':'#pragma message:','ignore':['None'],'correlator':['None'],'logtype':['EX'],'flags':0})
#
#minorWarningList.append({'string':'not available','ignore':['checking for'],'correlator':['file'],'logtype':['ALL'],'flags':0})
grandL=[successList,errorList,warningList,minorWarningList]
ig=0
for itemGrand in grandL:  
    ig+=1 
    for item in itemGrand[:]:
        lt=item.get('logtype',['ALL'])
        lt_lower=[lt.lower() for lt in lt]      
        if not optionV in lt_lower and 'all' not in lt_lower:
            itemGrand.remove(item)
##            print "REMOVED", item
##            print "AAAA",itemGrand
##            print "BBBB",grandL[2]
        else:
            flgs=item.get('flags',0)
##
            if ig == 1: strng=item.get('string','.*\s.*')
            else: strng=item.get('string','CVBFGB') 
            try: cmpl=re.compile(strng,flgs); is_valid=True 
            except Exception as e:
                is_valid=False
                logging.critical("ardoc_univ_errortester.py: error when compiling '%s' with flags '%s': '%s'" % (strng, flgs, e))
                itemGrand.remove(item)
##                print "CCCC",itemGrand
##                print "DDDD",grandL[2]
##                         
            strngIgnoreL=item.get('ignore','CVBFGB')
            cmplIgnoreL=[]
            for ltem in strngIgnoreL:
                try: cmplIgnore=re.compile(ltem,flgs)
                except: cmplIgnore=re.compile('CVBFGB',flgs)
                cmplIgnoreL.append(cmplIgnore)
            strngCorrelL=item.get('correlator','.*')
            cmplCorrelL=[]
            for ltem in strngCorrelL:
                strngCorrel=item.get('correlator','.*')
                try: cmplCorrel=re.compile(strngCorrel,flgs)
                except: cmplCorrel=re.compile('.*',flgs)
                cmplCorrelL.append(cmplCorrel)
            if is_valid:
                item['compiled']=cmpl 
                item['compiledIgnoreL']=cmplIgnoreL
                item['compiledCorrelL']=cmplCorrelL

#logging.debug("ardoc_univ_errortester.py:list of pattern dictionaries: '%s'" % (grandL))  
                
#lines_db=[]
#try:
#    mf=open(filename)
#    lines_db = mf.readlines()
#    mf.close()
#except:
#    lines_db=[]

successSign=False
counter=[0,0,0]
counterDesc=['Error','Warning','Minor warning']
counterStop=[False, False, False]
recordLineNumber=[]
recordLevel=[]
recordString=[]
recordCorrelString=[]
#recordIgnoreString=[]
iline=0
#16777216
with open(filename,"r",errors='surrogateescape') as lines:
  for x in lines:
    iline+=1
    line1=x.strip()
    if len(re.sub(r'\s+','',line1)) == 0 : continue
    ig=0
    for itemGrand in grandL:
        igm=ig-1
        ig+=1
#       Just one successful match to success pattern is sufficient, further checks against success patterns are bypassed
        if successSign :
            if ig == 1: continue
            else:
                if counter[igm] >=  maxRecords: continue
                if counter[2] >=  maxRecords: continue 
        for d in itemGrand:
            if d['compiled'].search(line1):
#                print "LLLL",line1,d['string'],iline,ig
                correlFound=True; ignoreNotFound=True
                for ltem in d['compiledCorrelL']:
                    if not ltem.search(line1): correlFound=False
                for ltem in d['compiledIgnoreL']:
                    if ltem.search(line1): ignoreNotFound=False
                if correlFound and ignoreNotFound:
                    correlString=" *AND* ".join(d['correlator'])
                    if ig == 1: successSign=True
                    else:
                        counter[igm]+=1
                        recordLevel.append(igm)
                        recordLineNumber.append(iline) 
                        recordString.append(d['string'])
                        recordCorrelString.append(correlString) 
## recordLevel: 0 - error, 1 - warning, 2 - minor warning
lineTotal=iline                           
lineIntervals=[[1, lineTotal]]
bottomLines=maxLines-topmaxLines
firstBottomLine=lineTotal-bottomLines+1
linesPrintedAroundProblemSignature=20

if lineTotal > maxLines + 50:
    lineIntervals=[[1,topmaxLines]]
    icn=-1
    for lnpb in recordLineNumber:
        icn+=1
        pb_level=recordLevel[icn]
        ln_1=max(0,lnpb-linesPrintedAroundProblemSignature)
        ln_2=min(lnpb+linesPrintedAroundProblemSignature,lineTotal)
        if ln_2 > topmaxLines and ln_1 < firstBottomLine :  
            lineIntervals.append([ln_1,ln_2])
    lineIntervals.append([firstBottomLine,lineTotal])
len_l=len(lineIntervals)
icn=-1
skip=False
#print "LLL111",lineIntervals
for i_lineIntervals in lineIntervals[:]:
    icn+=1
    if icn >= len(lineIntervals) - 1 : break
    if skip:
        skip=False
        continue
    for icnplus in range(icn+1,len(lineIntervals)):
       if i_lineIntervals[1] >= lineIntervals[icnplus][0]:
           if i_lineIntervals[1] <= lineIntervals[icnplus][1]:
                lineIntervals[icn][1] = lineIntervals[icnplus][1]      
           lineIntervals[icnplus] = [0,0]
           skip=True 
while [0,0] in lineIntervals: lineIntervals.remove([0,0])

logging.warning("ardoc_univ_errortester.py: total lines: '%s'" % (lineTotal))
logging.warning("ardoc_univ_errortester.py: line intervals written to html: '%s'" % (lineIntervals))
logging.warning("ardoc_univ_errortester.py: problem counter: '%s'" % (counter))
logging.warning("ardoc_univ_errortester.py: record level: '%s'" % (recordLevel))
logging.warning("ardoc_univ_errortester.py: record line number: '%s'" % (recordLineNumber))
logging.warning("ardoc_univ_errortester.py: problem string: '%s'" % (recordString))
logging.warning("ardoc_univ_errortester.py: problem correl string: '%s'" % (recordCorrelString))
logging.warning("ardoc_univ_errortester.py: line intervals printed: '%s'" % (lineIntervals))

exit_mess=""
if not successSign:
    pttrn_string=""
    for dctrn in successList:
        if pttrn_string == "":
            pttrn_string=pttrn_string+dctrn['string']
        else:
            pttrn_string=pttrn_string+" =OR= "+dctrn['string'] 
    exit_mess="G Required success pattern not found: %s" % pttrn_string 
else:
    icn=-1
    err_l=[];wrn_l=[];mwrn_l=[]
    err_s='';wrn_s='';mwrn_s=''
    for pbl in recordLevel:
        icn+=1
        pbs=recordString[icn]
        if pbl == 0: 
            if pbs not in err_l: err_l.append(pbs)
        if pbl == 1:
            if pbs not in wrn_l: wrn_l.append(pbs)
        if pbl == 2:
            if pbs not in mwrn_l: mwrn_l.append(pbs)    
        err_s=" =AND= ".join(err_l)
        wrn_s=" =AND= ".join(wrn_l)
        mwrn_s=" =AND= ".join(mwrn_l)
    if err_s != '':
        exit_mess="G error pattern found: %s" % err_s
    elif wrn_s != '':     
        exit_mess="W warning pattern found: %s" % wrn_s
    elif mwrn_s != '':
        exit_mess="M minior warning pattern found: %s" % mwrn_s
if exit_mess == "" :
    logging.warning("ardoc_univ_errortester.py: no problems found in logfile and exit message is empty")
else:
    logging.warning("ardoc_univ_errortester.py: exit message : '%s'" % (exit_mess))

filebase=os.path.basename(filename)
filedir=os.path.dirname(filename)
filebase_root=os.path.splitext(filebase)[0]
filehtmlbase=filebase_root+'.html'
if not re.match('^ardoc.*$',filehtmlbase): filehtmlbase='ardoc_'+filehtmlbase
filehtml=filedir+os.sep+filehtmlbase
if filedir == '': filehtml=filehtmlbase

filehtml_handle=open(filehtml, 'w')
write_header(filehtml_handle,optionD)
write_page_header(filehtml_handle)
filehtml_handle.write('<P><PRE>\n')

iline=0
interval=0
l_00=lineIntervals[interval][0]
l_10=lineIntervals[interval][1]
len_l=len(lineIntervals)
with open(filename,"r",errors='surrogateescape') as lines:
  for x1 in lines:
    iline+=1
    if iline < l_00 : continue
#    print "---",iline,interval,l_00,l_10,len_l
    
    if iline <= l_10 :
        write_line(filehtml_handle) 
    else:
        if len_l > interval + 1: 
#            print "+++",lineIntervals[interval+1][0]
            if iline < lineIntervals[interval+1][0]:
                write_truncation_statement(filehtml_handle,lineIntervals[interval][1],lineIntervals[interval+1][0])
                interval+=1
                l_00=lineIntervals[interval][0]
                l_10=lineIntervals[interval][1]
            else:
                write_line(filehtml_handle)
        else:
            break

filehtml_handle.write('</PRE>\n')
write_footer(filehtml_handle)
filehtml_handle.close()

print(exit_mess)

#copy generated htmllog to ${ARDOC_WEBDIR} 
destin_dir=ARDOC_WEBDIR+os.sep+"ARDOC_Log_"+ARDOC_PROJECT_RELNAME
if not os.path.exists(destin_dir):
    logging.warning("ardoc_univ_errortester.py: destination directory: '%s' does not exist, creating" % (destin_dir))
    os.mkdir(destin_dir)
copyhtml=destin_dir+os.sep+filehtmlbase
logging.warning("ardoc_univ_errortester.py: copying: '%s' to '%s'", filehtml, copyhtml)
shutil.copy2(filehtml, copyhtml)

