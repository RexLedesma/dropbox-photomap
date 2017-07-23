"""
photomap of dropbox folder
"""

from os import environ
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_googlemaps import GoogleMaps
from photo_map import create_photomap

load_dotenv(join(dirname(__file__), '.env'))
GOOGLEMAPS_KEY = environ.get('GOOGLEMAPS_KEY')

APP = Flask(__name__, template_folder='templates')
GoogleMaps(APP, key=GOOGLEMAPS_KEY)

@APP.route('/')
def photomap():
    """
    Renders photomap to root route.
    """
    dbx_photomap = create_photomap()
    return render_template('index.html', photomap=dbx_photomap)

if __name__ == "__main__":
    APP.run(debug=True, use_reloader=True)