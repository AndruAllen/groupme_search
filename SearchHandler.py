from elasticsearch import Elasticsearch, helpers
from elasticsearch.client import IndicesClient, CatClient
from pymongo import MongoClient

class SearchHandler:
    
    def __init__(self, mongo_client, es_client, ind_client):
        self.es_client = es_client#Elasticsearch()
        self.ind_client = ind_client
        self.cat_client = CatClient(es_client)
        self.mongo_client = mongo_client
        self.db = self.mongo_client['chats']
        self.DOC_TYPE = "message"
        self.CUTOFF = 10
        self.BODY = {"size":self.CUTOFF, "query": {"query_string": {"query": ""}}}
    
    def GetIdFromGroup(self, group):
        return group.data["id"]
    
    def DeleteIndex(self, group):
        self.es_client.indices.delete(index=self.GetIdFromGroup(group), ignore=[400, 404])
    
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
   
    #def YieldDBMessages(self, groupId):
    #    for doc in db.['group'+str(groupId)+'z'].find({}):
    #        if(doc): # check if there by id in ES, would need to add explicitly above
    #            temp_doc = dict(doc)
    #            del temp_doc['_id']
    #            yield temp_doc

    def InsertMessages(self, group, messages):
        groupId = self.GetIdFromGroup(group)
        if messages != []: 
            #turned off at creation of new index
            #self.ind_client.put_settings(index=[groupId], body={"index" : {"refresh_interval" : "-1"}})
            if(len(messages) > 1):
                res = helpers.bulk(self.es_client, self.YieldMessages(groupId, messages))
                print(res)
            else:
                doc = list(self.YieldMessages(groupId, messages))[0]
                res = self.es_client.index(index=groupId, doc_type=self.DOC_TYPE, body=doc['_source'])
                print(res['result'])
            self.ind_client.refresh(index=groupId)#,ignore_unavailable =True)
            self.db['group'+str(groupId)+'z'].insert_many(list(self.YieldMessages(groupId, messages)))
        
        
    #else:
    #    if(self.cat_client.count(index=groupId) != self.db['group'+str(groupId)+'z'].count({}):
    #            res = helpers.bulk(self.es_client, self.YieldDBMessages(groupId))
    #            print(res) # refresh es by mongodb store
    
    def PerformSearchOnKeyword(self, groupId, keyword):
        self.BODY["query"]["query_string"]["query"] = keyword
        res = self.es_client.search(index = groupId, doc_type = self.DOC_TYPE, body = self.BODY)
        return res["hits"]["hits"]
      
    def ExecuteSearch(self, group, keywords, myMention, timeCutoff):
        combinedResults = {}
        groupId = self.GetIdFromGroup(group)
        for keyword in keywords:
            curResults = self.PerformSearchOnKeyword(groupId, keyword)
            for result in curResults:
                if (result["_source"]["Timestamp"] >= timeCutoff or result["_source"]["Sender"] == myMention):
                    continue
                resultId = result["_source"]["Id"]
                if (resultId not in combinedResults):
                    combinedResults[resultId] = result
        return list(sorted(combinedResults.items(), key = lambda item: -item[1]["_source"]["Timestamp"])[:self.CUTOFF])
        
        
        
        
        
