NOTES
=====

Twitter Clone: SpringBoard SE Track

## Notes:
  -----

- on the homepage view method on line 350
  the way I'm showing messages is very hacky
  (grap all messages from users I'm following then inserting my messages at the top)
  and expensive(making so many queries by using looping over followed.messages)

  - on delete_user route on line 283, deleting a user object like this: db.session.delete(g.user)
    tends to create an integrity error for deleting the messages associated with the user,
    my suspecioin is that the user get's removed and then Message.user_id get's turned to null
    on table messages which then makes an issue for deleting the messages, I used
    User.query.filter_by(id = g.user.id).delete() instead.




## Testing Notes:
----------------

  1- on test_user_logout() in test_user_views.py, I can't test the request
  code, location and the session in one go, if I make a session_transaction and
  add to it [self.testuser.id] in addetion to "_flashes" I get an error
  I presume the issue is that the request has to be made first before the session is
  filled with the '_flashes', on the other hand, if I make the request first then make
  a session transaction and add to it [self.testuser.id] it's not bound on the session.
  so my solution was to make two seprate requests one to test logout and one to test the flashing.

  2- In adding and removing follow test cases (lines 157, 188 respectively), I find myself forced to send a request to a
  follower with a non existing id, and test for 404. the reason being that when I tried to
  test for testuser_two I get a DetachedInstanceError where Instance <User at 0x1029352b0> is not bound to a session, I learned that the problem is  my object is being detached
  once the session is closed, after doing some work to change the state of the object to persistent,
  by copying the function (strong_reference_session) from sqlalchemy docs, I still ended up with the same error.

  3- After attempting to solve  point no.2 for a while, I ended up saving the id of testuser_two before I open up a flask session and then making a a request to my end point for following and removing a follow
  using the id variable. this seems like a legitimate solution but I'm yet to understand how to solve the
  issues arised from the session being closed and how to change the state of my object to being persistent.