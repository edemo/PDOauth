from flask import json

class ResponseInfo(object):

    def getResponseText(self, resp):
        text = ""
        for msgPart in resp.response:
            text += msgPart
        return text

    def printResponse(self, resp):
        text = self.getResponseText(resp)
        print "{0.status_code}\n{0.headers}\n{1}".format(resp,text)

    def fromJson(self, resp):
        text = self.getResponseText(resp)
        data = json.loads(text)
        return data


