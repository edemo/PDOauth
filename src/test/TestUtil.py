# -*- coding: UTF-8 -*-
from pdoauth.CredentialManager import CredentialManager
from flask_login import login_user
from HTMLParser import HTMLParser
from pdoauth.app import app
import pdoauth.main  # @UnusedImport

class UserCreation(object):
    @classmethod
    def create_user_with_credentials(self):
        return CredentialManager.create_user_with_creds('password', 'userid', 'password', 'test@example.com')

class CSRFParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag=="input":
            a = dict(attrs)
            if a.has_key('name') and a['name']=='csrf_token':
                self.csrf = a['value']

class CSRFMixin(object):

    def getResponseText(self, resp):
        text = ""
        for i in resp.response:
            text += i
        return text

    def parseCSRF(self, text):
        parser = CSRFParser()
        parser.feed(text)
        csrf = parser.csrf
        return csrf

    def getCSRF(self, c=None):
        if c is None:
            with app.test_client() as c:
                return self._getCSRF(c)
        else:
            return self._getCSRF(c)

    def _getCSRF(self, c):
        resp = c.get('http://localhost.local/login')
        text = self.getResponseText(resp)
        csrf = self.parseCSRF(text)
        return csrf

class AuthenticatedSessionMixin(UserCreation):
    def makeSessionAuthenticated(self):
        user = self.create_user_with_credentials()
        user.activate()
        user.set_authenticated()
        user.save()
        login_user(user)
        self.userid = user.id
