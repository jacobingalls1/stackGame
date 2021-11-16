import sys
from lexer import Token, tokSpace
from collections import defaultdict

class Rule:
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        self.rhs = [i.split(' ') for i in self.rhs.split(' | ')]
        for i in self.rhs:
            for j in range(len(i)):
                if not 'A' <= i[j][0] <= 'Z' and i[j][-1] != '*':
                    i[j] = tokSpace(i[j], -1)
                    if i[j]:
                        i[j]=i[j][0]
                elif i[j][-1] == '*':
                    i[j] = Token(i[j])
        self.defined = False

    def __repr__(self):
        return self.lhs + ' -> ' + str(self.rhs)

    def nonterminals(self):
        ret = []
        for i in self.rhs:
            for j in i:
                if type(j) is str:
                    ret.append(j)
                    break
        for i in range(len(ret)):
            if ret[i][-1] == '_':
                ret[i] = ret[i][:-1]
        return list(set(ret))

    def fullyDefined(self, rules):
        toDefine = self.nonterminals()
        for t in toDefine:
            if not rules[t].defined:
                return False    
        return True

    def optional(self):
        ret = []
        for i in self.rhs:
            for j in range(len(i)):
                if type(i[j]) is str and i[j][-1] == '_':
                    if j<len(i)-1:
                        ret.append((i[j][:-1], i[j+1]))
                    else:
                        ret.append(self.lhs)
        return ret

    def findAfterNT(self, nt):
        ret = [False]
        for i in self.rhs:
            for j in range(len(i)):
                if i[j] == nt:
                    if j<len(i)-1:
                        ret.append(i[j])
                    else:
                        ret[0] = True
        return ret


    


def updateTable(table, rule, rules):
    for o in rule.rhs:
        if type(o[0]) is Token:
            table[rule.lhs][o[0]] = o
        else:
            for k in table[o[0]].keys():
                if k in table[rule.lhs].keys():
                    print("Collision in the %s rule over the %s terminal"%(rule.lhs, k))
                    exit(1)
                table[rule.lhs][k] = o


def table(grammarFile):
    table = defaultdict(lambda: {})
    rules = {}
    first = None
    with open(grammarFile) as gf:
        for line in gf:
            r = Rule(*(line.strip().split(' -> ')))
            rules[r.lhs] = r
            if not first:
                first = r.lhs
    undefinedNT = list(rules.values())
    good = True
    optional = []
    for r in rules.values():
        optional += r.optional()
    lmbda = [o for o in optional if type(o) is str]
    for l in lmbda:

    optional = [o for o in optional if type(o) is tuple]

    while good:
        good = False
        for r in undefinedNT:
            if r.fullyDefined(rules):
                updateTable(table, r, rules)
                good = True
                r.defined = True
                undefinedNT.remove(r)

        for o in optional:
            if type(o[1]) is Token:
                table[o[0]][o[1]] = [o[1]]
            else:
                k = list(table[o[0]].keys())
                intersect = list(set(k)|set(table[o[1]].keys()))
                if intersect:
                    print("Collision in the %s rule over the %s terminal(s)"%(o[0], str(intersect)))
                    exit(1)
                table[o[0]].update(table[o[1]])
                if list(set(table[o[0]].keys())-set(k)):
                    good = True
    for r in table.keys():
        for k in table[r].keys():
            for i in range(len(table[r][k])):
                if type(table[r][k][i]) is str and table[r][k][i][-1] == '_':
                    table[r][k][i] = table[r][k][i][:-1]


    if not rules[first].defined:
        print('Failed to define %s from the CFG file'%first)
        exit(1)

    return table




