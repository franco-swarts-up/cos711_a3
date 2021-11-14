import torch
from PIL import Image, ImageDraw
from sys import argv
from os import mkdir

weight_path = argv[1]

model = torch.hub.load('ultralytics/yolov5', 'custom', path=weight_path)

mkdir('predictions')

file = open('predictions/predictions.csv', 'w')

file.write('Image_ID,class,confidence,ymin,xmin,ymax,xmax\n')

count = 0

for line in open('./data/test/test.csv'):
    if line.startswith('Image_ID'):
        continue
    id = line.strip()
    img = './data/test/{}.jpg'.format(id)
    result = model(img)
    predictions = result.pandas().xywh[0]

    image = Image.open(img)
    # draw_image = ImageDraw.Draw(image)

    t = result.pandas().xyxy[0]

    for i in range(len(predictions)):
        prediction = predictions.loc[i]
        xcenter = prediction.iloc[0]
        ycenter = prediction.iloc[1]
        width = prediction.iloc[2]
        height = prediction.iloc[3]
        confidence = prediction.iloc[4]
        label = prediction.iloc[6]
        minx = (xcenter - width / 2)
        maxx = (xcenter + width / 2)
        miny = (ycenter - height / 2)
        maxy = (ycenter + height / 2)
        width = width
        height = height

        # shape = [(minx, miny), (minx + width, miny + height)]
        # draw_image.rectangle(shape, outline="red")

        file.write('{},{},{},{},{},{},{}\n'.format(id, label, confidence, miny, minx, maxy, maxx))
        file.flush()

    if len(predictions) == 0:
        file.write('{},{},{},{},{},{},{}\n'.format(id, 'fruit_healthy', 0.0, 0.0, 0.0, 0.0, 0.0))

    result.save('predictions/')

    count += 1
    print(count)

file.close()
