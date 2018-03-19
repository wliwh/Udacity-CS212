#! python3

"""
扑克牌型
"""

import random
from collections import defaultdict
from math import factorial


##########
# 构造程序
##########


def poker(hands):
    """ 从一组牌中返回最好的一手牌 """
    return max(hands, key=hand_rank)


def hand_rank(hand):
    """ 一手扑克牌的等级 """
    nums = card_nums(hand)
    if straight(nums) and flush(hand):
        return 8, nums[0]
    elif kind(4, nums):
        return 7, kind(4, nums), kind(1, nums)
    elif kind(3, nums) and kind(2, nums):
        return 6, kind(3, nums), kind(2, nums)
    elif flush(hand):
        return 5, nums
    elif straight(nums):
        return 4, nums[0]
    elif kind(3, nums):
        return 3, kind(3, nums), nums
    elif two_pairs(nums):
        return 2, two_pairs(nums), nums
    elif kind(2, nums):
        return 1, kind(2, nums), nums
    else:
        return 0, nums


def card_nums(hand):
    """ 扑克牌的字符映射为数字，从大到小排列 """
    ch_to_num = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
                 '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    sort_nums = sorted([ch_to_num[n] for n, s in hand], reverse=True)
    return [5, 4, 3, 2, 1] if (sort_nums == [14, 5, 4, 3, 2]) else sort_nums


def straight(nums):
    """ 五张顺连? """
    return [x - nums[-1] for x in nums] == [4, 3, 2, 1, 0]


def flush(hand):
    """ 花色相同？ """
    suits = [s for _, s in hand]
    return len(set(suits)) == 1


def kind(n, nums):
    """ n 张相同的牌？ """
    for i in nums:
        if nums.count(i) == n:
            return i


def two_pairs(nums):
    """ 一组牌中是否有两对牌 """
    pair, sec_pair = kind(2, nums), kind(2, nums[::-1])
    if pair and sec_pair != pair:
        return pair, sec_pair


##########
# 重构
##########


def allmax(lst, key=None):
    """ 所有的最大元素 """
    key = key or (lambda x: x)
    res, maxval = [], None
    for x in lst:
        xval = key(x)
        if not res or xval > maxval:  # maxval -> res
            res, maxval = [x], xval
        elif xval == maxval:
            res.append(x)
    return res


def test_allmax():
    assert allmax([1, 1, 1, 0, -1, 0], abs) == [1, 1, 1, -1]
    assert allmax([(1, 1), (1, 0), (0, 1)],
                  key=lambda x: x[0]) == [(1, 1), (1, 0)]
    return 'test_allmax pass.'


def group(items):
    """ 一组牌由相同点数的个数，点数分组 """
    groups = [(items.count(x), x) for x in set(items)]
    return sorted(groups, reverse=True)


def hand_rank2(hand):
    """ 一手扑克牌的等级 """
    groups = group(['--23456789TJQKA'.index(n) for n, s in hand])
    counts, nums = zip(*groups)
    if nums == (14, 5, 4, 3, 2):
        nums = (5, 4, 3, 2, 1)
    is_straight = [x - nums[-1] for x in nums] == [4, 3, 2, 1, 0]
    is_flush = len(set([s for n, s in hand])) == 1
    str_flu = 8 if (is_straight and is_flush) else 4 * is_straight + 5 * is_flush
    counts_rank = {(5,): 10, (4, 1): 7, (3, 2): 6, (3, 1, 1): 3, (2, 2, 1): 2,
                   (2, 1, 1, 1): 1, (1, 1, 1, 1, 1): 0}
    return max(counts_rank[counts], str_flu), nums


##########
# 测试
##########


