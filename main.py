import sys
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import QApplication,QSplashScreen
from PyQt5.QtCore import Qt
from Labeling_tool import Window
import time


def main():
    app = QApplication(sys.argv)
    splash = QSplashScreen(QPixmap("./configure_files/splash.jpg"))
    splash.show()
    font = QFont()
    font.setPointSize(30)
    font.setBold(True)
    font.setWeight(75)
    splash.setFont(font)
    splash.showMessage("Labeling_tool by LWZ ",Qt.AlignCenter,Qt.red,)
    time.sleep(1)
    splash.showMessage("Please wait。。。", Qt.AlignCenter, Qt.red)
    time.sleep(1)
    app.processEvents()
    scr = app.primaryScreen()
    screen = Window(scr)
    screen.show()
    splash.finish(screen)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()


