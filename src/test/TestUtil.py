# -*- coding: UTF-8 -*-
from pdoauth.CredentialManager import CredentialManager
from flask_login import login_user

class UserCreation(object):
    @classmethod
    def create_user_with_credentials(self):
        return CredentialManager.create_user_with_creds('password', 'userid', 'password')

class AuthenticatedSessionMixin(UserCreation):
    def makeSessionAuthenticated(self):
        user = self.create_user_with_credentials()
        user.activate()
        user.set_authenticated()
        user.save()
        login_user(user)
        self.userid = user.id
