# dropbox-photomap

## Setup
1. Clone repository
2. `pip install -U Flask python-dotenv flask-googlemaps dropbox`
3. Add `.env` file with the following variables:
    * Dropbox access token: https://www.dropbox.com/developers/apps/create
    * Google Maps api key: https://developers.google.com/maps/documentation/javascript/get-api-key
    * Dropbox folder path with your pictures/videos
```
DROPBOX_ACCESS_TOKEN='DROPBOX_ACCESS_TOKEN'
GOOGLEMAPS_KEY='GOOGLEMAPS_KEY'
DROPBOX_FOLDER_PATH='/PATH_OF_FOLDER_WITH_PICTURES_AND_VIDEOS'
```
4. `python app.py`
5. Point your browser to http://127.0.0.1:5000/
