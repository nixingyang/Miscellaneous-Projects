import ctypes
import os
import time
from urllib.request import urlopen, urlretrieve
from xml.etree import ElementTree

from gi.repository import Gio

BING_MARKET = "zh-cn"
SCREEN_RESOLUTION = "UHD"
GALLERY_FOLDER_PATH = os.path.join(os.environ["HOME"], "Pictures/Bing Gallery")
WAITING_TIME_WHEN_SUCCESSFUL = 600
WAITING_TIME_WHEN_UNSUCCESSFUL = 60


def validate_internet_connection(server_URL="https://www.bing.com"):
    try:
        # Re-read the resolver configuration file
        # http://stackoverflow.com/questions/21356781
        libc = ctypes.cdll.LoadLibrary("libc.so.6")
        libc.__res_init()  # pylint: disable=protected-access

        with urlopen(server_URL) as _:
            return True
    except:
        return False


extract_urlBase = lambda file_name: file_name.split(".")[0].split("_")[1]


def delete_redundant_files(folder_path):
    previous_urlBase_list = []
    file_name_list = sorted(
        os.listdir(folder_path), key=lambda file_name: int(file_name.split("_")[0])
    )
    for file_name in file_name_list:
        urlBase = extract_urlBase(file_name)
        if urlBase in previous_urlBase_list:
            os.remove(os.path.join(folder_path, file_name))
        else:
            previous_urlBase_list.append(urlBase)
    return previous_urlBase_list


def retrieve_image_detail():
    image_detail_list = []
    market_argument = "" if BING_MARKET is None else "&mkt={}".format(BING_MARKET)
    for idx in [-1, 100]:
        # Compose the query URL
        query_URL = (
            "https://www.bing.com/HPImageArchive.aspx?format=xml&idx={}&n=100{}".format(
                idx, market_argument
            )
        )

        # Fetch the image metadata
        with urlopen(query_URL) as query_connection:
            image_metadata_list = (
                ElementTree.parse(query_connection).getroot().findall("image")
            )

            # Get the image detail
            for image_metadata in image_metadata_list:
                image_name = "{}_{}.jpg".format(
                    image_metadata.find("startdate").text,
                    image_metadata.find("urlBase")
                    .text.split("/")[-1]
                    .split("_")[0]
                    .split(".")[-1],
                )
                image_URL = "https://www.bing.com{}_{}.jpg".format(
                    image_metadata.find("urlBase").text, SCREEN_RESOLUTION
                )

                # Append the image detail
                image_detail = (image_name, image_URL)
                if image_detail not in image_detail_list:
                    image_detail_list.append(image_detail)
    return image_detail_list


def change_background(image_path):
    def _format_file_path(file_path):
        return "file://{}".format(file_path)

    def _change_setting(schema, key, value):
        setting_object = Gio.Settings.new(schema)
        setting_object.set_string(key, value)
        setting_object.apply()

    _change_setting(
        "org.gnome.desktop.background", "picture-uri", _format_file_path(image_path)
    )


def run():
    # Create the parent directory
    if not os.path.isdir(GALLERY_FOLDER_PATH):
        os.makedirs(GALLERY_FOLDER_PATH)

    while True:
        try:
            # Validate internet connection
            assert validate_internet_connection()

            # Delete redundant files
            previous_urlBase_list = delete_redundant_files(GALLERY_FOLDER_PATH)

            # Iterate over image detail
            for image_index, (image_name, image_URL) in enumerate(
                retrieve_image_detail()
            ):
                # Download the image if necessary
                urlBase = extract_urlBase(image_name)
                image_path = os.path.join(GALLERY_FOLDER_PATH, image_name)
                if urlBase not in previous_urlBase_list and not os.path.isfile(
                    image_path
                ):
                    urlretrieve(image_URL, image_path)
                assert os.path.isfile(image_path)

                # Set today's photo as the background
                if image_index == 0:
                    change_background(image_path)

            waiting_time = WAITING_TIME_WHEN_SUCCESSFUL
        except:
            waiting_time = WAITING_TIME_WHEN_UNSUCCESSFUL
        finally:
            time.sleep(waiting_time)


if __name__ == "__main__":
    run()
