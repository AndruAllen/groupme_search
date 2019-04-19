from elasticsearch import Elasticsearch, helpers

class SearchHandler:
    
    def __init__(self):
        self.client = Elasticsearch()
        self.DOC_TYPE = "message"
        self.BODY = {"size":100, "query": {"query_string": {"query": ""}}}
        self.CUTOFF = 10
    
    def GetIdFromGroup(self, group):
        return group.data["id"]
    
    def DeleteIndex(self, group):
        self.client.indices.delete(index=self.GetIdFromGroup(group), ignore=[400, 404])
    
    def YieldMessages(self, groupId, messages):
        for message in messages:
            yield   {
                        "_index": groupId,
                        "_type": self.DOC_TYPE,
                        "_source":  {
                                        "Sender": message.data["name"],
                                        "Text": message.data["text"],
                                        "Timestamp": message.data["created_at"],
                                        "Id": message.data["id"]
                                    }
                    }
    
    def InsertMessages(self, group, messages):
        groupId = self.GetIdFromGroup(group)
        helpers.bulk(self.client, self.YieldMessages(groupId, messages))
    
    def PerformSearchOnKeyword(self, groupId, keyword):
        self.BODY["query"]["query_string"]["query"] = keyword
        res = self.client.search(index = groupId, doc_type = self.DOC_TYPE, body = self.BODY)
        print(len(res["hits"]["hits"]))
        return res["hits"]["hits"]
      
    def ExecuteSearch(self, group, keywords, myMention):
        print(group, keywords, myMention)
        combinedResults = {}
        groupId = self.GetIdFromGroup(group)
        for keyword in keywords:
            curResults = self.PerformSearchOnKeyword(groupId, keyword)
            print(curResults)
            for result in curResults:
                if (result["_source"]["Sender"] == myMention):
                    continue
                resultId = result["_source"]["Id"]
                if (resultId not in combinedResults):
                    combinedResults[resultId] = result
        return list(sorted(combinedResults.items(), key = lambda item: -item[1]["_source"]["Timestamp"])[:self.CUTOFF])
        
        
        
        
        