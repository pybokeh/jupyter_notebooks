import remi.gui as gui
from remi import start, App
import pandas as pd
from db import DB

# import ipdb; ipdb.set_trace()

class MyApp(App):
    def __init__(self, *args):
        super(MyApp, self).__init__(*args)

    def main(self):
        self.masterContainer = gui.Widget(1200, 1000, gui.Widget.LAYOUT_VERTICAL, 10)

        topContainer = gui.Widget(800, 300, gui.Widget.LAYOUT_HORIZONTAL, 10)
        self.bottomContainer = gui.Widget(800, 300, gui.Widget.LAYOUT_HORIZONTAL, 10)

        self.lbl = gui.Label(200, 30, 'Team name:')
        self.txt = gui.TextInput(200, 30)
        self.btn = gui.Button(200, 30, 'Submit')
        self.btn.set_on_click_listener(self, 'on_button_pressed')
        topContainer.append('1', self.lbl)
        topContainer.append('2', self.txt)
        topContainer.append('3', self.btn)

        self.masterContainer.append('1', topContainer)
        #self.masterContainer.append('2', self.bottomContainer)

        return self.masterContainer

    def on_button_pressed(self):
        db = DB(filename="/home/pybokeh/Dropbox/data_sets/nba", dbtype="sqlite")

        column_names = [column.name for column in db.tables.regular_season_avgs._columns]

        sql = """
        select *

        from player_shooting_stats

        where
        team_name like '{{ name }}';"""

        token = self.txt.get_text()

        parameter = '%' + token + '%'

        params = [
                  {"name": parameter}
                 ]

        sql2 = """
        select *

        from player_game_stats

        where
        team_name like '%Laker%'
        """

        row_data = db.query(sql, data=params).values

        #row_data = db.query(sql2).values

        self.table = gui.Table(800, 600)

        row = gui.TableRow()
        for column in column_names:
            item = gui.TableTitle()
            item.append(str(id(item)), str(column))
            row.append(str(id(item)), item)

        self.table.append(str(id(row)), row)


        for _row in row_data:
            row = gui.TableRow()
            for row_item in _row:
                item = gui.TableTitle()
                item.append(str(id(item)), str(row_item))
                row.append(str(id(item)), item)

                self.table.append(str(id(row)), row)

        self.masterContainer.append('2', self.bottomContainer)
        self.bottomContainer.append('1', self.table)

        print(len(row_data))


if __name__ == "__main__":
    start(MyApp)
