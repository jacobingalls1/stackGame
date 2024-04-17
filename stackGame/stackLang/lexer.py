import re
import sys
from os.path import exists

# symbol = '$@.+-~&%!><=#^/${'

# keyword = r'split|swap|stack|merge|while|if|else|return|push|input|output|pop|rotate|add|sub|neg|and|not|or|gt|lt|eq|swap|height|top|temp|dump|in|out|nil|reverse|fun|routine|test|import|odd|shift'

numberLiteral = r'0|-?[1-9][0-9]*'

name = r'[a-zA-Z]([a-zA-Z0-9\.])*'


class Token(object):
    def __init__(self, typ, content=None, line=-1, file=None):
        self.type = typ
        self.content = content
        self.line = line
        self.file = file

    def __repr__(self):
        return '(%s, %s, %i)' % (self.type, self.content, self.line)

    def __eq__(self, other):
        if type(self) == type(other) and self.type == other.type and (
                self.content == other.content or self.content == None or other.content == None\
                or self.type[-1] == '*'):
            return True
        return False

    def __hash__(self):
        ret = hash(self.type)
        if self.type in ['keyword', 'symbol']:
            ret += hash(self.content)
        return ret

    def write(self):
        return '<%s> %s </%s>' % (self.type, self.content, self.type)

    def clean(self):
        return Token(self.type, self.content)

    def getLine(self):
        return self.line

class Lexer:
    def __init__(self, workingDir, tokenf):
        with open(tokenf, 'r') as toks:
            self.symbols = toks.readline()
            self.keywords = toks.readline()
        self.workingDir = workingDir
        self.fName = None

    def loadProgram(self, fileName):
        self.fName = fileName
        ret = []
        with open(fileName) as f:
            ignore = False
            for line in f:
                if "'''" in line:
                    ignore = not ignore
                    continue
                if ignore:
                    continue
                ret.append(line.strip().split('#')[0])
        return ret

    def loadProgramFromText(self, text):
        ignore = False
        ret = []
        for line in text.split('\n'):
            if "'''" in line:
                ignore = not ignore
                continue
            if ignore:
                continue
            ret.append(line.strip().split('#')[0])
        return ret

    def tokSpace(self, tok, line):
        ret = []
        while tok:
            x = re.match(numberLiteral, tok)
            if x:
                ret.append(Token('numberLiteral*', int(tok[:x.end()]), line, self.fName))
                tok = tok[x.end():]
                continue
            if tok[0] in self.symbols:
                ret.append(Token('symbol', tok[0], line, self.fName))
                tok = tok[1:]
                continue
            x = re.match(self.keywords, tok)
            if x and (len(tok) == x.end() or tok[x.end()] in  ' '+self.symbols):
                ret.append(Token('keyword', tok[:x.end()], line, self.fName))
                tok = tok[x.end():]
                continue
            x = re.match(name, tok)
            if x:
                if exists(self.workingDir + '/' + tok[:x.end()]):
                    ret.append(Token('fname*', tok[:x.end()], line, self.fName))
                    tok = tok[x.end():]
                    continue
                ret.append(Token('name*', tok[:x.end()], line, self.fName))
                tok = tok[x.end():]
                continue
            return False
        return ret

    def tokenize(self, program):
        lineCount = 1
        ret = []
        for line in program:
            if line:
                ls = []
                for t in line.split(' '):
                    t = self.tokSpace(t, lineCount)
                    if type(t) == list:
                        ls += t
                    else:
                        raise Exception('Tokenizing error on line %i'%(lineCount))
                ret += ls
            lineCount += 1
        ret.append(Token('symbol', '$', lineCount))
        return ret

    def matchToken(self, s):
        if s[-1] == '*':
            return Token(s, -1, -1)
        return self.tokSpace(s, -1)[0]
