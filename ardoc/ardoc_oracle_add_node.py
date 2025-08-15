import re
import os
import sys
import getpass
import platform
import cx_Oracle
from pprint import pprint
import datetime
import getopt

try:
    optionslist, args = getopt.getopt(sys.argv[1:],'n:')
except getopt.error:
    print('''ardoc_oracle_hbeat.py: Error: You tried to use an unknown option or the
          argument for an option that requires it was missing.''')
    sys.exit(0)

name="NONE"
for a in optionslist[:]:
    if a[0] in ('-n') and a[1] != '': name=a[1]

if name == "":
    print(("ardoc_oracle_add_node.py: Error: node ",name," is not defined"))  
    sys.exit(1)

oracle_schema=os.environ.get('ARDOC_ORACLE_SCHEMA','ATLAS_NICOS').strip()
cFN="/afs/cern.ch/atlas/software/dist/nightlies/cgumpert/TC/OW_crdntl"
lne=open(cFN,'r')
lne_res=lne.readline()
lne.close()
lnea=re.split(r'\s+',lne_res)          
accnt,pwf,clust=lnea[0:3]
#print "XXXX",accnt,pwf,clust
connection = cx_Oracle.connect(accnt,pwf,clust)
#print ("Oracle DB version: " + connection.version)
#print ("Oracle client encoding: " + connection.encoding)
connection.clientinfo = 'python 2.6 @ home'
connection.module = 'cx_Oracle test_ARDOC.py'
connection.action = 'TestArdocJob'
cursor = connection.cursor()
try:
    connection.ping()
except cx_Oracle.DatabaseError as exception:
    error, = exception.args
    print(("ardoc_oracle_add_node.py: Database connection error: ", error.code, error.offset, error.message))

cursor.execute("ALTER SESSION SET current_schema = "+oracle_schema)    

hostnam_b=re.split(r'\.',name)[0]
hostnam_n=re.sub('[^0-9]','',hostnam_b)
hostnam_id=hostnam_n.lstrip('0')
print(("ardoc_oracle_add_node.py: Info: adding node ",name," id ",hostnam_id, "to table nodes"))
cmnd="select hid,hname from nodes"
cursor.execute(cmnd)
result = cursor.fetchall()
lresult=len(result)
sign_add=True
sign_dupl=False
if lresult > 0:
    for row in result:
        hid=row[0]; hname=row[1]
        if hid == hostnam_id and hname == name: sign_add=False
        if hid == hostnam_id and hname != name: 
            sign_dupl=True
            print(("ardoc_oracle_add_node.py: Error: id ",hostnam_id," is assigned to another node ",hname))
        if hid != hostnam_id and hname == name: 
            sign_dupl=True
            print(("ardoc_oracle_add_node.py: Error: node ",hostnam_id," already exists in the table, with different id ",hid))
if sign_dupl: sys.exit(1)
if not sign_add:
    print(("ardoc_oracle_add_node.py: Warning: node ",hostnam_id," already exists in the table,  id ",hid))
#
cmnd="""
insert into nodes (hid,hname,hstat) values 
( :hid, :hname, 'OK')
"""
cursor.execute(cmnd, {'hid' : hostnam_id, 'hname' : name})
print(("ardoc_oracle_add_node.py: Info: ADDED node ",name," id ",hostnam_id, "to table nodes"))

cursor.close()
connection.commit()
connection.close()
