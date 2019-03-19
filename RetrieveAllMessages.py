from groupy import Client
from difflib import SequenceMatcher
import json
import os.path

SCRIPT_DIR = os.path.dirname(__file__)
USE_PERSONAL_DATA = True
MAX_GROUP = 100
INCLUDE = []
SIMILARITY_THRESHOLD = 0.8

def messageToJson(message):
    dictMsg = {
            "sender": message.data["name"],
            "text": message.data["text"],
            "date": str(message.created_at)[:16]
        }
    return json.dumps(dictMsg)

def isIncluded(groupName):
    for includedGroup in INCLUDE:
        similarity=SequenceMatcher(None,includedGroup,groupName).ratio()
        if (similarity > SIMILARITY_THRESHOLD):
            return True
    return False

if (USE_PERSONAL_DATA):
    accessTokenFile = open(SCRIPT_DIR + "/../MyAccessToken.txt", "r")
    ACCESS_TOKEN = accessTokenFile.read()
else:
    ACCESS_TOKEN = "yrrudwbqjnb8BbrDqZ6oAhLMfqPfGBaGt5Y97WqV"

includeFile = open("IncludeLarge.txt", "r")
for line in includeFile:
    INCLUDE.append(line)

client = Client.from_token(ACCESS_TOKEN)
groups = list(client.groups.list_all())
groupCt = 0

GroupNamesIncluded = []
GroupNamesExcluded = []
totalMessages = 0
allMessageCounts = []

for group in groups:
    if (groupCt == MAX_GROUP):
        break
    groupCt += 1
    messageCount = group.data["messages"]["count"]
    allMessageCounts.append(messageCount)
    """
    groupName = group.data["name"]
    if (not isIncluded(groupName)):
        GroupNamesExcluded.append(groupName)
        continue
    GroupNamesIncluded.append("[" + str(messageCount) + "] " + groupName)
    totalMessages += messageCount
    
    filename = "Messages for " + groupName + ".txt"
    messageFile = open(SCRIPT_DIR + '/datafiles/' + filename, "w")
    for message in group.messages.list_all():
        messageFile.write(messageToJson(message) + "\n")
    messageFile.close()
    """
    
