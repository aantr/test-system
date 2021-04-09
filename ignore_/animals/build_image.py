import json
import os
from PIL import Image


def clear_images():
    colors = json.load(open('colors.json', 'r'))
    count = 0
    for i in os.walk('pictures'):
        for j in i[2]:
            path = os.path.join(i[0], j).replace('\\', '/')
            if path not in colors.values():
                os.remove(path)
                count += 1
    print(count)


def crop_im(filename):
    size = 256, 256
    im: Image.Image = Image.open(filename)
    max_ = max(im.width, im.height)
    min_ = min(im.width, im.height)
    if im.height > im.width:
        h = im.width + (im.height - im.width) / 3
        im = im.crop((0, (im.height - h) / 2, im.width, h))
    else:
        w = im.height + (im.width - im.height) / 3
        im = im.crop(((im.width - w) / 2, 0, w, im.height))
    im = im.resize((max_, max_))
    im.thumbnail(size, Image.ANTIALIAS)
    im.save(filename)


def get_ready():
    for i in os.walk('pictures'):
        for j in i[2]:
            path = os.path.join(i[0], j)
            # crop_im(path)
            im: Image.Image = Image.open(path)
            if im.size != (256, 256):
                print(im.size)
                im.close()
                os.remove(path)


w, h = 128, 128
im = Image.new('RGB', (w * 256, h * 256))
im.show()