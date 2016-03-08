from twatson.unittest_annotations import Fixture, test
from pdoauth.models.KeyData import KeyData

class KeyDataTest(Fixture):

    def setUp(self):
        KeyData('client_id2', 'user_id2', 'access_key2', 'refresh_key2', 'authorization_code2')

    @test  
    def KeyData_can_be_created_with_client_id__user_id__acess_key__refresh_key_and_authorization_code(self):
        self.clientData = KeyData.new('client_id', 'user_id', 'access_key', 'refresh_key')
    
    @test
    def Access_key_and_refresh_key_can_be_retrieved_by_client_id_and_refresh_token(self):
        clientData = KeyData.find_by_refresh_token('client_id2', 'refresh_key2')
        self.assertEquals(clientData.access_key,'access_key2')
        self.assertEquals(clientData.refresh_key,'refresh_key2')
        self.assertEquals("KeyData(client_id=client_id2, user_id=user_id2, access_key=access_key2, refresh_key=refresh_key2, authorization_code=authorization_code2)",
                          "{0}".format(clientData))
        

    @test
    def Access_key_and_refresh_key_can_be_retrieved_by_client_id_and_authorizaton_code(self):
        clientData = KeyData.find_by_code('client_id2', 'authorization_code2')
        self.assertEquals(clientData.access_key,'access_key2')
        self.assertEquals(clientData.refresh_key,'refresh_key2')
        self.assertEquals("KeyData(client_id=client_id2, user_id=user_id2, access_key=access_key2, refresh_key=refresh_key2, authorization_code=authorization_code2)",
                          "{0}".format(clientData))
    
    @test
    def None_is_returned_for_nonexistent_client_id_when_looking_up_keydata_by_code(self):
        clientData = KeyData.find_by_code('nonexistent', 'authorization_code2')
        self.assertEqual(clientData, None)

    @test
    def None_is_returned_for_nonexistent_code_when_looking_up_keydata_by_code(self):
        clientData = KeyData.find_by_code('client_id2', 'nonexistent')
        self.assertEqual(clientData, None)

    @test
    def None_is_returned_for_nonexistent_client_id_when_looking_up_keydata_by_refresh_token(self):
        clientData = KeyData.find_by_refresh_token('nonexistent', 'refresh_key2')
        self.assertEqual(clientData, None)

    @test
    def None_is_returned_for_nonexistent_refresh_token_when_looking_up_keydata_by_refresh_token(self):
        clientData = KeyData.find_by_refresh_token('client_id2', 'nonexistent')
        self.assertEqual(clientData, None)
        
    @test
    def New_always_creates_new_keydata(self):
        currentKeyData = KeyData.find_by_code('client_id2', 'authorization_code2')
        KeyData('client_id2', 'user_id2', 'access_key2', 'refresh_key2', 'authorization_code3')
        newKeyData = KeyData.find_by_code('client_id2', 'authorization_code3')
        self.assertNotEqual(currentKeyData, newKeyData)
