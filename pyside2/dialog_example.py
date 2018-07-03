from PySide2 import QtCore, QtGui, QtWidgets
import os

class DialogDemo(QtWidgets.QWidget):
    """"""
 
    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        # super(DialogDemo, self).__init__()
        QtWidgets.QWidget.__init__(self)
 
        self.label = QtWidgets.QLabel("Python rules!")
 
        # create the buttons
        colorDialogBtn = QtWidgets.QPushButton("Open Color Dialog")
        fileDialogBtn =  QtWidgets.QPushButton("Open File Dialog")
        self.fontDialogBtn = QtWidgets.QPushButton("Open Font Dialog")
        inputDlgBtn = QtWidgets.QPushButton("Open Input Dialog")
 
        # connect the buttons to the functions (signals to slots)
        colorDialogBtn.clicked.connect(self.openColorDialog)
        fileDialogBtn.clicked.connect(self.openFileDialog)
        self.fontDialogBtn.clicked.connect(self.openFontDialog)
        self.connect(inputDlgBtn, QtCore.SIGNAL("clicked()"), self.openInputDialog)
 
        # layout widgets
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(colorDialogBtn)
        layout.addWidget(fileDialogBtn)
        layout.addWidget(self.fontDialogBtn)
        layout.addWidget(inputDlgBtn)
        self.setLayout(layout)
 
        # set the position and size of the window
        self.setGeometry(100, 100, 400, 100)
 
        self.setWindowTitle("Dialog Demo")
 
    #----------------------------------------------------------------------
    def openColorDialog(self):
        """
        Opens the color dialog
        """
        color = QtWidgets.QColorDialog.getColor()
 
        if color.isValid():
            print(color.name())
            btn = self.sender()
            pal = btn.palette()
            pal.setColor(QtGui.QPalette.Button, color)
            btn.setPalette(pal)
            btn.setAutoFillBackground(True)
 
            #btn.setStyleSheet("QPushButton {background-color: %s}" % color)
 
    #----------------------------------------------------------------------
    def openFileDialog(self):
        """
        Opens a file dialog and sets the label to the chosen path
        """
        import os
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", os.getcwd())
        self.label.setText(path)
 
 
    #----------------------------------------------------------------------
    def openFontDialog(self):
        """
        Open the QFontDialog and set the label's font
        """
        font, ok = QtWidgets.QFontDialog.getFont()
        if ok:
            self.label.setFont(font)
 
    #----------------------------------------------------------------------
    def openInputDialog(self):
        """
        Opens the text version of the input dialog
        """
        text, result = QtWidgets.QInputDialog.getText(self, "I'm a text Input Dialog!",
                                            "What is your favorite programming language?")
        if result:
            print("You love %s!" % text)
 
#----------------------------------------------------------------------
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    form = DialogDemo()
    form.show()
    app.exec_()