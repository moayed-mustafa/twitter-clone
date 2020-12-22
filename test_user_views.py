""" Test user view methods """
#    FLASK_ENV=production python -m unittest test_user_views.py

import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows


os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY
from flask import Flask
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from sqlalchemy.event import listens_for




db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    def setUp(self):
        # remove everything before each test
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        # setup the client
        self.client = app.test_client()
        #  setup  test users
        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser_two = User.signup(username="testuser2",
                                    email="test2@test2.com",
                                    password="testuser123",
                                    image_url=None)



        # let testusers follow each other:
        self.testuser.following.append(self.testuser_two)
        self.testuser_two.following.append(self.testuser)
        # db.session.add_all([self.testuser, self.testuser_two])
        db.session.expire_on_commit=False
        db.session.commit()
        #  set up a test message
        self.testmsg = Message(text='This is a messge by test user', user_id=self.testuser.id)
        db.session.add(self.testmsg)
        db.session.commit()

        self.MSG = "MSG"
    # ===================================================================================================
        # Test logout

    def test_user_logout(self):
        # 'logged out successfuly', 'success'
        with self.client as client:

            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            res = client.get('/logout')
                # Assert
            self.assertEqual(res.status_code, 302)
            self.assertEqual(res.location, 'http://localhost/login')
            # test flash messaggin
            # make a new session to put them in
            second_request = client.get('/logout')
            with client.session_transaction() as sess:
                flash_message_danger = dict(sess['_flashes']).get('danger')
                flash_message_success = dict(sess['_flashes']).get('success')
            self.assertIsNotNone(flash_message_danger, sess['_flashes'])
            self.assertIsNotNone(flash_message_success, sess['_flashes'])
            self.assertEqual(flash_message_danger, 'log in first')
            self.assertEqual(flash_message_success, 'logged out successfuly')
    # ===================================================================================================
    def test_user_login(self):
        with self.client as client:
            # testing a get request
            res = client.get('/login')
            self.assertEqual(res.status_code, 200)
            tag = '<h2 class="join-message">Welcome back.</h2>';
            html = res.get_data(as_text=True)
            self.assertIn(tag, html)
            # sending a post request
            post_res = client.post('/login', data={"username": self.testuser.username, "password": self.testuser.password})
            self.assertEqual(post_res.status_code, 200)
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            post_tag = f'<p>@{self.testuser.username}</p>'
            html = post_res.get_data(as_text=True)
            self.assertIn(tag,html)
# ===================================================================================================
    def test_user_list(self):
        with self.client as client:
            res = client.get('/users')
            # Assert
            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)
            tag = f'<p>@{self.testuser.username }</p>'
            self.assertIn(tag, html)
# ===================================================================================================
    def test_user_show(self):
        with self.client as client:
            res = client.get(f'users/{self.testuser.id}')
            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)
            tag = f'<a href="/users/{ self.testuser.id }">@{ self.testuser.username }</a>'
            self.assertIn(tag, html)

# ===================================================================================================
    def test_user_show_following(self):
        with self.client as client:
            name = self.testuser_two.username
            # testing with no user in session:
            res = client.get(f'users/{self.testuser.id}/followers')
            self.assertEqual(res.status_code, 302)
            self.assertEqual(res.location, 'http://localhost/')

            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            res = client.get(f'users/{self.testuser.id}/followers')
            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)
            tag = f'<p>@{name}</p>'
            self.assertIn(tag, html)
# ===================================================================================================
    def test_user_show_followers(self):
        with self.client as client:
            name = self.testuser_two.username
            # testing with no user in session:
            res = client.get(f'users/{self.testuser.id}/followers')
            self.assertEqual(res.status_code, 302)
            self.assertEqual(res.location, 'http://localhost/')

            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            res = client.get(f'users/{self.testuser.id}/followers')
            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)
            tag = f'<p>@{name}</p>'
            self.assertIn(tag, html)
# ===================================================================================================
    def test_add_follow(self):
        with self.client as client:
            id = self.testuser_two.id
            name = self.testuser_two.username
            # test with no user in session
            res = client.post(f'users/follow/{self.testuser.id}')
            with client.session_transaction() as sess:
                flash_message_danger = dict(sess['_flashes']).get('danger')
            # Assert
            self.assertEqual(res.status_code, 302)
            self.assertEqual(res.location, 'http://localhost/')
            self.assertEqual(flash_message_danger, 'Access unauthorized.')

        # test with a user in session
        with client.session_transaction() as sess:
            sess[CURR_USER_KEY] = self.testuser.id
        # test an existing user
        res =client.post(f'users/follow/{id}', follow_redirects=True)
            # Assert
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)
        tag = f'<p>@{name}</p>'
        self.assertIn(tag, html)
        # test a non-existing user
        res = client.post('users/follow/9000')
            # Assert
        self.assertEqual(res.status_code, 404)
        html = res.get_data(as_text=True)
        tag = '<title>404 Not Found</title>'
        self.assertIn(tag, html)
