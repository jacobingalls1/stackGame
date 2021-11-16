import re
import sys


symbol = '@.+-~&v!><=x'

keyword = r'split|swap|stack|merge|while|if|else|return|push|input|output|pop|rotate|add|sub|and|not|or|gt|eq|swap|height|top|temp|dump|in|out'

numberLiteral = r'0|-?[1-9][0-9]*'

class Token(object):
    def __init__(self, type, content=None, line=-1):
        self.type = type
        self.content = content
        self.line = line
    
    def __repr__(self):
        return '(%s, %s, %i)'%(self.type, self.content, self.line)

    def __eq__(self, other):
        if type(self)==type(other) and self.type == other.type and (self.content == other.content or self.content==None or other.content==None):
            return True
        return False
    
    def __hash__(self):
        ret = hash(self.type)
        if self.type in ['keyword', 'symbol']:
            ret+=hash(self.content)
        return ret

    def write(self):
        return '<%s> %s </%s>'%(self.type, self.content, self.type)

    def clean(self):
        return Token(self.type, self.content)

def loadProgram(fileName):
    ret = []
    with open(fileName) as f:
        for line in f:
            ret.append(line.strip().split('#')[0])
    return ret


line = 0

def tokSpace(tok, line):
    ret = []
    while tok:
        if tok[0] in symbol:
            ret.append(Token('symbol', tok[0], line))
            tok = tok[1:]
            continue
        x = re.match(keyword, tok)
        if x:
            ret.append(Token('keyword', tok[:x.end()], line))
            tok = tok[x.end():]
            continue
        x = re.match(numberLiteral, tok)
        if x:
            ret.append(Token('numberLiteral*', int(tok[:x.end()]), line))
            tok = tok[x.end():]
            continue
        return False
    return ret
    

def tokenize(program):
    lineCount = 0
    ret = []
    for line in program:
        if line:
            l = []
            for t in line.split(' '):
                t = tokSpace(t, lineCount)
                if type(t) == list:
                    l += t
                else:
                    print('Tokenizing error on line %i,'%lineCount, line)
                    exit(1)
            ret+=l
        lineCount += 1
    ret.append([Token('control', 'EOF', -1)])
    return ret





