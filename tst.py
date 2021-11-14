from os import listdir

map = {}

class_map = {
    'fruit_woodiness': 0,
    'fruit_brownspot': 1,
    'fruit_healthy': 2
}

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

for id in map:

    count = sum(map[id])

    if count > 4:
        continue

    full = False

    for i in range(len(usages[count])):
        if map[id][i] + usages[count][i] > min(counts[count]):
            full = True

    if full:
        continue

    for i in range(len(map[id])):
        usages[count][i] += map[id][i]

    training_set.append(id)

print(counts)
print(usages)


