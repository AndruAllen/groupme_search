from groupy import Client
from time import sleep
#import json

ACCESS_TOKEN = "yrrudwbqjnb8BbrDqZ6oAhLMfqPfGBaGt5Y97WqV"
MY_MENTION = "@Search Buddy"
client = Client.from_token(ACCESS_TOKEN)
groups = []
mostRecentMessages = {}

def retrieveGroupIdsFromDatabase():
    return []

def retrieveLastMessageIdsFromDatabase():
    return {}

def updateGroups():
    pass

def checkGroupForNewMessages(group):
    groupId = group.id
    mostRecentMessageId = 0
    if (groupId in mostRecentMessages):
        mostRecentMessageId = mostRecentMessages[groupId]
    messages = group.messages.list_after(mostRecentMessageId)
    return messages

def updateMostRecentMessages(group, messages):
    global mostRecentMessages
    groupId = group.id
    lastMessageId = messages.items[-1].id
    mostRecentMessages[groupId] = lastMessageId

def parseMessagesForSearchQuery(messages):
    searches = []
    for message in messages:
        messageText = message.text
        if (messageText == None):
            continue
        findIndex = messageText.find(MY_MENTION)
        print(messageText, findIndex)
        if (findIndex != -1):
            searchTerms = messageText[findIndex + len(MY_MENTION):].split()
            searchPoster = message.name
            searches.append({"terms": searchTerms, "poster": searchPoster})
    return searches

def respondToSearches(group, searches):
    for search in searches:
        response = "Hello " + "@" + search["poster"] + ", searching for " + str(search["terms"]) + " was a really dumb idea"
        group.post(response)


groups = list(client.groups.list_all())
while (True):
    for group in groups:
        noNewMessages = True
        while (True):
            newMessages = checkGroupForNewMessages(group)
            if (len(newMessages.items) == 0):
                break
            noNewMessages = False
            updateMostRecentMessages(group, newMessages)
            searches = parseMessagesForSearchQuery(newMessages)
            respondToSearches(group, searches)
        if (noNewMessages):
            break
    sleep(10)




















