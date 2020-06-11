NOTES
=====

Twitter Clone: SpringBoard SE Track

Notes:
-----

- on the homepage view method on line 350
 the way I'm showing messages iss very hacky
 (grap all messages from users I'm following then inserting my messages at the top)
  and expensive(making so many queries by using looping over followed.messages)

- testng guide on springboard website:

    - Prompt: Does User.create successfully create a new user given valid credentials?
    Does User.create fail to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail?

    - The User model given in this exercise does not contain a
     calss method with the name of create.