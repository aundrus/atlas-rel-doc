import re
import os
import sys
import getpass
import platform
import cx_Oracle
from pprint import pprint
import datetime
import getopt

oracle_schema=os.environ.get('ARDOC_ORACLE_SCHEMA','ATLAS_NICOS').strip()
cFN="/afs/cern.ch/atlas/software/dist/nightlies/cgumpert/TC/OW_crdntl"
lne=open(cFN,'r')
lne_res=lne.readline()
lne.close()
lnea=re.split(r'\s+',lne_res)          
accnt,pwf,clust=lnea[0:3]
connection = cx_Oracle.connect(accnt,pwf,clust)
connection.clientinfo = 'python 2.6 @ home'
connection.module = 'cx_Oracle test_ARDOC.py'
connection.action = 'TestArdocJob'
cursor = connection.cursor()
try:
    connection.ping()
except cx_Oracle.DatabaseError as exception:
    error, = exception.args
    print(("ardoc_oracle_hbeat.py: Database connection error: ", error.code, error.offset, error.message))
else:
    print("ardoc_oracle_hbeat.py: Connection is alive!")

cursor.execute("ALTER SESSION SET current_schema = "+oracle_schema)    

cmnd="""select projid,projname from projects"""
cursor.execute(cmnd)
result = cursor.fetchall()
for row in result:
     print(row[0],row[1])
cursor.close()
connection.commit()
connection.close()
