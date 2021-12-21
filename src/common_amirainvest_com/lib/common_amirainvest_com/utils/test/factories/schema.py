"""
https://factoryboy.readthedocs.io/en/stable/orms.html#sqlalchemy
https://factoryboy.readthedocs.io/en/stable/index.html
"""
import factory

from common_amirainvest_com.schemas.schema import Users
from common_amirainvest_com.utils.test.factories.base import FactoryBase


class UsersFactory(FactoryBase):
    class Meta:
        model = Users

    sub = "Test"
    name = "Test Name"
    username = "Test Username"
    picture_url = "https://test.com"
    email = "test@test.com"
    email_verified = True
factory.SubFactory
