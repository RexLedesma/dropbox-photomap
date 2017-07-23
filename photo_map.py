"""
Application to map photo data from photos folder and render locations on
google maps
"""

from os import environ
from os.path import join, dirname
from base64 import b64encode
from dotenv import load_dotenv
from flask_googlemaps import Map
import dropbox

load_dotenv(join(dirname(__file__), '.env'))
DROPBOX_ACCESS_TOKEN = environ.get('DROPBOX_ACCESS_TOKEN')
DBX = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

def list_folder_photos_locations():
    """
    Returns `Markers` of photos/videos for `NYC July 2017` folder and
    parses out photos with no location metadata
    """
    response = DBX.files_list_folder('/NYC July 2017', include_media_info=True)
    photos = response.entries

    # remove files that do not have location metadata
    entries = [f for f in photos if f.media_info and f.media_info.get_metadata().location]

    # map data to lat/long json
    markers = [convert_metadata_to_marker(metadata) for metadata in entries]

    return markers

def convert_metadata_to_marker(metadata):
    """
    Converts Dropbox FileMetadata to Marker object for google maps.
    """
    gps_coord = metadata.media_info.get_metadata().location
    uri = get_thumbnail_uri(metadata)

    return({
        'lat': gps_coord.latitude,
        'lng': gps_coord.longitude,
        'infobox': ("<img alt='dbx thumbnail' src=" + uri + '>')
    })

def get_thumbnail_uri(metadata):
    """
    Returns the uri representation of the thumbnail of dropbox file.
    """
    path = metadata.path_lower
    print 'processing file: {}'.format(path)
    _, response = DBX.files_get_thumbnail(path)
    uri = ("data:" + response.headers['Content-Type'] + ";" + "base64," +
           b64encode(response.content))

    return uri


def create_photomap():
    """
    Returns map with markers from dropbox folder
    """
    markers = list_folder_photos_locations()
    photomap = Map(
        identifier="fullmap",
        varname="fullmap",
        style=(
            "height:100%;"
            "width:100%;"
            "top:0;"
            "left:0;"
            "position:absolute;"
            "z-index:200;"
        ),
        lat=40.7128,
        lng=-74.0059,
        cluster=True,
        cluster_gridsize=50,
        markers=markers,
        cluster_imagepath='static/m'
        )

    return photomap
