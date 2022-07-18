from stackLang import machine, tests
import display
import sys

if tests.runTests():
    print('All tests successful!')
SM = machine.StackMachine()
SM.runProgram(*SM.getProgram())
# SM.print()