def test_poker():
    sf = "6C 7C 8C 9C TC".split()  # straight flush
    fk = "9D 9H 9S 9C 7D".split()  # four kind
    fh = "TC TD TH 7C 7D".split()  # full house
    s1 = "AD 2D 3D 4D 5D".split()  # straight A - 5
    s2 = "2C 3C 4C 5C 6C".split()  # straight 2 - 6
    tp = "KD KH 4C JC JD".split()  # two pairs
    assert straight(card_nums(sf)) and flush(sf) is True
    assert flush(fk) is False
    assert straight(card_nums(fh)) is False
    assert kind(4, card_nums(fk)) == 9
    assert kind(2, card_nums(fh)) == 7
    assert kind(4, card_nums(fh)) is None
    assert two_pairs(card_nums(tp)) == (13, 11)
    assert hand_rank(sf) == (8, 10)
    assert hand_rank(fk) == (7, 9, 7)
    assert hand_rank(fh) == (6, 10, 7)
    assert hand_rank(s1) == (8, 5)
    assert hand_rank(tp) == (2, (13, 11), [13, 13, 11, 11, 4])
    assert poker([sf, s1, fk]) == sf
    assert poker([s1, s2, tp]) == s2
    assert poker([fk, fh, tp]) == fk
    assert poker([fk]) == fk
    assert poker([tp] + [s1] * 99) == s1
    return 'test_poker pass.'


##########
# 计算频率
##########


def take_deal(numhands, nums=5, deck=[r + s for r in '23456789TJQKA' for s in 'SHDC']):
    """ 从一副洗好的牌中选出 numhands 组牌，每组牌 nums 张 """
    random.shuffle(deck)
    numhands = (numhands - 1) % 10 + 1
    return [deck[nums * i:nums * i + nums] for i in range(numhands)]


def hand_rank_freq(nums=700 * 1000):
    """ 扑克牌牌型出现的频率 """
    hand_names = ["散牌", "一对", "两对", "三条", "顺子", "同花", "葫芦", "四条", "同花顺"]
    counts = [0] * 9
    for i in range(nums // 10):
        for hand in take_deal(10):
            rank = hand_rank2(hand)[0]
            counts[rank] += 1
    for i in reversed(range(9)):
        print("%s: %6.4f %%" % (hand_names[i], 100. * counts[i] / nums))


##########
# 洗牌
##########

def swap_it(lst, i, j):
    """ 交换列表中的元素 """
    lst[i], lst[j] = lst[j], lst[i]


def shuffle1(deck):
    """ 打乱元素的顺序 """
    n = len(deck)
    shuffled = [False] * n
    while not all(shuffled):
        i, j = random.randrange(n), random.randrange(n)
        shuffled[i] = shuffled[j] = True
        swap_it(deck, i, j)


def shuffle2(lst):
    """ 打乱元素的顺序 """
    n = len(lst)
    for x in range(n - 1):
        swap_it(lst, x, random.randrange(x, n))


def shuffle3(deck):
    """ 打乱元素的顺序 """
    n = len(deck)
    shuffled = [False] * n
    while not all(shuffled):
        i, j = random.randrange(n), random.randrange(n)
        shuffled[i] = True
        swap_it(deck, i, j)


def shuffle4(lst):
    """ 打乱元素的顺序 """
    n = len(lst)
    for x in range(n):
        swap_it(lst, x, random.randrange(n))


def frequency_shuffle(shuffler, deck='ABC', n=10000):
    """ 一种洗牌方法得出各种排列的频率 """
    counts = defaultdict(int)
    for _ in range(n):
        to_lst = list(deck)
        shuffler(to_lst)
        counts[''.join(to_lst)] += 1
    mean = n * 1. / factorial(len(deck))
    is_ok = all(map(lambda x: 0.9 <= x / mean <= 1.1, counts.values()))
    print("%s '%s' %s" % (shuffler.__name__, deck,
                          ('ok' if is_ok else '*** bad ***')))
    print("mean prob: %.2f" % (mean / 100.), end='\t')
    for item, count in sorted(counts.items()):
        print("%s: %4.2f" % (item, count * 100. / n), end='\t')
    print()
