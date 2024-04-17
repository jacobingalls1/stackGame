import sys

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from hackenbush.bush import Bush, Vect

import random

random.seed(0)


DISPLAY_SIZE = (800,600)

class Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.ground = Bush.startGame()
        self.branches = {}
        self.realignBush(self.ground)

    def realignBush(self, branch):
        if branch.parent[0]:
            self.branches[branch] = branch.pos * Vect(600, 500) + Vect(100, 50)
        for c in branch.children:
            self.realignBush(c)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(Qt.red)
        print(self.branches)

        for b in self.branches.keys():
            painter.setPen(Qt.red if b.color == "RED" else Qt.blue)
            if len(b.parent) == 2:
                if b.parent[0] == b.parent[1]:
                    p = self.branches[b].first
                    p0 = p + Vect(-25, 0)
                    p1 = p + Vect(25, 50)
                    print("HERE")
                    print(p)
                    print(p0)
                    print(p1)
                    print("THERE")
                    exit()
                    painter.drawArc(p.x - 25, p.y,
                                    p.x + 25, p.y + 50,
                                    0, 16*360)

                continue
            painter.drawLine(*[int(i) for i in self.branches[b].unpack()])

        painter.end()

    def mouseReleaseEvent(self, ev):
        lpos = ev.position() if hasattr(ev, 'position') else ev.localPos()
        print(lpos)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Widget()
    ex.resize(*DISPLAY_SIZE)
    ex.show()
    sys.exit(app.exec_())