from twatson.unittest_annotations import Fixture, test
from pdoauth.models.KeyData import KeyData

class KeyDataTest(Fixture):
    
    def setUp(self):
        KeyData.query.delete()  # @UndefinedVariable
        self.KeyData_can_be_created_with_client_id__user_id__acess_key__and__refresh_key()
        
    def KeyData_can_be_created_with_client_id__user_id__acess_key__and__refresh_key(self):
        self.clientData = KeyData.new('client_id', 'user_id', 'access_key', 'refresh_key')
    
    @test
    def access_key_and_refresh_key_can_be_retrieved_by_client_id_and_user_id(self):
        clientData = KeyData.find('client_id', 'user_id')
        self.assertEquals(clientData.access_key,'access_key')
        self.assertEquals(clientData.refresh_key,'refresh_key')
    
    @test
    def None_is_returned_for_nonexistent_client_id(self):
        self.assertEquals(None, KeyData.find('nonexistent', 'user_id'))
        
    @test
    def None_is_returned_for_nonexistent_user_id(self):
        self.assertEquals(None, KeyData.find('client_id', 'nonexistent'))
        
    @test
    def None_is_returned_for_none_as_user_id(self):
        self.assertEquals(None, KeyData.find('client_id', None))
        
    @test
    def None_is_returned_for_none_as_client_id(self):
        self.assertEquals(None, KeyData.find(None, 'user_id'))