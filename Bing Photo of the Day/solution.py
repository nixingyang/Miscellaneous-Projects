import os
import time

from gi.repository import Gio
from urllib.request import urlopen, urlretrieve
from xml.etree import ElementTree

# http://stackoverflow.com/questions/21356781
import ctypes
libc = ctypes.cdll.LoadLibrary("libc.so.6")
res_init = libc.__res_init

BING_MARKET = None
SCREEN_RESOLUTION = "1920x1080"
GALLERY_FOLDER_PATH = "/run/media/nixingyang/Data Center/OneDrive/Pictures/Bing Gallery"
WAITING_TIME_WHEN_SUCCESSFUL = 600
WAITING_TIME_WHEN_UNSUCCESSFUL = 60

def get_image_detail():
    idx = -1
    market_argument = "" if BING_MARKET is None else "&mkt={}".format(BING_MARKET)
    image_name_list = []
    image_URL_list = []

    try:
        while True:
            # Compose the query URL
            query_URL = "https://www.bing.com/HPImageArchive.aspx?format=xml&idx={}&n=1{}".format(idx, market_argument)

            # Fetch the image metadata
            with urlopen(query_URL) as query_connection:
                image_metadata_list = ElementTree.parse(query_connection).getroot().findall("image")

                # Get the image detail
                for image_metadata in image_metadata_list:
                    image_name = "{}_{}.jpg".format(image_metadata.find("startdate").text, image_metadata.find("urlBase").text.split("/")[-1].split("_")[0])
                    image_URL = "https://www.bing.com{}_{}.jpg".format(image_metadata.find("urlBase").text, SCREEN_RESOLUTION)

                    image_name_list.append(image_name)
                    image_URL_list.append(image_URL)

            # Move to previous day
            idx += 1
    except:
        pass

    if len(image_name_list) > 0:
        return image_name_list, image_URL_list
    else:
        return None

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
    # Create the parent directory
    if not os.path.isdir(GALLERY_FOLDER_PATH):
        os.makedirs(GALLERY_FOLDER_PATH)

    while True:
        try:
            # Re-read the resolver configuration file
            res_init()

            # Get image detail
            image_detail = get_image_detail()
            if image_detail is None:
                assert False

            image_name_list, image_URL_list = image_detail
            for image_index, (image_name, image_URL) in enumerate(zip(image_name_list, image_URL_list)):
                # Download the image
                image_path = os.path.join(GALLERY_FOLDER_PATH, image_name)
                if not os.path.isfile(image_path):
                    urlretrieve(image_URL, image_path)
                assert os.path.isfile(image_path)

                if image_index == 0:
                    # Set today's photo as the background
                    change_background(image_path)
                elif image_index == 1:
                    # Set yesterday's photo as the screensaver
                    change_screensaver(image_path)

            waiting_time = WAITING_TIME_WHEN_SUCCESSFUL
        except:
            waiting_time = WAITING_TIME_WHEN_UNSUCCESSFUL
        finally:
            time.sleep(waiting_time)

if __name__ == "__main__":
    run()
