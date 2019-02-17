import requests
import json

#groupsURL = "https://api.groupme.com/v3/groups?token=yrrudwbqjnb8BbrDqZ6oAhLMfqPfGBaGt5Y97WqV"
#groupResponse = (requests.get(groupsURL)).json()

requestURL="https://api.groupme.com/v3/groups/48280673/messages"
params = {"token": "yrrudwbqjnb8BbrDqZ6oAhLMfqPfGBaGt5Y97WqV"}
data = {"message": {"text":"hi", "source_guid": "GUID"}}
messageResponse = (requests.post(requestURL, params=params, json=json.dumps(data)))
print(messageResponse)
