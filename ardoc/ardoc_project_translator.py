import sys

class ardocProjectTranslator:
    ''' short and full project names '''
    def __init__(self):
        self.dProjectTranslator={ 'AtlasCore':'Core', 'AtlasConditions':'Cond', 'DetCommon':'Det', 'AtlasEvent':'Evt', 'AtlasReconstruction':'Rec', 'AtlasSimulation':'Sim', 'AtlasTrigger':'Trg', 'AtlasAnalysis':'Anl', 'AtlasOffline':'Offl', 'AtlasProduction':'Prod', 'AtlasPoint1':'Pnt', 'AtlasTier0':'T0', 'AtlasP1HLT':'P1HLT' }
    def getShortName( self, fN ):
        fS=fN
        if fN in list(self.dProjectTranslator.keys()):
            fS=self.dProjectTranslator[fN]
        return fS
    def getProjTranslator( self ):
        return self.dProjectTranslator.copy()
def main(argv):
 """
 main
 """
 if len(argv)!=1:
  print("Name of project must be supplied\n")
  sys.exit(1)
 pName=argv[0]
 nPT=ardocProjectTranslator()
 pSName=nPT.getShortName(pName)
 print(pSName)  
if __name__=='__main__':
   main(sys.argv[1:])
