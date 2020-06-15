"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY
from flask import Flask


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


# ===================================================================================================
class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        db.session.commit()

        self.testmsg = Message(text='This is a messge by test user', user_id=self.testuser.id)
        db.session.add(self.testmsg)
        db.session.commit()

        # import pdb
        # pdb.set_trace()
        self.MSG = "MSG"

# ===================================================================================================

    def test_add_message_logged_in(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.filter(Message.text == 'Hello').first()
            self.assertEqual(msg.text, "Hello")
    # ===================================================================================================

    def test_show_message_logged_in(self):
        """ can we see a message"""
        # create a msg

        # make a client and session block
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                sess[self.MSG] =self.testmsg.id

            #  make a request
            url = f"/messages/{self.testmsg.id}"
            res = client.get(url)
            # check the response
            self.assertEqual(res.status_code, 200)
            # check the html
            html = res.get_data(as_text=True)
            tag = f'<p class="single-message">{self.testmsg.text}</p>'
            self.assertIn(tag, html)
    # ===================================================================================================

    def test_delete_message_logged_in(self):
        """ can we delete a message?"""
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                sess[self.MSG] = self.testmsg.id

            url = f"/messages/{self.testmsg.id}/delete"
            res = client.post(url)
            self.assertEqual(res.status_code, 302)
            self.assertEqual(res.location,f'http://localhost/users/{self.testuser.id}' )
            # the html
            tag = f'<a href="/users/{ self.testuser.id }">@{self.testuser.username}</a>'
            tag = '<title>Redirecting...</title>'
            html = res.get_data(as_text=True)
            self.assertIn(tag, html)
    # ===================================================================================================

    def test_add_message_logged_out(self):
        with self.client as client:
            res = client.post("/messages/new", data={"text": "Hello"})
            self.assertEqual(res.status_code, 302)
            self.assertEqual(res.location, 'http://localhost/')
# ===================================================================================================

    def test_delete_message_logged_out(self):
        with self.client as client:
            url = f"/messages/{self.testmsg.id}/delete"
            res = client.post(url)
            self.assertEqual(res.status_code, 302)
            self.assertEqual(res.location, 'http://localhost/')
# ===================================================================================================

    def test_show_message_logged_out(self):
        with self.client as client:
            url = f"/messages/{self.testmsg.id}"
            res = client.get(url)
            self.assertEqual(res.status_code, 302)
            self.assertEqual(res.location, 'http://localhost/')



