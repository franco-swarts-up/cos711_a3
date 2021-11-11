from os import listdir

count = 0

for f in listdir('./data/labels/training'):
    for line in open('./data/labels/training/{}'.format(f)):
        count += 1

print(count)