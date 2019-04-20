from QueryHandler import QueryHandler

ACCESS_TOKEN = "yrrudwbqjnb8BbrDqZ6oAhLMfqPfGBaGt5Y97WqV"
MY_MENTION = "@Search Buddy"

queryHandler = QueryHandler(ACCESS_TOKEN, MY_MENTION)

while (True):
    queryHandler.Execute()