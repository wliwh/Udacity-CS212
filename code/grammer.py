#! python3

"""
函数作为返回值
"""

import re
from functools import update_wrapper


def decorator(d):
    def _d(f):
        return update_wrapper(d(f), f)

    return update_wrapper(_d, d)


@decorator
def n_ary(f):
    """ 将二元函数变为 n 元函数 """

    def nf(x, *args):
        return f(x, nf(*args)) if args else x

    # update_wrapper(nf, f)
    return nf


def memo(f):
    """ 记忆法 """
    cache = {}

    def _f(*args):
        try:
            return cache[args]
        except KeyError:
            cache[args] = result = f(*args)
            return result
        except TypeError:
            return f(args)

    return _f


@decorator
def trace(f):
    """ 追踪一个函数 """
    indent = '    '

    def traced_fn(*args):
        signature = '%s(%s)' % (f.__name__, ', '.join(map(repr, args)))
        print('%s -> %s' % (trace.level * indent, signature))
        trace.level += 1
        try:
            result = f(*args)
            print('%s <- %s == %s' %
                  ((trace.level - 1) * indent, signature, result))
        finally:
            trace.level -= 1
        return result

    trace.level = 0
    return traced_fn


def disable(f): return f


##########
# 语法
#########


def split(text, sep=None, maxsplit=-1):
    return [t.strip() for t in text.strip().split(sep, maxsplit)]


def grammar(description, whitespace=r'\s*'):
    """ 建立语法规则表 """
    g = {' ': whitespace}
    description = description.replace('\t', ' ')  # no tabs!
    for line in split(description, '\n'):
        lhs, rhs = split(line, ' => ', 1)
        alternatives = split(rhs, ' | ')
        g[lhs] = tuple(map(split, alternatives))
    return g


ExpG = grammar(r"""
Exp     => Term [+-] Exp | Term
Term    => Factor [*/] Term | Factor
Factor  => Funcall | Var | Num | [(] Exp [)]
Funcall => Var [(] Exps [)]
Exps    => Exp [,] Exps | Exp
Var     => [a-zA-Z_]\w*
Num     => [-+]?[0-9]+([.][0-9]*)?
""")


def parse(start_symbol, text, grammar):
    """ 语法分析器 """

    tokenizer = grammar[' '] + '(%s)'

    def parse_sequence(sequence, text):
        result = []
        for atom in sequence:
            tree, text = parse_atom(atom, text)
            if text is None:
                return Fail
            result.append(tree)
        return result, text

    @memo
    def parse_atom(atom, text):
        if atom in grammar:
            for alternative in grammar[atom]:
                tree, rem = parse_sequence(alternative, text)
                if rem is not None:
                    return [atom] + tree, rem
            return Fail
        else:
            m = re.match(tokenizer % atom, text)
            return Fail if (not m) else (m.group(1), text[m.end():])

    return parse_atom(start_symbol, text)


Fail = (None, None)

JSON = grammar(r"""
object => [{] [}] | [{] members [}]
members => pair , members | pair
pair => string : value
array => [[] []] | [[] elements []]
elements => value , elements | value
value => string | number | object | array | true | false | null
string => "[^"]*"
number => int frac exp | int frac | int exp | int
int =>  -?[0] | -?[1-9][0-9]*
frac => [.][0-9]+
exp => [eE][-+][0-9]+
""", whitespace='\s*')


def json_parse(text):
    return parse('value', text, JSON)
