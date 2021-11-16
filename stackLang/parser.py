from lexer import loadProgram, tokenize, Token
import CFG
import sys

class Tree:
    def __init__(self, parent, content):
        self.parent = parent
        self.content = content
        self.children = []

    def print(self, tabs=0):
        print('\t'*tabs, self.content)
        for i in self.children:
            if type(i) == Token:
                print('\t'*(tabs+1), i)
            else:
                i.print(tabs+1)

class LLParser:
    def __init__(self, grammarf):
        self.program = None
        self.expected = ['Program', Token('control', 'EOF', -1)]
        self.table = CFG.table(grammarf)
        self.head = Tree(None, 'Program')
        self.root = self.head

    def loadProgram(self, f):
        self.program = tokenize(loadProgram(f))

    def doError(self):
        self.printTree(self.root, [])
        print('Token error, line %i: \n\tunexpected token in %s: \n\t\t%s\n\texpected %s'%
                (self.program[0].line, self.head.name, self.program[0], self.expected[0]))
        exit(1)

    def exp(self):
        print('self.expected', self.expected)
        print('exp', self.head.content, self.program[0])
        print('table[exp][]', self.table[self.head.content][self.program[0]])
        return self.table[self.head.content][self.program[0]]

    def tokPop(self):
        while self.expected[0] == self.program[0] or self.expected[0] == Token('control', 'treeup', -1):
            if self.expected[0] == Token('control', 'treeup', -1):
                self.expected = self.expected[1:]
                self.head = self.head.parent
                continue
            self.head.children.append(self.expected.pop(0))
            self.program.pop(0)
        if type(self.expected[0]) is Token:
            print('Unexpected token %s in %s, expected %s'%(self.program[0], self.head.content, self.expected[0]))
            exit(1)

    def doStep(self):
        self.head.children.append(Tree(self.head, self.expected[0]))
        self.head = self.head.children[-1]
        self.expected = self.expected[1:]
        self.expected = self.exp() + [Token('control', 'treeup', -1)] + self.expected
        self.tokPop()
        print('expected', self.expected)
        print('program', self.program)

    def parse(self):
        while self.program:
            self.doStep()
            self.root.print()
        return self.head


sp = LLParser(sys.argv[1])
sp.loadProgram(sys.argv[2])
print(sp.program)
t = sp.table
print(t)




sp.parse().print()





















































