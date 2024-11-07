# -*- coding:utf8 -*-
import requests
import json
from urllib import parse
import os
import time
import dlib
import cv2
import numpy as np

class BaiduImageSpider(object):
    def __init__(self):
        self.json_count = 20  # Total number of JSON files to request
        self.start_index = 1  # Start numbering from 1
        self.url = 'https://image.baidu.com/search/acjson?tn=resultjson_com&logid=5179920884740494226&ipn=rj&ct' \
                   '=201326592&is=&fp=result&queryWord={' \
                   '}&cl=2&lm=-1&ie=utf-8&oe=utf-8&adpicid=&st=-1&z=&ic=0&hd=&latest=&copyright=&word={' \
                   '}&s=&se=&tab=&width=&height=&face=0&istype=2&qc=&nc=1&fr=&expermode=&nojc=&pn={' \
                   '}&rn=30&gsm=1e&1635054081427='
        self.directory = r"./pics{}"  # Storage directory
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '  
                          'Chrome/95.0.4638.54 Safari/537.36 Edg/95.0.1020.30 '
        }
        self.detector = dlib.get_frontal_face_detector()  # Initialize the face detector

    # Create storage directory
    def create_directory(self, name):
        self.directory = self.directory.format(name)
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        self.directory += r'\{}'

    # Get image links
    def get_image_link(self, url):
        list_image_link = []
        try:
            strhtml = requests.get(url, headers=self.header)  # Get webpage data
            jsonInfo = json.loads(strhtml.text)
            # Make sure we have enough data returned
            if 'data' in jsonInfo:
                for index in range(len(jsonInfo['data'])):  # Loop through available image data
                    if 'thumbURL' in jsonInfo['data'][index]:
                        list_image_link.append(jsonInfo['data'][index]['thumbURL'])
        except json.JSONDecodeError:
            print(f"Failed to decode JSON from URL: {url}")
        except requests.RequestException as e:
            print(f"Request failed: {e}")
        return list_image_link

    # Check if the image has a face
    def has_face(self, img_link):
        try:
            img_data = requests.get(img_link).content
            # Convert the image to a format that can be processed by dlib
            img_array = np.asarray(bytearray(img_data), dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

            # Detect faces
            dets = self.detector(img, 1)  # Find the faces in the image
            return len(dets) > 0  # Return True if at least one face is detected
        except Exception as e:
            print(f"Error checking for faces in {img_link}: {e}")
            return False

    # Download image
    def save_image(self, img_link, filename):
        try:
            res = requests.get(img_link, headers=self.header)
            res.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
            with open(filename, "wb") as f:
                f.write(res.content)
                print("Stored at: " + filename)
        except requests.HTTPError:
            print(f"Error downloading image {img_link} - HTTP Error")
        except requests.RequestException as e:
            print(f"Error downloading image {img_link} - {e}")

    # Main function
    def run(self):
        searchName = input("Enter search term: ")
        searchName_parse = parse.quote(searchName)  # URL encode the search term

        self.create_directory(searchName)

        pic_number = self.start_index  # Start numbering from 1
        for index in range(self.json_count):
            pn = (index + 1) * 30 + self.start_index  # Adjust pagination
            request_url = self.url.format(searchName_parse, searchName_parse, str(pn))
            list_image_link = self.get_image_link(request_url)
            for link in list_image_link:
                if self.has_face(link):  # Check if the image has a face
                    self.save_image(link, self.directory.format(str(pic_number) + '.jpg'))
                    pic_number += 1
                    time.sleep(0.2)  # Sleep to prevent IP bans
                else:
                    print(f"No face detected in image: {link}")
        print(searchName + " ---- Image download completed --------->")


if __name__ == '__main__':
    spider = BaiduImageSpider()
    spider.run()