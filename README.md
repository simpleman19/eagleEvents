# eagleEvents

Steps to get running
1. Clone repo
2. Install python 3.6 or 3.7
3. pip install --global virtualenv
4. virtualenv .env
5. source .env/bin/activate (terminal should have a prefix of (.env)
6. pip install -r requirements.txt (Should install all dependencies)
7. python manage.py runserver (Should have a link in terminal to connect to app)

If you want to run with live reloading to allow for auto refresh of pages
python manage.py livereload