import os
import shutil
import time
from threading import Thread

from PIL import Image
import requests
import json


def middle_color(s):
    im = Image.open(s)
    pix = im.load()
    s = [0, 0, 0]
    for i in range(im.size[0]):
        for j in range(im.size[1]):
            s[0] += pix[i, j][0]
            s[1] += pix[i, j][1]
            s[2] += pix[i, j][2]
    al = im.size[0] * im.size[1]
    return [i // al for i in s]


def thread():
    response = requests.get('http://dog.ceo/api/breeds/image/random').json()
    picture = requests.get(response['message'], stream=True)
    path = f'pictures/{os.path.split(response["message"])[-1]}'
    if os.path.exists(path):
        print(f'FILE EXISTS: {path}')
    with open(path, 'wb') as out_file:
        shutil.copyfileobj(picture.raw, out_file)
    del picture
    color = ','.join(map(str, middle_color(path)))
    colors[color] = path
    print(path)


colors = json.load(open('colors.json', 'r'))

for _ in range(1):
    t = Thread(target=thread)
    t.start()
    time.sleep(0.1)

json.dump(colors, open('colors.json', 'w'))
