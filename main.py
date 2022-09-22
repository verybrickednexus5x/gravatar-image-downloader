import hashlib
import os
import requests

def convert_string_to_MD5_hash(s):
    m = hashlib.md5()
    m.update(s.encode('utf-8'))
    return m.hexdigest()

def download_img(d, url):
    img = requests.get(url)
    file_name = './gravatar_imgs/' + d + '.png'
    with open(file_name, 'wb') as f:
        f.write(img.content)

s = convert_string_to_MD5_hash(input('Enter string:'))
ds = [ 'monsterid', 'wavatar', 'retro', 'robohash' ]

for d in ds:
    url = 'https://www.gravatar.com/avatar/' + s + '?d=' + d + '&f=y'
    os.makedirs('./gravatar_imgs', exist_ok=True)
    download_img(d, url)
    print(url)
    print(d)
