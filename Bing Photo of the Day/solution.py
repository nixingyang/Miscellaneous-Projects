import os
import time

from gi.repository import Gio
from urllib.request import urlopen, urlretrieve
from xml.etree import ElementTree

# http://stackoverflow.com/questions/21356781
import ctypes
libc = ctypes.cdll.LoadLibrary("libc.so.6")
res_init = libc.__res_init  # pylint: disable=protected-access

BING_MARKET = None
SCREEN_RESOLUTION = "1920x1080"
GALLERY_FOLDER_PATH = os.path.join(os.environ["HOME"], "Pictures/Bing Gallery")
WAITING_TIME_WHEN_SUCCESSFUL = 600
WAITING_TIME_WHEN_UNSUCCESSFUL = 60

def has_internet_connection(server_URL="https://www.bing.com"):
    try:
        with urlopen(server_URL) as _:
            return True
    except:
        return False

def yield_image_detail():
    market_argument = "" if BING_MARKET is None else "&mkt={}".format(BING_MARKET)

    for idx in [-1, 100]:
        # Compose the query URL
        query_URL = "https://www.bing.com/HPImageArchive.aspx?format=xml&idx={}&n=100{}".format(idx, market_argument)

        # Fetch the image metadata
        with urlopen(query_URL) as query_connection:
            image_metadata_list = ElementTree.parse(query_connection).getroot().findall("image")

            # Get the image detail
            for image_metadata in image_metadata_list:
                image_name = "{}_{}.jpg".format(image_metadata.find("startdate").text, image_metadata.find("urlBase").text.split("/")[-1].split("_")[0])
                image_URL = "https://www.bing.com{}_{}.jpg".format(image_metadata.find("urlBase").text, SCREEN_RESOLUTION)

                yield image_name, image_URL

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

def delete_redundant_files(folder_path):
    previous_urlBase_list = []
    file_name_list = sorted(os.listdir(folder_path), key=lambda file_name: int(file_name.split("_")[0]))
    for file_name in file_name_list:
        urlBase = file_name.split(".")[0].split("_")[1]
        if urlBase in previous_urlBase_list:
            os.remove(os.path.join(folder_path, file_name))
        else:
            previous_urlBase_list.append(urlBase)
    return previous_urlBase_list

def run():
    # Create the parent directory
    if not os.path.isdir(GALLERY_FOLDER_PATH):
        os.makedirs(GALLERY_FOLDER_PATH)

    while True:
        try:
            # Re-read the resolver configuration file
            res_init()

            # Check internet connection
            assert has_internet_connection()

            # Delete redundant files
            _ = delete_redundant_files(GALLERY_FOLDER_PATH)

            # Iterate over image detail
            for image_index, (image_name, image_URL) in enumerate(yield_image_detail()):
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
