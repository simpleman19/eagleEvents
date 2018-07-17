from flask import Blueprint, render_template

main = Blueprint('main', __name__)


@main.route('/', methods=['GET'])
@main.route('/home', methods=['GET'])
def home():
    return render_template('test.html.j2', test='"Test Argument to Page"')

