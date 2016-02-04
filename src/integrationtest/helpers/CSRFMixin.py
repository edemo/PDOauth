# -*- coding: UTF-8 -*-

class CSRFMixin(object):
    def getCSRFCookieFromJar(self, cookieJar):
        for cookie in cookieJar:
            if cookie.name == 'csrf':
                return cookie.value

    def getCSRF(self, client):
        cookieJar = client.cookie_jar
        return self.getCSRFCookieFromJar(cookieJar)
