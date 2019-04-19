from datetime import datetime

class ResponseFormatter:
    
    def __init__(self):
        self.HEADER_MESSAGE = "Hello {NAME}, your search for {KEYWORDS} returned {NUMBER} results."
        self.SINGLE_RESULT_MESSAGE = "[{DATE}] {SENDER}: {TEXT}"
        self.FOOTER_MESSAGE = "Thank you for using Search Buddy!"
        self.STRFTIME_FORMAT = "%m/%d %H:%M:%S"
        self.NAME_REPLACE = "{NAME}"
        self.KEYWORDS_REPLACE = "{KEYWORDS}"
        self.NUMBER_REPLACE = "{NUMBER}"
        self.DATE_REPLACE = "{DATE}"
        self.SENDER_REPLACE = "{SENDER}"
        self.TEXT_REPLACE = "{TEXT}"
    
    def GenerateHeader(self, search, searchResults):
        message = self.HEADER_MESSAGE
        message = message.replace(self.NAME_REPLACE, search["poster"])
        message = message.replace(self.KEYWORDS_REPLACE, str(search["keywords"]).replace("'",""))
        message = message.replace(self.NUMBER_REPLACE, str(len(searchResults)))
        return message
    
    def GenerateFooter(self):
        return self.FOOTER_MESSAGE
    
    def GetDatetime(self, UTC):
        return datetime.utcfromtimestamp(int(UTC)).strftime(self.STRFTIME_FORMAT)
    
    def GenerateSingleResultResponse(self, search, result):
        message = self.SINGLE_RESULT_MESSAGE
        message = message.replace(self.DATE_REPLACE, self.GetDatetime(result["_source"]["Timestamp"]))
        message = message.replace(self.SENDER_REPLACE, result["_source"]["Sender"])
        message = message.replace(self.TEXT_REPLACE, result["_source"]["Text"])
        return message