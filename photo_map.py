"""
Application to map photo data from photos folder and render locations on
google maps
"""

from os import environ
from os.path import join, dirname
from base64 import b64encode
from multiprocessing.dummy import Pool as ThreadPool
from math import cos, sin, atan2, sqrt, pi
from dotenv import load_dotenv
from flask_googlemaps import Map
import dropbox

load_dotenv(join(dirname(__file__), '.env'))
DROPBOX_ACCESS_TOKEN = environ.get('DROPBOX_ACCESS_TOKEN')
DROPBOX_FOLDER_PATH = environ.get('DROPBOX_FOLDER_PATH')
DBX = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

def list_folder_photos_locations():
    """
    Returns `Markers` of photos/videos for `DROPBOX_FOLDER_PATH` directory and
    filters out photos with no location metadata.
    """
    res = DBX.files_list_folder(DROPBOX_FOLDER_PATH, include_media_info=True)
    photos = res.entries

    # remove files that do not have location metadata
    entries = [f for f in photos if f.media_info and f.media_info.get_metadata().location]

    # map data to lat/long json with threads to make it faster
    pool = ThreadPool(20)
    markers = pool.map(convert_metadata_to_marker, entries)

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
    Returns the base64 uri representation of the thumbnail of dropbox file.
    """
    path = metadata.path_lower
    print 'processing file: {}'.format(path)
    _, response = DBX.files_get_thumbnail(path, size=dropbox.files.ThumbnailSize.w640h480)
    uri = ("data:" + response.headers['Content-Type'] + ";" + "base64," +
           b64encode(response.content))

    return uri


def create_photomap():
    """
    Returns map with markers from dropbox folder
    """
    markers = list_folder_photos_locations()
    locations = [(m['lat'], m['lng']) for m in markers]
    lat, lng = center_geolocation(locations)
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
        lat=lat,
        lng=lng,
        cluster=True,
        cluster_gridsize=50,
        markers=markers,
        cluster_imagepath='static/m'
        )

    return photomap

def center_geolocation(geolocations):
    """
    Provide a relatively accurate center lat, lon returned as a list pair, given
    a list of list pairs in decimal degrees.
    ex: in: geolocations = [(lat1,lon1), (lat2,lon2), ...]
        out: (center_lat, center_lon)
    """
    x, y, z = 0, 0, 0

    # convert pairs to cartesian coordinates and sum
    for lat, lon in geolocations:
        # convert degrees to radians
        lat = lat * pi/180
        lon = lon * pi/180

        # sum of cartesian coordinates
        x += cos(lat) * cos(lon)
        y += cos(lat) * sin(lon)
        z += sin(lat)

    # average of coordinates
    n = len(geolocations)
    x, y, z = x / n, y / n, z / n

    # convert back to 2D decimal degrees
    central_lat = atan2(z, sqrt(x * x + y * y))
    central_lng = atan2(y, x)
    return (central_lat * 180/pi, central_lng * 180/pi)
