import random
import sys

from PyQt5.uic.properties import QtWidgets

from stackLang.machine import StackMachine
from hackenbush.bush import Bush
from PySide6.QtCore import Qt, Slot
from PyQt5.QtGui import QPainter, QBrush, QPen
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow
from PySide6.QtWidgets import (QApplication, QLabel, QPushButton,
                               QVBoxLayout, QWidget, QLineEdit, QTextEdit)

DISPLAY_SIZE = (800,600)

class HackenBush(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.ground = Bush.startGame()
        self.branches = {}
        self.realignBush(self.ground)

    def realignBush(self, branch):
        if branch.parent[0]:
            self.branches[branch] = branch.pos.mulV(DISPLAY_SIZE)
        for c in branch.children:
            self.realignBush(c)

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin()
        qp.drawLine(10, 10, 300, 200)
        qp.end()


class MyWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.machine = StackMachine()
        self.button = QPushButton("Execute")
        self.message = QLabel("Type your code")
        self.message.alignment = Qt.AlignCenter
        self.box = QTextEdit()
        self.box.setText('''push 1
push 5
push 4
add
add
push 10
eq
test''')

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.message)
        self.layout.addWidget(self.box)
        self.layout.addWidget(self.button)

        # Connecting the signal
        self.button.clicked.connect(self.executeBox)

    @Slot()
    def executeBox(self):
        print('executing')
        txt = self.box.toPlainText()
        print(txt)
        self.machine.runProgram(self.machine.getProgramFromText(txt))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    widget = HackenBush()
    # widget = MyWidget()

    widget.show()

    sys.exit(app.exec())