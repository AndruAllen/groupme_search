from groupy import Client
from elasticsearch import Elasticsearch, helpers
from elasticsearch.client import IndicesClient
from SearchHandler import SearchHandler
from ResponseFormatter import ResponseFormatter
from time import sleep
from datetime import datetime
from pymongo import MongoClient

class QueryHandler:
    
    def __init__(self, ACCESS_TOKEN, MY_MENTION):
        self.ACCESS_TOKEN = ACCESS_TOKEN
        self.MY_MENTION = MY_MENTION
        self.INIT_TIME = self.GetInitTime()
        self.GROUPME_CHAR_LIM = 1000
        self.DOC_TYPE = "message"
        self.mongo_client = MongoClient()
        self.es_client = Elasticsearch()
        self.ind_client = IndicesClient(self.es_client)
        self.searchHandler = SearchHandler(self.mongo_client, self.es_client, self.ind_client)
        self.db = self.mongo_client['chats']
        self.client = Client.from_token(ACCESS_TOKEN)
        # new format: recentMessageIdLookup = {'_id':0, group_id_0:message_id_latest, ...}
        self.recentMessageIdLookup = self.db['recentMessageIdLookup'].find_one({'_id':0}) # single document collection...
        if self.recentMessageIdLookup == None:
            self.db['recentMessageIdLookup'].insert_one({'_id':0})
        self.searchesByGroup = []
        self.groupsToSearch = []
        #self.searchHandler = SearchHandler() #moved above so there is only one instance of MongoClient() and ElasticSearch()
        self.responseFormatter = ResponseFormatter()
        #self.DeleteIndexAllGroups()
        self.reboot = True
    
    def GetGroupsFromUser(self):
        userGroups = []
        try:
            userGroups = list(self.client.groups.list_all())
        except:
            print("Request timeout on GetGroupsFromUser")
        return userGroups
    
    def DeleteIndexAllGroups(self):
        groups = self.GetGroupsFromUser()
        for group in groups:
            self.searchHandler.DeleteIndex(group)
            
    def GetInitTime(self):
        return int(datetime.utcnow().timestamp() - 24*60*60)
    
    def GetRecentMessagesFromGroup(self, group, recentMessageId):
        recentMessages = []
        while (True):
            messagesBlock = []
            try:
                messagesBlock = group.messages.list_after(recentMessageId)
                if (len(messagesBlock.items) == 0):
                    return recentMessages
                for message in messagesBlock:
                    recentMessages.append(message)
                recentMessageId = messagesBlock[-1].data["id"]
            except:
                print("Request timeout on GetRecentMessagesFromGroup")
                return []
    def PartitionMessages(self, messages, minTimestamp):
        searches = []
        userMessages = []
        for message in messages:
            messageText = message.text
            messagePoster = message.name
            if (messageText == None):
                continue
            if (messagePoster == self.MY_MENTION[1:]):
                #posted by Search Buddy, ignore
                continue
            findIndex = messageText.find(self.MY_MENTION)
            if (findIndex != -1):
                searchKeywords = messageText[findIndex + len(self.MY_MENTION):].split()
                searchTimestamp = message.data["created_at"]
                if (searchTimestamp < minTimestamp):
                    #old search, ignore
                    continue
                #Search
                searches.append({"keywords": searchKeywords, "poster": messagePoster, "timestamp": searchTimestamp})
            else:
                #User message
                userMessages.append(message)
        return [searches, userMessages]
    
    def GetRecentMessageId(self, group):
        groupId = self.searchHandler.GetIdFromGroup(group)
        if (groupId not in self.recentMessageIdLookup): # new group
            self.recentMessageIdLookup[groupId] = 0
            if(not self.ind_client.exists(index=groupId)):
                self.ind_client.create(index=groupId, body={"settings" : {"index" : {"refresh_interval":"-1"}}})
                print('created es index for:', groupId)
        return self.recentMessageIdLookup[groupId]
    
    def UpdateRecentMessageId(self, group, messages):
        if (len(messages) > 0):
            groupId = self.searchHandler.GetIdFromGroup(group)
            recentMessageId = messages[-1].data["id"]
            self.recentMessageIdLookup[groupId] = recentMessageId
        
    def PostResponse(self, group, text):
        print(text)
        for i in range(0, len(text), self.GROUPME_CHAR_LIM):    
            group.post(text[i:i+self.GROUPME_CHAR_LIM])
        
    def RespondToSearch(self, group, search):
        searchResults = self.searchHandler.ExecuteSearch(group, search["keywords"], self.MY_MENTION[1:], search["timestamp"])
        responseHeader = self.responseFormatter.GenerateHeader(search, searchResults)
        responseFooter = self.responseFormatter.GenerateFooter()
        allResponseText = [responseHeader]
        for [key, result] in searchResults:
            responseSingleResult = self.responseFormatter.GenerateSingleResultResponse(search, result)
            allResponseText.append(responseSingleResult)
        allResponseText.append(responseFooter)
        responseString = ""
        for responseText in allResponseText:
            responseString += responseText + "\n"
        self.PostResponse(group, responseString)
        
    def HandleGroupOperations(self, group):
        recentMessageId = self.GetRecentMessageId(group)
        messages = self.GetRecentMessagesFromGroup(group, recentMessageId)
        [searches, userMessages] = self.PartitionMessages(messages, self.INIT_TIME)
        self.UpdateRecentMessageId(group, messages)
        self.searchHandler.InsertMessages(group, userMessages)
        self.groupsToSearch.append(group)
        self.searchesByGroup.append(searches)
        
    def BulkRespondToSearches(self):
        for i in range(len(self.groupsToSearch)):
            group = self.groupsToSearch[i]
            searches = self.searchesByGroup[i]
            for search in searches:
                self.RespondToSearch(group, search)
        self.groupsToSearch = []
        self.searchesByGroup = []
    
    def Execute(self):
        #print("Executing query handler")
        groups = self.GetGroupsFromUser()
        self.recentMessageIdLookup = self.db['recentMessageIdLookup'].find_one({'_id':0})
        '''
        if(self.reboot):
            self.reboot = False # run only once
            for key in self.recentMessageIdLookup.keys():
                try:
                    exists = self.ind_client.exists(index=int(key))
                    print(exists)
                    if(not exists):
                        self.ind_client.create(index=key, body={"settings" : {"index" : {"refresh_interval":"-1"}}})
                        print(key, 'created just now?')
                except:
                    print(key, 'already in ES?')
        '''
        for group in groups:
            self.HandleGroupOperations(group)
        self.db['recentMessageIdLookup'].replace_one({'_id':0}, self.recentMessageIdLookup, upsert=True)
        #sleep(10)
        self.BulkRespondToSearches()
        
        
        
        
        
        
        
