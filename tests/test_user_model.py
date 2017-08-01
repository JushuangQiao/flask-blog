# coding=utf-8

import unittest
from app.models.models import User

'''
class TestUserModel(unittest.TestCase):

    def test_password_setter(self):
        u = User(username='test', email='test@gmail.com', password='123456')
        # u = User(password='123456') delete
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(username='test', email='test@gmail.com', password_hash='123456')
        # u = User(password='123456')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verificatwion(self):
        u = User(username='test', email='ver@gmail.com', password='123456')
        # u = User(password='123456')
        self.assertTrue(u.verify_password('123456'))
        self.assertFalse(u.verify_password('test'))

    def test_password_salts_are_random(self):
        self.assertFalse(User(username='a', email='a@qq.com', password='123456').password_hash ==
                         User(username='b', email='b@qq.com', password='123456').password_hash)
'''
