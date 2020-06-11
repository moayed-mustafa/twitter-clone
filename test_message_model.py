"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

from sqlalchemy.exc import IntegrityError

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


from app import app
db.create_all()

class MessageModelTestCAse(TestCase):
    def setUp(self):

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        """Create test client, add sample data."""
        self.user = User.signup(
                email="test@test.com",
                username="testuser",
                password="thisisapassword",
                image_url = 'https://images.unsplash.com/photo-1575436231712-50839f5aa73a?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=882&q=80'
            )
        self.user_two = User.signup(
                email="test@test2.com",
                username="testuser2",
                password="thisisapassword2",
                image_url = 'https://images.unsplash.com/photo-1575436231712-50839f5aa73a?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=882&q=80'
            )
        db.session.commit()
        self.client = app.test_client()
        # ==============================================================================================================
    def test_model(self):
        """ does Message Model works?"""
        msg = Message(text='This is a message', user_id=self.user.id)
        db.session.add(msg)
        db.session.commit()

        self.assertIn(msg,self.user.messages )
        self.assertEqual(len(self.user.messages), 1)

        # ==============================================================================================================

    def test_message_add(self):
        """ does it add a message?"""
        # create message
        msg = Message(text='This is a message', user_id=self.user.id)
        db.session.commit()
        self.user.messages.append(msg)
        self.assertIn(msg, self.user.messages)
        # ==============================================================================================================

    def test_message_like(self):
        """ does it add a like?"""
        # create message
        msg = Message(text='This is a message', user_id=self.user.id)
        db.session.commit()
        self.user.messages.append(msg)
        # message not liked:
        self.assertNotIn(msg, self.user_two.likes)
        # message liked:
        self.user_two.likes.append(msg)
        self.assertIn(msg, self.user_two.likes)
        # unlike a message
        self.user_two.likes.remove(msg)
        self.assertNotIn(msg, self.user_two.likes)

    def test_message_delete(self):
        """ can we delete a message?"""
        msg = Message(text='This is a message', user_id=self.user.id)
        db.session.commit()
        self.user.messages.append(msg)
        self.assertIn(msg,self.user.messages)
        self.user.messages.remove(msg)
        # db.session.commit()
        self.assertNotIn(msg,self.user.messages)

