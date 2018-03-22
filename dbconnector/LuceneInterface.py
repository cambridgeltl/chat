####################
#   FileName:    LuceneInterface.py
#   Author:      Simon Baker
#   Affiliation: University of Cambridge
#                Computer Laboratory and Language Technology Laboratory
#   Contact:     simon.baker.gen@gmail.com
#                simon.baker@cl.cam.ac.uk
#
#   Description: This file represents an interface with the Lucene indexer.  From this file, you should instantiate the class LuceneInterface.
#

from __future__ import division
import lucene
from java.io import File
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field
from org.apache.lucene.search import IndexSearcher,BooleanClause
from org.apache.lucene.index import IndexReader, Term, MultiFields, TermContext
from org.apache.lucene.queryparser.classic import QueryParser, MultiFieldQueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.util import BytesRef
from org.apache.lucene.util import BytesRefIterator
from org.apache.lucene.index import TermsEnum
from org.apache.lucene.search import DocIdSetIterator
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.search import TotalHitCountCollector

from logging import debug

class LuceneInterface:

    def __init__(self, indexPath, initialHeap, maxHeap):
        lucene.initVM(initialheap=initialHeap, maxheap=maxHeap)
        self.analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)
        self.indexPath = indexPath
        self.indexDir = SimpleFSDirectory(File(self.indexPath))

    def open(self):
        debug('Opening index "%s"' % self.indexPath)
        self.reader = IndexReader.open(self.indexDir)
        self.searcher = IndexSearcher(self.reader)
        self.totalDocs = self.getTotalSentenceCount()

    def close(self):
        self.reader.close()

    def getTFForField(self, field):
        tfs = {}
        fields = MultiFields.getFields(self.reader)
        terms = fields.terms(field)
        enum = BytesRefIterator.cast_(terms.iterator(None))
        try:
          while enum.next():
                termval = TermsEnum.cast_(enum)
                termString  = termval.term().utf8ToString()
                freq    = self.reader.totalTermFreq(Term(field, termString))
                tfs[termString] = freq
        except:
            pass
        return tfs

    def getTotalSentenceCount(self):
        num =  self.reader.numDocs()
        return num

    def sentenceCountForQuery(self, query, field='text'):
        qp = QueryParser(Version.LUCENE_CURRENT, field, self.analyzer).parse(query)
        collector = TotalHitCountCollector()
        self.searcher.search(qp, collector)
        return collector.getTotalHits()

    # def sentenceCountForPMIDs(self, PMIDList):
    #
    #     #qp = QueryParser(Version.LUCENE_CURRENT, field, self.analyzer).parse(query)
    #
    #     q = TermQuery(Term(field, "hello world"))
    #
    #     collector = TotalHitCountCollector()
    #     self.searcher.search(qp, collector)
    #     return collector.getTotalHits()

    #def getQueryCount(self, query, field='text'):
        #qp = QueryParser(Version.LUCENE_CURRENT, field, self.analyzer).parse(query)
        #collector = TotalHitCountCollector()
        #self.searcher.search(qp, collector)
        #return collector.getTotalHits()

    def getIntersectionCount(self, query, countTermString, sfield, cfield):
        qp = MultiFieldQueryParser.parse(Version.LUCENE_CURRENT,[query,countTermString],[sfield,cfield],[BooleanClause.Occur.MUST,BooleanClause.Occur.MUST],self.analyzer)
        collector = TotalHitCountCollector()
        self.searcher.search(qp, collector)
        return collector.getTotalHits()

    # Return a list of records, where each record is a dictionary; the keys are the the field names in lucene.
    def search(self, query, field, count=100, offset=0):
        qp = QueryParser(Version.LUCENE_CURRENT, field, WhitespaceAnalyzer(Version.LUCENE_CURRENT)).parse(query)
        hits = self.searcher.search(qp, offset+count)
        result = []
        for hit in hits.scoreDocs[offset:]:
            record = dict()
            doc = self.searcher.doc(hit.doc)
            record["id"] = doc.get("id")
            record["pos"]  = doc.get("pos")
            record["hallmarks"] = doc.get("hallmarks").split()
            #record["hallmarks-exp"] = doc.get("hallmarks-exp").split()
            record["text"] = doc.get("text")
            result.append(record)
        return result

    def searchGivenHallmarks(self, query, hallmarksList, hallmarksField, count=100, offset=0):
        qList = [query]
        qList.extend(hallmarksList)
	#print(qList)
        fList = ["text"]
        fList.extend([hallmarksField]*len(hallmarksList))
	#print(fList)
        flagList = [BooleanClause.Occur.MUST]
        flagList.extend([BooleanClause.Occur.MUST]*len(hallmarksList))
        #print(flagList)
        qp = MultiFieldQueryParser.parse(Version.LUCENE_CURRENT, qList, fList, flagList, self.analyzer)
        #print (qp)
        hits = self.searcher.search(qp, offset+count)
        result = []
        for hit in hits.scoreDocs[offset:]:
            record = dict()
            doc = self.searcher.doc(hit.doc)
            record["id"] = doc.get("id")
            record["pos"]  = doc.get("pos")
            record["hallmarks"] = doc.get("hallmarks").split()
            #record["hallmarks-exp"] = doc.get("hallmarks-exp").split()
            record["text"] = doc.get("text")
            result.append(record)
        return result
