from stackLang import parser, ast
import sys
import CFG

keyword2symbol = {'add': '+',
        'sub': '-',
        'and': '&',
        'or': '%',
        'gt': '>',
        'lt': '<',
        'eq': '=',
        'neg': '~',
        'not': '!',
        'swap': '#',
        'rotate': '^',
        'test': '/'}

class StackMachine:
    def __init__(self):
        self.inputs = {0:3, 1:6}
        self.outputs = {0:0, 1:0}
        self.stack = []
        self.temp = 0
        self.functions = {}
        self.returned = False
        self.nest = 0
        self.workingDir = ''
        self.parser = None

    def print(self):
        print('\t' * self.nest, 'Stack:',self.stack)
        print('\t' * self.nest, 'Temp:',self.temp)
        print('\t' * self.nest, 'Outputs:',self.outputs)
        print('\t' * self.nest, 'Inputs:',self.inputs)
        print()

    def update(self):
        pass
        self.print()

    def push(self, value):
        self.update()
        self.stack.append(value)

    def input(self, input):
        if input not in self.inputs.keys():
            raise Exception("Runtime error: there are only %i inputs"%(len(self.inputs.keys())))
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
            raise Exception("Runtime error: there are only %i outputs"%(len(self.outputs.keys())))
        else:
            p = self.pop()
            if output == 0:
                return
            if type(p) == bool:
                raise Exception("Runtime error, tried to pop off the empty stack")
            self.outputs[output] = p

    def signalName(self, name):
        if name == 'height':
            return len(self.stack)
        elif name == 'top':
            return self.stack[-1]
        elif name == 'temp':
            return self.temp

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
        self.nest += 1
        fun = tree.children[0].content
        print('start', fun)
        if fun not in self.functions:
            raise Exception('Unknown function %s: line %i'%(fun, tree.children[0].line))
        f = self.functions[fun]
        if len(f) == 3:
            if len(self.stack) < f[0]:
                raise Exception('Runtime error line %i: %s takes %i items, @height is %i'%(tree.children[0].line, fun, f[0], len(self.stack)))
            st = (self.stack[:-f[0]], self.stack[-f[0]:])
            self.stack = st[1]
            self.runProgram(f[2])
            if len(self.stack) < f[1]:
                 raise Exception('Runtime error line %i: %s expected %i items for return, got %i'%(tree.children[0].line, fun, f[1], len(self.stack)))
            self.stack = st[0]+self.stack[-f[1]:]
        else:
            self.runProgram(f[0])
        print('end', fun)
        self.nest -= 1


    def signal(self, tree):
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
        stacks = (self.stack[:split], self.stack[split:])
        for c in tree.children[1:-1]:
            if c.content.symbol == 'Op1_':
                self.stack = stacks[1]
                self.dispatch(c.children[0])
            elif c.content.symbol == 'Op2_':
                self.stack = stacks[0]
                self.dispatch(c.children[1])
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
        a, b = self.pop(), self.pop()
        if not (type(a) == int and type(b) == int):
            raise RuntimeError('Line %i: tried to pop off the empty stack for %s'%(tree.children[0].line, tree.children[0].content))
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
        else:
            raise RuntimeError("unknown binary operator %s"%op)

    def unaryop(self, tree):
        op = tree.children[0].content
        if len(op) > 1:
            op = keyword2symbol[op]
        if op == '^' and self.signalName('height') == 0:
            return
        a = self.pop()
        if op == '~':
            self.push(-a)
        elif op == '!':
            self.push(0 if a else 1)
        elif op == '#':
            self.push(self.temp)
            self.temp = a
        elif op == '^':
            self.stack = [a] + self.stack
        elif op == '/':
            if a:
                pass
            else:
                raise RuntimeError('Line %i: tested negative'%tree.children[0].line)
        else:
            raise RuntimeError("unknown unary operator %s"%op)

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
                raise RuntimeError("line %i: tried to pop off the empty stack"%tree.children[0].line)
        self.output(int(tree.children[1].content))

    def returnst(self, tree):
        self.returned = True

    def importst(self, tree):
        try:
            print(self.getProgram(program=self.workingDir + '/' + tree.children[1].content))
        except FileNotFoundError:
            raise RuntimeError('Line %i: Attempted to import %s, could not find file'%(tree.children[0].line, tree.children[1].content))

    def dispatch(self, tree):
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
            raise Exception("runtime error, unknown name: %s" % tree.content.symbol)

    def runProgram(self, program, workingDir):
        self.workingDir = workingDir
        for c in program.children:
            self.dispatch(c)
            if self.returned:
                self.returned = False
                if not self.stack:
                    raise Exception('Tried to return from empty stack, line %i' % c.line())
                break
        return

    def getProgram(self, grammar=None, program=None):
        lines = []
        with open('languageDef.txt', 'r') as ld:
            for line in ld:
                lines.append(line.strip())
        if grammar:
            lines[0] = grammar
        if program:
            lines[1] = program
        print('l1, "%s"'%lines[1])
        if not self.parser:
            self.parser = parser.LLParser(lines[0])
        workingDir = '/'.join(lines[1].split('/')[:-1])
        self.parser.loadProgram(lines[1], workingDir)
        print(self.parser.program)
        cst = self.parser.parse()
        program = ast.getAst(cst)
        # program.print()
        return program, workingDir


SM = StackMachine()
SM.runProgram(*SM.getProgram())
SM.print()
