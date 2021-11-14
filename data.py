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


class Label:

    label: int
    x: float
    y: float
    width: float
    height: float

    def __init__(self, label: int, x: float, y: float, width: float, height: float):
        self.label = label
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __str__(self) -> str:
        return '{} {} {} {} {}'.format(self.label, self.x / 512, self.y / 512, self.width / 512, self.height / 512)




def convert_labels(file_path: str, target_directory: str):

    for line in open(file_path):

        if line.startswith('Image_ID'):
            continue

        data = line.split(',')

        image = data[0]
        label = class_map[data[1]]
        x_min = float(data[2])
        y_min = float(data[3])
        width = float(data[4])
        height = float(data[5].strip())

        label = Label(label, x_min + width / 2, y_min + height / 2, width, height)

        file = open('{}/{}.txt'.format(target_directory, image), 'a')
        file.write('{}\n'.format(label.__str__()))
        file.close()

mkdir('./data/images/train')
mkdir('./data/images/val')
mkdir('./data/labels/train')
mkdir('./data/labels/val')

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

map = {}

for line in open('./data/train/train.csv'):
    if line.startswith('Image_ID'):
        continue
    data = line.split(',')
    image_id = data[0]
    label = data[1]

    if not map.__contains__(image_id):
        map[image_id] = [0, 0, 0]

    map[image_id][class_map[label]] += 1


counts = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]
for i in map:
    index = sum(map[i])
    for j in range(len(map[i])):
        counts[index][j] += map[i][j]

usages = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]

training_set = []
validation_set = []

for id in map:

    count = sum(map[id])

    if count != 2:
        validation_set.append(id)
        continue

    # full = False
    #
    # for i in range(len(usages[count])):
    #     if map[id][i] + usages[count][i] > min(counts[count]):
    #         full = True
    #
    # if full:
    #     continue
    #
    # for i in range(len(map[id])):
    #     usages[count][i] += map[id][i]

    training_set.append(id)

count = 0

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

    image.save('./data/images/val/{}.jpg'.format(image_id))

    label_file = open('./data/labels/val/{}.txt'.format(image_id), 'a')
    label_file.write('{} {} {} {} {}\n'.format(label,
                                               (x_min + width / 2) / 512,
                                               (y_min + height / 2) / 512,
                                               width / 512,
                                               height / 512))
    label_file.flush()
    label_file.close()

    if image_id not in training_set:
        continue

    for i in [0, 90, 270]:
        rotated_image = image.rotate(i)
        rotated_x1, rotated_y1 = rotate(x_min,y_min, -i,
                                        image.width / 2,
                                        image.height / 2)
        rotated_x2, rotated_y2 = rotate(x_max, y_max, -i,
                                        image.width / 2,
                                        image.height / 2)
        rotated_x_min = min(rotated_x1, rotated_x2)
        rotated_y_min = min(rotated_y1, rotated_y2)
        rotated_x_max = max(rotated_x1, rotated_x2)
        rotated_y_max = max(rotated_y1, rotated_y2)
        rotated_width = rotated_x_max - rotated_x_min
        rotated_height = rotated_y_max - rotated_y_min

        rotated_image.save('./data/images/train/{}_{}.jpg'.format(image_id, i))
        label_file = open('./data/labels/train/{}_{}.txt'.format(image_id, i), 'a')
        label_file.write('{} {} {} {} {}\n'.format(label,
                                                   (rotated_x_min + rotated_width / 2) / image.width,
                                                   (rotated_y_min + rotated_height / 2) / image.height,
                                                   rotated_width / image.width,
                                                   rotated_height / image.height))
        label_file.flush()
        label_file.close()

        transpose_image = rotated_image.transpose(Image.FLIP_LEFT_RIGHT)
        transpose_x_min, transpose_y_max = transpose(rotated_x_max, rotated_y_max,
                                                     image.width,
                                                     image.height, 0)
        transpose_x_max, transpose_y_min = transpose(rotated_x_min, rotated_y_min,
                                                     image.width,
                                                     image.height, 0)
        transpose_width = transpose_x_max - transpose_x_min
        transpose_height = transpose_y_max - transpose_y_min

        if transpose_x_min < 0 or transpose_y_min < 0 or transpose_width < 0 or transpose_height < 0:
            print(transpose_x_min)
            print(transpose_y_min)
            print(transpose_x_max)
            print(transpose_y_max)
            draw = Draw(transpose_image)
            draw.rectangle([(transpose_x_min, transpose_y_min),
                            (transpose_x_min + transpose_width, transpose_y_min + transpose_height)])
            transpose_image.show()
            exit()

        transpose_image.save('./data/images/train/{}_{}_th.jpg'.format(image_id, i))
        label_file = open('./data/labels/train/{}_{}_th.txt'.format(image_id, i), 'a')
        label_file.write('{} {} {} {} {}\n'.format(label,
                                                   (transpose_x_min + transpose_width / 2) / image.width,
                                                   (transpose_y_min + transpose_height / 2) / image.height,
                                                   transpose_width / image.width,
                                                   transpose_height / image.height))
        label_file.flush()
        label_file.close()

        # transpose_image = rotated_image.transpose(Image.FLIP_TOP_BOTTOM)
        # transpose_x_max, transpose_y_min = transpose(rotated_x_max, rotated_y_max,
        #                                              image.width,
        #                                              image.height, 1)
        # transpose_x_min, transpose_y_max = transpose(rotated_x_min, rotated_y_min,
        #                                              image.width,
        #                                              image.height, 1)
        # transpose_width = transpose_x_max - transpose_x_min
        # transpose_height = transpose_y_max - transpose_y_min
        #
        # if transpose_x_min < 0 or transpose_y_min < 0 or transpose_width < 0 or transpose_height < 0:
        #     print(transpose_x_min)
        #     print(transpose_y_min)
        #     print(transpose_x_max)
        #     print(transpose_y_max)
        #     draw = Draw(transpose_image)
        #     draw.rectangle([(transpose_x_min, transpose_y_min), (transpose_x_min + transpose_width, transpose_y_min + transpose_height)])
        #     transpose_image.show()
        #     exit()
        #
        # transpose_image.save('./data/images/train/{}_{}_tv.jpg'.format(image_id, i))
        # label_file = open('./data/labels/train/{}_{}_tv.txt'.format(image_id, i), 'a')
        # label_file.write('{} {} {} {} {}\n'.format(label,
        #                                            (transpose_x_min + transpose_width / 2) / image.width,
        #                                            (transpose_y_min + transpose_height / 2) / image.height,
        #                                            transpose_width / image.width,
        #                                            transpose_height / image.height))
        # label_file.flush()
        # label_file.close()

    count += 1

    # if count >= 3:
    #     exit()

    print(count)




