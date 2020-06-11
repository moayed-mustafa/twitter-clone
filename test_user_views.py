""" Test user view methods """
#    FLASK_ENV=production python -m unittest test_user_views.py

import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY
from flask import Flask

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTEstCase(TestCase):
    def setUp(self):

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        db.session.commit()

        self.testmsg = Message(text='This is a messge by test user', user_id=self.testuser.id)
        db.session.add(self.testmsg)
        db.session.commit()
        self.MSG = "MSG"

    def test_user_login(self):
        with self.client as client:
            # first logout self.testuser
            logout = client.get('/logout')
            self.assertEqual(logout.status_code, 302)
            self.assertEqual(logout.location, 'http://localhost/login')

            # test an existing user
            # this is a redirect
            res = client.post(logout.location, data={"username":self.testuser.username, "password":self.testuser.password})
            # # test the user creadintials
            self.assertEqual(res.status_code, 302)
            # html = res.get_data()
            # import pdb;
            # pdb.set_trace()



            # test an non user
            # this is a rendering condition
            resp = client.post('/login', data={"username":'notauser', "password":'12345678'})
            self.assertEqual(resp.status_code, 200)
            # tag = "<h1>What's Happening?</h1>"
            # html = res.get_data(as_text=True)
            # self.assertIn(tag, html)

