import random
import string

class RandomUtil(object):

    def mkRandomString(self, length):
        return ''.join(random.choice(string.ascii_letters) for _ in range(length))
    
    def mkRandomPassword(self):
        return ''.join((
            random.choice(string.ascii_lowercase) +
            random.choice(string.ascii_uppercase) +
            random.choice(string.digits)
            ) for _ in range(8))
    
    def setupRandom(self):
        self.randString = self.mkRandomString(6)

    def createRandomUserId(self):
        self.setupRandom()
        userid = "aaa_{0}".format(self.randString)
        return userid

    def setupUserCreationData(self, userid=None, password=None, email=None):
        self.setupRandom()
        if email is None:
            email = "email{0}@example.com".format(self.randString)
        if userid is None:
            userid = self.createRandomUserId()
        if password is None:
            password = "{0}".format(self.mkRandomPassword())
        self.usercreation_email = email
        self.usercreation_userid = userid
        self.usercreation_password = password
        return userid, password, email
