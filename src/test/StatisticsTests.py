# pylint: disable=line-too-long
from test.helpers.PDUnitTest import PDUnitTest, test
from test.helpers.FakeInterFace import FakeInterface
from pdoauth.Statistics import Statistics
from pdoauth.models.User import User
from pdoauth.models.Application import Application
from pdoauth.models.Assurance import Assurance
from test.helpers.UserUtil import UserUtil
from test.helpers.AuthProviderUtil import AuthProviderUtil
from pdoauth.Responses import Responses
import json

class TestStatter(Statistics, FakeInterface, Responses):
    pass

class StatisticsTest(PDUnitTest, UserUtil, AuthProviderUtil):

    def setUp(self):
        self.setupRandom()
        self.controller = TestStatter()
        self.stats = self.controller.getStats()

    @test
    def statistics_contain_user_count(self):
        self.assertEqual(self.stats['users'], User.query.count())  # @UndefinedVariable

    @test
    def statistics_contain_app_count(self):
        self.assertEqual(self.stats['applications'], Application.query.count())  # @UndefinedVariable

    @test
    def statistics_contain_assurance_counts(self):
        self.assertTrue(isinstance(self.stats['assurances'],dict))

    @test
    def assurance_counts_include_all_assurances(self):
        assurances = list()
        for assurance in Assurance.query.distinct(Assurance.name):  # @UndefinedVariable
            assurances.append(assurance.name)
        self.assertEqual(sorted(self.stats['assurances'].keys()),sorted(assurances))

    @test
    def assurance_counts_are_correct(self):
        assurercount = Assurance.query.filter(Assurance.name=='assurer').count()  # @UndefinedVariable
        self.assertEqual(self.stats['assurances']['assurer'],assurercount)

    @test
    def assurance_counts_are_increasing_with_new_assurance(self):
        assurercount = Assurance.query.filter(Assurance.name=='assurer').count()  # @UndefinedVariable
        user = User.query.first()  # @UndefinedVariable
        Assurance.new(user, 'assurer', user).save()
        self.stats = self.controller.getStats()
        self.assertEqual(self.stats['assurances']['assurer'],assurercount+1)

    @test
    def user_counts_are_increasing_with_new_user(self):
        usercount = User.query.count()  # @UndefinedVariable
        self.createUserWithCredentials()
        self.stats = self.controller.getStats()
        self.assertEqual(self.stats['users'],usercount+1)

    @test
    def application_counts_are_increasing_with_new_application(self):
        applicationCount = Application.query.count()  # @UndefinedVariable
        self.createApp()
        self.stats = self.controller.getStats()
        self.assertEqual(self.stats['applications'],applicationCount+1)

    @test
    def getstatsAsJson_gives_the_statistics_in_json(self):
        applicationCount = Application.query.count()  # @UndefinedVariable
        stats = self.controller.getStatsAsJson()
        self.stats=json.loads(stats.data)
        self.assertEqual(self.stats['applications'],applicationCount)
