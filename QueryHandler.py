from groupy import Client
from SearchHandler import SearchHandler
from ResponseFormatter import ResponseFormatter
from time import sleep

class QueryHandler:
    
    def __init__(self, ACCESS_TOKEN, MY_MENTION):
        self.ACCESS_TOKEN = ACCESS_TOKEN
        self.MY_MENTION = MY_MENTION
        self.client = Client.from_token(ACCESS_TOKEN)
        self.recentMessageIdLookup = {}
        self.searchHandler = SearchHandler()
        self.responseFormatter = ResponseFormatter()
    
    def GetGroupsFromUser(self):
        return list(self.client.groups.list_all())
    
    def GetRecentMessagesFromGroup(self, group, recentMessageId):
        recentMessages = []
        while (True):
            messagesBlock = group.messages.list_after(recentMessageId)
            if (len(messagesBlock.items) == 0):
                return recentMessages
            for message in messagesBlock:
                recentMessages.append(message)
            recentMessageId = messagesBlock[-1].data["id"]
    
    def GetSearchRequestsFromMessages(self, messages):
        searches = []
        for message in messages:
            messageText = message.text
            if (messageText == None):
                continue
            findIndex = messageText.find(self.MY_MENTION)
            if (findIndex != -1):
                searchKeywords = messageText[findIndex + len(self.MY_MENTION):].split()
                searchPoster = message.name
                searches.append({"keywords": searchKeywords, "poster": searchPoster})
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
        group.post(text)
        
    def RespondToSearch(self, group, search):
        searchResults = self.searchHandler.ExecuteSearch(group, search["keywords"], self.MY_MENTION[1:])
        responseHeader = self.responseFormatter.GenerateHeader(search, searchResults)
        responseFooter = self.responseFormatter.GenerateFooter()
        allResponseText = [responseHeader]
        for [key, result] in searchResults:
            responseSingleResult = self.responseFormatter.GenerateSingleResultResponse(search, result)
            allResponseText.append(responseSingleResult)
        allResponseText.append(responseFooter)
        for responseText in allResponseText:
            self.PostResponse(group, responseText)
        
    def HandleGroupOperations(self, group):
        recentMessageId = self.GetRecentMessageId(group)
        messages = self.GetRecentMessagesFromGroup(group, recentMessageId)
        self.UpdateRecentMessageId(group, messages)
        self.searchHandler.InsertMessages(group, messages)
        self.searches = self.GetSearchRequestsFromMessages(messages)
        print("Sleeping in between group operations")
        sleep(10)
        for search in self.searches:
            self.RespondToSearch(group, search)
    
    def Execute(self):
        groups = self.GetGroupsFromUser()
        for group in groups:
            self.HandleGroupOperations(group)
        
        
        
        
        
        
        
        
        
        