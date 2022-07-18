from stackLang.lexer import Lexer, Token
import stackLang.CFG as CFG


class Tree:
    def __init__(self, parent, content, line, file=''):
        self.parent = parent
        self.content = content
        self.children = []
        self.line = line
        self.file = file

    def print(self, tabs=0):
        print('\t'*tabs, self.content)
        for i in self.children:
            if type(i) == Token:
                print('\t'*(tabs+1), i)
            else:
                i.print(tabs+1)

class LLParser:
    def __init__(self, grammarf, tokenf):
        self.tokenf = tokenf
        self.program = None
        self.expected = ['Program']
        self.table = CFG.getTable(grammarf, tokenf)
        self.head = Tree(None, 'TREETOP', -1)
        self.root = self.head
        self.line = -1
        self.file = ''

    def loadProgram(self, f, workingDir):
        lexer = Lexer(workingDir, self.tokenf)
        self.program = lexer.tokenize(lexer.loadProgram(f))

    def doError(self):
        self.printTree(self.root, [])
        raise Exception('Token error, line %i: \n\tunexpected token in %s: \n\t\t%s\n\texpected %s'%
                (self.program[0].line, self.head.name, self.program[0], self.expected[0]))

    def exp(self):
        nt = self.head.content
        if type(nt) != str:
            nt = nt.symbol
        if self.table[nt][self.program[0]] is None:
            raise Exception('None in table for NT%s, with terminal %s'%(nt, self.program[0]))
        return self.table[nt][self.program[0]]

    def tokPop(self):
        while (self.program and self.expected and self.expected[0] == self.program[0]) or \
                (self.expected and type(self.expected[0]) == CFG.Token and self.expected[0].type == 'control'):#tree up or exp tok and prog tok
            if self.expected[0] == Token('control', 'treeup', -1):
                self.expected = self.expected[1:]
                self.head = self.head.parent
            elif self.expected[0] == Token('control', 'empty', -1):
                self.expected = self.expected[2:]
                temp = self.head
                self.head = self.head.parent
                self.head.children.remove(temp)
            elif self.expected[0] == self.program[0]:
                self.line = self.program[0].line
                self.file = self.program[0].file
                self.head.children.append(self.program.pop(0))
                self.expected.pop(0)
            elif not (self.program and self.expected):
                if self.expected and self.expected[0] == Token('control', 'treeup', -1):
                    continue
                if self.program:
                    raise Exception('Error, line %i: expected end of program, got %s' %
                                    (self.program[0].line, self.program[0]))
                elif self.expected:
                    raise Exception('Error: expected %s but got end of file' % self.expected[0])
                break
        if self.expected and type(self.expected[0]) is Token:
            raise Exception('Unexpected token, line %i: %s in %s, expected %s' %
                            (self.program[0].line, self.program[0], self.head.content, self.expected[0]))

    def doStep(self):
        # self.root.print()
        self.head.children.append(Tree(self.head, self.expected[0], self.line, self.file))
        self.head = self.head.children[-1]
        self.expected = self.expected[1:]
        self.expected = self.exp() + [Token('control', 'treeup', -1)] + self.expected
        if None in self.expected:
            raise Exception('None added to expected list: %s with terminal %s'%(self.head.content, self.program[0]))
        self.tokPop()

    def parse(self):
        while self.program:
            self.doStep()
        return self.head.children[0]
























































