from flask_login import login_user
from test.helpers.UserUtil import UserUtil

class AuthenticatedSessionMixin(UserUtil):
    def makeSessionAuthenticated(self):
        user = self.createUserWithCredentials()
        user.activate()
        user.set_authenticated()
        user.save()
        login_user(user)
        self.userid = user.userid
