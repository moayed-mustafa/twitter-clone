# Warbler
- Warbler is a twitter clone application that creates a social network where users could post
about topics they are interested in, follow other users and message them directly.

## Technology
- Warbler relies on postgres for the database and Flask Python for building the backend api.
- the frontend UI is done using Jinja templates and styled using css

## Installition:
- To install the code locally:-

- Create a virtual environment in the root of the project : python -m venv venv
Activate the virtual environment on a mac : source venv/bin/activate
Activate the virtual environment on windows : venv/Scripts/activate.bat
Inside a virtual environment run : pip install -r requirements.txt
Create an empty postgresql database using the following command on terminal :-

- createdb word-search-db
- Run seed.py on terminal using python3 seed.py to create the tables and some data.

- Create an empty database for running test files and call it warbler

- All test files are written in unittest, install it likewise: pip install unittest2

