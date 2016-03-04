from pdoauth.models.User import User
from pdoauth.models.Application import Application
from pdoauth.models.Assurance import Assurance

class Statistics(object):

    def getStats(self):
        ret = dict()
        ret['users'] = User.getStats()
        ret['applications'] = Application.getStats()
        ret['assurances'] = Assurance.getStats()
        return ret
    
    def getStatsAsJson(self):
        return self.makeJsonResponse(self.getStats())