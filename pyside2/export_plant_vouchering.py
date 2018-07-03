from datetime import datetime
from PySide2 import QtCore, QtGui, QtWidgets
import luigi
import os


class MyGlobals(luigi.Config):
    """Define 'global' parameter values here"""

    mydate = datetime.today()
    data_folder = 'outputs/text_files/'

    #labor_rate = input("Enter labor rate in GBP: ")
    #part_factor = input("Enter part cost factor (0.#): ")
    #handling_factor = input("Enter handling cost factor (0.#): ")
    start_voucher_date = input("Enter start voucher date (YYYY-MM-DD): ")
    end_voucher_date = input("Enter end voucher date (YYYY-MM-DD): ")

class DialogDemo(QtWidgets.QWidget):
    """"""
 
    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        # super(DialogDemo, self).__init__()
        QtWidgets.QWidget.__init__(self)
 
        layout = QtWidgets.QFormLayout()
        self.start_voucher_date = QtWidgets.QLineEdit()
        layout.addRow(QtWidgets.QLabel("Start Voucher Date: "), self.start_voucher_date)
        self.end_voucher_date = QtWidgets.QLineEdit()
        layout.addRow(QtWidgets.QLabel("End Voucher Date: "), self.end_voucher_date)
        self.setLayout(layout)
 
        self.setGeometry(100, 100, 400, 100)
 
        self.setWindowTitle("Export Plant Vouchering")

 
#----------------------------------------------------------------------
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    form = DialogDemo()
    form.show()
    app.exec_()