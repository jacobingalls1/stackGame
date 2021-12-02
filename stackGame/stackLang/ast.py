from lexer import Token

redundant = ['push', 'pop', 'while', 'if', 'else', 'split', '$', '.', 'fun', 'routine']
save = ['BinaryOp', 'UnaryOp', 'PushOp', 'PopOp', 'FunCall', 'Returnst', 'Op1_', 'Op2_']

def reduce(tree):
    change = False
    for c in tree.children:
        if type(c) == Token:
            if c.content in redundant:
                tree.children.remove(c)
                change = True
        else:
            if len(c.children) == 1 and c.content.symbol not in save:
                tree.children[tree.children.index(c)] = c.children[0]
                change = True
            elif c.content != 'Program' and c.content.symbol == 'Stmts':
                i = tree.children.index(c)
                tree.children = tree.children[:i] + c.children + tree.children[i+1:]
                return True
            change += reduce(c)
    return change


def getAst(tree):
    while reduce(tree):
        pass
    return tree