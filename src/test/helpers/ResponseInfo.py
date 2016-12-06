from flask import json

class ResponseInfo(object):


    def getResponseBytes(self, resp):
        text = b""
        for msgPart in resp.response:
            text += msgPart
        return text

    def getResponseText(self, resp):
        text = self.getResponseBytes(resp)
        return text.decode('utf-8')

    def printResponse(self, resp):
        text = self.getResponseText(resp)
        print("{0.status_code}\n{0.headers}\n{1}".format(resp,text))

    def fromJson(self, resp):
        text = self.getResponseText(resp)
        data = json.loads(text)
        return data


