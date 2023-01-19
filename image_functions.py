
import os
import urllib.request
def download_image(url, directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = url.split("/")[-1]
    filepath = os.path.join(directory, filename)
    urllib.request.urlretrieve(url, filepath)