from stackLang.machine import StackMachine
import sys
from stackLang import parser, ast
import stackLang.lexer as lexer

with open('stackLang/languageDef.txt') as lang:
    grammar, _ = lang.readlines()
    grammar = grammar.strip()

lex = lexer.Lexer('stackLang')

def getProgram(op):
    sp = parser.LLParser(grammar)
    sp.program = lex.tokenize([op + '.'])
    cst = sp.parse()
    program = ast.getAst(cst)
    program.print()
    return program


def toList(string):
    string = string[1:-1]
    return [int(i) for i in string.split(',')]


def toDict(string):
    pairs = string[1:-1].split(',')
    pairs = [p.split(':') for p in pairs]
    return {int(p[0]):int(p[1]) for p in pairs}


def opTest():
    SM = StackMachine()
    with open('stackLang/tests/ops', 'r') as ops:
        for line in ops:
            line = line.strip()
            if not line or '#' in line:
                continue
            line = line.split(' ')
            op = line[0]
            print('RUNNING %s NOW'%op)
            start = toList(line[1])
            final = toList(line[2])
            line = line[3:]
            if line:
                SM.temp = int(line[0])
            SM.stack = start
            prog = getProgram(op)
            SM.runProgram(prog, '')
            if SM.stack != final:
                raise Exception('Failure in testing %s, expected %s, got %s'%(op, final, SM.stack))


def pushPopTest():
    SM = StackMachine()
    with open('stackLang/tests/pushpop', 'r') as ops:
        for line in ops:
            line = line.strip()
            if not line or '#' in line:
                continue
            print('line:', line)
            line = line.split(' | ')
            op = line[0]
            line = line[1].split(' ')
            print('RUNNING %s NOW'%op)
            start = toList(line[0])
            final = toList(line[1])
            temp = int(line[2])
            inputs = toDict(line[3])
            expectedOutput = toDict(line[4])
            SM.stack = start
            SM.inputs = inputs
            SM.temp = temp
            SM.outputs = {0:0, 1:0}
            print('outputs', SM.outputs)
            prog = getProgram(op)
            SM.runProgram(prog, '')
            if SM.stack != final:
                raise Exception('Failure in testing %s, expected %s, got %s'%(op, final, SM.stack))
            elif SM.outputs != expectedOutput:
                raise Exception('Failure in testing %s, expected %s, got %s' % (op, expectedOutput, SM.outputs))


def runProgram(program):
    lines = []
    with open('stackLang/languageDef.txt', 'r') as ld:
        for line in ld:
            lines.append(line.strip())
    sp = parser.LLParser(lines[0])
    workingDir = '/'.join(program.split('/')[:-1])
    sp.loadProgram(program, workingDir)
    cst = sp.parse()
    program = ast.getAst(cst)
    program.print()
    SM = StackMachine()
    SM.runProgram(program, workingDir)
    SM.print()


tests = [opTest, pushPopTest, 'stackLang/examples/functions.test']


def runTests():
    with open('log.txt', 'w+') as f:
        successes = []
        std, sys.stdout = sys.stdout, f
        for test in tests:
            try:
                if type(test) == str:
                    runProgram(test)
                    successes.append(test)
                else:
                    test()
                    successes.append(test.__name__)
            except Exception:
                pass
        sys.stdout = std
        for test in tests:
            if type(test) != str:
                test = test.__name__
            outcome = 'Success' if test in successes else 'Failure'
            print('{0:<40} {1}'.format(test+':', outcome))
        return len(successes) == len(tests)




