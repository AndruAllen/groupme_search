from groupy import Client
from SearchHandler import SearchHandler
from ResponseFormatter import ResponseFormatter
from time import sleep
from datetime import datetime

class QueryHandler:
    
    def __init__(self, ACCESS_TOKEN, MY_MENTION):
        self.ACCESS_TOKEN = ACCESS_TOKEN
        self.MY_MENTION = MY_MENTION
        self.INIT_TIME = self.GetInitTime()
        self.GROUPME_CHAR_LIM = 1000
        self.client = Client.from_token(ACCESS_TOKEN)
        self.recentMessageIdLookup = {}
        self.searchesByGroup = []
        self.groupsToSearch = []
        self.searchHandler = SearchHandler()
        self.responseFormatter = ResponseFormatter()
        self.DeleteIndexAllGroups()
    
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
            except:
                print("Request timeout on GetRecentMessagesFromGroup")
            if (len(messagesBlock.items) == 0):
                return recentMessages
            for message in messagesBlock:
                recentMessages.append(message)
            recentMessageId = messagesBlock[-1].data["id"]
    
    def GetSearchRequestsFromMessages(self, messages, minTimestamp):
        searches = []
        for message in messages:
            messageText = message.text
            if (messageText == None):
                continue
            findIndex = messageText.find(self.MY_MENTION)
            if (findIndex != -1):
                searchKeywords = messageText[findIndex + len(self.MY_MENTION):].split()
                searchPoster = message.name
                searchTimestamp = message.data["created_at"]
                if (searchPoster == self.MY_MENTION[1:] or searchTimestamp < minTimestamp):
                    continue
                searches.append({"keywords": searchKeywords, "poster": searchPoster, "timestamp": searchTimestamp})
        return searches
    
    def GetRecentMessageId(self, group):
        groupId = self.searchHandler.GetIdFromGroup(group)
        if (groupId not in self.recentMessageIdLookup):
            self.recentMessageIdLookup[groupId] = 0
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
        self.UpdateRecentMessageId(group, messages)
        self.searchHandler.InsertMessages(group, messages)
        self.groupsToSearch.append(group)
        self.searchesByGroup.append(self.GetSearchRequestsFromMessages(messages, self.INIT_TIME))
        
    def BulkRespondToSearches(self):
        for i in range(len(self.groupsToSearch)):
            group = self.groupsToSearch[i]
            searches = self.searchesByGroup[i]
            for search in searches:
                self.RespondToSearch(group, search)
        self.groupsToSearch = []
        self.searchesByGroup = []
    
    def Execute(self):
        print("Executing query handler")
        groups = self.GetGroupsFromUser()
        for group in groups:
            self.HandleGroupOperations(group)
        sleep(5)
        self.BulkRespondToSearches()
        
        
        
        
        
        
        
        