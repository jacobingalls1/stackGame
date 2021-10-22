from lexer import loadProgram, tokenize, Token
import CFG
import sys

lmbda = Token('keyword', 'lambda', -1)
table = CFG.table(sys.argv[1])
toks = tokenize(loadProgram(sys.argv[2]))
print(table)















































