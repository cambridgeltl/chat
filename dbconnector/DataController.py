####################
#   FileName:    DataController.py
#   Author:      Simon Baker
#   Affiliation: University of Cambridge
#                Computer Laboratory and Language Technology Laboratory
#   Contact:     simon.baker.gen@gmail.com
#                simon.baker@cl.cam.ac.uk
#
#   Description: This file represents a controller class that abstracts the database layer for the Cancer Hallmarks Analytics Tool (CHAT).
#                It is aimed to be used as part of MVC design pattern (or something similar).


from LuceneInterface import LuceneInterface

from logging import debug
import QueryFormatter

class DataController:
    INITIAL_HEAP = "4G"
    MAX_HEAP = "32G"

    def __init__(self, indexPath):
	    self.indexPath = indexPath
	    self.interface = LuceneInterface(indexPath, DataController.INITIAL_HEAP,DataController.MAX_HEAP)

    def open(self):
	    debug('DataController.open(): start')
	    self.interface.open()
	    self.hallmarkCounts = self.interface.getTFForField("hallmarks")
	    #self.hallmarkExtCounts = self.interface.getTFForField("hallmarks-exp")
	    debug('DataController.open(): finished')

    def getTotalNumberOfSentences(self):
	    return self.interface.totalDocs

    def getHallmarksCount(self, expandHallmarks=True):
	    return self.hallmarkCounts

    def getHallmarksForQuery(self,query, expandHallmarks=True):
        query = QueryFormatter.formatQuery(query)
        hallmarksField = "hallmarks"
        hmCounts = {}
        queryReturnCount = self.interface.sentenceCountForQuery(query)
        for hm in self.hallmarkCounts.keys():
            if queryReturnCount ==0 :
                hmCounts[hm]=0
            else:
                hmCounts[hm] = self.interface.getIntersectionCount(query, hm, "text", hallmarksField)
        return [queryReturnCount,hmCounts]

    def getHallmarksForPMIDs(self, pmids):
        pmids = [id+"-*" for id in pmids]
        query = " OR ".join(pmids)
        print(query)
        #query="26500746-* OR 25995984-*"
        queryReturnCount = self.interface.sentenceCountForQuery(query,field="id")
        print(queryReturnCount)
        #result = self.interface.getHallmarksForPMIDs(PMIDS)
        hallmarksField = "hallmarks"
        hmCounts = {}
        queryReturnCount = self.interface.sentenceCountForQuery(query, field="id")
        for hm in self.hallmarkCounts.keys():
            if queryReturnCount == 0:
                hmCounts[hm] = 0
            else:
                hmCounts[hm] = self.interface.getIntersectionCount(query, hm, "id", hallmarksField)
        return [queryReturnCount, hmCounts]



    def search(self,query, maxReturnLimit,count=100, offset=0):
        query = QueryFormatter.formatQuery(query)
        result = self.interface.search(query, "text", maxReturnLimit)
        return result

    def searchTextAndHallmarks(self, query, hallmarks, count=100, offset=0, expandHallmarks=True):
        query = QueryFormatter.formatQuery(query)
        hallmarksField = "hallmarks"
        result = self.interface.searchGivenHallmarks(query, hallmarks, hallmarksField, count, offset)
        return result

    def searchPMIDs(self,pmids,count=100, offset=0):
        query = " OR ".join([id + "-*" for id in pmids])
        result = self.interface.search(query, "id", count=count, offset=offset)
        orderedResult=[]
        for pmid in pmids: # sorts the list by PMID, then by sentenceID
            sentencesForPMID =  [r for r in result if r["id"].startswith(pmid)]
            orderedResult.extend(sorted(sentencesForPMID, key= lambda r: int(r["id"].split("-")[1])))
        #result = self.interface.searchGivenHallmarks(query, hallmarks, hallmarksField, count, offset)
        return orderedResult



    def close(self):
	    self.interface.close()

def test():
    from config import INDEX_PATH
    indexPath = INDEX_PATH
    controller = DataController(indexPath)
    controller.open()
    # x = controller.getTotalNumberOfSentences()
    # print "total number of sentences = " + str(x)
    hm = controller.getHallmarksCount()
    hm2 = controller.getHallmarksCount(True)

    #for h in hm.keys():
    #    print "%s:%d\t%d" % (h,hm[h],hm2[h])

    print "--"*10
    q = "breast cancer"
    [numSent,res]= controller.getHallmarksForQuery(q,True)
    print "hallmarks distribution for query '%s' over %d matching sentences " % (q,numSent)
    print str(res)
    for h in hm.keys(): print "%s:%d" % (h,res[h])

    print "--"*10
    q = "asbestos"
    [numSent,res]= controller.getHallmarksForQuery(q,True)
    print "hallmarks distribution for query '%s' over %d matching sentences " % (q,numSent)
    print str(res)
    for h in hm.keys(): print "%s:%d" % (h,res[h])


    #res = controller.search("p53",1000)
   # print "retruned search hits:%d" % len(res)

    #res = controller.searchTextAndHallmarks("p53", ["x"], 1000)
    #print "retruned search for [x] hits:%d" % len(res)

    res = controller.searchTextAndHallmarks("disease",["1"], count=10,offset=0)
    print "retruned search for [x] hits:%d" % len(res)
    for r in res: print(str(r))

    res = controller.searchTextAndHallmarks("disease", ["1"], count=10, offset=1)
    print
    "retruned search for [x] hits:%d" % len(res)
    for r in res: print(str(r))

    test_PMIDS = ["26500746", "25995984","25441643"]

    [numSent, res] = controller.getHallmarksForPMIDs(test_PMIDS)
    print "hallmarks distribution for test PMIDs '%s' has %d matching sentences " % (str(test_PMIDS), numSent)
    print str(res)
    for h in hm.keys(): print "%s:%d" % (h, res[h])

    res = controller.searchPMIDs(test_PMIDS)
    print "hallmarks distribution for test PMIDs '%s' has %d matching sentences " % (str(test_PMIDS), len(res))
    for r in res: print(str(r))


    controller.close()

if __name__ == '__main__':
    test()
