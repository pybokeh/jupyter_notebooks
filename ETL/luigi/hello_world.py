import luigi
from time import sleep
import datetime


class MyGlobals(luigi.Config):
    """Define 'global' parameter values here"""

    labor_rate = input("Enter labor rate in GBP: ")
    part_factor = input("Enter part cost factor: ")
    handling_factor = input("Enter handling cost factor: ")
    start_voucher_date = input("Enter start voucher date: ")
    end_voucher_date = input("Enter end voucher date: ")


class HelloTask(luigi.Task):
    """Task that writes 'Hello' to a text file"""

    def run(self):
        sleep(10)
        with open('hello.txt', 'w') as hello_file:
            hello_file.write('Hello')
            hello_file.close()

    def output(self):
        """output is what notifies Luigi that a task was complete or note"""

        return luigi.LocalTarget('hello.txt')

class WorldTask(luigi.Task):
    """Task that writes 'World!' to a text file"""

    def run(self):
        sleep(5)
        with open('world.txt', 'w') as world_file:
            world_file.write('World!')
            world_file.close()

    def output(self):
        return luigi.LocalTarget('world.txt')

class HelloWorldTask(luigi.Task):
    """Task that opens the 2 files and concatenates the 2 words
       and then saves the 2 words into a file"""

    def run(self):
        sleep(15)
        with open('hello.txt', 'r') as hello_file:
            hello = hello_file.read()
        with open('world.txt', 'r') as world_file:
            world = world_file.read()
        with open('hello_world.txt', 'w') as output_file:
            content = f'{hello} {world}'
            output_file.write(content)

    def requires(self):
        """HelloWorldTask will not run unless both HelloTask() and WorldTask()
           have been completed"""

        return [HelloTask(), WorldTask()]

    def output(self):
        return luigi.LocalTarget('hello_world.txt')



if __name__ == '__main__':
    luigi.run()