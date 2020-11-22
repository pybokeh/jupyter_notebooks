import remi.gui as gui
from remi import start, App
from db import DB    # db.py: useful library from Yhat for interfacing with databases

class MyApp(App):
    def __init__(self, *args):
        super(MyApp, self).__init__(*args)

    def main(self):
        # create "master" container which will hold top container and bottom container
        # We will add widgets to it vertically
        self.masterContainer = gui.Widget(1200, 50, gui.Widget.LAYOUT_VERTICAL, 10)

        # Create top container and then widgets will be added to it horizontally
        topContainer = gui.Widget(1200, 50, gui.Widget.LAYOUT_HORIZONTAL, 10)

        # Create bottom container
        self.bottomContainer = gui.Widget(1200, 0, gui.Widget.LAYOUT_HORIZONTAL, 0)

        # Create widgets that will be placed in the top container
        self.lbl = gui.Label(200, 30, 'Team name:')
        self.txt = gui.TextInput(200, 30)
        self.btn = gui.Button(200, 30, 'Submit')
        self.btn.set_on_click_listener(self, 'on_button_pressed')

        # Add those widgets to the top container
        topContainer.append('1', self.lbl)
        topContainer.append('2', self.txt)
        topContainer.append('3', self.btn)
        
        # At startup, we want to just add the top container to the master container
        self.masterContainer.append('1', topContainer)
        
        # At startup, make it so the textinput widget is ready to accept input
        self.txt.attributes['tabindex'] = "1"
        self.txt.attributes['autofocus'] = "autofocus"

        # return / render the master container
        return self.masterContainer

    # What happens when the user clicks on the "Submit" button
    def on_button_pressed(self):
        # Connect to the sqlite database using DB.py
        db = DB(filename="/home/pybokeh/Dropbox/data_sets/nba", dbtype="sqlite")

        sql = """
        select *

        from player_game_stats

        where
        team_name like '{{ name }}';"""

        # Get the text the user entered into the textinput widget
        token = self.txt.get_text()

        # To prevent sql injection attacks, parameterize the sql string
        parameter = '%' + token + '%'

        params = [
                  {"name": parameter}
                 ]

        # Execute the query and store the results into a pandas dataframe
        df = db.query(sql, data=params)

        # Get the column names of the query result and the query row_data
        column_names = df.columns
        row_data = df.values

        # Create the table widget with the specified dimensions
        self.table = gui.Table(1200, 800)
       
        # Generate the table row containing the table column names
        row = gui.TableRow()
        for column in column_names:
            item = gui.TableTitle()  # TableTitle refers to the column header/names
            item.append(str(id(item)), str(column))
            row.append(str(id(item)), item)

        # Now add the row to the table
        self.table.append(str(id(row)), row)

        # Generate rows that will contain the table data
        for _row in row_data:
            row = gui.TableRow()
            for row_item in _row:
                item = gui.TableItem() # TableItem refers to the table data
                item.append(str(id(item)), str(row_item))
                row.append(str(id(item)), item)

                self.table.append(str(id(row)), row)

        # Now render / add the bottom container to the master container
        self.masterContainer.append('2', self.bottomContainer)

        # Now add the table widget to the bottom container        
        self.bottomContainer.append('1', self.table)

if __name__ == "__main__":
    start(MyApp)
