# -*- coding: UTF-8 -*-
from pdoauth.CredentialManager import CredentialManager
from flask_login import login_user
from pdoauth.app import app, mail
import pdoauth.main  # @UnusedImport
import random
import string
from pdoauth.models.Application import Application
from flask import json
from pdoauth.models.User import User
import config

app.extensions["mail"].suppress = True

def mkRandomString(length):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

class ResponseInfo(object):

    def getResponseText(self, resp):
        text = ""
        for i in resp.response:
            text += i
        return text

    def printResponse(self, resp, text=None):
        if text is None:
            text = self.getResponseText(resp)
        print "{0.status_code}\n{0.headers}\n{1}".format(resp,text)

    def fromJson(self, resp):
        text = self.getResponseText(resp)
        data = json.loads(text)
        return data


class UserTesting(ResponseInfo):

    def setupRandom(self):
        self.randString = mkRandomString(6)

    def createUserWithCredentials(self, credType='password', userid=None, password=None, email=None):
        self.setupRandom()
        if email is None:
            email = "email{0}@example.com".format(self.randString)
        if userid is None:
            userid = "aaa_{0}".format(self.randString)
        if password is None:
            password = "password_{0}".format(self.randString)

        self.usercreation_email = email
        self.usercreation_userid = userid
        self.usercreation_password = password
        user = CredentialManager.create_user_with_creds(credType, userid, password, email)
        self.assertTrue(user)
        return user
    
    def login(self, c, activate = True, createUser = True):
        self.setupRandom()
        if createUser:
            user = self.createUserWithCredentials()
        else:
            user = User.getByEmail(self.usercreation_email)
        if activate:
            user.activate()
        data = {
                'credentialType': 'password',
                'username': self.usercreation_userid,
                'password': self.usercreation_password
        }
        resp = c.post(config.base_url+'/login', data=data)
        return resp

    def getCode(self, c):
        redirect_uri = 'https://test.app/redirecturi'
        appid = "app-{0}".format(self.randString)
        self.appsecret = "secret-{0}".format(self.randString)
        application = Application.new(appid, self.appsecret, redirect_uri)
        self.appid = application.appid
        uri = config.base_url + '/v1/oauth2/auth'
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

    def register(self, c, email = None):
        with mail.record_messages() as outbox:
            if email is None:
                email = "{0}@example.com".format(self.randString)
            self.registered_email = email
            data = {
                'credentialType':'password', 
                'identifier': "id_{0}".format(self.randString), 
                'secret':"password_{0}".format(self.randString+self.randString),
                'email': email, 
                'digest': self.randString
            }
            resp = c.post(config.base_url + '/v1/register', data=data)
            return resp, outbox

    def assertUserResponse(self, resp):
        self.assertEquals(resp.status_code, 200)
        data = self.fromJson(resp)
        self.assertEquals(data['assurances'], {})
        self.assertTrue("@example.com" in data['email'])
        self.assertTrue(data.has_key('userid'))
        return data


class ServerSide(ResponseInfo):
    def doServerSideRequest(self, code):
        data = {'code':code, 
            'grant_type':'authorization_code', 
            'client_id':self.appid, 
            'client_secret':self.appsecret, 
            'redirect_uri':'https://test.app/redirecturi'}
        with app.test_client() as serverside:
            resp = serverside.post(config.base_url + "/v1/oauth2/token", data=data)
            data = self.fromJson(resp)
            self.assertTrue(data.has_key('access_token'))
            self.assertTrue(data.has_key('refresh_token'))
            self.assertEquals(data['token_type'], 'Bearer')
            self.assertEquals(data['expires_in'], 3600)
            return data


class CSRFMixin(object):
    def getCSRFCookieFromJar(self, cookieJar):
        for cookie in cookieJar:
            if cookie.name == 'csrf':
                return cookie.value

    def getCSRF(self, c, uri=None):
        cookieJar = c.cookie_jar
        return self.getCSRFCookieFromJar(cookieJar)

class AuthenticatedSessionMixin(UserTesting):
    def makeSessionAuthenticated(self):
        user = self.createUserWithCredentials()
        user.activate()
        user.set_authenticated()
        user.save()
        login_user(user)
        self.userid = user.userid
