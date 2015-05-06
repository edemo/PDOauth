# -*- coding: UTF-8 -*-
from pdoauth.CredentialManager import CredentialManager
from flask_login import login_user
from pdoauth.app import app, mail
import pdoauth.main  # @UnusedImport
from bs4 import BeautifulSoup
import random
import string
from pdoauth.models.Application import Application
from flask import json

class UserTesting(object):

    def setupRandom(self):
        self.randString = ''.join(random.choice(string.ascii_letters) for _ in range(6))

    def create_user_with_credentials(self, credType='password', userid=None, password=None, email=None):
        if email is None:
            email = "email{0}@example.com".format(self.randString)
        if userid is None:
            userid = "aaa_{0}".format(self.randString)
        if password is None:
            password = "bbb_{0}".format(self.randString)

        self.usercreation_email = email
        self.usercreation_userid = userid
        self.usercreation_password = password
        return CredentialManager.create_user_with_creds(credType, userid, password, email)
    
    def login(self, c):
        self.setupRandom()
        user = self.create_user_with_credentials()
        user.activate()
        data = {
                'username': self.usercreation_userid,
                'password': self.usercreation_password,
                'next': '/v1/oauth2/auth'
        }
        csrf = self.getCSRF(c)
        data['csrf_token']=csrf
        resp = c.post('http://localhost.local/login', data=data)
        self.assertEqual(302, resp.status_code)
        self.assertEqual('http://localhost.local/v1/oauth2/auth', resp.headers['Location'])
        return resp

    def getCode(self, c):
        redirect_uri = 'https://test.app/redirecturi'
        appid = "app-{0}".format(self.randString)
        self.appsecret = "secret-{0}".format(self.randString)
        application = Application.new(appid, self.appsecret, redirect_uri)
        self.appid = application.id
        uri = 'https://localhost.local/v1/oauth2/auth'
        query_string = 'response_type=code&client_id={0}&redirect_uri={1}'.format(self.appid, 
            redirect_uri)
        resp = c.get(uri, query_string=query_string)
        self.assertEqual(302, resp.status_code)
        location = resp.headers['Location']
        self.assertTrue(location.startswith('https://test.app/redirecturi?code='))
        return location.split('=')[1]

    def loginAndGetCode(self):
        with app.test_client() as c:
            self.login(c)
            return self.getCode(c)

    def register(self, c, csrf, email = None):
        with mail.record_messages() as outbox:
            if email is None:
                email = "{0}@example.com".format(self.randString)
            data = {
                'credentialtype':'password', 
                'identifier': "id_{0}".format(self.randString), 
                'secret':"password_{0}".format(self.randString), 
                'csrf':csrf, 
                'email': email, 
                'digest': self.randString,
                'next': '/registered'}
            resp = c.post('https://localhost.local/v1/register', data=data)
            return resp, outbox

class ServerSide(object):
    def doServerSideRequest(self, code):
        data = {'code':code, 
            'grant_type':'authorization_code', 
            'client_id':self.appid, 
            'client_secret':self.appsecret, 
            'redirect_uri':'https://test.app/redirecturi'}
        with app.test_client() as serverside:
            resp = serverside.post("https://localhost.local/v1/oauth2/token", data=data)
            data = json.loads(self.getResponseText(resp))
            self.assertTrue(data.has_key('access_token'))
            self.assertTrue(data.has_key('refresh_token'))
            self.assertEquals(data['token_type'], 'Bearer')
            self.assertEquals(data['expires_in'], 3600)
            return data


class CSRFParser(object):
    def feed(self,text):
            soup = BeautifulSoup(text)
            csrf = unicode(soup.find(id="csrf_token").attrs['value'])
            self.csrf = csrf

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

    def getCSRF(self, c=None, uri=None):
        if c is None:
            with app.test_client() as c:
                return self._getCSRF(c)
        else:
            return self._getCSRF(c)

    def _getCSRF(self, c, uri=None):
        if uri is None:
            uri = 'http://localhost.local/login'
        resp = c.get(uri)
        text = self.getResponseText(resp)
        csrf = self.parseCSRF(text)
        return csrf

    def printResponse(self, resp):
        print "{0.status_code}\n{0.headers}\n{1}".format(resp,self.getResponseText(resp))

class AuthenticatedSessionMixin(UserTesting):
    def makeSessionAuthenticated(self):
        user = self.create_user_with_credentials()
        user.activate()
        user.set_authenticated()
        user.save()
        login_user(user)
        self.userid = user.id
