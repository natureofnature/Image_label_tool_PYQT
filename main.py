import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from Labeling_tool import Window



def main():
    app = QApplication(sys.argv)
    scr = app.primaryScreen()
    screen = Window(scr)
    screen.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()


