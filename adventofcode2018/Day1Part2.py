import itertools

freq_list = itertools.cycle([int(item.replace('+','')) for item in open('data/Day1_Input.txt', mode='r')])

sum = 0
already_seen = set()
i = 0
for i, value in enumerate(freq_list):
    sum = sum + value
    if sum in already_seen:
        print(i, "ith sum:", sum)
        break
    already_seen.add(sum)
    if i > 1000000:
        break