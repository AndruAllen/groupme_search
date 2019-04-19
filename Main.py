from SearchHandler import SearchHandler
from QueryHandler import QueryHandler

ACCESS_TOKEN = "yrrudwbqjnb8BbrDqZ6oAhLMfqPfGBaGt5Y97WqV"
MY_MENTION = "@Search Buddy"

searchHandler = SearchHandler()
queryHandler = QueryHandler(ACCESS_TOKEN, MY_MENTION)

groups = queryHandler.GetGroupsFromUser()
curGroup = groups[0]
messages = queryHandler.GetRecentMessagesFromGroup(curGroup, 0)
searchHandler.InsertMessages(curGroup, messages)
results = searchHandler.ExecuteSearch(curGroup, ["test", "ssh"])