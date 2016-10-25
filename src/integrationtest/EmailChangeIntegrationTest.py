from test.helpers.EmailUtil import EmailUtil
from integrationtest.helpers.IntegrationTest import IntegrationTest, test
from integrationtest.helpers.UserTesting import UserTesting
from pdoauth.app import app
from integrationtest.helpers.CSRFMixin import CSRFMixin
from integrationtest import config
from pdoauth import Messages
import json
from pdoauth.models.User import User


class EmailChangeIntegrationTest(IntegrationTest, UserTesting, EmailUtil, CSRFMixin):

    
    def test_logged_in_user_can_initiate_changing_email_address(self):
        with app.test_client() as client:
            resp = self.initiateEmailChange(client)
            self.assertEmailChangeIsInitiated(resp)

    
    def test_email_change_can_be_confirmed(self):
        with app.test_client() as client:
            resp = self.initiateEmailChange(client)
            self.assertEmailChangeIsInitiated(resp)
            data = dict(confirm=True,secret=self.secret)
            resp = client.post(config.BASE_URL + '/v1/confirmemailchange', data=data)
            text = self.getResponseText(resp)
            self.assertEqual(200,resp.status_code)
            self.assertEqual(Messages.emailChanged, json.loads(text)["message"])
            user=User.get(self.userid)
            self.assertEqual(self.newEmail,user.email)
