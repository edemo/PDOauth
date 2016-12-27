import random
import string

class RandomUtil(object):

    @staticmethod
    def mkRandomString(length):
        return ''.join(
            random.choice(string.ascii_letters) for _ in range(length))

    def mkRandomPassword(self):
        return ''.join((
            random.choice(string.ascii_lowercase) +
            random.choice(string.ascii_uppercase) +
            random.choice(string.digits)
            ) for _ in range(8))

    def setupRandom(self):
        self.randString = self.mkRandomString(6)

    @classmethod
    def createRandomUserId(cls):
        userid = "aaa_{0}".format(cls.mkRandomString(6))
        return userid

    @classmethod
    def createRandomEmailAddress(cls):
        return "email{0}@example.com".format(cls.mkRandomString(6))

    def setupUserCreationData(self, userid=None, password=None, email=None):
        self.setupRandom()
        if email is None:
            email = self.createRandomEmailAddress()
        if userid is None:
            userid = self.createRandomUserId()
        if password is None:
            password = "{0}".format(self.mkRandomPassword())
        self.userCreationEmail = email
        self.userCreationUserid = userid
        self.usercreationPassword = password
