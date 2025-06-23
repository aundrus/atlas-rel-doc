minorWarningList=[]
minorWarningList.append({'string':'Warning: the last line','ignore':['checking for'],'correlator':['None'],'logtype':['ALL','EX'],'flags':0})
minorWarningList.append({'string':'Could.*NOT.*find','ignore':['None'],'correlator':['missing:'],'logtype':['CB','EX','CPACK'],'flags':0})
grandL=[minorWarningList]
optionV='ex'
for itemGrand in grandL:
    for item in itemGrand[:]:
        lt=[]
        lt=item.get('logtype',['ALL','EX'])
        lt_lower=[lt.lower() for lt in lt]
        print("LTTTT ",lt) 
        print("LLLLL ",lt_lower)
        if not optionV in lt_lower and 'all' not in lt_lower:
            print("not optionV")
        else:
            print("optionV")
