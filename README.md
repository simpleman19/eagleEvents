# eagleEvents

Steps to get running
1. Clone repo
2. Install python 3.6 or 3.7
3. `pip3 install --global virtualenv` (--global may not be required on mac)
4. `virtualenv .env -p python3`
5. `source .env/bin/activate` (terminal should have a prefix of (.env)
6. `pip3 install -r requirements.txt` (Should install all dependencies)
7. `python manage.py runserver` (Should have a link in terminal to connect to app)

If you want to run with live reloading to allow for auto refresh of pages

`python manage.py livereload`

Database seed - This will wipe your current database automatically

`python manage.py seed`


Always be sure that you are inside your virtual environment (.env should be prepended to your terminal prompt)


In order to reactivate it:

`source .env/bin/activate`


I am using blueprints for all routes so it is much cleaner, work basically the same as adding a route directly to the app
just without the nasty import structure to get app to every route file


I defined certain things as lazy loading (Don't load on intial database query) if you
think something is misdefined as lazy/not lazy then feel free to change it for speed


Jinja Page
http://jinja.pocoo.org/docs/2.10/templates/

ORM Basic Reference
http://flask-sqlalchemy.pocoo.org/2.3/quickstart/

Flask Documentation
http://flask.pocoo.org/docs/1.0/