"""Reviewed v0.3 curriculum revisions. Keep image concepts and v1 topic IDs stable.

These are authored exercises, not automatic difficulty/word-count inflation.
Every reference answer has explicit, executable acceptance cases.
"""
from copy import deepcopy
from textwrap import dedent


def apply(chapters):
    units = {u['unitId']: u for ch in chapters for topic in ch['lessons'] for u in topic['tiers']}

    def enrich(identity, why, thinking, acceptance, *, minutes=None, prerequisites=()):
        u = units[identity]
        u['body'] += '\n\n### 深入一层\n\n' + why + '\n\n### 推理自检\n\n' + thinking
        u['exercise'] += '\n\n验收要求：' + acceptance
        if minutes:
            u['minutes'] = minutes
        for prerequisite in prerequisites:
            if prerequisite not in u['prerequisites']:
                u['prerequisites'].append(prerequisite)
        return u

    def answer(identity, exercise, code, output, tests, *, title=None):
        u = units[identity]
        u['exercise'] = exercise
        u['solution'] = dedent(code).strip() + '\n'
        u['solutionExpectedOutput'] = output
        # Preserve independently authored example cases; replace obsolete answer
        # cases instead of allowing a stale assertion to validate the wrong task.
        cases = [deepcopy(c) for c in u['testCases'] if c['field'] != 'solution']
        cases.insert(1, {'name':'answer','field':'solution','stdin':u['stdin'],'expectedOutput':output})
        for name, assertions in tests:
            cases.append({'name':name,'field':'solution','stdin':u['stdin'],
                          'expectedOutput':output,'assertions':dedent(assertions).strip()})
        u['testCases'] = cases
        if title:
            u['title'] = title

    def checks(identity, *tests):
        u = units[identity]
        for name, assertions in tests:
            u['testCases'].append({'name':name,'field':'solution','stdin':u['stdin'],
                                  'expectedOutput':u['solutionExpectedOutput'],
                                  'assertions':dedent(assertions).strip()})

    answer('l03:advanced',
        '实现apply_movements(opening,movements)：初始库存是非负整数，变动是有符号整数（bool不算数量）。逐项计算旧库存、变动、新库存；任意一步库存不足就抛ValueError，不能只检查最后净额。返回received、shipped、closing和trace，不修改输入。用20、[8,-11,-3]输出结存14和三条追踪记录。',
        '''
def apply_movements(opening, movements):
    if type(opening) is not int or opening < 0:
        raise ValueError("初始库存应为非负整数")
    balance = opening
    received = shipped = 0
    trace = []
    for position, change in enumerate(movements, 1):
        if type(change) is not int:
            raise ValueError(f"第{position}项不是整数")
        candidate = balance + change
        if candidate < 0:
            raise ValueError(f"第{position}项库存不足")
        trace.append((balance, change, candidate))
        received += max(change, 0)
        shipped += max(-change, 0)
        balance = candidate
    assert opening + received == shipped + balance
    return {"received": received, "shipped": shipped, "closing": balance, "trace": trace}
report = apply_movements(20, [8, -11, -3])
print(report["closing"])
print(report["trace"])
''', '14\n[(20, 8, 28), (28, -11, 17), (17, -3, 14)]\n', [
        ('先亏空后补货仍拒绝', '''
source = [-3, 5]
try:
    apply_movements(2, source)
except ValueError as error:
    assert '第1项' in str(error)
else:
    raise AssertionError('不能用最终正库存掩盖中途亏空')
assert source == [-3, 5]
'''),
        ('空账零值恰好用尽与类型', '''
assert apply_movements(0, [])['trace'] == []
assert apply_movements(3, [0, -3])['closing'] == 0
for opening, changes in [(True, []), (0, [False]), (-1, [])]:
    try: apply_movements(opening, changes)
    except ValueError: pass
    else: raise AssertionError('非法数量被接受')
''')])
    enrich('l03:advanced', '从固定数值升级为可复用的库存流水。事实记录不变，结存由事实推导；守恒关系只能证明算术一致，不能证明每个中间状态都合法。',
           '初始2，先出库3再入库5，最终是4；为什么仍应拒绝？把两笔顺序交换后，哪些结果相同，哪些追踪记录不同？',
           '每轮写出opening+received=shipped+closing；至少测试空流水、零变动、恰好用尽及先透支再补货。', minutes=65, prerequisites=('l11','l25','l30'))

    answer('l04:advanced',
        '实现shift_clock(display,shift)：钟面为1至12，位移为任意正负整数，bool不算整数；返回(新钟面,跨越的有符号整圈数)。先转零起点，再用divmod一次求圈数和余数，最后转回钟面。2点后退5小时应返回(9,-1)。',
        '''
def shift_clock(display, shift):
    if type(display) is not int or not 1 <= display <= 12 or type(shift) is not int:
        raise ValueError("钟面与位移无效")
    turns, position = divmod(display - 1 + shift, 12)
    return position + 1, turns
print(shift_clock(2, -5))
print(shift_clock(12, 25))
''', '(9, -1)\n(1, 3)\n', [
        ('重建位移与往返性质', '''
for display in range(1, 13):
    for shift in range(-37, 38):
        new_display, turns = shift_clock(display, shift)
        assert 1 <= new_display <= 12
        assert display-1+shift == 12*turns+new_display-1
        assert shift_clock(new_display, -shift)[0] == display
'''),
        ('周期边界和非法类型', '''
assert shift_clock(1,-1)==(12,-1) and shift_clock(12,1)==(1,1)
for pair in [(0,0),(13,0),(True,0),(1,1.5)]:
    try: shift_clock(*pair)
    except ValueError: pass
    else: raise AssertionError(pair)
''')])
    enrich('l04:advanced', '模运算只保留位置，整除还记录越过多少整圈。负位移下的圈数采用向下取整，因此2点后退5小时得到圈数-1，而不是0。',
           '只保存余数能分清前进1小时和25小时吗？试用q×12+r重建原来的零起点位置。',
           '检验大位移、负位移、整圈及逆向恢复；解释“圈数”以零起点边界为准。', minutes=55, prerequisites=('l25',))

    answer('l07:advanced',
        '实现parse_rgb(text)与format_rgb(channels)。文本严格为#加6位ASCII十六进制字符，不接受空白或其他长度；返回三整数元组。反向函数接受恰好三个0至255整数（排除bool），返回大写#RRGGBB。证明解析后再格式化能规范大小写，不能用int转换成功代替格式校验。',
        '''
def parse_rgb(text):
    if not isinstance(text, str) or len(text) != 7 or text[0] != "#":
        raise ValueError("需要#RRGGBB")
    if any(ch not in "0123456789abcdefABCDEF" for ch in text[1:]):
        raise ValueError("通道必须是ASCII十六进制")
    return tuple(int(text[start:start+2], 16) for start in (1,3,5))
def format_rgb(channels):
    values = tuple(channels)
    if len(values) != 3 or any(type(x) is not int or not 0 <= x <= 255 for x in values):
        raise ValueError("需要三个0至255整数")
    return "#" + "".join(f"{value:02X}" for value in values)
print(parse_rgb("#ff8000"))
print(format_rgb((255,128,0)))
''', '(255, 128, 0)\n#FF8000\n', [
        ('格式校验不能只依靠转换', '''
for text in ('FF8000','#fff','#１２３４５６','#GG0000',' #000000','#000000\\n'):
    try: parse_rgb(text)
    except ValueError: pass
    else: raise AssertionError(text)
for values in [(0,0),(0,0,256),(True,0,0),(0,0,-1)]:
    try: format_rgb(values)
    except ValueError: pass
    else: raise AssertionError(values)
'''),
        ('边界通道往返', '''
for r in (0,1,127,255):
    for g in (0,128,255):
        for b in (0,16,255):
            original=(r,g,b)
            assert parse_rgb(format_rgb(original))==original
assert format_rgb(parse_rgb('#aBcD01'))=='#ABCD01'
''')])
    enrich('l07:advanced', '转换负责求数值，协议校验负责决定哪些文本可以进入系统。即使int能接受某种写法，产品协议也未必允许；反向格式化还要补足前导零。',
           '为什么#000001不能格式化成#1？为什么颜色通道255.9不能先int截断后接受？写出parse(format(rgb))=rgb与format(parse(text))的区别。',
           '覆盖全零、最大通道、大小写、前导零、Unicode数字和往返性质。', minutes=60, prerequisites=('l17','l25','l30'))

    answer('l08:advanced',
        '实现within_tolerance(a,b,*,absolute=0.001,relative=0.0001)。只接受有限int/float（不含bool），容差非负；当差值不大于max(absolute,relative×max(abs(a),abs(b)))时返回True。不能先四舍五入，也不能只看单侧差值。',
        '''
import math
def within_tolerance(a, b, *, absolute=0.001, relative=0.0001):
    values = (a,b,absolute,relative)
    if any(type(x) not in (int,float) or not math.isfinite(x) for x in values):
        raise ValueError("比较值和容差必须有限")
    if absolute < 0 or relative < 0:
        raise ValueError("容差不能为负")
    error = abs(a-b)
    allowed = max(absolute, relative*max(abs(a),abs(b)))
    return error <= allowed
print(within_tolerance(9.9998,10))
print(within_tolerance(10000,10000.5))
print(within_tolerance(0,0.002))
''', 'True\nTrue\nFalse\n', [
        ('容差闭边界与对称性', '''
assert within_tolerance(0,0.125,absolute=0.125,relative=0)
assert not within_tolerance(0,0.126,absolute=0.125,relative=0)
for a,b in [(0,0),(-100,-100.001),(10000,10000.5),(-1,1)]:
    assert within_tolerance(a,b)==within_tolerance(b,a)
assert not within_tolerance(1,1.0001,absolute=0,relative=0)
'''),
        ('拒绝非有限和负容差', '''
for kwargs in ({'a':float('nan'),'b':1},{'a':1,'b':float('inf')},
               {'a':True,'b':1},{'a':1,'b':1,'absolute':-1}):
    try: within_tolerance(**kwargs)
    except ValueError: pass
    else: raise AssertionError(kwargs)
''')])
    enrich('l08:advanced', '同一个绝对误差，在接近零和非常大的量上含义不同。绝对容差保护零附近，相对容差随量级变化；两者取较大值，比较必须对称。这里的规则用于数值判断，不能代替金额按分记账。',
           '若用abs(a-b)/abs(b)，b为0怎么办？如果只判断a-b<=容差，一个极小的a为什么会错误通过？',
           '加入零附近、数量级变化、恰在容差边界、交换参数及NaN/Infinity用例。', minutes=65, prerequisites=('l25','l28','l30'))

    answer('l09:advanced',
        '实现can_join(registered,cancelled,paid,fee)：三个状态必须是bool，fee为非负整数。报名且未取消，并且已付款或免费才可参加。分别写正向与拒绝逻辑，遍历所有状态与fee=0、8，验证两种结果一致。免费0不能被“fee or 默认价”改写。',
        '''
def can_join(registered, cancelled, paid, fee):
    if any(type(x) is not bool for x in (registered,cancelled,paid)):
        raise ValueError("状态必须是bool")
    if type(fee) is not int or fee < 0:
        raise ValueError("价格必须为非负整数")
    allowed = registered and not cancelled and (paid or fee == 0)
    rejected = not registered or cancelled or (not paid and fee != 0)
    assert allowed == (not rejected)
    return allowed
for fee in (0,8):
    print(fee, can_join(True,False,False,fee))
''', '0 True\n8 False\n', [
        ('穷举16种状态的独立规则', '''
for registered in (False,True):
    for cancelled in (False,True):
        for paid in (False,True):
            for fee in (0,8):
                expected=False
                if registered:
                    if not cancelled:
                        if paid or fee==0: expected=True
                assert can_join(registered,cancelled,paid,fee) is expected
'''),
        ('类型与优先级反例', '''
assert not can_join(False,False,True,0)
assert not can_join(True,True,True,0)
for args in [(1,False,True,0),(True,False,False,-1),(True,False,False,True)]:
    try: can_join(*args)
    except ValueError: pass
    else: raise AssertionError(args)
''')])
    enrich('l09:advanced', '逻辑式有三层要求：资格、取消状态、费用条件。只验证一组True/False不足以证明括号正确；对有限的布尔状态，完整真值表很便宜。',
           'registered and not cancelled and paid or fee==0为什么会让未报名的人免费入场？找出一组最小反例，再写德摩根变换。',
           '列出16组组合，并用嵌套分支作为独立参照，避免把同一个表达式复制成测试答案。', minutes=60, prerequisites=('l11','l25'))

    answer('l11:advanced',
        '实现longest_word_span(text)，一次扫描找以ASCII空格分隔的最长非空段，返回(start,end)左闭右开区间；长度并列保留最早的一段。空串或全空格返回None，不用split或正则。利用区间取回原单词，并说明末段没有尾空格时怎样处理。',
        '''
def longest_word_span(text):
    start = None
    best = None
    for index in range(len(text)+1):
        ch = text[index] if index < len(text) else " "
        if ch != " ":
            if start is None: start = index
        elif start is not None:
            if best is None or index-start > best[1]-best[0]:
                best = (start,index)
            start = None
    return best
text = " red blue sky "
span = longest_word_span(text)
print(span)
print(text[span[0]:span[1]])
''', '(5, 9)\nblue\n', [
        ('无尾分隔并列保留最早', '''
assert longest_word_span('ab cd')==(0,2)
assert longest_word_span('a longest')==(2,9)
assert longest_word_span('') is None and longest_word_span('   ') is None
assert longest_word_span('  中文  x')==(2,4)
'''),
        ('扫描与独立小输入枚举对照', '''
from itertools import product
for size in range(6):
    for chars in product('a ', repeat=size):
        text=''.join(chars)
        candidates=[(a,b) for a in range(size) for b in range(a+1,size+1)
                    if ' ' not in text[a:b] and (a==0 or text[a-1]==' ')
                    and (b==size or text[b]==' ')]
        expected=next(iter(sorted(candidates,key=lambda p: (-(p[1]-p[0]),p[0]))),None)
        assert longest_word_span(text)==expected
''')])
    enrich('l11:advanced', '保存长度只能回答“有多长”，保存区间还能定位证据。终点不包含字符，因而段长总是end-start；并列时用严格大于更新，才不会用后面的同长段覆盖前面的。',
           'red blue sky没有尾空格，若只在遇到空格时结算会遗漏哪一段？把“>”改为“>=”会改变什么？',
           '覆盖首尾空格、连续空格、无尾空格、并列、全空及中文；给出时间O(n)、额外空间O(1)的理由。', minutes=65, prerequisites=('l17','l25'))

    answer('l12:advanced',
        '实现page_chunks(total,size,*,resume=0)，返回零起点左闭右开区间列表；总量非负、size正、resume在0至total，均为整数且排除bool。从resume继续处理，覆盖余下数据，尾块不得越界。23页、每组7页、从第15页继续即resume=14，得到[(14,21),(21,23)]。',
        '''
def page_chunks(total,size,*,resume=0):
    if any(type(x) is not int for x in (total,size,resume)):
        raise ValueError("参数必须是整数")
    if total<0 or size<=0 or not 0<=resume<=total:
        raise ValueError("总量、块长或恢复位置无效")
    return [(start,min(start+size,total)) for start in range(resume,total,size)]
chunks=page_chunks(23,7,resume=14)
for start,end in chunks: print(f"{start+1}至{end}")
print("剩余",sum(end-start for start,end in chunks))
''', '15至21\n22至23\n剩余 9\n', [
        ('无重叠无遗漏与恢复边界', '''
for total in range(12):
    for size in range(1,6):
        for resume in range(total+1):
            result=page_chunks(total,size,resume=resume)
            assert [i for a,b in result for i in range(a,b)]==list(range(resume,total))
            assert all(0<b-a<=size for a,b in result)
assert page_chunks(23,7,resume=23)==[]
'''),
        ('非法步长不能无限等待', '''
for args in [(1,0,0),(1,-1,0),(-1,2,0),(1,2,2),(1,2,-1),(True,1,0)]:
    total,size,resume=args
    try: page_chunks(total,size,resume=resume)
    except ValueError: pass
    else: raise AssertionError(args)
''')])
    enrich('l12:advanced', '分块除了正常从零开始，还要支持中断后的恢复位置。恢复点表示“下一项尚未完成”，因此resume=total必须返回空列表，不重新处理最后一项。',
           '单独检查各块长度<=size为什么仍可能漏项或重复？把所有块展开，与range(resume,total)逐项比较能发现什么？',
           '验证覆盖顺序、相邻块连接、已完成无需再运行及size=0的拒绝策略。', minutes=60, prerequisites=('l25',))

    answer('l13:advanced',
        '实现reduce_fraction(numerator,denominator)，接受任意整数（排除bool），分母不能为0。用余数循环约分，把负号统一放到分子，零统一为(0,1)。不导入math.gcd；返回二元组，并证明约分前后的交叉乘积相等。',
        '''
def reduce_fraction(numerator,denominator):
    if type(numerator) is not int or type(denominator) is not int or denominator==0:
        raise ValueError("需要整数与非零分母")
    if denominator<0:
        numerator,denominator=-numerator,-denominator
    a,b=abs(numerator),denominator
    while b:
        a,b=b,a%b
    return numerator//a,denominator//a
for n,d in [(42,56),(42,-56),(0,-9)]:
    a,b=reduce_fraction(n,d)
    print(f"{a}/{b}")
''', '3/4\n-3/4\n0/1\n', [
        ('符号守恒与幂等规范化', '''
for n in range(-10,11):
    for d in range(-10,11):
        if not d: continue
        a,b=reduce_fraction(n,d)
        assert b>0 and n*b==a*d
        assert reduce_fraction(a,b)==(a,b)
        assert not any(a%factor==b%factor==0 for factor in range(2,b+1))
'''),
        ('零分母和非整数拒绝', '''
for pair in [(1,0),(True,2),(1,False),(1.0,2)]:
    try: reduce_fraction(*pair)
    except ValueError: pass
    else: raise AssertionError(pair)
''')])
    enrich('l13:advanced', '算法答案还需要统一表示。3/-4与-3/4表示同一数，但比较、保存和展示更适合选择唯一形式。规范化不仅约掉公因数，还要固定分母符号与零的表示。',
           '为什么numerator=0时仍能进入同一段余数算法？若分母为0，会在哪一步产生问题？怎样不用浮点除法证明数值未变？',
           '用交叉乘积、不可再约分、正分母以及重复规范化不再改变结果四项性质验收。', minutes=60, prerequisites=('l25',))

    answer('l15:advanced',
        '实现coin_plans(amount,max_coins)，用1、2、5元硬币凑非负整数amount，硬币总数最多max_coins。只枚举5元和2元数量，由余量直接算1元数量；返回按枚举顺序的(1元数,2元数,5元数)列表。不重复枚举硬币排列，0元允许全零方案。',
        '''
def coin_plans(amount,max_coins):
    if any(type(x) is not int or x<0 for x in (amount,max_coins)):
        raise ValueError("金额与数量上限应为非负整数")
    result=[]
    for fives in range(min(amount//5,max_coins)+1):
        remaining=amount-5*fives
        for twos in range(min(remaining//2,max_coins-fives)+1):
            ones=remaining-2*twos
            if ones+twos+fives<=max_coins:
                result.append((ones,twos,fives))
    return result
print(coin_plans(6,4))
''', '[(2, 2, 0), (0, 3, 0), (1, 0, 1)]\n', [
        ('与小范围三重暴力法独立对照', '''
for amount in range(16):
    for cap in range(6):
        expected={(a,b,c) for a in range(cap+1) for b in range(cap+1) for c in range(cap+1)
                  if a+2*b+5*c==amount and a+b+c<=cap}
        found=coin_plans(amount,cap)
        assert set(found)==expected and len(found)==len(set(found))
'''),
        ('零方案和无解上限', '''
assert coin_plans(0,0)==[(0,0,0)] and coin_plans(3,1)==[]
assert coin_plans(5,1)==[(0,0,1)]
for args in [(-1,2),(1,-1),(1,True)]:
    try: coin_plans(*args)
    except ValueError: pass
    else: raise AssertionError(args)
''')])
    enrich('l15:advanced', '组合记录的是各类硬币数量，排列记录的是取币顺序；把同一组合的取币顺序重排不应增加方案数。利用等式推出最后一个变量，能把三重枚举缩成两重。',
           '凑6元时1+5与5+1应算几种？先限制枚举上界与在最内层才过滤，各自访问多少无效候选？',
           '用小规模三重枚举校对优化结果；解释剪枝不会丢失任何合法方案。', minutes=65, prerequisites=('l25',))

    answer('l16:advanced',
        '实现top_two_distinct(values)，一次遍历返回最大的两个不同整数，按降序组成元组；空输入返回()，只有一个不同值返回单元素元组。不得使用sort/sorted/max/set。既要处理全负数，也要避免重复最大值占据两个位置。',
        '''
def top_two_distinct(values):
    first=second=None
    for value in values:
        if type(value) is not int: raise ValueError("只接受整数")
        if first is None or value>first:
            second,first=first,value
        elif value!=first and (second is None or value>second):
            second=value
    if first is None: return ()
    if second is None: return (first,)
    return first,second
print(top_two_distinct([-8,-3,-11,-3]))
print(top_two_distinct([4,4]))
print(top_two_distinct([]))
''', '(-3, -8)\n(4,)\n()\n', [
        ('小输入穷举对照与来源保全', '''
from itertools import product
for size in range(5):
    for values in product((-3,-1,0,2),repeat=size):
        source=list(values)
        assert top_two_distinct(source)==tuple(sorted(set(source),reverse=True)[:2])
        assert source==list(values)
'''),
        ('次大值更新和非法数量', '''
assert top_two_distinct([1,9,8,10])==(10,9)
assert top_two_distinct([10,1,9,9])==(10,9)
for source in ([True],[1,2.0]):
    try: top_two_distinct(source)
    except ValueError: pass
    else: raise AssertionError(source)
''')])
    enrich('l16:advanced', '只找最大值容易隐藏状态设计问题；保留两个不同的最大值，需要在新冠军出现时把旧冠军移到第二位，同时跳过重复冠军。None表示“还没有值”，不会与负数、零混淆。',
           '依次读入1、9、8、10，逐轮写出first和second。若先覆盖first再令second=first，第一次丢失证据发生在哪一轮？',
           '覆盖全负、重复冠军、递增、递减、零个/一个不同值，用独立排序参照验证小输入。', minutes=65, prerequisites=('l25',))

    answer('l18:advanced',
        '实现encode_runs(values)，把相邻相同值编码为(value,count)，例如A,A,B,A,A变为[(A,2),(B,1),(A,2)]；再实现decode_runs(runs)还原序列。count必须是正整数且排除bool，不能把非相邻相同项合并，不能修改输入。',
        '''
def encode_runs(values):
    result=[]
    for value in values:
        if result and result[-1][0]==value:
            previous,count=result[-1]
            result[-1]=(previous,count+1)
        else:
            result.append((value,1))
    return result
def decode_runs(runs):
    result=[]
    for value,count in runs:
        if type(count) is not int or count<=0:
            raise ValueError("段长必须为正整数")
        result.extend([value]*count)
    return result
encoded=encode_runs(["A","A","B","A","A"])
print(encoded)
print(decode_runs(encoded))
''', "[('A', 2), ('B', 1), ('A', 2)]\n['A', 'A', 'B', 'A', 'A']\n", [
        ('往返与连续段数量', '''
from itertools import product
for n in range(6):
    for values in product('AB',repeat=n):
        source=list(values); encoded=encode_runs(source)
        assert decode_runs(encoded)==source
        assert sum(count for _,count in encoded)==len(source)
        assert all(a[0]!=b[0] for a,b in zip(encoded,encoded[1:]))
        assert source==list(values)
'''),
        ('空输入None数据和非法段长', '''
assert encode_runs([])==[] and decode_runs([])==[]
assert encode_runs([None,None,0])==[(None,2),(0,1)]
for count in (0,-1,True,1.5):
    try: decode_runs([('A',count)])
    except ValueError: pass
    else: raise AssertionError(count)
''')])
    enrich('l18:advanced', '连续压缩与全局去重保留的信息不同。仅留下A,B,A无法知道原来每一段有多长；补充段长才能实现可逆编码。示例中的稳定去重不变，练习对比这两种目标。',
           'A,A,B,A经过set、稳定去重、连续段编码后，各会丢掉什么信息？哪一种允许恢复原来的四项？',
           '验证解码编码后的结果等于原序列、段长之和等于原长度，相邻编码段不应相同。', minutes=60, prerequisites=('l25',))

    answer('l19:advanced',
        '实现push_snapshot(history,item,limit)：容量是正整数且排除bool；忽略与最后一项相同的内容，但每次都保证容量不超限，包括容量缩小时。item可以是嵌套列表/字典，必须保存deepcopy使以后修改来源不污染历史。历史列表原地更新，让别名仍能观察变化。',
        '''
from copy import deepcopy
def push_snapshot(history,item,limit):
    if type(limit) is not int or limit<=0:
        raise ValueError("容量必须为正整数")
    if not history or history[-1]!=item:
        snapshot=deepcopy(item)
        history.append(snapshot)
    del history[:-limit]
history=[]
for item in ["A","A","B","A"]:
    push_snapshot(history,item,2)
print(history)
document={"lines":["原文"]}
push_snapshot(history,document,2)
document["lines"].append("新文字")
print(history[-1])
''', "['B', 'A']\n{'lines': ['原文']}\n", [
        ('嵌套快照与别名隔离', '''
history=[];alias=history;original={'x':[1]}
push_snapshot(history,original,3)
original['x'].append(2)
assert history==[{'x':[1]}] and alias is history
push_snapshot(history,original,3)
history[-1]['x'].append(3)
assert history[0]=={'x':[1]} and original=={'x':[1,2]}
'''),
        ('重复项缩容和失败不修改', '''
history=['A','B','C'];push_snapshot(history,'C',1)
assert history==['C']
for limit in (0,-1,True,1.5):
    before=deepcopy(history)
    try: push_snapshot(history,'D',limit)
    except ValueError: pass
    else: raise AssertionError(limit)
    assert history==before
''')])
    enrich('l19:advanced', '历史记录只有在旧内容不再随来源变化时才是快照。直接append保存的是引用；只做外层copy仍可能共享嵌套列表。另一个边界是容量缩小：新内容重复，也必须淘汰多出的旧项。',
           'history.append(document)后再修改document的内层列表，撤销会回到旧内容吗？为何“重复就立即return”会破坏新容量上限？',
           '测试嵌套修改、别名身份、重复追加、重复时缩容及非法容量不改变历史。', minutes=65, prerequisites=('l20','l28'))

    answer('l20:intermediate',
        '实现make_grid(rows,cols,fill=0)，rows/cols为非负整数且排除bool，fill限定为整数。每一行独立；允许零行或零列。再用两个矩阵证明行之间、矩阵之间都不共享可变列表，负尺寸必须明确拒绝。',
        '''
def make_grid(rows,cols,fill=0):
    if any(type(x) is not int or x<0 for x in (rows,cols)) or type(fill) is not int:
        raise ValueError("尺寸必须为非负整数，填充值必须为整数")
    return [[fill]*cols for _ in range(rows)]
grid=make_grid(2,3)
grid[0][1]=7
print(grid)
other=make_grid(2,3)
print(other)
''', '[[0, 7, 0], [0, 0, 0]]\n[[0, 0, 0], [0, 0, 0]]\n', [
        ('零维与独立行矩阵', '''
assert make_grid(0,3)==[] and make_grid(2,0)==[[],[]]
g=make_grid(3,2,-1);h=make_grid(3,2,-1);g[0][0]=5
assert g[1][0]==g[2][0]==h[0][0]==-1
assert len({id(row) for row in g})==3
'''),
        ('负数浮点布尔尺寸拒绝', '''
for args in [(-1,2),(2,-1),(True,2),(2,1.5)]:
    try: make_grid(*args)
    except ValueError: pass
    else: raise AssertionError(args)
''')])
    enrich('l20:intermediate', '列表重复能复制多个引用，不能自动复制引用指向的行。尺寸也属于函数契约：Python允许负数乘列表得到空列表，但矩阵接口不能把负尺寸默默解释为零。',
           '[[0]*3]*2与[[0]*3 for _ in range(2)]外观看起来一样，怎样用一次修改和is比较证明它们不同？',
           '测试负尺寸、零维、非零填充值，并证明每行及两次调用都独立。', minutes=45)

    answer('l20:advanced',
        '实现moving_average(values,width)，width为正整数且排除bool，输入是整数列表，窗口不足返回[]。先写切片求和作参照，再让参考实现以“减去离开项、加上进入项”滚动更新，时间O(n)、除结果外额外空间O(1)，不修改来源。',
        '''
def moving_average(values,width):
    if type(width) is not int or width<=0:
        raise ValueError("窗口必须为正整数")
    if any(type(x) is not int for x in values):
        raise ValueError("本练习只接受整数数据")
    if len(values)<width: return []
    total=sum(values[:width])
    result=[total/width]
    for right in range(width,len(values)):
        total+=values[right]-values[right-width]
        result.append(total/width)
    return result
print(moving_average([2,4,6,8],2))
''', '[3.0, 5.0, 7.0]\n', [
        ('滚动结果与朴素切片参照', '''
for data in ([],[0],[-2,4],[2,-3,8,0,7],list(range(100))):
    original=data[:]
    for width in range(1,len(data)+3):
        expected=[sum(data[i:i+width])/width for i in range(len(data)-width+1)]
        assert moving_average(data,width)==expected
    assert data==original
'''),
        ('窗口边界和拒绝无效尺寸', '''
assert moving_average([4,8],2)==[6.0]
assert moving_average([4,8],3)==[]
for width in (0,-1,True,1.5):
    try: moving_average([1,2],width)
    except ValueError: pass
    else: raise AssertionError(width)
''')])
    enrich('l20:advanced', '相邻窗口重叠width-1项，每次重新切片求和会重复读取它们。维护窗口总和后，每移一步只需两个数据更新。当前练习限定整数，避免把浮点累计误差和算法改写混成同一个问题。',
           'width=3时，从[2,4,6]移到[4,6,8]，应该减谁、加谁？right-width为什么是离开项的下标？',
           '与朴素切片法对照；解释O(n×width)到O(n)的改进，并覆盖width=1、等于/大于长度。', minutes=65, prerequisites=('l25',))

    answer('l21:advanced',
        '实现freeze_grid(grid)，仅接受矩形二维整数数据（bool排除），返回元组的元组，空表及零宽矩阵允许；不规则行必须拒绝。证明来源修改不污染快照，快照能作为字典键，再比较两个内容相同但身份不同的快照。',
        '''
def freeze_grid(grid):
    rows=[tuple(row) for row in grid]
    width=len(rows[0]) if rows else 0
    if any(len(row)!=width or any(type(x) is not int for x in row) for row in rows):
        raise ValueError("需要矩形整数数据")
    return tuple(rows)
grid=[[1,2],[3,4]]
snapshot=freeze_grid(grid)
grid[0][0]=99
cache={snapshot:"已计算"}
print(snapshot)
print(cache[freeze_grid([[1,2],[3,4]])])
''', '((1, 2), (3, 4))\n已计算\n', [
        ('别名隔离与内容寻址', '''
source=[[1],[2]];frozen=freeze_grid(source);source[0].append(9)
assert frozen==((1,),(2,))
assert {frozen:7}[freeze_grid([[1],[2]])]==7
assert freeze_grid([])==() and freeze_grid([[],[]])==((),())
'''),
        ('拒绝不规则和可变单元格', '''
for grid in ([[1,2],[3]],[[True]],[[[1]]]):
    try: freeze_grid(grid)
    except ValueError: pass
    else: raise AssertionError(grid)
''')])
    enrich('l21:advanced', '元组只禁止替换它自己的槽位；若槽位仍装着列表，内部内容仍可变化，也不能直接作为字典键。本练习先验证叶子是整数，再冻结每一层，建立可用作缓存键的稳定值。',
           'tuple([[1],[2]])为什么仍不能作为字典键？同内容的两个快照不必是同一个对象，字典查找为何仍能命中？',
           '用真正的字典查找证明可哈希，用修改来源证明独立；解释零宽矩阵与空矩阵的结构区别。', minutes=60, prerequisites=('l22','l25'))

    answer('l22:advanced',
        '实现resolve_settings(defaults,overrides)：只允许defaults中已有的键，返回(新配置,每个键的来源)。overrides显式存在就覆盖，包括0、False、空串和None；未知键整批拒绝，两份输入都不修改。值限定为不可变标量，避免浅复制被误当深复制。',
        '''
def resolve_settings(defaults,overrides):
    unknown=set(overrides)-set(defaults)
    if unknown: raise ValueError("未知配置："+",".join(sorted(unknown)))
    allowed=(str,int,float,bool,type(None))
    if any(type(v) not in allowed for v in [*defaults.values(),*overrides.values()]):
        raise ValueError("配置值必须是不可变标量")
    result={};sources={}
    for key,value in defaults.items():
        explicit=key in overrides
        result[key]=overrides[key] if explicit else value
        sources[key]="显式" if explicit else "默认"
    return result,sources
settings,sources=resolve_settings({"volume":5,"theme":"light"},{"volume":0})
print(settings)
print(sources)
''', "{'volume': 0, 'theme': 'light'}\n{'volume': '显式', 'theme': '默认'}\n", [
        ('假值和None不是缺失', '''
defaults={'a':1,'b':2,'c':3,'d':4};overrides={'a':False,'b':0,'c':'','d':None}
result,sources=resolve_settings(defaults,overrides)
assert result==overrides and result is not overrides
assert set(sources.values())=={'显式'}
assert defaults=={'a':1,'b':2,'c':3,'d':4}
'''),
        ('未知键整批拒绝与空配置', '''
defaults={'x':1};overrides={'x':0,'y':2}
try: resolve_settings(defaults,overrides)
except ValueError as error: assert 'y' in str(error)
else: raise AssertionError('未知键不能静默丢弃')
assert defaults=={'x':1} and overrides=={'x':0,'y':2}
assert resolve_settings({}, {})==({}, {})
''')])
    enrich('l22:advanced', '返回值之外还要保留“这个值来自哪里”，才能解释配置覆盖。缺失键和显式None具有不同语义；读取result.get(key)再用or补默认，会把多种合法假值混在一起。',
           '用户把volume设为0，系统为什么不应回退到5？若出现拼错的volumn，应丢弃它、保留它还是拒绝？本课选择怎样的可核查策略？',
           '覆盖全部假值、未知键、空配置和输入保全；显示每一项的来源证据。', minutes=65, prerequisites=('l25','l30'))

    answer('l25:intermediate',
        '实现convert_temperatures(values,*,scale="F")，返回新的转换列表；scale为F时摄氏转华氏，为C时华氏转摄氏，其他值抛ValueError。拆出两个纯转换函数，不在计算函数里打印。空输入返回[]，摄氏-40与华氏-40是同一点。',
        '''
def celsius_to_fahrenheit(value): return value*9/5+32
def fahrenheit_to_celsius(value): return (value-32)*5/9
def convert_temperatures(values,*,scale="F"):
    if scale not in ("F","C"): raise ValueError("目标单位应为F或C")
    converter=celsius_to_fahrenheit if scale=="F" else fahrenheit_to_celsius
    return [converter(value) for value in values]
print(convert_temperatures([-40,0,100]))
print(convert_temperatures([32,212],scale="C"))
''', '[-40.0, 32.0, 212.0]\n[0.0, 100.0]\n', [
        ('往返近似与来源不变', '''
values=[-40,-5.5,0,37,100];before=values[:]
back=convert_temperatures(convert_temperatures(values),scale='C')
assert all(abs(a-b)<1e-10 for a,b in zip(values,back)) and values==before
assert convert_temperatures([])==[]
'''),
        ('错误选项与纯函数不打印', '''
from contextlib import redirect_stdout
from io import StringIO
buffer=StringIO()
with redirect_stdout(buffer): result=convert_temperatures([0])
assert buffer.getvalue()=='' and result==[32.0]
try: convert_temperatures([0],scale='K')
except ValueError: pass
else: raise AssertionError('单位不能猜测')
''')])
    enrich('l25:intermediate', '返回一个值使函数能参与另一轮计算；对列表批量转换时，这个区别更加明显。单位选项只决定选用哪个纯函数，输入输出边界负责展示，避免业务函数只能在控制台使用。',
           '如果转换函数只print而不return，连续做F再做C会得到什么？为何浮点往返应比较容差，而不总用严格==？',
           '覆盖空列表、负温度、两个方向、无效单位以及不修改来源；证明计算阶段没有输出。', minutes=50, prerequisites=('l26',))

    answer('l26:advanced',
        '实现with_tag(tag,existing=None,*,limit=3)。返回按首次出现顺序去重后的新标签列表；去掉每个标签两端空白，空标签拒绝。新标签若已有则不占新容量，否则末尾追加；超过正整数limit时整批拒绝。连续默认调用互不共享，即使显式传列表也不修改它。',
        '''
def with_tag(tag,existing=None,*,limit=3):
    if type(limit) is not int or limit<=0: raise ValueError("容量应为正整数")
    source=[] if existing is None else list(existing)
    result=[]
    for value in source+[tag]:
        if not isinstance(value,str) or not value.strip(): raise ValueError("标签不能为空")
        value=value.strip()
        if value not in result: result.append(value)
    if len(result)>limit: raise ValueError("标签超过容量")
    return result
base=[" python ","python"]
print(with_tag("offline",base))
print(base)
print(with_tag("first"),with_tag("second"))
''', "['python', 'offline']\n[' python ', 'python']\n['first'] ['second']\n", [
        ('独立默认与显式假空列表', '''
first=with_tag('A');second=with_tag('B');first.append('C')
assert second==['B']
source=[];result=with_tag('A',source)
assert source==[] and result is not source
assert with_tag('A',['A'],limit=1)==['A']
'''),
        ('容量失败不修改和清洗去重顺序', '''
source=[' A ','A']
assert with_tag(' A ',source,limit=1)==['A']
try: with_tag('B',source,limit=1)
except ValueError: pass
else: raise AssertionError('超限')
assert source==[' A ','A']
for tag in (' ',None):
    try: with_tag(tag)
    except ValueError: pass
    else: raise AssertionError(tag)
''')])
    enrich('l26:advanced', '默认参数只在定义函数时求值。None提供“调用方没有给集合”的标记，新结果则明确保证调用之间和与来源之间的独立性。现在还要决定规范化、去重与容量检查的顺序，顺序错了会误拒绝重复标签。',
           '已有[" A ","A"]且容量1，追加A应通过吗？为何先数原长度再去重会错误拒绝？空列表与None是否一定表达相同的接口意图？',
           '测试多次默认调用、显式空列表、清洗后重复、恰满容量和失败时来源保全。', minutes=60)

    # Actual contract defects: v2 migration previously trusted unvalidated tasks.
    u=units['l33:advanced']
    u['code']=dedent('''
def migrate(data):
    if not isinstance(data,dict) or type(data.get("version")) is not int:
        raise ValueError("版本存档必须为对象")
    version=data["version"]
    if version==1:
        titles=data.get("titles")
        if not isinstance(titles,list) or any(not isinstance(x,str) or not x.strip() for x in titles):
            raise ValueError("旧任务格式无效")
        return {"version":2,"tasks":[{"id":i,"title":title,"done":False} for i,title in enumerate(titles,1)]}
    if version==2:
        tasks=data.get("tasks")
        if not isinstance(tasks,list): raise ValueError("任务必须为列表")
        result=[];seen=set()
        for task in tasks:
            if not isinstance(task,dict) or set(task)!={"id","title","done"}:
                raise ValueError("任务字段无效")
            key=task["id"]
            if type(key) is not int or key<=0 or key in seen:
                raise ValueError("任务ID无效或重复")
            if not isinstance(task["title"],str) or not task["title"].strip() or type(task["done"]) is not bool:
                raise ValueError("任务内容无效")
            seen.add(key);result.append(dict(task))
        return {"version":2,"tasks":result}
    raise ValueError("不支持的版本")
old={"version":1,"titles":["阅读","练习"]}
print(migrate(old))
''').strip()+'\n'
    u['testCases'].append({'name':'已有v2存档也必须验证','field':'code','stdin':'','expectedOutput':u['expectedOutput'],
        'assertions':dedent('''
valid={'version':2,'tasks':[{'id':1,'title':'A','done':False}]}
copy=migrate(valid);copy['tasks'][0]['title']='B'
assert valid['tasks'][0]['title']=='A'
for bad in (None,{'version':True,'titles':[]},{'version':2},
            {'version':2,'tasks':[{'id':1,'title':'A','done':0}]},
            {'version':2,'tasks':valid['tasks']*2}):
    try: migrate(bad)
    except ValueError: pass
    else: raise AssertionError(bad)
''').strip()})
    enrich('l33:advanced', '版本号只决定使用哪个解释规则，不能证明内容合法。即使存档已经是v2，仍要校验唯一ID、非空标题和真正的布尔状态，再复制出独立结果；迁移重复执行应得到同一结构。',
           '为什么version=True会在宽松比较中被当成1？JSON对象中两个相同键为何可能在普通loads后失去冲突证据？',
           '严格JSON测试必须覆盖嵌套重复键、非标准数字和合法相同词出现在不同对象中；迁移检查v2也不能省略。', minutes=65)
    checks('l33:advanced',('嵌套冲突和合法独立对象','''
assert strict_loads('[{"x":1},{"x":2}]')==[{'x':1},{'x':2}]
for text in ('{"outer":{"x":1,"x":2}}','[NaN]','{"x":Infinity}'):
    try: strict_loads(text)
    except ValueError: pass
    else: raise AssertionError(text)
'''))

    # Smaller targeted tasks retain their accessible examples, but require
    # transfer, counterexamples or an actual executable acceptance property.
    pedagogical = {
        'l01:intermediate':('把预测写成逐条输出的记录；调换顺序、删除空行、提前打印结束各是不同故障。运行前先确定哪条语句贡献了哪些字符。',
            '把最后两次print交换后，屏幕哪两行会变化？删除print()与写print("")是否具有同样输出？',
            '先提交四行逐步预测，再做“交换两句/删除空行”两次单独实验；每次解释第一处差异。'),
        'l02:intermediate':('输出验收需要同时数调用次数与最终行数。两次调用可以组成一行，一次调用也可以输出内部带换行的文本；分隔符只存在于本次调用的参数之间。',
            '把end="/"改成sep="/"为什么不能连接两次调用？多一次默认print会怎样改变最后一个换行？',
            '再输出一行数量为0、商品名为空的记录，保留空字段；用repr展示完整结果中的分隔符和换行，而不靠肉眼对齐。'),
        'l03:intermediate':('总和相等是必要线索，但不是充分证明：2、5、9与4、4、8总和一样，内容不同。轮换应保证每个原值恰好出现一次，并且连续三次轮换回到原顺序。',
            '为什么只核对total会漏掉覆盖错误？给出一个总和相同却不是轮换的三元组。',
            '分别用三项互异、含0、存在重复的输入手工追踪；连续轮换三次后必须恢复原状。'),
        'l04:intermediate':('商余结果可以重建原输入。时间拆分不是显示好看就结束，hours×3600+minutes×60+rest应等于seconds，同时后两项都在0至59。',
            '59、60、3599、3600分别在哪一位进位？若先除以60再舍入，哪些输入会产生60秒？',
            '覆盖0、59、60、3599、3600及超过一天的秒数；用重建等式验证，小时数不强制模24。'),
        'l05:intermediate':('宽度是最小显示宽度，并不会替你截断超长编号。保留原数再计算，也与先舍入再计算产生不同结果。格式化应发生在展示边界。',
            '编号1007使用03d会截成007吗？单价1.236乘4，与显示成1.24后再乘4，结果为什么不同？',
            '用负温度、零温度、四位编号和两次连续计算验证；写出“显示宽度”和“限制最大长度”的区别。'),
        'l08:intermediate':('边界由业务契约决定；大于0且不超过5是左开右闭。只测试5无法发现写成0<=weight的错误。',
            '若误写0<=weight<5，最少用哪两项输入同时发现两个端点错误？',
            '分别预测并验证-0.1、0、0.1、4.9、5、5.1的结果，把每项归入等价类。'),
        'l18:intermediate':('zip默认停在较短序列，可能把未匹配的末项悄悄丢掉。数量相等仍不能证明业务顺序正确，因此姓名与数量的关联必须由上游协议保证。',
            '姓名有两项、数量只有一项时，直接list(zip(...))会保留什么？两边同长度但顺序交换又能否被长度检查发现？',
            '测试两边为空、仅一边为空、左长和右长；明确本函数只保证位置对齐，不猜测商品身份。'),
        'l24:intermediate':('筛选应在转换之前，才能跳过约定的空字段；但非空坏数据不应该被悄悄当0。本课约定所有非空字段都是合法整数，破坏约定时应明确失败。',
            '把if field放在int(field)之后，空字段会怎样？isdigit为什么不能直接判定带负号的合法整数？',
            '覆盖全空白、负数、零、两端空格；加入x并观察ValueError，解释为何不能静默过滤它。'),
        'l28:advanced':('工厂每次应返回独立状态；不同调用间不共享counts字典，比只返回不同外层字典更重要。模块缓存意味着模块级可变对象会活得比一次函数调用更久。',
            '若把counts={}放到模块顶层，两次new_inventory会如何互相污染？外层copy能否解决内层共享？',
            '用两次独立构造、重复品名、零库存和晚出现负数证明隔离与失败不保留部分结果。'),
        'l34:advanced':('CSV负责字段结构，电子表格公式解释是另一个层次。展示转义会主动改变文本，不能宣称同时保持业务原始值；保留原始导出与展示导出的用途区别。',
            '名字中有逗号应该交给谁处理？值以空格后等号开头，为什么仅检查value[0]仍不够？',
            '覆盖=、+、-、@、前导空格和制表符、普通负数字符串及空串；说明数字列为何应独立建模。'),
        'l38:advanced':('并列规则决定后面的名次。竞争排名90、90、80是1、1、3；密集排名是1、1、2。稳定性决定同分内部顺序，不能靠额外姓名排序偷偷改变约定。',
            '输入B90、A90、C80后，同分的B和A应保持什么顺序？把previous初始化为0会影响全负分吗？',
            '测试空列表、全部同分、全负分、乱序和多组并列，验证不修改来源且相同分数同名次。'),
        'l43:advanced':('分组迭代器不能预先消耗整个来源。每次next最多取两项，尾项补位只发生一次，之后应持续耗尽；真实None不表示来源结束。',
            '输入[None,None,None]会生成几组？若使用next(source,None)并把None当耗尽，会丢失哪些数据？',
            '用可记录读取次数的来源证明第一次next只读取两项；尾项处理后重复next始终StopIteration。'),
        'l47:advanced':('Protocol描述协作能力，不要求继承同一个具体类。固定时钟让日期相关测试不随系统日期改变；生产时钟和测试时钟都应通过同一接口进入函数。',
            '如果dated_title内部又调用date.today，传入FixedClock还有效吗？如何用一次调用计数发现偷偷重复读取时钟？',
            '验证空标题、闰日、两个不同的时钟实现，且每次格式化只读取一次today。'),
        'l49:advanced':('本课是受限的精确版本清单，不是完整包管理器。额外已安装包不等于冲突；真正需要报告的是必需包缺失或同名版本不符。报告顺序必须稳定便于比较。',
            'required为空但installed有包，应当报告缺失吗？字符串比较版本大小不能替代这里要求的精确匹配。',
            '分别测试全匹配、全缺失、部分版本不同、额外包和输入不变；对报告按名字稳定排序。'),
    }
    for identity,(why,thinking,acceptance) in pedagogical.items():
        enrich(identity,why,thinking,acceptance)

    checks('l18:intermediate',('两种长度方向与来源保留','''
assert pair_items([],[])==[]
for names,counts in [([], [1]),(['A'],[]),(['A','B'],[1]),(['A'],[1,2])]:
    before=(names[:],counts[:])
    try: pair_items(names,counts)
    except ValueError: pass
    else: raise AssertionError('静默截断')
    assert (names,counts)==before
'''))
    checks('l28:advanced',('无共享全局和晚失败','''
source=[('x',1),('x',2),('z',0)]
a=new_inventory(source);b=new_inventory(source)
a['counts']['x']=100
assert b['counts']=={'x':3,'z':0} and source==[('x',1),('x',2),('z',0)]
try: new_inventory([('x',1),('y',-1)])
except ValueError: pass
else: raise AssertionError('负值')
assert new_inventory([])=={'counts':{}}
'''))
    checks('l34:advanced',('公式前缀和普通值边界','''
for prefix in '=+-@':
    for space in ('',' ','\t'):
        text=space+prefix+'1'
        assert spreadsheet_text(text)=="'"+text
for text in ('','   ','hello','1+1',"'=1"):
    assert spreadsheet_text(text)==text
'''))
    checks('l38:advanced',('稳定并列与多个分组','''
source=[('B',-1),('A',-1),('Z',-5),('C',0),('D',-5)]
assert dense_rank(source)==[('C',0,1),('B',-1,2),('A',-1,2),('Z',-5,3),('D',-5,3)]
assert source[0]==('B',-1) and dense_rank([])==[]
'''))
    checks('l43:advanced',('消费数量与持续耗尽','''
reads=[]
def source():
    for x in [None,None,3]: reads.append(x);yield x
it=Pairs(source())
assert next(it)==(None,None) and reads==[None,None]
assert next(it)==(3,None) and reads==[None,None,3]
for _ in range(3):
    try: next(it)
    except StopIteration: pass
    else: raise AssertionError('尾项重复')
'''))
    checks('l47:advanced',('时钟只读一次且多实现','''
class CountingClock:
    def __init__(self): self.calls=0
    def today(self): self.calls+=1;return date(2000,1,1)
clock=CountingClock()
assert dated_title('',clock)=='2000-01-01:' and clock.calls==1
assert dated_title('A',FixedClock(date(2024,2,29)))=='2024-02-29:A'
'''))
    checks('l49:advanced',('稳定顺序与输入不变','''
required={'z':'1','a':'2','b':'3'};installed={'b':'4','extra':'1'}
assert audit_lock(required,installed)==(['a','z'],[('b','3','4')])
assert required=={'z':'1','a':'2','b':'3'} and installed=={'b':'4','extra':'1'}
assert audit_lock({},installed)==([],[])
'''))

