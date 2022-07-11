import csv
import numpy as np

# generate 2 sets of matrices, target numbers and correct answers:
def task_generator(n):
    matrices = []
    targets = []
    results = []
    for i in range(0, n):
        matrix = np.random.randint(low = 10, high = 99, size = 9)
        matrices.append(list(matrix))
        c = np.random.choice(matrix, 2, replace = False)
        results.append(list(c))
        targets.append(sum(c))
    return matrices, targets, results

matrices1, targets1, results1 = task_generator(30)
matrices2, targets2, results2 = task_generator(30)

# write files as csv:
with open('tasks1.csv', 'w') as f:
    write = csv.writer(f)
    write.writerows(matrices1)
with open('targets1.csv', 'w') as f:
    write = csv.writer(f)
    write.writerows(map(lambda x: [x], targets1))
with open('pairs1.csv', 'w') as f:
    write = csv.writer(f)
    write.writerows(results1)

with open('tasks2.csv', 'w') as f:
    write = csv.writer(f)
    write.writerows(matrices2)
with open('targets2.csv', 'w') as f:
    write = csv.writer(f)
    write.writerows(map(lambda x: [x], targets2))
with open('pairs2.csv', 'w') as f:
    write = csv.writer(f)
    write.writerows(results2)