# ===================================================================================================
    def test_remove_follow(self):
        with self.client as client:
            id = self.testuser_two.id
            name = self.testuser_two.username
            # test with no user in session
            res = client.post(f'users/stop-following/{self.testuser.id}')
            with client.session_transaction() as sess:
                flash_message_danger = dict(sess['_flashes']).get('danger')
            self.assertEqual(res.status_code, 302)
            self.assertEqual(res.location, 'http://localhost/')
            self.assertEqual(flash_message_danger, 'Access unauthorized.')

              # test with a user in session
        with client.session_transaction() as sess:
            sess[CURR_USER_KEY] = self.testuser.id
         # test an existing user
        res =client.post(f'users/follow/{id}', follow_redirects=True)
            # Assert
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)
        tag = f'<p>@{name}</p>'
        self.assertIn(tag, html)
        # test a non existing user
        res = client.post('users/follow/4')
        self.assertEqual(res.status_code, 404)
# ========================================================================================================
    def test_add_like_no_user_in_session(self):
         with self.client as client:
                id = self.testmsg.id

                url = f'users/add_like/{id}'
                res = client.post(url)
                with client.session_transaction() as sess:
                    flash_message_danger = dict(sess['_flashes']).get('danger')
                    #Assert
                self.assertEqual(res.status_code, 302)
                self.assertEqual(res.location, 'http://localhost/')
                self.assertEqual(flash_message_danger, 'got to be signed up first')

# ===================================================================================================
    def test_add_like_with_user_in_session(self):
        with self.client as client:
            id = self.testmsg.id
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                flash_message_success = dict(sess['_flashes']).get('success')

            url = f'users/add_like/{id}'
            res = client.post(url)
            self.assertEqual(res.status_code, 302)
            self.assertEqual(res.location, 'http://localhost/')
            self.assertEqual(flash_message_success, 'like added')
            # test flash messagin
            with client.session_transaction() as sess:
                 flash_message_success = dict(sess['_flashes']).get('success')
            self.assertEqual(flash_message_success, 'like added')
# ===================================================================================================
    def test_delete_user_unauthorized(self):
            with self.client as client:
                # no user in session
                res = client.post('/users/delete')
                self.assertEqual(res.status_code, 302)
                with client.session_transaction() as sess:
                    flash_message_success = dict(sess['_flashes']).get('danger')
                self.assertEqual(flash_message_success, 'Access unauthorized.')

 # ===================================================================================================
    def test_delete_user_authorized(self):
            with self.client as client:
                # no user in session
                    # add user to session
                with client.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.testuser.id
                res = client.post('/users/delete')
                self.assertEqual(res.status_code, 302)
                self.assertEqual(res.location, 'http://localhost/signup')


 # ===================================================================================================
    def test_home_page(self):
        with self.client as client:
            # no user in session
            res = client.get('/')
            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)
            tag = '<h4>New to Warbler?</h4>'
            self.assertIn(tag, html)
            # add user to session
            #
# ===================================================================================================
    def test_home_page_with_user_in_session(self):
            with self.client as client:
                with client.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.testuser.id
                res = client.get('/')
                self.assertEqual(res.status_code, 200)
                html = res.get_data(as_text=True)
                tag = f'<p>@{self.testuser.username}</p>'
                self.assertIn(tag, html)
# ===================================================================================================

# this function with the event decorator should facilitate strong refrence
def strong_reference_session(session):
    listens_for(session, "pending_to_persistent")
    listens_for(session, "deleted_to_persistent")
    listens_for(session, "detached_to_persistent")
    listens_for(session, "loaded_as_persistent")

    def strong_ref_object(sess, instance):
        if 'refs' not in sess.info:
            sess.info['refs'] = refs = set()
        else:
            refs = sess.info['refs']

        refs.add(instance)


    listens_for(session, "persistent_to_detached")
    listens_for(session, "persistent_to_deleted")
    listens_for(session, "persistent_to_transient")
    def deref_object(sess, instance):
        sess.info['refs'].discard(instance)

my_session = Session()
strong_reference_session(my_session)