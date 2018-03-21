#! python3

"""
正则表达式
"""


def search(pattern, text):
    """ text 中是否含有 pattern 模式的字符串 """
    if pattern.startswith('^'):
        return match(pattern[1:], text)
    else:
        return match('.*' + pattern, text)


def match(pattern, text):
    """ text 的开头是否为 pattern 模式的字符串 """
    if pattern == '':
        return True
    elif pattern == '$':
        return text == ''
    elif len(pattern) > 1 and pattern[1] in '*?':
        p, op, pat = pattern[0], pattern[1], pattern[2:]
        if op == '*':
            return match_star(p, pat, text)
        elif op == '?':
            if match1(p, text) and match(pat, text[1:]):
                return True
            else:
                return match(pat, text)
    else:
        return match1(pattern[0], text) and match(pattern[1:], text[1:])


def match1(p, text):
    """ 匹配单个字符 '.' """
    if not text:
        return False
    return p == '.' or p == text[0]


def match_star(p, pattern, text):
    """ 匹配任意个字符 p + 字符串 pattern '*' """
    return match(pattern, text) or (match1(p, text) and match_star(p, pattern, text[1:]))


def match_test():
    assert search('baa*!', 'Sheep said baaa!')
    assert search('baa*!', 'Sheep said baaa humbug!') is False
    assert match('baa*!', 'Sheep said baaa!') is False
    assert match('baa*!', 'baaaaa! said the sheep')
    assert search('a?t$', 'text')
    assert search('^.*$', 'anything is ok')
    assert match('x?', 'text')
    assert match('tex?t?', 'text')
    assert match('text?', 'tex')
    assert match('a*b*c*', 'anything')
    assert all(match('aa*bb*cc*$', s) for s in 'abc aaabbccc aabccc'.split())
    assert all(match('ab.*aca.*a', s)
               for s in 'abacaa abracadabra about-acacia-fa'.split())
    assert any(match('aa*bb*cc*$', s)
               for s in 'ab aaabcccd aaa-b-ccc'.split()) is False
    assert all(search('t.p', s) for s in 'tip tap atypical tepid stop'.split())
    assert any(search('t.p', s) for s in 'teepee tp TYPE'.split()) is False

    return 'tests pass'


##########
# 解释器
##########

def matchset(pattern, text):
    """ pattern 匹配 text 的开头; 返回 text 余下的内容。
    例如： star(lit(a)) 匹配 'aaab' 返回 {'aaab', 'aab', 'ab', 'b'} """
    op, x, y = components(pattern)
    if 'lit' == op:
        return {text[len(x):]} if text.startswith(x) else null
    elif 'seq' == op:
        return set(t2 for t1 in matchset(x, text) for t2 in matchset(y, t1))
    elif 'alt' == op:
        return matchset(x, text) | matchset(y, text)
    elif 'dot' == op:
        return {text[1:]} if text else null
    elif 'oneof' == op:
        return {text[1:]} if text.startswith(x) else null
        #                      if any(text.startswith(c) for c in x)
    elif 'eol' == op:
        return {''} if text == '' else null
    elif 'star' == op:
        return ({text} |
                set(t2 for t1 in matchset(x, text)
                    for t2 in matchset(pattern, t1) if t1 != text))
    else:
        raise ValueError('unknown pattern: %s' % pattern)


null = frozenset()


def components(pattern):
    """ 返回 pattern 的 op, x, y; 若 x, y 不存在返回 None。"""
    x = pattern[1] if len(pattern) > 1 else None
    y = pattern[2] if len(pattern) > 2 else None
    return pattern[0], x, y


def matchset_test():
    assert matchset(('lit', 'abc'), 'abcdef') == {'def'}
    assert matchset(('seq', ('lit', 'hi '), ('lit', 'there ')), 'hi there nice to meet you') == {'nice to meet you'}
    assert matchset(('alt', ('lit', 'dog'), ('lit', 'cat')), 'dog and cat') == {' and cat'}
    assert matchset(('dot',), 'am i missing something?') == {'m i missing something?'}
    assert matchset(('oneof', 'a'), 'aabc123') == {'abc123'}
    assert matchset(('eol',), '') == {''}
    assert matchset(('eol',), 'not end of line') == frozenset([])
    assert matchset(('star', ('lit', 'hey')), 'heyhey!') == {'!', 'heyhey!', 'hey!'}

    return 'tests pass'


def lit(string):
    return 'lit', string


def seq(x, y):
    return 'seq', x, y


def alt(x, y):
    return 'alt', x, y


def star(x):
    return 'star', x


def plus(x):
    return seq(x, star(x))


def opt(x):
    """ x? """
    return alt(lit(''), x)


def oneof(chars):
    return 'oneof', tuple(chars)


dot = ('dot',)
eol = ('eol',)


def api_test():
    assert lit('abc') == ('lit', 'abc')
    assert seq(('lit', 'a'), ('lit', 'b')) == ('seq', ('lit', 'a'), ('lit', 'b'))
    assert alt(('lit', 'a'), ('lit', 'b')) == ('alt', ('lit', 'a'), ('lit', 'b'))
    assert star(('lit', 'a')) == ('star', ('lit', 'a'))
    assert plus(('lit', 'c')) == ('seq', ('lit', 'c'), ('star', ('lit', 'c')))
    assert opt(('lit', 'x')) == ('alt', ('lit', ''), ('lit', 'x'))
    assert oneof('abc') == ('oneof', ('a', 'b', 'c'))
    return 'tests pass'


def int_search(pattern, text):
    """ text 中是否含有 pattern 模式的字符串 ; 返回return longest earliest match or None."""
    for i in range(len(text)):
        m = int_match(pattern, text[i:])
        if m:
            return m


def int_match(pattern, text):
    """ 以 text 的开头匹配 pattern 模式的字符串；返回能够匹配的最长字符串或 None."""
    remainders = matchset(pattern, text)
    if remainders:
        shortest = min(remainders, key=len)
        return text[:len(text) - len(shortest)]

##########
# 编译器
##########
