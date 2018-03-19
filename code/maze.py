#! python3

"""
谜题
    哪国人养鱼（Zebra Puzzle）
    字母数字填空
"""

import time
import itertools
import re


def next_to(a, b):
    return abs(a - b) == 1


def im_right(a, b):
    return a - b == 1


def zebra_puzzle():
    """ 哪国人养鱼 """
    houses = first, _, middle, _, _ = [1, 2, 3, 4, 5]
    orderings = list(itertools.permutations(houses))  # 1

    return ((WATER, ZEBRA)
            for (red, green, ivory, yellow, blue) in orderings
            if im_right(green, ivory)  # 6
            for (Englishman, Spaniard, Ukranian, Japanese, Norwegian) in orderings
            if Englishman is red  # 2
            if Norwegian is first  # 10
            if next_to(Norwegian, blue)  # 15
            for (coffee, tea, milk, oj, WATER) in orderings
            if coffee is green  # 4
            if Ukranian is tea  # 5
            if milk is middle  # 9
            for (OldGold, Kools, Chesterfields, LuckyStrike, Parliaments) in orderings
            if Kools is yellow  # 8
            if LuckyStrike is oj  # 13
            if Japanese is Parliaments  # 14
            for (dog, snails, fox, horse, ZEBRA) in orderings
            if Spaniard is dog  # 3
            if OldGold is snails  # 7
            if next_to(Chesterfields, fox)  # 11
            if next_to(Kools, horse))  # 12


##########
# 生成器
##########


def gen_pos_int(start, end=None):
    """ 从 start 开始生成间隔为 1 的整数 """
    i = start
    while end is None or i <= end:
        yield i
        i += 1


def gen_int():
    """ 生成 0 1 -1 2 -2 ... """
    yield 0
    pi = gen_pos_int(1)
    while True:
        i = next(pi)
        yield i
        yield -i


##########
# 计数器
##########


def timedcall(f, *args):
    t0 = time.clock()
    res = f(*args)
    return time.clock() - t0, res


def cnts(seq):
    cnts.starts += 1
    for item in seq:
        cnts.item += 1
        yield item


def call_times(f, *args):
    cnts.starts, cnts.item = 0, 0
    res = f(*args)
    str_res = f.__name__ + ' got ' + str(res)
    print('%s, and %d iters, %d items.' % (str_res, cnts.starts, cnts.item))


##########
#
##########

def solve(formula):
    """ 给出 'ODD + ODD == EVEN' 一样的式子, 填入数字 """
    for f in fill_in(formula):
        if valid(f):
            return f


def fill_in(formula):
    """ 将数字的全排列填入等式中 """
    letters = ''.join(set(re.findall('[A-Z]', formula)))
    for digits in itertools.permutations('0123456789', len(letters)):
        table = str.maketrans(letters, ''.join(digits))
        yield formula.translate(table)


def valid(f):
    """ 判断式子是否正确：当且仅当数字不以 0 开头，且求值后为真. """
    try:
        return not re.search(r'\b0[0-9]', f) and eval(f) is True
    except ArithmeticError:
        return False


def compile_word(word):
    """  """
    if word.isupper():
        terms = ('%s*%d' % (c, 10 ** d) for d, c in enumerate(word[::-1]))
        return '(' + '+'.join(terms) + ')'
    else:
        return word


def fast_solve(formula):
    f, letters = compile_formula(formula)
    for digits in itertools.permutations(range(10), len(letters)):
        try:
            if f(*digits) is True:
                table = str.maketrans(letters, ''.join(map(str, digits)))
                return formula.translate(table)
        except ArithmeticError:
            pass


def compile_formula(formula, verbose=False):
    letters = ''.join(set(re.findall('[A-Z]', formula)))
    first_letters = set(re.findall(r'\b([A-Z])[A-Z]', formula))
    parms = ', '.join(letters)
    tokens = map(compile_word, re.split('([A-Z]+)', formula))
    body = ''.join(tokens)
    if first_letters:
        nozero = ' and '.join(c + '!=0' for c in first_letters)
        body = '%s and (%s)' % (nozero, body)
    f = 'lambda ' + parms + ': ' + body
    if verbose: print(f)
    return eval(f), letters


formulas = r"""ODD + ODD == EVEN
ATOM**0.5 == A + TO + M
RAMN == R**3 + RM**3 == N**3 + RX**3
A**D + B**D == C**D and (D>1)
FOUR > TWO > ONE
sum(range(AA)) == BB
sum(range(POP)) == BOBO
ABCD * 4 == EFGH""".splitlines()


def test_solve(solve=fast_solve):
    t0 = time.clock()
    for f in formulas:
        print()
        print(' ' * 11, f)
        print('%6.4f sec: %s' % timedcall(solve, f))
    print('\n%6.4f tot.' % (time.clock() - t0))