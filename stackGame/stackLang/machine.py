from stackLang import parser, ast
import sys
import stackLang.CFG as CFG
# from inspect import getouterframes, currentframe

keyword2symbol = {'add': '+',
        'sub': '-',
        'and': '&',
        'or': '%',
        'gt': '>',
        'lt': '<',
        'eq': '=',
        'neg': '~',
        'not': '!',
        'odd': '#',
        'rotate': '^',
        'test': '/',
        'shift': '{'}

class StackMachine:
    def __init__(self):
        self.inputs = {0:3, 1:6}
        self.outputs = {0:0, 1:0}
        self.stack = []
        self.calls = []
        self.stacks = []
        self.temp = 0
        self.functions = {}
        self.returned = False
        self.workingDir = ''
        self.parser = None
        self.screen = []
        self.line = -1
        self.file = ''

    def print(self, caller=None):
        tab = '\t' * len(self.calls)
        if caller:
            print(tab, 'called from %s' % caller)
        print(tab, 'Stack:', self.stack)
        print(tab, 'Temp:', self.temp)
        print(tab, 'Outputs:', self.outputs)
        print(tab, 'Inputs:', self.inputs)
        print(tab, 'Screen:', self.screen)
        print()

    def update(self):
        # caller = getouterframes(currentframe(), 2)[1][3]
        caller = None
        # return
        self.print(caller)

    def push(self, value):
        self.update()
        self.stack.append(value)

    def input(self, input):
        if input not in self.inputs.keys():
            raise RuntimeError("there are only %i inputs"%(len(self.inputs.keys())))
        else:
            self.push(self.inputs[input])

    def pop(self):
        self.update()
        if len(self.stack) == 0:
            return False
        a = self.stack.pop(-1)
        return a

    def output(self, output):
        if output not in self.outputs.keys():
            raise RuntimeError("there are only %i outputs"%(len(self.outputs.keys())))
        else:
            p = self.pop()
            if output == 0:
                return
            if type(p) == bool:
                raise RuntimeError("tried to pop off the empty stack")
            self.outputs[output] = p

    def signalName(self, name):
        if name == 'height':
            return len(self.stack)
        elif name == 'top':
            if len(self.stack) == 0:
                raise RuntimeError("tried to access @top of empty stack")
            return self.stack[-1]
        elif name == 'temp':
            return self.temp
        else:
            raise RuntimeError('Unrecognized signal name "%s"' % name)

    def fundec(self, tree):
        name = tree.children[0].content
        numIn, numOut = int(tree.children[1].content), int(tree.children[2].content)
        tree.children.pop(0)
        tree.children.pop(0)
        tree.children.pop(0)
        self.functions[name] = (numIn, numOut, tree)

    def routinedec(self, tree):
        name = tree.children[0].content
        tree.children.pop(0)
        self.functions[name] = [tree]

    def funcall(self, tree):
        self.line = tree.line
        self.file = tree.file
        fun = tree.children[0].content
        print('start', fun)
        self.calls.append((self.line, 'function \'%s\''%fun, self.file))
        if fun not in self.functions:
            raise RuntimeError('Unknown function %s' % fun)
        f = self.functions[fun]
        if len(f) == 3:
            if len(self.stack) < f[0]:
                raise RuntimeError('%s takes %i items, @height is %i'
                                % (fun, f[0], len(self.stack)))
            st = (self.stack[:-f[0]], self.stack[-f[0]:])
            if f[0] == 0:
                st = st[::-1]
            self.stack = st[1]
            self.runProgram(f[2], self.workingDir)
            if len(self.stack) < f[1]:
                 raise RuntimeError('%s expected %i items for return, got %i'
                                 % (fun, f[1], len(self.stack)))
            self.stack = st[0]+self.stack[-f[1]:]
        else:
            self.runProgram(f[0])
        self.calls.pop()
        print('end', fun)

    def signal(self, tree):
        self.line = tree.line
        self.file = tree.file
        if tree.children[0].type == 'symbol': #@
            return self.signalName(tree.children[1].content)
        elif tree.children[0].type == 'name*':
            self.funcall(tree)
        else:
            return int(tree.children[0].content)>0

    def whilest(self, tree):
        while self.signal(tree.children[0]):
            for c in tree.children[1:]:
                self.dispatch(c)

    def splitst(self, tree):
        split = int(tree.children[0].content)
        stacks = [self.stack[:split], self.stack[split:]]
        print('stacks', split, stacks, self.stack)
        for c in tree.children[1:-1]:
            print(c.content.symbol)
            if c.content.symbol == 'Stmts1':
                self.stack = stacks[0]
                for child in c.children:
                    self.dispatch(child)
                stacks[0] = self.stack
            if c.content.symbol == 'Stmts2':
                self.stack = stacks[1]
                for child in c.children:
                    self.dispatch(child)
                stacks[1] = self.stack
        close = tree.children[-1].content
        if close == 'reverse':
            self.stack = stacks[1] + stacks[0]
        elif close == 'stack':
            self.stack = stacks[0] + stacks[1]
        elif close == 'merge':
            raise Exception("Unimplemented splitclose 'merge', TODO")
        else:
            raise Exception("Unimplemented splitclose '%s'" % close)

    def ifst(self, tree):
        if self.signal(tree.children[0]):
            for c in tree.children[1:]:
                if c.content.symbol == 'Elsest':
                    return
                self.dispatch(c)
        else:
            try:
                i = tree.children.index(CFG.Nonterminal('Elsest'))
            except Exception:
                return
            for c in tree.children[i+1:]:
                self.dispatch(c)

    def binaryop(self, tree):
        self.line = tree.line
        self.file = tree.file
        a, b = self.pop(), self.pop()
        if not (type(a) == int and type(b) == int):
            raise RuntimeError('tried to pop off the empty stack for %s'
                               % tree.children[0].content)
        op = tree.children[0].content
        if len(op) > 1:
            op = keyword2symbol[op]
        if op == '+':
            self.push(a + b)
        elif op == '-':
            self.push(a - b)
        elif op == '&':
            self.push(1 if (a and b) else 0)
        elif op == '%':
            self.push(1 if (a or b) else 0)
        elif op == '>':
            self.push(int(a > b))
        elif op == '<':
            self.push(int(a < b))
        elif op == '=':
            self.push(int(a == b))
        elif op == '{':
            if b < 0:
                self.push(int(a >> -b))
            else:
                self.push(int(a << b))
        else:
            raise RuntimeError("unknown binary operator %s" % op)

    def unaryop(self, tree):
        self.line = tree.line
        self.file = tree.file
        op = tree.children[0].content
        if op in keyword2symbol.keys():
            op = keyword2symbol[op]
        if op == '^' and self.signalName('height') == 0:
            return
        a = self.pop()
        if op == '~':
            self.push(-a)
        elif op == '!':
            self.push(0 if a else 1)
        elif op == '#':
            self.push(0 if a % 2 else 1)
            self.temp = a
        elif op == '^':
            self.stack = [a] + self.stack
        elif op == 'printc':
            self.screen.append(chr(a))
        elif op == 'printn':
            self.screen.append(str(a))
        elif op == '/':
            if a:
                print('test successful')
            else:
                raise RuntimeError('tested negative')
        else:
            raise RuntimeError("unknown unary operator %s" % op)

    def pushop(self, tree):
        if tree.children[0].type == 'symbol':#@
            self.push(self.signalName(tree.children[1].content))
        elif tree.children[0].type == 'keyword':#input
            self.input(int(tree.children[1].content))
        else: #numberliteral
            self.push(int(tree.children[0].content))

    def popop(self, tree):
        if tree.children[0].type == 'symbol': #@
            if tree.children[1].content != 'temp':
                raise RuntimeError("Unacceptable destination for pop \'%s\'"%tree.children[1].content)
            t = self.pop()
            if type(t) == int:
                self.temp = t
                return
            else:
                raise RuntimeError("tried to pop off the empty stack")
        self.output(int(tree.children[1].content))

    def returnst(self, tree):
        self.returned = True

    def importst(self, tree):
        try:
            self.calls.append((self.line, 'file ' + tree.children[1].content, self.file))
            self.runProgram(*self.getProgram(program=self.workingDir + '/' + tree.children[1].content))
            self.calls.pop()
        except FileNotFoundError:
            raise RuntimeError('Attempted to import %s, could not find file'
                               % tree.children[1].content)

    def dispatch(self, tree):
        self.line = tree.line
        self.file = tree.file
        if tree.content.symbol == 'Whilest':
            self.whilest(tree)
        elif tree.content.symbol == 'Splitst':
            self.splitst(tree)
        elif tree.content.symbol == 'Ifst':
            self.ifst(tree)
        elif tree.content.symbol == 'BinaryOp':
            self.binaryop(tree)
        elif tree.content.symbol == 'UnaryOp':
            self.unaryop(tree)
        elif tree.content.symbol == 'PushOp':
            self.pushop(tree)
        elif tree.content.symbol == 'PopOp':
            self.popop(tree)
        elif tree.content.symbol == 'FunDec':
            self.fundec(tree)
        elif tree.content.symbol == 'RoutineDec':
            self.routinedec(tree)
        elif tree.content.symbol == 'FunCall':
            self.funcall(tree)
        elif tree.content.symbol == 'Returnst':
            self.returnst(tree)
        elif tree.content.symbol == 'Importst':
            self.importst(tree)
        else:
            raise RuntimeError("runtime error, unknown name: %s" % tree.content.symbol)

    def doRunProgram(self, program, workingDir=None):
        if workingDir is None:
            workingDir = self.workingDir
        self.workingDir = workingDir
        for c in program.children:
            self.dispatch(c)
            if self.returned:
                self.returned = False
                if not self.stack:
                    raise RuntimeError('Tried to return from empty stack')
                self.update()
                break
        return

    def runProgram(self, program, workingDir=None):
        try:
            self.doRunProgram(program, workingDir)
        except RuntimeError as e:
            print('Traceback:')
            files = {}
            for c in self.calls:
                location = c[1].split(' ')
                if location[0] == 'file':
                    location = 'in main body'
                else:
                    location = 'in function %s' % location[1]
                print("Line %i in file %s %s" % (c[0], c[2], location))
                if c[2] not in files.keys():
                    with open(c[2], 'r') as fIn:
                        files[c[2]] = fIn.readlines()
                    print('\t', files[c[2]][c[0]-1])
            print("RuntimeError:", e.args[0])
            exit(2)

    def getProgram(self, grammar=None, tokens=None, program=None):
        lines = []
        with open('stackLang/stackLang/languageDef.txt', 'r') as ld:
            for line in ld:
                lines.append(line.strip())
        if grammar:
            lines[0] = grammar
        if program:
            lines[2] = program
        llParser = parser.LLParser(lines[0], lines[1])
        workingDir = '/'.join(lines[2].split('/')[:-1])
        llParser.loadProgram(lines[2], workingDir)
        cst = llParser.parse()
        program = ast.getAst(cst)
        return program, workingDir

    def getProgramFromText(self, text, grammar=None, tokens=None, program=None):
        lines = []
        with open('/home/ophiuchus/Documents/stackGame/stackGame/stackLang/stackLang/languageDef.txt', 'r') as ld:
            for line in ld:
                lines.append(line.strip())
        if grammar:
            lines[0] = grammar
        if program:
            lines[2] = program
        llParser = parser.LLParser(lines[0], lines[1])
        workingDir = '/'.join(lines[2].split('/')[:-1])
        llParser.loadProgramFromText(text)
        cst = llParser.parse()
        program = ast.getAst(cst)
        return program, workingDir


if __name__ == '__main__':
    SM = StackMachine()
    SM.runProgram(*SM.getProgram())
    SM.print()
