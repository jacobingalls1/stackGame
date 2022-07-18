import sys
from stackLang.lexer import Token, Lexer


class Nonterminal():
    def __init__(self, symbol):
        self.symbol = symbol
        self.null = False

    def first(self, rules):
        first = {}
        for prod in rules[self.symbol].rhs:
            if type(prod[0]) is Nonterminal:
                p = list(prod[0].first(rules).keys())
                for t in p:
                    first[t] = prod
            else:
                first[prod[0]] = prod
        rem = []
        for k in first.keys():
            if k == Token('keyword', 'nil', -1):
                self.null = True
                rem.append(k)
            elif list(first.keys()).count(k) > 1:
                raise Exception("Collision in terminal '%s' for the %s nonterminal before nil" % (k, self.symbol))
        for k in rem:
            first.pop(k)
        return first

    def follow(self, rules):
        finals = []
        follow = []
        for r in rules.values():
            for prod in r.rhs:
                for i in range(len(prod)):
                    if prod[i] != self:
                        continue
                    if len(prod) == i + 1:
                        finals.append(r.lhs)
                    else:
                        follow.append(prod[i + 1])
        for e in follow:
            if type(e) == Nonterminal:
                follow += e.first(rules).keys()
                if e.nullable():
                    follow += e.follow(rules)
                follow.remove(e)
        for nt in finals:
            follow += nt.follow(rules)
        return list(set(follow))

    def nullable(self, rules=None):
        return self.null

    def __repr__(self):
        return "NT"+self.symbol

    def getLine(self):
        return False


class Rule:
    NTs = {}

    def __init__(self, lhs, rhs, tokenf):
        lexer = Lexer('', tokenf)
        self.rhs = [i.split(' ') for i in rhs.split(' | ')]
        if lhs not in Rule.NTs.keys():
            Rule.NTs[lhs] = Nonterminal(lhs)
        self.lhs = Rule.NTs[lhs]
        for i in self.rhs:
            for j in range(len(i)):
                if 'A' <= i[j][0] <= 'Z':
                    if i[j] not in Rule.NTs.keys():
                        Rule.NTs[i[j]] = Nonterminal(i[j])
                    i[j] = Rule.NTs[i[j]]
                else:
                    i[j] = lexer.matchToken(i[j])

    def __repr__(self):
        return str(self.lhs) + ' -> ' + str(self.rhs)

    @staticmethod
    def getNTs():
        return Rule.NTs


def getRules(rulesFile, tokenf):
    rulesList = {}
    with open(rulesFile, 'r') as rules:
        for line in rules:
            rulesList[line.split(' -> ')[0]] = Rule(*line.strip().split(' -> '), tokenf)
    return rulesList


def getTable(rulesFile, tokenf):
    rules = getRules(rulesFile, tokenf)
    nonterminals = Rule.getNTs()
    table = {nt: nt.first(rules) for nt in nonterminals.values()}  # first() returns a dictionary
    for nt in nonterminals.values():
        if nt.nullable(rules):
            for f in nt.follow(rules):
                if f in table[nt].keys():
                    raise Exception("Collision in terminal '%s' for the %s nonterminal due to nil" % (f, nt.symbol))
                table[nt][f] = [Token('control', 'empty', -1)]
    new = {}
    for key in table.keys():
        new[key.symbol] = table[key]
    return new
