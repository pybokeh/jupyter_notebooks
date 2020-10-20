# pip install psutil
import csv
import psutil
import time

x_value = 0

fieldnames = ["x_value", "cpu_perc"]


with open('data.csv', 'w') as csv_file:
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    csv_writer.writeheader()

while True:

    with open('data.csv', 'a') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        y_value = psutil.cpu_percent()

        info = {
            "x_value": x_value,
            "cpu_perc": y_value
        }

        csv_writer.writerow(info)
        print(x_value, y_value)

        x_value += 1

    time.sleep(1)
