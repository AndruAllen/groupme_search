from groupy import Client

class QueryHandler:
    
    def __init__(self, ACCESS_TOKEN, MY_MENTION):
        self.ACCESS_TOKEN = ACCESS_TOKEN
        self.MY_MENTION = MY_MENTION
        self.client = Client.from_token(ACCESS_TOKEN)
    
    def GetGroupsFromUser(self):
        return list(self.client.groups.list_all())
    
    def GetRecentMessagesFromGroup(self, group, timestamp):
        return group.messages.list_after(timestamp)
    
    def GetSearchRequestsFromMessages(self, messages):
        searches = []
        for message in messages:
            messageText = message.text
            if (messageText == None):
                continue
            findIndex = messageText.find(self.MY_MENTION)
            print(messageText, findIndex)
            if (findIndex != -1):
                searchTerms = messageText[findIndex + len(self.MY_MENTION):].split()
                searchPoster = message.name
                searches.append({"terms": searchTerms, "poster": searchPoster})
        return searches
    
    def PartitionGroups(self, currentGroups, existingGroups):
        newGroups = []
        oldGroups = []
        for group in currentGroups:
            if group in existingGroups:
                oldGroups.append(group)
            else:
                newGroups.append(group)
        return [newGroups, oldGroups]
    
    #--- To be completed
    
    def SendSearchResponse(self):
        pass
    
    def HandleSearch(self, group, search):
        pass
    
    def GetGroupsFromDatabase(self):
        return []
    
    def CreateGroupInDatabse(self, group):
        pass
    
    def GetTimestampFromDatabase(self, group):
        return 0
    
    def InsertMessagesIntoDatabase(self, messages):
        pass
    
    def InsertMessagesIntoElasticSearch(self, messages):
        pass
    
    #--- To be completed
    
    def HandleGroupOperations(self, group):
        timestamp = self.GetTimestampFromDatabase(group)
        messages = self.GetRecentMessagesFromGroup(group, timestamp)
        self.InsertMessagesIntoDatabase(messages)
        self.InsertMessagesIntoElasticSearch(messages)
        searches = self.GetSearchRequestsFromMessages(messages)
        for search in searches:
            self.HandleSearch(group, search)
    
    def Execute(self):
        currentGroups = self.GetGroupsFromUser()
        existingGroups = self.GetGroupsFromDatabase()
        [newGroups, oldGroups] = self.PartitionGroups(currentGroups, existingGroups)
        for group in newGroups:
            self.CreateGroupInDatabase(group)
            self.HandleGroupOperations(group)
        for group in oldGroups:
            self.HandleGroupOperations(group)