from groupy import Client
import json

ACCESS_TOKEN = "yrrudwbqjnb8BbrDqZ6oAhLMfqPfGBaGt5Y97WqV"
MAX_GROUP = 10

def messageToJson(message):
    dictMsg = {
            "sender": message.data["name"],
            "text": message.data["text"],
            "date": str(message.created_at)[:16]
        }
    return json.dumps(dictMsg)

client = Client.from_token(ACCESS_TOKEN)
groups = list(client.groups.list_all())
groupCt = 0

for group in groups:
    if (groupCt == MAX_GROUP):
        break
    groupName = group.data["name"]
    filename = "Messages for " + groupName + ".txt"
    messageFile = open(filename, "w")
    for message in group.messages.list_all():
        messageFile.write(messageToJson(message) + "\n")
    messageFile.close()
    groupCt += 1