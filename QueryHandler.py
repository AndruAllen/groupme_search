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
    
    def SendSearchResponse(self):
        pass
    
    