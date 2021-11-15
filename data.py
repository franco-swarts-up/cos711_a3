from PIL.ImageDraw import Draw
from PIL import Image
from os import mkdir
import math

class_map = {
    'fruit_woodiness': 0,
    'fruit_brownspot': 1,
    'fruit_healthy': 2
}


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


image_labels = {}
image_label_counts = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]

for line in open('./data/train/train.csv'):

    if line.startswith('Image_ID'):
        continue

    data = line.split(',')

    image_id = data[0]
    label = class_map[data[1]]

    if not image_labels.__contains__(image_id):
        image_labels[image_id] = [0, 0, 0]

    image_labels[image_id][label] += 1

for image_id in image_labels:

    index = sum(image_labels[image_id])

    for i in range(3):
        image_label_counts[index][i] += image_labels[image_id][i]

max_count = min(min(image_label_counts[1]), min(image_label_counts[2]))
training_label_counts = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]

training_set = []
validation_set = []

for image_id in image_labels:

    count = sum(image_labels[image_id])

    if count != 1 and count != 2:
        validation_set.append(image_id)
        continue

    # full = False
    #
    # for i in range(3):
    #     if count == 1:
    #         if training_label_counts[count][i] + image_labels[image_id][i] > max_count / 6:
    #             full = True
    #     else:
    #         if training_label_counts[count][i] + image_labels[image_id][i] > max_count:
    #             full = True
    #
    # if full:
    #     validation_set.append(image_id)
    #     continue
    #
    # for i in range(3):
    #     training_label_counts[count][i] += image_labels[image_id][i]
    #
    # training_set.append(image_id)

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

    # if image_id in validation_set:
    image.save('./data/images/val/{}.jpg'.format(image_id))

    label_file = open('./data/labels/val/{}.txt'.format(image_id), 'a')
    label_file.write('{} {} {} {} {}\n'.format(label,
                                                   (x_min + width / 2.0) / 512.0,
                                                   (y_min + height / 2.0) / 512.0,
                                                   width / 512.0,
                                                   height / 512.0))
    label_file.flush()
    label_file.close()

        # continue

    if image_id not in training_set:
        continue

    padding = 10
    size_scale = 5

    crop_boxes = []

    crop_min_x = x_min - padding
    if crop_min_x < 0:
        crop_min_x = 0
    crop_min_y = y_min - padding
    if crop_min_y < 0:
        crop_min_y = 0
    crop_max_x = x_min + width * 1 + padding
    if crop_max_x > image.width:
        crop_max_x = image.width
    crop_max_y = y_min + height * 1 + padding
    if crop_max_y > image.height:
        crop_max_y = image.height

    crop_boxes.append((crop_min_x, crop_min_y, crop_max_x, crop_max_y))

    crop_min_x = x_min - padding
    if crop_min_x < 0:
        crop_min_x = 0
    crop_min_y = y_min - padding
    if crop_min_y < 0:
        crop_min_y = 0
    crop_max_x = x_min + width * size_scale + padding
    if crop_max_x > image.width:
        crop_max_x = image.width
    crop_max_y = y_min + height * 1 + padding
    if crop_max_y > image.height:
        crop_max_y = image.height

    crop_boxes.append((crop_min_x, crop_min_y, crop_max_x, crop_max_y))

    crop_min_x = x_min - padding
    if crop_min_x < 0:
        crop_min_x = 0
    crop_min_y = y_min - padding
    if crop_min_y < 0:
        crop_min_y = 0
    crop_max_x = x_min + width * 1 + padding
    if crop_max_x > image.width:
        crop_max_x = image.width
    crop_max_y = y_min + height * size_scale + padding
    if crop_max_y > image.height:
        crop_max_y = image.height

    crop_boxes.append((crop_min_x, crop_min_y, crop_max_x, crop_max_y))

    if sum(image_labels[image_id]) != 1:
        crop_boxes.clear()
        crop_boxes.append((0, 0, image.width, image.height))

    # draw = Draw(image)
    # draw.rectangle((x_min, y_min, x_max, y_max))
    # image.show()

    for c in range(len(crop_boxes)):

        crop_box = crop_boxes[c]

        croppedImage = image.crop(crop_box).resize((image.width, image.height))

        crop_min_x = crop_box[0]
        crop_min_y = crop_box[1]
        crop_max_x = crop_box[2]
        crop_max_y = crop_box[3]
        crop_width = crop_max_x - crop_min_x
        crop_height = crop_max_y - crop_min_y

        cropped_min_x = (padding if crop_min_x != 0 else x_min)
        cropped_min_y = (padding if crop_min_y != 0 else y_min)
        cropped_max_x = (cropped_min_x + width)
        cropped_max_y = (cropped_min_y + height)

        cropped_min_x = cropped_min_x / crop_width * image.width
        cropped_min_y = cropped_min_y / crop_height * image.height
        cropped_max_x = cropped_max_x / crop_width * image.width
        cropped_max_y = cropped_max_y / crop_height * image.height

        for i in [0, 90, 180, 270]:
            rotated_image = croppedImage.rotate(i)
            rotated_x1, rotated_y1 = rotate(cropped_min_x, cropped_min_y, -i,
                                            image.width / 2,
                                            image.height / 2)
            rotated_x2, rotated_y2 = rotate(cropped_max_x, cropped_max_y, -i,
                                            image.width / 2,
                                            image.height / 2)
            rotated_x_min = min(rotated_x1, rotated_x2)
            rotated_y_min = min(rotated_y1, rotated_y2)
            rotated_x_max = max(rotated_x1, rotated_x2)
            rotated_y_max = max(rotated_y1, rotated_y2)
            rotated_width = rotated_x_max - rotated_x_min
            rotated_height = rotated_y_max - rotated_y_min

            rotated_image.save('./data/images/train/{}_{}_{}.jpg'.format(image_id, c, i))
            label_file = open('./data/labels/train/{}_{}_{}.txt'.format(image_id, c, i), 'a')
            label_file.write('{} {} {} {} {}\n'.format(label,
                                                       (rotated_x_min + rotated_width / 2) / image.width,
                                                       (rotated_y_min + rotated_height / 2) / image.height,
                                                       rotated_width / image.width,
                                                       rotated_height / image.height))
            label_file.flush()
            label_file.close()

            # draw = Draw(rotated_image)
            # draw.rectangle((rotated_x_min, rotated_y_min, rotated_x_min + rotated_width, rotated_y_min + rotated_height))
            # rotated_image.show()

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

            transpose_image.save('./data/images/train/{}_{}_{}_th.jpg'.format(image_id, c, i))
            label_file = open('./data/labels/train/{}_{}_{}_th.txt'.format(image_id, c, i), 'a')
            label_file.write('{} {} {} {} {}\n'.format(label,
                                                       (transpose_x_min + transpose_width / 2.0) / image.width,
                                                       (transpose_y_min + transpose_height / 2.0) / image.height,
                                                       transpose_width / image.width,
                                                       transpose_height / image.height))
            label_file.flush()
            label_file.close()

            # draw = Draw(transpose_image)
            # draw.rectangle((transpose_x_min, transpose_y_min, transpose_x_min + transpose_width, transpose_y_min + transpose_height))
            # transpose_image.show()

            transpose_image = rotated_image.transpose(Image.FLIP_TOP_BOTTOM)
            transpose_x_max, transpose_y_min = transpose(rotated_x_max, rotated_y_max,
                                                         image.width,
                                                         image.height, 1)
            transpose_x_min, transpose_y_max = transpose(rotated_x_min, rotated_y_min,
                                                         image.width,
                                                         image.height, 1)
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

            transpose_image.save('./data/images/train/{}_{}_{}_tv.jpg'.format(image_id, c, i))
            label_file = open('./data/labels/train/{}_{}_{}_tv.txt'.format(image_id, c, i), 'a')
            label_file.write('{} {} {} {} {}\n'.format(label,
                                                       (transpose_x_min + transpose_width / 2.0) / image.width,
                                                       (transpose_y_min + transpose_height / 2.0) / image.height,
                                                       transpose_width / image.width,
                                                       transpose_height / image.height))
            label_file.flush()
            label_file.close()

            # draw = Draw(transpose_image)
            # draw.rectangle((transpose_x_min, transpose_y_min, transpose_x_min + transpose_width, transpose_y_min + transpose_height))
            # transpose_image.show()

    count += 1

    # if count >= 1:
    #     exit()

    print(count)
