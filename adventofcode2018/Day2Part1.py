from collections import Counter

twos_counter = 0
threes_counter = 0
for id in [item for item in open("data/Day2_Input.txt")]:
    counts = Counter(id)
    if 2 in counts.values():
        twos_counter = twos_counter + 1
    if 3 in counts.values():
        threes_counter = threes_counter + 1