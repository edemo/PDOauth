# -*- coding: UTF-8 -*-
from twatson.unittest_annotations import Fixture, test
from pdoauth.app import app
from pdoauth.models.Application import Application
from pdoauth import main  # @UnusedImport
from pdoauth.models.Credential import Credential
from pdoauth.models.User import User
from HTMLParser import HTMLParser
import json
from test.TestUtil import UserCreation
from flask_login import logout_user

class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag=="input":
            a = dict(attrs)
            if a.has_key('name') and a['name']=='csrf_token':
                self.csrf = a['value']
        
class MainTest(Fixture):

    def setUp(self):
        Credential.query.delete()  # @UndefinedVariable
        User.query.delete()  # @UndefinedVariable
        Application.query.delete()  # @UndefinedVariable
        self.app = app.test_client()

    @test
    def NoRootUri(self):
        resp = self.app.get("/")
        self.assertEquals(resp.status_code, 404,)

    @test
    def Unauthenticated_user_is_redirected_to_login_page_when_tries_to_do_oauth_with_us(self):
        redirectUri = 'https://client.example.com/oauth/redirect'
        Application.new('app','secret',redirectUri)
        uri = "v1/oauth2/auth?response_type=code&client_id=app&redirect_uri=https%3A%2F%2Fclient.example.com%2Foauth%2Fredirect"
        resp = self.app.get(uri)
        self.assertEquals(302,resp.status_code)
        self.assertTrue(resp.headers.has_key('Content-Length'))
        self.assertTrue(resp.headers['Location'].startswith("http://localhost/login"))
        
    def getResponseText(self, resp):
        text = ""
        for i in resp.response:
            text += i
        return text

    @test
    def User_can_authenticate_on_login_page(self):
        user = UserCreation.create_user_with_credentials()
        user.activate()
        data = {
                'username': 'userid',
                'password': 'password',
                'next': '/foo'
        }
        with app.test_client() as c:
            resp=c.get('http://localhost.local/login')
            text = self.getResponseText(resp)
            parser = MyHTMLParser()
            parser.feed(text)
            data['csrf_token']=parser.csrf
            resp = c.post('http://localhost.local/login', data=data)
            self.assertEqual(302, resp.status_code)
            self.assertEqual('http://localhost.local/foo',resp.headers['Location'])

    @test
    def Authentication_with_bad_userid_is_rejected(self):
        UserCreation.create_user_with_credentials()
        data = {
                'username': 'baduser',
                'password': 'password',
                'next': '/foo'
        }
        with app.test_client() as c:
            resp=c.get('http://localhost.local/login')
            text = self.getResponseText(resp)
            parser = MyHTMLParser()
            parser.feed(text)
            data['csrf_token']=parser.csrf
            resp = c.post('http://localhost.local/login', data=data)
            text = self.getResponseText(resp)
            self.assertEqual(200, resp.status_code)
            self.assertTrue("Bad username or password" in text)

    @test
    def Authentication_with_bad_password_is_rejected(self):
        UserCreation.create_user_with_credentials()
        data = {
                'username': 'userid',
                'password': 'badpassword',
                'next': '/foo'
        }
        with app.test_client() as c:
            resp=c.get('http://localhost.local/login')
            text = self.getResponseText(resp)
            parser = MyHTMLParser()
            parser.feed(text)
            data['csrf_token']=parser.csrf
            resp = c.post('http://localhost.local/login', data=data)
            text = self.getResponseText(resp)
            self.assertEqual(200, resp.status_code)
            self.assertTrue("Bad username or password" in text)




    def goToLoginPageAndGetCSRF(self, testClient):
        resp = testClient.get('http://localhost.local/login')
        text = self.getResponseText(resp)
        parser = MyHTMLParser()
        parser.feed(text)
        csrf = parser.csrf
        return csrf

    def login(self, c):
        user = UserCreation.create_user_with_credentials()
        user.activate()
        data = {'username':'userid', 'password':'password', 
            'next':'/v1/oauth2/auth'}
        data['csrf_token'] = self.goToLoginPageAndGetCSRF(c)
        resp = c.post('http://localhost.local/login', data=data)
        self.assertEqual(302, resp.status_code)
        self.assertEqual('http://localhost.local/v1/oauth2/auth', resp.headers['Location'])
        return resp


    def getCode(self, c):
        redirect_uri = 'https://test.app/redirecturi'
        application = Application.new("test app 7", "secret7", redirect_uri)
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
    @test
    def authorization_code_can_be_obtained_by_an_authenticated_user_using_correct_client_id_and_redirect_uri(self):
        self.loginAndGetCode()

    def doServerSideRequest(self, code):
        data = {'code':code, 
            'grant_type':'authorization_code', 
            'client_id':self.appid, 
            'client_secret':'secret7', 
            'redirect_uri':'https://test.app/redirecturi'}
        with app.test_client() as serverside:
            resp = serverside.post("https://localhost.local/v1/oauth2/token", data=data)
            data = json.loads(self.getResponseText(resp))
            self.assertTrue(data.has_key('access_token'))
            self.assertTrue(data.has_key('refresh_token'))
            self.assertEquals(data['token_type'], 'Bearer')
            self.assertEquals(data['expires_in'], 3600)
            return data

    @test
    def server_side_request(self):
        code = self.loginAndGetCode()
        self.doServerSideRequest(code)

    @test
    def get_user_info(self):
        code = self.loginAndGetCode()
        data = self.doServerSideRequest(code)
        with app.test_client() as serverside:
            resp = serverside.get("https://localhost.local/v1/users/me", headers=[('Authorization', '{0} {1}'.format(data['token_type'], data['access_token']))])
            self.assertEquals(resp.status_code, 200)
            data = json.loads(self.getResponseText(resp))
            self.assertTrue(data.has_key('userid'))

    def register(self, c, csrf):
        data = {'name':'Dr. Árvíztűrő Tükörfúrógépné Phd. Med. Szőrösfülű Vénsírásóúr', 
            'credentialtype':'password', 
            'identifier':'arvizturogepne', 
            'secret':'Th3 passWord ez unencriptid hir', 
            'csrf':csrf, 
            'email':'kukac@example.com', 
            'digest':'DEADBEEFBAD1FEED',
            'next': '/registered'}
        return c.post('https://localhost.local/v1/register', data=data)


    @test
    def register_with_real_name_and_password_and_get_our_info(self):
        with app.test_client() as c:
            csrf = self.goToLoginPageAndGetCSRF(c)
            self.register(c, csrf)
            data = {
                'username':'arvizturogepne', 
                'password':'Th3 passWord ez unencriptid hir', 
                'next':'/v1/users/me', 
                'csrf_token':csrf}
            resp = c.post('http://localhost.local/login', data=data)
            self.assertEqual(302, resp.status_code)
            location = resp.headers['Location']
            self.assertEquals(location, 'http://localhost.local/v1/users/me')
            
            resp = c.get('http://localhost.local/v1/users/me')
            text = self.getResponseText(resp)
            self.assertEquals(resp.status_code, 200)
            data = json.loads(text)
            self.assertTrue(data.has_key('userid'))
            self.assertEquals(u'kukac@example.com',data['email'])

    @test
    def logged_in_user_can_get_its_info(self):
        with app.test_client() as c:
            self.login(c)
            resp = c.get('http://localhost.local/v1/users/me')
            text = self.getResponseText(resp)
            self.assertEquals(resp.status_code, 200)
            data = json.loads(text)
            self.assertTrue(data.has_key('userid'))

    @test
    def user_cannot_register_twice(self):
        with app.test_client() as c:
            csrf = self.goToLoginPageAndGetCSRF(c)
            resp = self.register(c, csrf)
            logout_user()
            self.assertEquals(302, resp.status_code)
            self.assertEquals('http://localhost.local/registered', resp.headers['Location'])
        with app.test_client() as c:
            csrf = self.goToLoginPageAndGetCSRF(c)
            resp = self.register(c, csrf)
            logout_user()
            text = self.getResponseText(resp)
            self.assertEquals(200, resp.status_code)
            self.assertTrue("There is already a user" in text)
