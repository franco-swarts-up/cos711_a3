from PIL.ImageDraw import Draw
from PIL import Image, ImageDraw
from os import listdir, rmdir, mkdir
from random import randint
import math

class_map = {
    'fruit_woodiness': 0,
    'fruit_brownspot': 1,
    'fruit_healthy': 2
}

def rotate(x, y, degrees, ox, oy):
    angle = math.radians(degrees)

    qx = ox + math.cos(angle) * (x - ox) - math.sin(angle) * (y - oy)
    qy = oy + math.sin(angle) * (x - ox) + math.cos(angle) * (y - oy)
    return qx, qy

def transpose(x, y, width, height, dir):

    if dir == 0:
        rx, ry = width - x, y
    else:
        rx, ry = x, height - y

    if rx < 0:
        rx = 0
    if ry < 0:
        ry = 0

    return rx, ry

for line in open('./data/train/train.csv'):

    if line.startswith('Image_ID'):
        continue

    data = line.split(',')

    image_id = data[0]
    label = class_map[data[1]]
    x_min = float(data[2])
    y_min = float(data[3])
    width = float(data[4])
    height = float(data[5].strip())
    x_max = x_min + width
    y_max = y_min + height

    image: Image = Image.open('./data/train/{}.jpg'.format(image_id))

    x_rand = randint(0, int(x_min))
    y_rand = randint(0, int(y_min))
    width_rand = randint(256, 512)
    height_rand = randint(256, 512)
    resize_crop = image.crop((x_rand, y_rand, x_rand + width_rand, y_rand + height_rand))

    resize_crop.show()
    exit(0)





