import re
import os,getopt
import sys
import logging
import datetime
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

def append_head_tail_lines_large_file(source_file, destination_file, nHeadLines, nTailLines):
    try:
        head_lines = []
        tail_lines = []
        line_count = 0

        # Read the first nHeadLines
        with open(source_file, 'r', errors='replace') as src:
            for _ in range(nHeadLines):
                line = src.readline()
                if not line:
                    break
                line_count += 1
                head_lines.append(line.rstrip('\n'))
        noTail=False
#        print(line_count, nHeadLines)
        if line_count < nHeadLines:
            noTail=True

        nTailLinesCorr=nTailLines
        fullTail=False
        if noTail:
            logging.info("ardoc_headtail.py: number of input lines '%s' is less or equal to the head count. No truncation", line_count)
        else:
            # Check if iFile has lines
            nHeadPlusTail=nHeadLines + nTailLines
            with open(source_file, 'r', errors='replace') as src:
                for icoun, _ in enumerate(src, 1):
                    if icoun > nHeadPlusTail:
                        fullTail=True
                        break
                else:
                    logging.info("ardoc_headtail.py: small number of input lines '%s' is less than head and tail count", icoun)
            if not fullTail:
                nTailLinesCorr=icoun - nHeadLines
                if nTailLinesCorr <= 0 or nTailLinesCorr > nTailLines:
                    logging.warning("ardoc_headtail.py: corrected tail number of lines '%s' is out of range 0 - '%s'" % (nTailLinesCorr,nTailLines))
                    logging.warning("ardoc_headtail.py: setting tail line number to 1")
                    nTailLinesCorr=1
            else:
                logging.info("ardoc_headtail.py: number of input lines is at least '%s' which is greater than head and tail count '%s'" % (icoun,nHeadPlusTail))
                
            # Read the last nTailLinesCorr
            with open(source_file, 'rb') as src:
                src.seek(0, 2)  # Move to the end of the file
                position = src.tell()
                buffer = b''
                lines = []

                while position > 0 and len(lines) < nTailLinesCorr:
                    position -= 1
                    src.seek(position)
                    char = src.read(1)

                    if char == b'\n':
                        if buffer:
                            lines.append(buffer[::-1].decode(errors='replace'))
                            buffer = b''
                    else:
                        buffer += char

                if buffer:
                    lines.append(buffer[::-1].decode(errors='replace'))

                tail_lines = lines[::-1][:nTailLinesCorr]

        # Append both head and tail lines to the destination file
#        print("===========",noTail,fullTail)
        with open(destination_file, 'a', errors='replace') as dest:
            if not noTail and fullTail:
                dest.write('===================================================\n')
                dest.write('Truncated content of the file '+os.path.basename(source_file)+': first '+str(nHeadLines)+' and last '+str(nTailLinesCorr)+' lines\n')
                dest.write('This file is generated to serve as the log file for the pseudo package CMake_BuildLogTail, intended to be displayed in the build results views\n') 
                dest.write('Reference: JIRA ticket ATLINFR-5694\n')
                dest.write('===================================================\n')
            else:
                dest.write('===================================================\n')
                dest.write('Content of the file '+os.path.basename(source_file)+'\n')
                dest.write('This file is generated to serve as the log file for the pseudo package CMake_BuildLogTail, intended to be displayed in the build results views\n')
                dest.write('Reference: JIRA ticket ATLINFR-5694\n')
                dest.write('===================================================\n')
            for line in head_lines:
                dest.write(line + '\n')
            if not noTail and fullTail:    
                dest.write('...................................................\n')
                dest.write('...................................................\n')
                dest.write('THE CENTRAL PORTION OF THE CONTENT HAS BEEN SKIPPED\n')
                dest.write('...................................................\n')
                dest.write('...................................................\n')
            for line in tail_lines:
                dest.write(line + '\n')
            dest.write('This file is generated to serve as the log file for the pseudo package CMake_BuildLogTail, intended to be displayed in the build results views\n')    

        logging.info("ardoc_headtail.py: first '%s' and last '%s' lines were appended successfully" % (nHeadLines, nTailLinesCorr))

    except FileNotFoundError:
        logging.error("ardoc_headtail.py: file not found. Please check the file paths")
    except Exception as e:
        logging.error("ardoc_headtail.py: file writing error occurred: '%s'", e)

try:
    optionslist, args = getopt.getopt(sys.argv[1:],'i:o:h:t:',['input=','output=','head=','tail='])
except getopt.error:
    logging.warning('''ardoc_oracle_test_results: Error: You tried to use an unknown option or the
    argument for an option that requires it was missing.''')
    sys.exit(2)

if len(optionslist) == 0:
    logging.error('''Error: ardoc_send_mail.py requires coomand line options  
                   Try "ardoc_send_mail.py -h" for more information.''')
    sys.exit(2)
defaultHeadLines=20    
defaultTailLines=500
headLines=""
tailLines=""
iFile=""
oFile=""
    
for a in optionslist[:]:
    if ( a[0] == '--input' or a[0] == '-i' ) and a[1] != '':
        iFile=a[1]
    if ( a[0] == '--output' or a[0] == '-o' ) and a[1] != '':
        oFile=a[1]
    if ( a[0] == '--head' or a[0] == '-h' ) and a[1] != '':
        headLines=a[1]
    if ( a[0] == '--tail' or a[0] == '-t' ) and a[1] != '':
        tailLines=a[1]

if headLines == '' :
    headLines=int(defaultHeadLines)
    logging.info("ardoc_headtail.py: number of head lines forwared to output was not specified, set to default: '%s'",headLines)
else:
    headLines=int(headLines)
    logging.info("ardoc_headtail.py: number of head lines forwared to output was specified in command line: '%s'",headLines)

if tailLines ==	'' :
    tailLines=int(defaultTailLines)
    logging.info("ardoc_headtail.py: number of tail lines forwared to output was not specified, set to default: '%s'",tailLines)
else:
    tailLines=int(tailLines)
    logging.info("ardoc_headtail.py: number of tail lines forwared to output was specified in command line: '%s'",tailLines)

logging.info("ardoc_headtail.py: going to copy '%s' head and '%s' tail lines from '%s' to '%s'" % (headLines,tailLines,iFile,oFile))
if os.path.exists(oFile):
    if os.path.isfile(oFile):
        logging.info("ardoc_headtail.py: old destination file '%s' exists, deleting",oFile)
        os.remove(oFile)
    else:
        logging.error("ardoc_headtail.py: fatal error: old destination path '%s' exists and it is not a file",oFile)
        sys.exit(1)

append_head_tail_lines_large_file(iFile,oFile,headLines,tailLines)
