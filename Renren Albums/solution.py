from __future__ import absolute_import, division, print_function

import os
import re
import json
import time
import piexif
import requests
import argparse
from datetime import datetime

# http://bugs.python.org/issue22377
# https://docs.python.org/2/library/time.html
os.environ["TZ"] = "CST"
time.tzset()

class Cookie(object):
    def __init__(self, account, password):
        self.cookie_instance = self._init_cookie(account, password)

    def _get_headers(self):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "http//www.renren.com",
            "Referer": "http://www.renren.com/SysHome.do",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 7_0like Mac OS X; en-us) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11A465 Safari/9537.53",
            "X-Requested-With": "XMLHttpRequest",
        }
        return headers

    def _get_data(self, account, password):
        data = {
            "email": account,
            "password": password,
            "icode": "",
            "origURL": "http://www.renren.com/home",
            "domain": "renren.com",
            "key_id": "1",
            "captcha_type": "web_login"
        }
        return data

    def _get_response(self, account, password):
        kwargs = {}
        kwargs["headers"] = self._get_headers()
        kwargs["data"] = self._get_data(account, password)
        kwargs["allow_redirects"] = True

        response = requests.post("http://www.renren.com/ajaxLogin/login", **kwargs)
        assert response.status_code == 200, "status_code is {}!".format(response.status_code)
        return response.cookies, response.text

    def _init_cookie(self, account, password):
        cookie, text = self._get_response(account, password)
        response_dict = json.loads(text)
        assert response_dict["code"], "Failed to get the cookie because of {}!".format(response_dict["failDescription"])
        return cookie

    def get_cookie(self):
        return "; ".join(["{}={}".format(key, value) for key, value in self.cookie_instance.items()])

    def get_user_id(self):
        return self.cookie_instance["id"]

class Album(object):
    def __init__(self, cookie_object):
        self.cookie = cookie_object.get_cookie()
        self.user_id = cookie_object.get_user_id()
        self.headers = self._get_headers()
        self.re_pattern = re.compile("'albumList': (.*),")

    def _get_headers(self):
        headers = {
            "Host": "photo.renren.com",
            "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:35.0) Gecko/20100101 Firefox/35.0"),
            "Accept": ("application/json, text/javascript, */*; q=0.01"),
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Cookie": self.cookie
        }
        return headers

    def _get_response(self):
        response = requests.get("http://photo.renren.com/photo/{}/albumlist/v7".format(self.user_id), headers=self.headers)
        assert response.status_code == 200, "status_code is {}!".format(response.status_code)
        return response.text

    def iterate_album_info(self):
        raw_content = self._get_response()
        for album_info in json.loads(re.search(self.re_pattern, raw_content).groups()[0]):
            album_name = album_info["albumName"]
            album_URL = "http://photo.renren.com/photo/{}/album-{}/list".format(self.user_id, album_info["albumId"])
            yield album_name, album_URL

class Image(Album):
    def __init__(self, cookie_object, album_URL):
        super(Image, self).__init__(cookie_object=cookie_object)
        self.album_URL = album_URL

    def _get_response(self):
        response = requests.get(self.album_URL, headers=self.headers)
        assert response.status_code == 200, "status_code is {}!".format(response.status_code)
        return response.text

    def iterate_image_info(self):
        raw_content = self._get_response()
        for image_info in json.loads(raw_content)["list"]:
            large_image_URL = image_info["largeUrl"]
            original_image_URL = large_image_URL.replace("large", "original")
            image_name = image_info["title"] if image_info["title"] else int(image_info["id"])
            image_name = str(image_name).replace(os.sep, " ") + "." + large_image_URL.split("/")[-1].split(".")[-1]
            image_time = image_info["time"]
            yield image_name, (original_image_URL, large_image_URL), image_time

def download_image(image_URL, image_file_path, timeout=3, sleep_duration=0.3, retry_num=3):
    assert not os.path.isfile(image_file_path), "File {} already exists!".format(image_file_path)

    while retry_num:
        try:
            response = requests.get(image_URL, stream=True, timeout=timeout)
            assert response.status_code == 200, "status_code is {}!".format(response.status_code)

            if os.path.isfile(image_file_path):
                os.remove(image_file_path)

            with open(image_file_path, "wb") as file_object:
                for chunk in response.iter_content():
                    file_object.write(chunk)

            break
        except Exception as exception:
            print("Exception for {}: {}".format(image_URL, exception))
            retry_num -= 1
            continue
        finally:
            time.sleep(sleep_duration)

def download_album(account, password, main_folder_path):
    cookie_object = Cookie(account=account, password=password)
    for album_name, album_URL in Album(cookie_object=cookie_object).iterate_album_info():
        print("Working on album {} ...".format(album_name))
        album_folder_path = os.path.join(main_folder_path, album_name)
        os.makedirs(album_folder_path, exist_ok=True)

        for image_name, image_URL_tuple, image_time in Image(cookie_object=cookie_object, album_URL=album_URL).iterate_image_info():
            image_file_path = os.path.join(album_folder_path, image_name)
            if os.path.isfile(image_file_path):
                continue

            print("Working on image {} ...".format(image_name))
            for image_URL in image_URL_tuple:
                download_image(image_URL, image_file_path)
                if os.path.isfile(image_file_path):
                    break

            if not os.path.isfile(image_file_path):
                print("Failed to download image {}!".format(image_name))
                continue

            # Insert EXIF information
            datetime_object = datetime.strptime(image_time, "%a %b %d %H:%M:%S %Z %Y")
            exif_ifd = {piexif.ExifIFD.DateTimeOriginal: datetime_object.isoformat(" ")}
            exif_dict = {"Exif": exif_ifd}
            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, image_file_path)

def run():
    print("Parsing command-line arguments ...")
    parser = argparse.ArgumentParser(description="A toolkit for downloading renren albums")
    parser.add_argument("--account", required=True, help="Account")
    parser.add_argument("--password", required=True, help="Password")
    parser.add_argument("--main_folder_path", default="/tmp/renren_albums", help="Folder which stores the downloaded albums")
    args = parser.parse_args()

    print("Downloading renren albums ...")
    download_album(args.account, args.password, args.main_folder_path)

    print("All done!")

if __name__ == "__main__":
    run()
