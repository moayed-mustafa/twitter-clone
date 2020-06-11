"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

from sqlalchemy.exc import IntegrityError

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
    # these guys will delete everything from these models:
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()
    # ==============================================================================================================

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
    # ==============================================================================================================

    def test_followig_methods(self):
        """ testing
            is_followed_by
            is_following instance methods
        """
        # create a user
        u1 = User.signup(
            username="testuser",
            email="test@test.com",
            password="HASHED_PASSWORD",
            image_url="https://images.unsplash.com/photo-1584339093038-949dff9ed942?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1950&q=80"
        )
        u2 = User.signup(
            username="testuser2",
            email="test2@test2.com",
            password="HASHED_PASSWORD",
            image_url="https://images.unsplash.com/photo-1584339093038-949dff9ed942?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1950&q=80"

        )
        db.session.commit()
        # u1 not following u2, u2 not followed by u1
        self.assertEqual(u1.is_following(u2), False)
        self.assertEqual(u2.is_followed_by(u1), False)
        # u1 following u2,u2 not followed by u1
        u1.following.append(u2)
        db.session.commit()
        self.assertEqual(u1.is_following(u2), True)
        self.assertEqual(u2.is_followed_by(u1), True)

 # ==============================================================================================================

    def test_user_signup(self):
        """ tests the signup class method """
        # user signed up correctly
        uname = 'test'
        email = 'test@thisuser.com'
        pw = 'thisisapassword'
        image_url = 'https://images.unsplash.com/photo-1575436231712-50839f5aa73a?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=882&q=80'
        sign_up_user= User.signup(uname, email, pw, image_url)
        db.session.commit()
        user = User.query.filter_by(username=uname).first()
        self.assertEqual(user, sign_up_user)
        # user's sign up raises an error
        with self.assertRaises(IntegrityError):
            sign_up_user= User.signup(uname, email, pw, image_url)
            db.session.commit()
            self.sign_up_user
     # ==============================================================================================================

    def test_user_authenticate(self):
        """ tests the signup class method """
        # create a user
        u = User.signup(
            username="testuser",
            email="test@test.com",
            password="thisisapassword",
            image_url = 'https://images.unsplash.com/photo-1575436231712-50839f5aa73a?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=882&q=80'
        )

        db.session.commit()
        # user authenticate correctly
        authenticated = User.authenticate("testuser", "thisisapassword")
        user = User.query.filter_by(username="testuser").first()
        self.assertEqual(user, authenticated)
        # user not authenticate because  the password in invalid
        authenticated = User.authenticate("testuser", "thisispassword")
        self.assertEqual(authenticated, False)
        # user not authenticate because the uesrname in invalid
        authenticated = User.authenticate("testuserman", "thisisapassword")
        self.assertEqual(authenticated, False)