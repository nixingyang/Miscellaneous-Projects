import os
import time

from gi.repository import Gio
from urllib.request import urlopen, urlretrieve
from xml.etree import ElementTree

# http://stackoverflow.com/questions/21356781
import ctypes
libc = ctypes.cdll.LoadLibrary("libc.so.6")
res_init = libc.__res_init

WAITING_TIME = 5
BING_MARKET = None
SCREEN_RESOLUTION = "1920x1080"
GALLERY_FOLDER_PATH = "/run/media/nixingyang/Data Center/OneDrive/Pictures/Bing Gallery"

def get_image_detail():
    # Compose the query URL
    market_argument = "" if BING_MARKET is None else"&mkt={}".format(BING_MARKET)
    query_URL = "https://www.bing.com/HPImageArchive.aspx?format=xml&idx=0&n=2{}".format(market_argument)

    # Fetch the image metadata
    with urlopen(query_URL) as query_connection:
        image_metadata_list = ElementTree.parse(query_connection).getroot().findall("image")
        assert len(image_metadata_list) == 2

        # Get the image detail
        for image_index, image_metadata in enumerate(image_metadata_list):
            image_name = "{}.jpg".format(image_metadata.find("startdate").text)
            image_URL = "https://www.bing.com{}_{}.jpg".format(image_metadata.find("urlBase").text, SCREEN_RESOLUTION)
            yield (image_index, image_name, image_URL)

def format_file_path(file_path):
    return "file://{}".format(file_path)

def change_setting(schema, key, value):
    setting_object = Gio.Settings.new(schema)
    setting_object.set_string(key, value)
    setting_object.apply()

def change_background(image_path):
    change_setting("org.gnome.desktop.background", "picture-uri", format_file_path(image_path))

def change_screensaver(image_path):
    change_setting("org.gnome.desktop.screensaver", "picture-uri", format_file_path(image_path))

def run():
    ready_to_exit = False
    while not ready_to_exit:
        try:
            res_init()

            for image_index, image_name, image_URL in get_image_detail():
                # Create the parent directory
                if not os.path.isdir(GALLERY_FOLDER_PATH):
                    os.makedirs(GALLERY_FOLDER_PATH)
                image_path = os.path.join(GALLERY_FOLDER_PATH, image_name)

                # Download the image
                if not os.path.isfile(image_path):
                    urlretrieve(image_URL, image_path)
                assert os.path.isfile(image_path)

                if image_index == 0:
                    # Set today's photo as the background
                    change_background(image_path)
                elif image_index == 1:
                    # Set yesterday's photo as the screensaver
                    change_screensaver(image_path)

            ready_to_exit = True
        except:
            time.sleep(WAITING_TIME)

if __name__ == "__main__":
    run()
