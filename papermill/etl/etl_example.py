from getpass import getpass
import papermill as pm
import schedule
import time


def etl():
    """ Function that performs ETL """


    # Extract the Ohio teachers' salary information
    pm.execute_notebook(
        'Extract.ipynb',
        'output/Extract.ipynb'
    )

    # Transform the data
    pm.execute_notebook(
        'Transform.ipynb',
        'output/Transform.ipynb'
    )

    # Load (email) the data
    pm.execute_notebook(
        'Load.ipynb',
        'output/Load.ipynb',
        parameters=dict(RECIPIENT_EMAIL='somebody@company.com',
                        GMAIL_PWD='your_password'
                   )
    )

    #return schedule.CancelJob

schedule.every().day.at("11:52").do(etl)

while True:
    schedule.run_pending()
    time.sleep(1)