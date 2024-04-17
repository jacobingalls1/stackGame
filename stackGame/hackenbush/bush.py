import random

class Vect:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vect(self.x + other.x, self.y + other.y)

    def __neg__(self):
        return Vect(-self.x, -self.y)

    def __sub__(self, other):
        return self + -other

    def __mul__(self, other):
        if type(other) is int:
            return Vect(self.x * other, self.y * other)
        return Vect(self.x * other.x, self.y * other.y)

    def __repr__(self):
        print('<%f, %f>' % (self.x, self.y))

    def unpack(self):
        return self.x, self.y

class Rect:
    def __init__(self, x0, y0, x1=None, y1=None):
        if type(x0) == type(y0) == Vect and x1 is None and y1 is None:
            self.first = x0
            self.last = y0
        else:
            self.first = Vect(x0, y0)
            self.last = Vect(x1, y1)

    def __add__(self, other):
        if type(other) is Vect:
            return Rect(self.first + other, self.last + other)

    def __neg__(self):
        return Rect(-self.first, -self.last)

    def __sub__(self, other):
        return self + -other

    def __mul__(self, other):
        if type(other) in (int, Vect):
            return Rect(self.first * other, self.last * other)
        elif type(other is Rect):
            r = Rect(self.first, self.last)
            r -= other.BLCorner()
            r *= Vect(other.width() / self.width(), other.height / self.height())

    def x(self):
        return self.first.x, self.last.x

    def y(self):
        return self.first.y, self.last.y

    def height(self):
        return abs(self.y()[0] - self.y()[1])

    def width(self):
        return abs(self.x()[0] - self.x()[1])

    def top(self):
        return max(self.y())

    def bottom(self):
        return min(self.y())

    def left(self):
        return min(self.x())

    def right(self):
        return max(self.x())

    def BLCorner(self):
        return Vect(self.left(), self.bottom())

    def TRCorner(self):
        return Vect(self.right(), self.top())

    def unpack(self):
        return *self.first.unpack(), *self.last.unpack()

class Bush:
    ID = 0
    def __init__(self, parent, color, ground=False):
        self.ID = Bush.ID
        Bush.ID += 1
        self.parent = [parent]
        self.color = color
        self.children = []
        self.ground = ground
        self.pos = None

    def __repr__(self):
        return str(self.ID) + (str(self.children) if self.children else '')

    def growChild(self, color):
        self.children.append(Bush(self, color))
        return self.children[-1]

    def floating(self):
        if any([self in p.children for p in self.parent]):
            return False

    def fall(self, branches):
        ret = []
        for b in branches:
            if b.floating():
                ret.append(b)
                ret += self.fall(b.children)
        return ret

    def chop(self, color):
        if color != self.color:
            raise Exception("COLOR %s is not COLOR %s"%(color, self.color))
        if self.ground:
            raise Exception("CANNOT CHOP GROUND")
        self.parent.children.remove(self)
        f = self.fall(self.children)
        return f

    def cullNone(self):
        self.children = [c for c in self.children if c]
        for c in self.children:
            c.cullNone()

    def depth(self):
        if self.children:
            return max([c.depth() for c in self.children]) + 1
        return 0

    def alignBush(self, r=2/3, rect=Rect(0, 0, 1, 1)):
        if self.ground:
            self.pos = Rect(.5, 0, .5, 0)
        if len(self.parent) == 2:
            if self.parent[0] == self.parent[1]:
                p = self.parent[0].pos.first
                self.pos = Rect(p, p)
            else:
                self.pos = Rect(self.parent[0].pos.last, self.parent[1].pos.last)
        gc = len(self.children)
        if gc:
            d = max([c.depth() for c in self.children]) + 1
            sizeh = sum([r**(i+1) for i in range(d)])
            scaleh = rect.height() / sizeh
            for i in range(gc):
                c = self.children[i]
                c.pos = Rect(self.pos.last, Vect(rect.width() * (.5 + i)/gc, r * scaleh) + rect.BLCorner())
                c.alignBush(r, Rect(Vect(rect.width() * i/gc, r * scaleh) + rect.BLCorner(),
                                    Vect(rect.width() * (i+1)/gc + rect.BLCorner().x, rect.TRCorner().y)))


    # def alignBush(self, r=2/3, rect=Rect(0, 0, 1, 1)):
    #     if len(self.parent) == 2:
    #         self.pos = Rect(0, 0, 0, (1 - rect.y1)/4)
    #     gc = len(self.children)
    #     if gc:
    #         d = max([c.depth() for c in self.children]) + 1
    #         sizeh = sum([r**(i+1) for i in range(d)])
    #         scale = rect.height()/sizeh
    #         for i in range(gc):
    #             c = self.children[i]
    #             c.pos = Rect(.5+i/gc, 0,
    #                          .5+i/gc, r*scale) + rect.BLCorner()
    #             c.alignBush(r, Rect(i / gc + rect.x0, r * scale + rect.y0, (i+1) / gc + rect.x0, rect.top()))





    @staticmethod
    def startGame(maxChildren=3, numBranches=5, connectBack=.5):
        g = Bush(None, None)
        g.ground = True
        branches = [g.growChild(random.choice(("RED", "BLUE")))]
        for n in range(numBranches):
            b = [b for b in branches if len(b.children) < maxChildren]
            r = random.choice(b)
            c = r.growChild(random.choice(("RED", "BLUE")))
            if random.random() < connectBack:
                b = [b for b in branches if len(b.children) < maxChildren]
                if not b:
                    break
                r = random.choice(b)
                r.children.append(c)
                c.parent.append(r)
                c.children = [None for n in range(maxChildren)]
            branches.append(c)
        g.cullNone()
        g.alignBush()
        return g


# print(Bush.startGame())