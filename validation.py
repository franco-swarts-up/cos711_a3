
import torch
import torchvision.utils

model = torch.hub.load('ultralytics/yolov5', 'custom', path='./yolov5/runs/train/exp4/weights/best.pt')

for line in open('./data/test.csv'):
    if line.startswith('Image_ID'):
        continue
    id = line.strip()
    img = './data/images/test/{}.jpg'.format(id)
    result = model(img)
    predictions = result.pandas().xywh[0]

    for i in range(len(predictions)):
        prediction = predictions.loc[i]
        xcenter = prediction.iloc[0]
        ycenter = prediction.iloc[1]
        width = prediction.iloc[2]
        height = prediction.iloc[3]
        confidence = prediction.iloc[4]
        label = prediction.iloc[6]
        print('{},{},{},{},{},{},{}\n'.format(id, label, confidence, ycenter - height / 2, xcenter - width / 2, ycenter + height / 2, xcenter + width / 2))

    if len(predictions) == 0:
        print('{},{},{},{},{},{},{}\n'.format(id, 'fruit_healthy', 0.0, 0.0, 0.0, 0.0, 0.0))

    result.show()

    print('done')

