#pylint: disable=invalid-name, no-member, too-many-arguments
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Integer, String
from pdoauth.app import db
from pdoauth.ModelUtils import ModelUtils

class KeyData(db.Model, ModelUtils):
    __tablename__ = 'key_data'
    id = Column(Integer,primary_key=True)
    client_id = Column(String)
    user_id = Column(String)
    access_key = Column(String)
    refresh_key = Column(String)
    authorization_code = Column(String)

    @classmethod
    def new(cls, client_id, user_id, access_key, refresh_key):
        keyData = cls(client_id, user_id, access_key, refresh_key)
        keyData.save()
        return keyData

    def __init__(self, client_id, user_id=None, access_key=None, refresh_key=None, authorization_code=None):
        self.client_id = client_id
        self.access_key = access_key
        self.user_id = user_id
        self.refresh_key = refresh_key
        self.authorization_code = authorization_code
        self.save()

    @classmethod
    def find_by_refresh_token(cls, client_id, refreshToken):
        return cls.query.filter_by(client_id=client_id, refresh_key = refreshToken).first()

    @classmethod
    def find_by_code(cls, client_id, authorization_code):
        return cls.query.filter_by(client_id=client_id, authorization_code = authorization_code).first()

    @classmethod
    def byCode(cls,code):
        return cls.query.filter_by(authorization_code=code).first()

    def __repr__(self, *args, **kwargs):
        return "KeyData(client_id={0}, user_id={1}, access_key={2}, refresh_key={3}, authorization_code={4})".format(
            self.client_id,
            self.user_id,
            self.access_key,
            self.refresh_key,
            self.authorization_code)
