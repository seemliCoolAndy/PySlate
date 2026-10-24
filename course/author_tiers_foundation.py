"""Original intermediate/advanced lessons for the language foundation."""
from tier_helpers import add, case

def populate(t):
    add(t,'l01','intermediate','先预测，再运行：输出就是执行证据',
        ['按从上到下的顺序推演输出','区分代码文字与程序输出'],
        '程序不是把编辑器里所有文字原样展示出来。解释器执行一条语句，才产生那条语句规定的效果；引号是字符串的边界，不会自动出现在输出里。本例把一次实验拆成开始、测量、结束三个可观察步骤。先在纸上写下三行预测，再运行核对。如果顺序与预期不符，应检查语句所在位置，而不是多运行几次碰运气。这里还引入空行：print()没有参数仍会输出一个换行，可用它分隔报告段落。',
        ['逐条指向三次print，记录每条新增的输出','把空行计入预期，不把引号计入','调换两条语句，观察顺序由源码决定'],
        '''print("实验开始")
print("测量：18厘米")
print()
print("实验结束")''','实验开始\n测量：18厘米\n\n实验结束\n',
        '制作四行发货记录：接单、空行、装箱、发货。每行只由一次print产生；输出必须保持给定顺序。',
        '''print("接单")
print()
print("装箱")
print("发货")''','接单\n\n装箱\n发货\n',
        ['把引号写进预期输出，会多出程序没有打印的字符','空行也是输出；验收时不能随意忽略'],
        '执行顺序和换行属于可核对的行为，先预测再运行能缩小调试范围。',
        ('execution','空行来自哪一条语句？','四条print逐条追加到输出纸带',[('执行1','实验开始'),('执行2','测量：18厘米'),('执行3','空行'),('执行4','实验结束')]),
        [case('不同测量值','',replacements=[('18厘米','0厘米')],output='实验开始\n测量：0厘米\n\n实验结束\n'),case('记录改名','',field='solution',replacements=[('装箱','复核')],output='接单\n\n复核\n发货\n')])
    add(t,'l01','advanced','执行证据审计：定位缺失、重复与乱序',
        ['以完整事件序列定义程序验收协议','定位第一次偏离并区分异常结束与成功结束'],
        '高级路线建议先完成循环与函数主题，再回来看第一个程序。没有异常不等于完成了正确流程：日志可能缺项、重复或在工作完成前就打印END。本例把应发生的事件保存为有序列表，将实际事件逐项比较，首次不一致便报告位置；共同前缀完全相同后还要检查长度，才能发现尾部中断或多余输出。函数返回审计结论，外层负责展示。练习支持失败终点ERROR：先解析真实执行路径，再决定是否成功，不能只搜索记录中是否含有END几个字。',
        ['用规范列表定义BEGIN、检查、保存、END四步','在第一个不同位置停止并保留证据','前缀相同后检查长度，区分中断与额外记录'],
        '''def audit_trace(actual):
    expected=["BEGIN","CHECK","SAVE","END"]
    for index in range(min(len(actual),len(expected))):
        if actual[index]!=expected[index]:
            return f"第{index+1}项错误：预期{expected[index]}，实际{actual[index]}"
    if len(actual)<len(expected): return "中断：缺少"+expected[len(actual)]
    if len(actual)>len(expected): return "多余记录"
    return "完成"
for trace in (["BEGIN","CHECK","SAVE","END"],["BEGIN","CHECK"],["BEGIN","CHECK","CHECK","END"]):
    print(audit_trace(trace))''','完成\n中断：缺少SAVE\n第3项错误：预期SAVE，实际CHECK\n',
        '实现classify_run：严格接受BEGIN,READ,WRITE,END为成功，BEGIN,READ,ERROR为读取后失败；其他缺项、重复、错序均为协议错误。写明为什么含END也可能失败。',
        '''def classify_run(events):
    if events==["BEGIN","READ","WRITE","END"]: return "成功"
    if events==["BEGIN","READ","ERROR"]: return "读取后失败"
    return "协议错误"
for events in (["BEGIN","READ","WRITE","END"],["BEGIN","READ","ERROR"],["BEGIN","END","READ","WRITE"]):
    print(classify_run(events))''','成功\n读取后失败\n协议错误\n',
        ['只查END是否存在会把乱序记录误当成功','只比较共同前缀会漏掉截断或多余尾部'],
        '执行证据需要顺序、数量和终点同时满足契约，首次偏离是定位错误的线索。',
        ('protocol','日志中有END，就能证明程序完成了吗？','正确路径、提前中断与重复事件的审计对照',[('正确','BEGIN→CHECK→SAVE→END'),('中断','BEGIN→CHECK，缺SAVE'),('重复','第三项CHECK，预期SAVE')]),
        [case('空记录与多余尾部','assert audit_trace([])=="中断：缺少BEGIN"\nassert audit_trace(["BEGIN","CHECK","SAVE","END","END"])=="多余记录"'),case('缺项重复乱序均拒绝','for x in ([],["BEGIN","READ","END"],["BEGIN","READ","READ","END"],["END","BEGIN","READ","WRITE"]):\n    assert classify_run(x)=="协议错误"',field='solution')],prerequisites=['l01','l16','l25'])
    add(t,'l02','intermediate','把多条输出拼成表格',
        ['组合sep与end形成稳定分隔格式','识别分隔符与行结束符各自的职责'],
        'print的sep只放在同一次调用的多个对象之间，end则在这次调用最后追加。本例先输出表头，再用两个调用共同组成一行：第一段末尾保留竖线，第二段负责换行。因此不是看到两个print就一定有两行。做文本表格时，应先确定列分隔符和行终止符，避免边拼边补空格导致列错位。这里只处理不含分隔符的简单字段；真正包含逗号或换行的数据，后面的CSV课程会使用专门的格式工具。',
        ['表头sep设置为竖线','第一段end保留分隔符且不换行','第二段使用默认end结束整行'],
        '''print("姓名", "完成", sep="|")
print("小禾", end="|")
print(3)''','姓名|完成\n小禾|3\n',
        '输出一张两行小票：第一行商品/数量/单价，第二行铅笔/2/1.5。使用sep控制斜线，第二行至少分两次输出且不多换行。',
        '''print("商品", "数量", "单价", sep="/")
print("铅笔", 2, sep="/", end="/")
print(1.5)''','商品/数量/单价\n铅笔/2/1.5\n',
        ['sep不会影响相邻两次print，连接处要看end','end设置为空后忘记终结，会把下一段接到同一行'],
        '设计输出时分别决定对象间分隔和调用后终止，结果才能预测。',
        ('output-buffer','第二次print为何没有开始新行？','每次调用向同一输出缓冲区追加文本',[('表头','姓名|完成\\n'),('第一段','小禾|'),('第二段','3\\n')]),
        [case('改分隔符','',replacements=[('sep="|"','sep=","'),('end="|"','end=","')],output='姓名,完成\n小禾,3\n'),case('零数量','',field='solution',replacements=[('"铅笔", 2','"铅笔", 0')],output='商品/数量/单价\n铅笔/0/1.5\n')])
    add(t,'l02','advanced','输出协议设计：数据中的分隔符怎么办',
        ['设计可逆的字段转义规则','用状态扫描恢复分隔符与真实换行'],
        '仅用sep连接字段时，数据本身若含竖线就无法判断它是分隔符还是内容。高级路线在学过字符串与循环后设计一个小协议：反斜线写成两个反斜线，字段内竖线写成反斜线竖线，真实换行写成反斜线n，再用未转义竖线分列。替换顺序很重要，必须先转义原反斜线，否则新加的转义标记会再被改写。示例负责编码，练习负责状态解码；空字段必须保留，未知转义及末尾孤立反斜线拒绝。这是受限教学格式，真实通用表格应使用CSV。',
        ['先定义三种转义与一个字段边界','先处理原反斜线，再处理竖线和换行','解码时记录是否刚读到转义前缀'],
        r'''def encode_fields(fields):
    return "|".join(text.replace("\\","\\\\").replace("|","\\|").replace("\n","\\n") for text in fields)
fields=["a|b","x\ny","C:\\tmp"]
record=encode_fields(fields)
print(record)''','a\\|b|x\\ny|C:\\\\tmp\n',
        '实现decode_fields，按上述协议恢复列表，保留首尾空字段；未知转义和末尾孤立反斜线抛ValueError。空记录表示一个空字段。',
        r'''def decode_fields(record):
    result=[];current="";escaped=False
    for ch in record:
        if escaped:
            if ch not in "\\|n": raise ValueError("未知转义")
            current += "\n" if ch=="n" else ch
            escaped=False
        elif ch=="\\": escaped=True
        elif ch=="|": result.append(current);current=""
        else: current+=ch
    if escaped: raise ValueError("转义未完成")
    return result+[current]
print(decode_fields("A\\|B|line\\nnext|"))''',"['A|B', 'line\\nnext', '']\n",
        ['转义反斜线的顺序放最后会再次转义新生成的控制标记','直接split竖线仍会拆开已转义的数据竖线'],
        '输出边界与数据字符必须分离；可逆协议要同时规定编码、解码和非法状态。',
        ('escaping','字段本身的竖线如何与真正的列边界区分？','编码后的转义标记与解码状态转换',[('原字段','a|b 与 x换行y'),('编码','a\\|b|x\\ny'),('解码','转义态保留数据竖线；普通竖线分列')]),
        [case('空字段与原反斜线','assert encode_fields(["","", "\\\\"])=="||\\\\\\\\"'),case('非法转义与空字段',"assert decode_fields('')==[''] and decode_fields('|')==['','']\nfor bad in ('x\\\\','a\\\\q'):\n    try:\n        decode_fields(bad)\n    except ValueError:\n        pass\n    else:\n        raise AssertionError(bad)",field='solution')],prerequisites=['l02','l17','l25'])
    add(t,'l03','intermediate','交换与快照：变量记录哪个时刻',
        ['用中间变量保留旧值','跟踪重新绑定后的独立数值'],
        '赋值先计算右侧，再让左侧名字指向结果。连续写a=b、b=a并不能交换，因为第一步已失去旧a。中间变量可以保存这个历史值。本例把两人积分交换，同时保留交换前的总分作为不变量。整数不会被原地修改，修改其中一个名字不会追溯改变已算好的total。画变量表时，每执行一行就更新一格，不能把所有等号理解成数学上同时成立的关系。',
        ['先记录left与right的原值','用saved跨越第一次覆盖','交换后用总和检查有没有丢失数值'],
        '''left = 12
right = 7
total = left + right
saved = left
left = right
right = saved
print(left, right, total)''','7 12 19\n',
        '三箱数量a=2、b=5、c=9，向右轮换为9、2、5；保留轮换前总数并输出四个数，不能直接把最终数值写死。',
        '''a = 2
b = 5
c = 9
total = a + b + c
saved = c
c = b
b = a
a = saved
print(a, b, c, total)''','9 2 5 16\n',
        ['先覆盖再保存会丢失旧值','total是计算时的结果，不会自动随a重新计算'],
        '状态变化按时间发生，临时变量保存的是即将被覆盖的旧状态。',
        ('bindings','不借助saved，哪一个旧值会先消失？','三个时间点的变量绑定与总和不变量',[('起点','left12 right7 total19'),('暂存','saved12 left7'),('完成','left7 right12 total19')]),
        [case('相同值交换','assert left == right == 4 and total == 8',replacements=[('left = 12','left = 4'),('right = 7','right = 4')],output='4 4 8\n'),case('含零轮换','assert (a,b,c,total)==(0,2,5,7)',field='solution',replacements=[('c = 9','c = 0')],output='0 2 5 7\n')])
    add(t,'l03','advanced','读写库存账：覆盖错误怎样发生',
        ['把库存操作写成状态转移','用守恒关系定位重复扣减'],
        '库存程序常见错误不是算术不会做，而是同一事件扣了两次，或者把当前库存误当作起始库存。本例明确保留opening、received和shipped三个事实，再计算closing；后续新增出库只更新shipped并重新计算closing。这样原始事实和派生值的职责不同，能通过opening+received=shipped+closing核对。初学阶段也可以采用这样的设计：先命名事实，再计算结果，最后输出证据。避免用一个含糊的number反复承担不同含义。',
        ['列出入库和出库事实，不覆盖opening','新增订单只更新累计出库','重新计算结存并核对两边总数'],
        '''opening = 20
received = 8
shipped = 11
closing = opening + received - shipped
shipped = shipped + 3
closing = opening + received - shipped
print(opening + received, shipped + closing)
print("结存", closing)''','28 28\n结存 14\n',
        '设计水箱账：初始50升，加入12升，首次用去9升，第二次用去7升。保留事实，输出最终46升及总入量与总用量加余量的核对。',
        '''initial = 50
added = 12
used = 9
used = used + 7
remaining = initial + added - used
print("余量", remaining)
print(initial + added, used + remaining)''','余量 46\n62 62\n',
        ['在closing上重复减同一订单会重复记账','变量名复用为不同单位会破坏计算含义'],
        '区分事实与派生状态，用守恒关系为赋值顺序提供独立证据。',
        ('conservation','订单追加后，为什么要重算结存？','库存流入流出与守恒关系',[('总入','20+8=28'),('总出','11+3=14'),('结存','28-14=14；两边28')]),
        [case('无新订单','assert closing == 17',replacements=[('shipped + 3','shipped + 0')],output='28 28\n结存 17\n'),case('恰好用尽','assert remaining == 0',field='solution',replacements=[('used + 7','used + 53')],output='余量 0\n62 62\n')])
    add(t,'l04','intermediate','整除与余数：不漏装也不多收费',
        ['从总量求完整组与剩余量','用整数表达向上取整的组数'],
        '把物品每6个装一盒，17//6得到完整的2盒，17%6得到剩余5个。若实际发货，剩余物品还需要一盒，因此可用(total+size-1)//size计算非负整数的向上整除。这个公式的前提是size为正且total非负；对负数不能照搬业务含义。除法/会产生浮点数，表示平均值合适，表示盒子数量则不如整数清楚。本例同时输出分解结果与实际所需盒数，避免把完整盒数误作总盒数。',
        ['先按完整组与剩余拆分17','再把存在的剩余容纳进最后一盒','用groups*size+remainder恢复原总量'],
        '''total = 17
size = 6
groups = total // size
remainder = total % size
boxes = (total + size - 1) // size
print(groups, remainder, boxes)''','2 5 3\n',
        '把3671秒分成小时、分钟、秒，并输出01:01:11格式（格式化可查前课），不能用浮点舍入替代整除和余数。',
        '''seconds = 3671
hours = seconds // 3600
minutes = seconds % 3600 // 60
rest = seconds % 60
print(f"{hours:02d}:{minutes:02d}:{rest:02d}")''','01:01:11\n',
        ['total//size漏掉不足一盒的部分','先用/再转int会引入不必要的浮点精度问题'],
        '整除给商，余数给剩余；先界定非负数量的业务前提。',
        ('partition','17件为什么需要3盒而不是2盒？','完整组和剩余组共同覆盖全部物品',[('完整盒','6+6'),('剩余','5'),('需要','2+1=3盒')]),
        [case('空发货','assert groups==remainder==boxes==0',replacements=[('total = 17','total = 0')],output='0 0 0\n'),case('整点时间','assert (hours,minutes,rest)==(1,0,0)',field='solution',replacements=[('seconds = 3671','seconds = 3600')],output='01:00:00\n')])
    add(t,'l04','advanced','负数商余与单位约束',
        ['验证Python整除向下取整的规则','利用商余恒等式诊断错误假设'],
        'Python的//向负无穷方向取整，不是简单删除小数部分。-7//3是-3，相应余数是2，仍满足a=q*b+r。正除数下余数处于0至b-1之间，这让循环位置归一化很方便：从位置1后退3步，在长度5的环上可用(1-3)%5得到3。算术表达式本身没有业务单位，若把“第几页”与“字符数”混用，运行也可能成功但结果无意义。高级练习要求使用统一的零起点位置表示，最后一步才转换展示编号。',
        ['先计算负数商和余数并重建被除数','将移动后的位置通过模归入环内','只在显示时把零起点转换成人的编号'],
        '''a = -7
b = 3
q = a // b
r = a % b
position = (1 - 3) % 5
print(q, r, q * b + r)
print("位置", position)''','-3 2 -7\n位置 3\n',
        '12小时钟的内部位置为0至11。当前显示2点，后退5小时后显示9点。使用零起点计算，并展示最终1至12的钟面数值。',
        '''display = 2
shift = -5
zero_based = (display - 1 + shift) % 12
result = zero_based + 1
print("钟面", result)''','钟面 9\n',
        ['认为-7//3等于-2会破坏商余关系','一开始用1至12做模运算会让12点边界偏移'],
        '用恒等式而非直觉检查负数运算，索引与显示编号应明确转换。',
        ('cycle','后退跨过起点时，模运算怎样回到环内？','负位移在模空间中被归一化',[('原位置','零起点1'),('移动','1-3=-2'),('归一化','-2 % 5 = 3')]),
        [case('整除负数','assert (q,r)==(-2,0) and q*b+r==a',replacements=[('a = -7','a = -6')],output='-2 0 -6\n位置 3\n'),case('午夜边界','assert result == 12',field='solution',replacements=[('display = 2','display = 1'),('shift = -5','shift = -1')],output='钟面 12\n')])
    add(t,'l05','intermediate','格式化不是修改数据',
        ['控制字段宽度与小数位','区分原始数值和展示字符串'],
        '报表里把1.236显示成1.24，并不意味着变量本身变成1.24。f字符串中的格式说明只控制这一次文本表示。本例把价格右对齐到7个字符，数量右对齐到3个字符，再计算金额；对齐宽度是最小宽度，内容过长不会被截断。字符串len统计Python字符数量，含中文时不等于终端显示列宽，因此本课使用等宽的英文商品代码制作对齐表。需要精确财务计算时，将在Decimal课区分数值表示与舍入规则。',
        ['在冒号后设置宽度和小数位','计算仍使用原始price和quantity','比较显示结果与未改变的price'],
        '''price = 1.236
quantity = 4
line = f"P01 {quantity:3d} {price:7.2f} {price * quantity:.2f}"
print(line)
print(price)''','P01   4    1.24 4.94\n1.236\n',
        '生成一行传感器记录：编号007，温度-2.50，单位C；编号需补零到三位，并保留原温度用于下一次计算。',
        '''sensor_id = 7
temperature = -2.5
record = f"{sensor_id:03d}|{temperature:.2f}|C"
print(record)
print(temperature + 1)''','007|-2.50|C\n-1.5\n',
        ['把格式化结果当数值相加会得到类型错误','宽度限制不负责截断长字段'],
        '计算层保留数值，显示层负责格式；两个职责分清才容易复核。',
        ('representation','显示1.24后，参与计算的price为什么仍为1.236？','原数值生成格式化文本而不被覆盖',[('数值','1.236'),('展示','宽7，小数2 → 1.24'),('计算','1.236*4 → 4.944')]),
        [case('零数量','assert price==1.236 and quantity==0',replacements=[('quantity = 4','quantity = 0')],output='P01   0    1.24 0.00\n1.236\n'),case('编号越过宽度','assert sensor_id==1234',field='solution',replacements=[('sensor_id = 7','sensor_id = 1234')],output='1234|-2.50|C\n-1.5\n')])
    add(t,'l05','advanced','可诊断的字符串与有界预览',
        ['定位不可见字符并区分字符数和字节数','设计不超过预算的单行预览'],
        '标题里藏着换行或末尾空格时，只看普通print难以定位。repr显示诊断表示，enumerate提供每个字符的位置，encode("utf-8")则展示字节长度；三者回答不同问题。高级例子生成不可见字符位置表，不先strip破坏现场。练习为日志设计有界预览：先把回车和换行转为可见转义，再按字符预算截断；需要截断时预留一个省略号位置。这不是终端显示列宽或人类字素簇截断，组合字符和emoji可能跨多个码点，若产品要求更强视觉规则需专门处理。',
        ['对原文逐字符扫描并记录控制字符位置','比较原始字符数与UTF-8字节数','预览先转义再截断，省略号计入预算'],
        r'''def inspect_text(text):
    hidden=[(index,repr(ch)) for index,ch in enumerate(text) if ch in " \t\r\n"]
    return {"characters":len(text),"bytes":len(text.encode("utf-8")),"hidden":hidden}
text="  你好\n"
report=inspect_text(text)
print(report["characters"],report["bytes"])
print(report["hidden"])''',"5 9\n[(0, \"' '\"), (1, \"' '\"), (4, \"'\\\\n'\")]\n",
        '实现preview(text,budget)，budget至少1；先将回车、换行变成可见\\r、\\n，超预算保留前budget-1字符加…；不超预算原样，结果始终单行且字符长度不超过budget。',
        r'''def preview(text,budget):
    if type(budget) is not int or budget<1: raise ValueError("预算至少1")
    visible=text.replace("\r","\\r").replace("\n","\\n")
    return visible if len(visible)<=budget else visible[:budget-1]+"…"
print(preview("hello\nworld",8))
print(preview("你好",1))''','hello\\n…\n…\n',
        ['字符数不能推断UTF-8字节长度','先截断再转义可能让结果超过预算，省略号也占长度'],
        '诊断保存真实字符证据，预览明确长度单位、转义顺序和截断预算。',
        ('characters','五个字符为什么占九个UTF-8字节？','两个空格、两个中文码点和一个换行的两种计量',[('字符计数','2空格+2汉字+1换行=5'),('UTF-8','2+6+1=9字节'),('隐藏位置','0、1为空格，4为换行')]),
        [case('ASCII与空字符串','assert inspect_text("")=={"characters":0,"bytes":0,"hidden":[]}\nassert inspect_text("A\\tB")["hidden"]==[(1,repr("\\t"))]'),case('预算与单行性质','for text in ("", "abc", "x\\r\\ny", "你好世界"):\n    for n in range(1,6):\n        x=preview(text,n)\n        assert len(x)<=n and "\\n" not in x and "\\r" not in x\nassert preview("abc",3)=="abc"',field='solution')],prerequisites=['l05','l17','l25'])
    add(t,'l06','intermediate','输入协议：一行就是一个字段',
        ['明确input只读取一行','区分提示内容与输入回显'],
        'input在读到行结束时返回该行文本，不包含结尾换行。用户在一次输入里打下多个空格，它不会自动分字段；程序需要自己约定字段边界。本例要求三行依次提供姓名、课程、目标，并把接收到的原始字段放进方括号输出，以便检查空输入和多余空格。提示语由程序输出，输入内容由界面提供，两者不是同一来源。自动测试只比较程序产生的文本，不把终端可能显示的用户回显当作程序输出。',
        ['按三行协议准备标准输入','每个input只接收对应的一行','用边界括号检查字段是否真的为空'],
        '''name = input("姓名：")
course = input("课程：")
goal = input("目标：")
print(f"[{name}]学习[{course}]，目标[{goal}]")''','姓名：课程：目标：[小禾]学习[Python]，目标[写工具]\n',
        '读取订单号和备注两行，允许备注为空。输出两段带方括号的字段及备注字符数，不把空备注改成其他文字。',
        '''order = input("订单：")
note = input("备注：")
print(f"订单[{order}] 备注[{note}] 长度{len(note)}")''','订单：备注：订单[小禾] 备注[Python] 长度6\n',
        ['空行返回空字符串，不是没有发生读取','自动验收通常不会把用户输入回显算入stdout'],
        '先制定逐行输入协议，再决定如何验证每一个字段。',
        ('input-stream','备注为空时，第二次input有没有执行？','输入流按换行分成独立字段',[('输入1','小禾'),('输入2','Python'),('输入3','写工具')]),
        [case('空目标','assert goal==""',stdin='阿青\nPython\n\n',output='姓名：课程：目标：[阿青]学习[Python]，目标[]\n'),case('空备注','assert note==""',field='solution',stdin='A01\n\n',output='订单：备注：订单[A01] 备注[] 长度0\n')],stdin='小禾\nPython\n写工具\n')
    add(t,'l06','advanced','批量输入协议：空行、EOF与不完整提交',
        ['根据数量头读取恰好规定行数','遇到EOF拒绝半份数据而保留合法空字段'],
        '高级路线先学习函数和异常处理，再设计一个真实输入协议：第一行是字段数量，后面恰好读取相应数量的行。空行表示合法空字符串，EOF表示根本没有下一行，两者不能混淆。本例把读取函数作为参数传入，默认使用input；这样交互和测试使用同一业务逻辑。任何一行缺失都抛带位置的ValueError，不返回半份记录；数量还限制在0至20，避免错误头部造成无边界等待。练习把空白清洗设为显式选项，不要总自动strip，因为空格有时是数据。',
        ['数量头先转换并校验0至20','循环恰好读取count行，不额外读下一条记录','EOF报告缺失字段位置，空字符串仍保留'],
        '''def read_fields(count,reader=input):
    if type(count) is not int or not 0<=count<=20: raise ValueError("字段数应为0至20")
    result=[]
    for index in range(count):
        try: value=reader()
        except EOFError as error: raise ValueError(f"缺少第{index+1}项") from error
        result.append(value)
    return result
try:
    count=int(input("字段数："))
    fields=read_fields(count)
except (ValueError,EOFError) as error: print("输入失败：",error)
else: print(fields)''',"字段数：['', '   ']\n",
        '实现read_record(count,reader=input,*,trim=False)，数量范围同示例，缺项拒绝；trim只在显式为True时去两端空白，默认保留数据。',
        '''def read_record(count,reader=input,*,trim=False):
    if type(count) is not int or not 0<=count<=20: raise ValueError("字段数应为0至20")
    result=[]
    for index in range(count):
        try: text=reader()
        except EOFError as error: raise ValueError(f"缺少第{index+1}项") from error
        result.append(text.strip() if trim else text)
    return result
try:
    count=int(input("字段数："))
    record=read_record(count)
except (ValueError,EOFError) as error: print("输入失败：",error)
else: print(record)''',"字段数：['', '   ']\n",
        ['用空字符串表示EOF会误删合法空字段','发生缺项后仍返回部分结果会把不完整提交当完整'],
        '输入协议需要数量、边界与失败语义；注入读取能力可以稳定测试交互错误。',
        ('input-boundaries','第一字段为空和第二字段根本不存在，应是同一种结果吗？','数量头控制读取，空行保留而EOF拒绝整份',[('头部','count2'),('合法空行','返回空字符串，计一项'),('流耗尽','EOFError → 缺少指定项')]),
        [case('EOF定位不返回半份记录','values=iter(["first"])\ndef finite_reader():\n    try: return next(values)\n    except StopIteration as error: raise EOFError from error\ntry:\n    read_fields(2,finite_reader)\nexcept ValueError as error:\n    assert str(error)=="缺少第2项"\nelse:\n    raise AssertionError("partial record accepted")',stdin='2\n\n   \n'),case('零字段不读取与显式清洗','def forbidden(): raise AssertionError("unexpected read")\nassert read_record(0,forbidden)==[]\nit=iter([" x ", " "])\nassert read_record(2,lambda:next(it),trim=True)==["x",""]',field='solution',stdin='2\n\n   \n')],stdin='2\n\n   \n',prerequisites=['l06','l25','l30'])
    add(t,'l07','intermediate','先转换，再计算：类型错误与数值含义',
        ['区分文本拼接和整数运算','组合整数数量与浮点测量值'],
        'input总是返回字符串，即使屏幕上输入的是数字。字符串的加号执行拼接，数字的加号执行求和；转换并不是在显示时加一个数字外观，而是产生另一种类型的值。本例将箱数和每箱件数转换成int，再将单件重量转换成float，最后输出总件数与重量。数量要求整数，因此不能用int(float(text))悄悄截掉小数。输入是否符合格式与值是否满足业务限制是两层问题，后续条件与异常课会把它们分开处理。',
        ['三行输入分别约定整数、整数、小数','先完成转换，再形成带单位的计算','展示保留小数位不改变计算值'],
        '''boxes = int(input("箱数："))
per_box = int(input("每箱："))
weight = float(input("单件千克："))
items = boxes * per_box
print(f"{items}件，{items * weight:.2f}千克")''','箱数：每箱：单件千克：12件，3.00千克\n',
        '读取路程公里数和耗时分钟，转换为float后计算每小时平均速度；本层约定耗时为正，在练习注释中注明这个前提。',
        '''distance = float(input("公里："))
minutes = float(input("分钟："))
# 输入协议要求耗时大于0。
speed = distance / (minutes / 60)
print(f"{speed:.2f}公里/小时")''','公里：分钟：45.00公里/小时\n',
        ['数字字符串相加会拼接，不能当求和','截断转换不等于校验整数输入'],
        '转换要服务于明确的数量含义，先写下单位和输入前提。',
        ('conversion','为什么输入3和4得到12件而不是34？','文本经整数转换后参与乘法',[('文本','"3" "4" "0.25"'),('转换','int3 int4 float0.25'),('结果','12件 / 3.00千克')]),
        [case('零箱','assert items==0',stdin='0\n4\n0.25\n',output='箱数：每箱：单件千克：0件，0.00千克\n'),case('小数路程','assert speed==7.5',field='solution',stdin='2.5\n20\n',output='公里：分钟：7.50公里/小时\n')],stdin='3\n4\n0.25\n')
    add(t,'l07','advanced','进制转换与截断陷阱',
        ['使用int的base参数解释数字文本','区分向零截断和向下取整'],
        '数字文本的含义依赖进制："10"在十进制是10，在二进制是2。int(text, base)把这个约定变成可执行规则，而不是凭字符串外观猜测。另一个常见误会是把int用于取整：int(-2.8)向零截断得到-2，-2.8//1向下取整得到-3.0，两种规则不同。本例对比文本解释与数值截断，说明转换有明确语义，并不替代四舍五入。练习处理十六进制颜色通道；只转换数据，不把整段带逗号的记录直接交给int。',
        ['同一文本指定不同base后分别求值','对负数比较截断与整除规则','只在显示阶段把整数转换为字符串'],
        '''text = "10"
decimal_value = int(text, 10)
binary_value = int(text, 2)
truncated = int(-2.8)
print(decimal_value, binary_value)
print(truncated, -2.8 // 1)''','10 2\n-2 -3.0\n',
        '将十六进制通道文本FF、80、00转为十进制，求三个通道的总和，并输出十进制值；不得写死255、128、0作为答案。',
        '''red = int("FF", 16)
green = int("80", 16)
blue = int("00", 16)
total = red + green + blue
print(red, green, blue)
print(total)''','255 128 0\n383\n',
        ['忘写base会把十六进制字母判为非法输入','int的截断规则不是round的舍入规则'],
        '转换必须指定表示约定，负数边界能揭示看似相同操作的差别。',
        ('representation','同一串10，为何能表示10也能表示2？','不同进制的位权解释',[('十进制','1×10+0 = 10'),('二进制','1×2+0 = 2'),('负数转换','int(-2.8) = -2')]),
        [case('带前导零','assert decimal_value==1 and binary_value==1',replacements=[('text = "10"','text = "01"')],output='1 1\n-2 -3.0\n'),case('全白通道','assert total==765',field='solution',replacements=[('"80", 16','"FF", 16'),('"00", 16','"FF", 16')],output='255 255 255\n765\n')])
    add(t,'l08','intermediate','区间边界与链式比较',
        ['把业务区间准确翻译为比较式','识别等于边界时是否通过'],
        '“温度在18至26之间，含两端”对应18<=temperature<=26。链式比较把同一个中间值放在相邻关系里，表达比拆成两个无关判断更清楚。边界要逐一讨论：18能通过，26能通过，17.9和26.1不能。等号数量也有区别：=用于赋值，==用于比较。本例同时计算区间判断与是否恰在边界，为后续条件分支准备证据；布尔结果是真正的True或False，不是中文提示词。',
        ['把区间左右端点和包含关系写清','分别求范围判断与边界判断','用恰等于端点的测试检查等号'],
        '''temperature = 26
comfortable = 18 <= temperature <= 26
at_upper = temperature == 26
print(comfortable, at_upper)''','True True\n',
        '检查包裹重量是否在0到5千克，要求大于0且允许等于5；另外判断是否恰为5，输出两个布尔值。',
        '''weight = 5
accepted = 0 < weight <= 5
at_limit = weight == 5
print(accepted, at_limit)''','True True\n',
        ['将小于写成小于等于会放行不该接受的端点','布尔值不是字符串"True"，后续判断含义不同'],
        '区间比较的重点是端点是否包含；边界测试比随便选中间值有效。',
        ('interval','26可以通过，26.1为什么不行？','包含端点的闭区间与外部值',[('左端','18 ✓'),('内部','18至26'),('右端','26 ✓；26.1 ×')]),
        [case('刚超上界','assert not comfortable and not at_upper',replacements=[('temperature = 26','temperature = 26.1')],output='False False\n'),case('零重量拒绝','assert not accepted',field='solution',replacements=[('weight = 5','weight = 0')],output='False False\n')])
    add(t,'l08','advanced','比较的对象与近似数值',
        ['识别字符串比较是字典序','采用容差检查浮点结果'],
        '比较表达式是否正确，先看两边是什么类型。字符串"10"小于"2"，因为首个不同字符1排在2之前；数值10则大于2。另一类问题来自二进制浮点表示：0.1+0.2通常不与0.3精确相等。对于测量值，可以检查绝对差是否不超过约定容差；容差应来自业务精度，不是随意加大到所有错误都通过。货币等精确十进制需求将在Decimal课处理。本例并排展示两类比较陷阱，练习明确采用绝对误差阈值。',
        ['先比较原始文本，再比较转换后的整数','查看浮点差值而非只看短格式显示','用正负差都能覆盖的绝对值'],
        '''left = "10"
right = "2"
value = 0.1 + 0.2
close = abs(value - 0.3) <= 0.000001
print(left < right, int(left) < int(right))
print(value == 0.3, close)''','True False\nFalse True\n',
        '测得长度9.9998，目标10，容许绝对误差0.001。输出是否合格；同时保留实际误差，防止只检查“小于目标”的单侧错误。',
        '''measured = 9.9998
target = 10
tolerance = 0.001
error = abs(measured - target)
qualified = error <= tolerance
print(qualified)''','True\n',
        ['直接比较数字文本会按字符顺序判断','只用measured-target<=容差会放过很大的负误差'],
        '正确比较依赖类型和误差模型，显示相同并不保证内部精确相同。',
        ('comparison','显示都像0.3时，为什么还要检查差值？','文本序与数值序、精确相等与容差的对照',[('文本','"10" < "2"'),('数字','10 > 2'),('浮点','差约5.55e-17 < 1e-6')]),
        [case('相同数字文本','assert not (left < right)',replacements=[('right = "2"','right = "10"')],output='False False\nFalse True\n'),case('负方向大偏差','assert not qualified and error>1',field='solution',replacements=[('measured = 9.9998','measured = 8')],output='False\n')])
    add(t,'l09','intermediate','短路保护：先确认能算，再计算',
        ['利用and保护可能失败的除法','分辨and与or不同的停止条件'],
        'and会在左侧为假时停止，or会在左侧为真时停止。这不仅节省计算，也能为右侧建立前提。例如只有count非零才能计算total/count，因此count!=0必须写在除法前。本例又要求有数据且平均值达标才算通过，空数据直接得到False。交换两部分顺序虽然逻辑描述看起来相近，却会先执行除零而出错。短路保护应保持简洁，不能把许多有副作用的操作藏进一个长表达式，让读者猜哪一步发生。',
        ['左侧先建立分母非零的前提','只在有数据时求平均','测试空数据确认右侧被跳过'],
        '''total = 160
count = 2
passed = count != 0 and total / count >= 75
print(passed)''','True\n',
        '判断一个文件名文本是否非空且以.py结尾；大小写敏感。空文本应直接返回False，输出真正布尔值。',
        '''filename = "main.py"
is_python = filename != "" and filename.endswith(".py")
print(is_python)''','True\n',
        ['把除法放在保护条件之前仍会除零','and/or会返回操作数，想要布尔结果需让操作数是比较结果'],
        '先判断安全前提，再执行依赖这个前提的操作，表达式才有正确执行顺序。',
        ('short-circuit','count为0时，箭头为什么不能走向除法？','短路把空数据引向False并跳过除法',[('前提','count!=0'),('为真','160/2>=75 → True'),('为假','直接False，除法不执行')]),
        [case('空数据免除零','assert passed is False',replacements=[('count = 2','count = 0')],output='False\n'),case('空文件名','assert is_python is False',field='solution',replacements=[('filename = "main.py"','filename = ""')],output='False\n')])
    add(t,'l09','advanced','逻辑重构：括号、德摩根与默认值',
        ['用德摩根规律表达拒绝条件','避免把合法零值误当缺失值'],
        '“不满足A或B”容易在自然语言里含混，代码应明确写成not(A or B)，等价于not A and not B。本例用两个拒绝条件推导是否允许发布，核对两种写法应一致。另外，or常被用作默认值，但0、空串也是假值；若0代表合法的免费价格，price or 10就错误地收费10。缺失值要与业务上的零区分，后续None和条件表达式课程会给出更多写法。本层先通过比较和逻辑表达式，展示如何清楚声明“合法零值”的约定。',
        ['把每个拒绝条件单独命名','比较两种等价写法的结果','验证免费价格不会被默认逻辑替换'],
        '''blocked = False
expired = True
allowed_a = not (blocked or expired)
allowed_b = not blocked and not expired
price = 0
free = price == 0
print(allowed_a, allowed_b)
print("免费", free)''','False False\n免费 True\n',
        '活动要求已报名且未取消；拒绝条件是未报名或已取消。分别用正向与反向逻辑计算可参加，并验证两者一致。',
        '''registered = True
cancelled = False
eligible = registered and not cancelled
rejected = not registered or cancelled
print(eligible, not rejected)''','True True\n',
        ['省略括号可能让not只作用于左侧一项','将or默认值用于合法0，会丢失业务信息'],
        '逻辑重构要保持真值等价，同时尊重缺失值与合法假值的差别。',
        ('logic','任何一个拒绝条件为真，为什么都应禁止发布？','或门收集拒绝条件，再通过not反转',[('阻止','False'),('过期','True'),('拒绝或','True → 允许False')]),
        [case('无拒绝条件','assert allowed_a==allowed_b==True',replacements=[('expired = True','expired = False')],output='True True\n免费 True\n'),case('取消优先拒绝','assert not eligible and rejected',field='solution',replacements=[('cancelled = False','cancelled = True')],output='False False\n')])
    add(t,'l10','intermediate','分支顺序：先处理不合法值',
        ['按校验与分类两阶段组织分支','处理范围外数据而不误分类'],
        '如果直接写score>=90，150也会被标成优秀。因此先拒绝范围外值，再在有效区间里按高到低分类。elif只会在前面条件均不成立时判断，这意味着后续分支可以利用已经排除的范围，例如score>=60时已知它小于90。分支顺序就是程序对条件的优先级约定，不同顺序可能改变重叠区域的结果。本例把不合法数据、优秀、及格、待提高四种结果完整覆盖，练习还要求处理免运费门槛与非法金额。',
        ['先排除小于0或大于100','有效分数按高到低分类','让else覆盖剩余的有效低分'],
        '''score = 90
if score < 0 or score > 100:
    result = "非法"
elif score >= 90:
    result = "优秀"
elif score >= 60:
    result = "及格"
else:
    result = "待提高"
print(result)''','优秀\n',
        '订单金额非负；满99免邮，其余收8元邮费，负金额输出非法且不计算总价。按校验、定邮费、展示的顺序实现。',
        '''amount = 99
if amount < 0:
    print("非法")
else:
    if amount >= 99:
        shipping = 0
    else:
        shipping = 8
    print("应付", amount + shipping)''','应付 99\n',
        ['在范围校验前分类会放过150这样的输入','先写>=60会截走本应优秀的分数'],
        '分支先校验范围，再按业务优先级分类，边界才不会被误吞。',
        ('decision','150分会先走哪一条路？','范围校验在等级分类之前',[('范围外','<0或>100 → 非法'),('有效高分','>=90 → 优秀'),('其余','>=60及格，否则待提高')]),
        [case('范围外高分','assert result=="非法"',replacements=[('score = 90','score = 150')],output='非法\n'),case('门槛下一元','assert shipping==8',field='solution',replacements=[('amount = 99','amount = 98')],output='应付 106\n')])
    add(t,'l10','advanced','分段计费：别把整段费率套给全部',
        ['实现累计分段而非整量跳价','在断点验证连续性与边界'],
        '分段计费有两种不同规则：“超过10件全部按另一单价”和“前10件按原价，超出部分按另一单价”。自然语言如果没写清，程序可能实现错规则。本例明确采用累计分段：前10度每度2元，之后每度3元。超过门槛时只对超出部分使用3元，原来的20元保留。验证断点9、10、11时应分别得到18、20、23，不应在11突然把全部11度乘3。练习改为三级累计费用，要求每个分支都表达之前段落的固定累计值。',
        ['明确门槛内累计费用20','超出量只取units-10','比较门槛前后费用是否按增量变化'],
        '''units = 12
if units < 0:
    fee = None
elif units <= 10:
    fee = units * 2
else:
    fee = 20 + (units - 10) * 3
print(fee)''','26\n',
        '累计运费：重量0至1千克收5元，超过1至3的部分每千克2元，再超过3的部分每千克4元。负重非法；用4千克演示，结果13元。',
        '''weight = 4
if weight < 0:
    fee = None
elif weight <= 1:
    fee = 5
elif weight <= 3:
    fee = 5 + (weight - 1) * 2
else:
    fee = 9 + (weight - 3) * 4
print(fee)''','13\n',
        ['超门槛后把全部用量乘新价会错误跳涨','前一段累计金额漏加会让费用在门槛处倒退'],
        '先把分段规则画成增量，再让每个分支保留已经累计的费用。',
        ('piecewise','第11度应该增加2元还是3元？','累计分段保留前段并只计算超出量',[('前10度','10×2=20'),('新增2度','2×3=6'),('合计','26')]),
        [case('断点后一格','assert fee==23',replacements=[('units = 12','units = 11')],output='23\n'),case('第二断点','assert fee==9',field='solution',replacements=[('weight = 4','weight = 3')],output='9\n')])
    add(t,'l11','intermediate','一次遍历维护多个统计量',
        ['同时计数与累计而不重复扫描','在空数据上保留正确初值'],
        '遍历每个字符时，可以同时维护多个互不混淆的累计状态。本例统计字母a的次数以及所有数字字符的数值之和。初始化必须放在循环外，否则每轮都会清零。数字判断只约定ASCII字符0至9，避免把某些看起来像数字但不能按本规则转换的字符混进来。空字符串会让循环体执行零次，因此计数0、总和0应仍是合理结果。这种“读一项，更新几个统计量”的模式比先建立许多临时列表更直接，也为后续流式文件处理打基础。',
        ['循环前创建独立计数与累计状态','每个字符分别判断属于哪种统计','空输入不执行循环仍能输出初值'],
        '''text = "a2b3a0"
letters = 0
digit_sum = 0
for ch in text:
    if ch == "a":
        letters += 1
    if "0" <= ch <= "9":
        digit_sum += int(ch)
print(letters, digit_sum)''','2 5\n',
        '扫描aaB123C：统计小写字母数、大写字母数和ASCII数字个数，一次循环完成，空文本应全0。',
        '''text = "aaB123C"
lower = upper = digits = 0
for ch in text:
    if "a" <= ch <= "z":
        lower += 1
    elif "A" <= ch <= "Z":
        upper += 1
    elif "0" <= ch <= "9":
        digits += 1
print(lower, upper, digits)''','2 2 3\n',
        ['将累计变量放入循环会只剩最后一轮结果','两个独立统计不能误用elif来互斥必要更新'],
        '遍历中的状态各有含义，初值决定零次循环是否仍有正确结果。',
        ('accumulators','扫描到最后一个a时，哪一个状态会改变？','每个字符分别更新计数或数字和',[('a2','letters1 sum2'),('b3','letters1 sum5'),('a0','letters2 sum5')]),
        [case('空扫描','assert letters==digit_sum==0',replacements=[('text = "a2b3a0"','text = ""')],output='0 0\n'),case('非ASCII忽略','assert (lower,upper,digits)==(0,0,1)',field='solution',replacements=[('text = "aaB123C"','text = "中９4"')],output='0 0 1\n')])
    add(t,'l11','advanced','连续段状态：从计数到运行长度',
        ['维护当前连续长度与历史最大长度','遇到分隔项时正确重置局部状态'],
        '统计一共有几个1不能回答最长连续多少个1。为此需要current记录截至当前项的连续段长度，best保存已见最大值。遇到1时current加一，并尝试刷新best；遇到0则只清零current，不清零best。这个区分是状态设计的关键：局部状态会随分段重置，全局最优值应跨段保留。末尾恰好是一段连续1也不需要额外补算，因为每次增长都已更新best。练习把相同思想用于最长无空格词段，仍只需一次扫描和固定数量变量。',
        ['为当前段与历史最优分别建变量','只在段中增长时更新最大值','用末尾连续段验证无需额外结算'],
        '''text = "11011101"
current = best = 0
for ch in text:
    if ch == "1":
        current += 1
        if current > best:
            best = current
    else:
        current = 0
print(best)''','3\n',
        '扫描red blue sky，计算以空格分段的最长连续非空格长度。多个空格只是重复分隔，不生成负数或特殊长度。',
        '''text = "red blue sky"
current = longest = 0
for ch in text:
    if ch != " ":
        current += 1
        if current > longest:
            longest = current
    else:
        current = 0
print(longest)''','4\n',
        ['遇到0时把best也清零会丢掉历史最优','只在遇分隔符时结算会漏掉末尾段'],
        '局部连续状态与全局最优状态分离，可用固定空间完成连续段分析。',
        ('state-scan','遇到0时，为什么best仍要保留3？','current随断点归零而best保留历史',[('11','current2 best2'),('0','current0 best2'),('111','current3 best3')]),
        [case('末尾为最长段','assert best==4',replacements=[('text = "11011101"','text = "001111"')],output='4\n'),case('重复分隔与空文本','assert longest==0',field='solution',replacements=[('text = "red blue sky"','text = "   "')],output='0\n')])
    add(t,'l12','intermediate','索引区间与逆向扫描',
        ['把左闭右开区间对应到range','推演负步长停止边界'],
        'range(start,stop,step)不包含stop。正步长要求当前值仍小于stop，负步长则要求当前值仍大于stop。逆序处理索引时，要从len(text)-1开始，并以-1作为不包含的终点，这样0才能被访问。把终点误写为0会漏掉第一个字符；从len(text)开始则立即越界。本例用数字索引重建逆序字符串，练习再采用固定间距抽样。遇到空字符串时，起点为-1，range(-1,-1,-1)自然为空，不需要额外补丁。',
        ['从最后一个有效索引开始','用-1作排除终点确保包含0','每次向左一步并拼接当前字符'],
        '''text = "PYTHON"
reversed_text = ""
for index in range(len(text) - 1, -1, -1):
    reversed_text += text[index]
print(reversed_text)''','NOHTYP\n',
        '从字符串ABCDEFG的索引0开始每隔两位取一个字符，用range和下标得到ACEG；空文本仍输出空行。',
        '''text = "ABCDEFG"
sample = ""
for index in range(0, len(text), 2):
    sample += text[index]
print(sample)''','ACEG\n',
        ['负步长终点仍不包含，stop=0会漏首项','len(text)不是最后索引，最后索引需减1'],
        '索引扫描先写出第一个、最后一个应访问的位置，再选择排除终点。',
        ('index-path','逆序扫描怎样确保索引0也被访问？','索引从5走到0，-1只是排除终点',[('索引','5 4 3 2 1 0'),('字符','N O H T Y P'),('停止','不访问-1')]),
        [case('空字符串','assert reversed_text==""',replacements=[('text = "PYTHON"','text = ""')],output='\n'),case('单字符抽样','assert sample=="Z"',field='solution',replacements=[('text = "ABCDEFG"','text = "Z"')],output='Z\n')])
    add(t,'l12','advanced','区间分块：尾块不能越过总量',
        ['从range生成批次起点','为不足一个批次的尾部收紧终点'],
        '批量任务通常按固定大小处理，但总量不一定整除批次大小。range(0,total,batch)给出每个批次的起点，终点应取start+batch与total中的较小者，防止最后一批声称包含不存在的数据。本例采用左闭右开区间，长度直接等于end-start，相邻批次上一段end与下一段start相同，既不重叠也不留缝。练习要求累计所有批次长度，使用总量守恒检查分块是否完整，而不是只看打印出的区间似乎合理。',
        ['以0、4、8作为批次起点','每个终点限制在总量10内','累计长度验证所有数据恰覆盖一次'],
        '''total = 10
batch = 4
covered = 0
for start in range(0, total, batch):
    end = min(start + batch, total)
    covered += end - start
    print(start, end)
print("覆盖", covered)''','0 4\n4 8\n8 10\n覆盖 10\n',
        '把23页按每组7页分配，输出人读的1至7、8至14、15至21、22至23，并累计分配页数；内部仍使用零起点左闭右开区间。',
        '''pages = 23
size = 7
assigned = 0
for start in range(0, pages, size):
    end = min(start + size, pages)
    assigned += end - start
    print(f"{start + 1}至{end}")
print("共", assigned)''','1至7\n8至14\n15至21\n22至23\n共 23\n',
        ['尾块直接用start+batch会越过数据末端','同时把起终点都加1会让展示多出一页'],
        '内部使用统一的半开区间，尾部截断与总量核对让分批处理可靠。',
        ('chunks','最后一批为什么只有2项？','批次区间无缝覆盖0至10且尾块截断',[('第一批','[0,4) 4项'),('第二批','[4,8) 4项'),('尾批','[8,10) 2项')]),
        [case('整除批次','assert covered==8',replacements=[('total = 10','total = 8')],output='0 4\n4 8\n覆盖 8\n'),case('空页不分配','assert assigned==0',field='solution',replacements=[('pages = 23','pages = 0')],output='共 0\n')])
    add(t,'l13','intermediate','while维护余量与终止量',
        ['让每轮循环向终止条件推进','处理最后一轮不足标准量的情况'],
        'while适合次数取决于状态的过程，但必须能解释状态为何最终离开循环。本例每次最多搬4箱，剩余10箱时依次搬4、4、2。每轮从remaining里减去本轮实际搬运量，而不是固定减4，这样剩余不会变成负数。moves记录轮次，moved记录总量，两者不能混用。起始余量0时循环自然执行零次；初值和条件共同决定这个边界。练习用相同模式分期偿还整数金额，避免使用浮点货币掩盖本课状态问题。',
        ['先用min确定本轮实际处理量','余量严格减少，保证循环终止','总处理量与初始量进行核对'],
        '''remaining = 10
moved = 0
moves = 0
while remaining > 0:
    take = min(4, remaining)
    remaining -= take
    moved += take
    moves += 1
print(moved, moves, remaining)''','10 3 0\n',
        '欠款23元，每期最多还7元，打印每期实际还款，最后输出期数与剩余。用while完成，不允许最后一期多还。',
        '''debt = 23
periods = 0
while debt > 0:
    payment = min(7, debt)
    debt -= payment
    periods += 1
    print(payment)
print("期数", periods, "剩余", debt)''','7\n7\n7\n2\n期数 4 剩余 0\n',
        ['固定扣标准量会让最后余量为负','循环体未改变条件相关变量可能永不停止'],
        '为while找到单调减少的余量，并让每轮只处理实际可用量。',
        ('decreasing-state','最后一轮为什么只搬2箱？','余量由10单调下降至0',[('轮1','10→6 搬4'),('轮2','6→2 搬4'),('轮3','2→0 搬2')]),
        [case('零余量','assert (moved,moves,remaining)==(0,0,0)',replacements=[('remaining = 10','remaining = 0')],output='0 0 0\n'),case('一期结清','assert periods==1 and debt==0',field='solution',replacements=[('debt = 23','debt = 5')],output='5\n期数 1 剩余 0\n')])
    add(t,'l13','advanced','欧几里得算法：用不变量证明循环',
        ['根据余数更新最大公约数状态','解释循环为什么既终止又保持答案'],
        '最大公约数不必枚举到最小数。对a、b求余后，gcd(a,b)等于gcd(b,a%b)：能整除原两数的数，也能整除余数；反过来也成立。因此每轮把(a,b)换成(b,余数)，答案不变，而非负余数严格小于原来的b，保证最终到0。本例先取绝对值以统一负数输入，约定gcd(0,0)=0，与Python标准库一致。先用临时变量写清更新顺序，避免a被覆盖后再求余得到错误结果；练习用求出的公约数约分。',
        ['用abs把输入归一到非负','求余之前保存当前两数关系','b归零时a保留最大公约数'],
        '''a = abs(48)
b = abs(18)
steps = 0
while b != 0:
    remainder = a % b
    a = b
    b = remainder
    steps += 1
print("公约数", a, "步数", steps)''','公约数 6 步数 3\n',
        '将分数42/56约分，分母约定为正。复用余数循环求公约数，再用整除输出3/4；不要直接导入math.gcd代替算法。',
        '''numerator = 42
denominator = 56
a = abs(numerator)
b = denominator
while b:
    remainder = a % b
    a = b
    b = remainder
print(f"{numerator // a}/{denominator // a}")''','3/4\n',
        ['先覆盖a再计算a%b会改变本轮输入','约分前不规定零分母会让问题本身无定义'],
        '不变量证明答案被保留，递减量证明程序会结束，两者缺一不可。',
        ('algorithm-state','为什么余数变小仍保留同一个公约数？','每轮二元状态与不变的gcd',[('开始','(48,18) gcd6'),('迭代','(18,12) → (12,6)'),('结束','(6,0) 答案6')]),
        [case('零与非零','assert a==18 and steps==1',replacements=[('abs(48)','abs(0)')],output='公约数 18 步数 1\n'),case('零分子约分','assert a==56',field='solution',replacements=[('numerator = 42','numerator = 0')],output='0/1\n')])
    add(t,'l14','intermediate','搜索结果：找到与遍历完是两条路径',
        ['用循环else表达未找到','区分continue跳过与break终止'],
        '循环后的else只在循环没有通过break退出时执行，包含一次也没迭代的情况。它并不与内层if配对。本例跳过负数，再找第一个能被4整除的非负整数；找到即break，后面的元素不再检查。若所有候选都不满足，或输入为空，else输出没有候选。将“未找到”写成循环else能少维护一个标记，但缩进必须准确。练习把同样控制流用于字符串扫描，特别检查0是否作为合法命中而非被误当假值。',
        ['负数走continue，不参与整除判断','第一次命中后break终止搜索','只在自然耗尽时执行else'],
        '''values = [-4, 3, 8, 12]
for value in values:
    if value < 0:
        continue
    if value % 4 == 0:
        print("找到", value)
        break
else:
    print("未找到")''','找到 8\n',
        '扫描文本a-30b，跳过非ASCII数字，找到第一个数值为0的字符时打印“零”；未找到打印“无零”。',
        '''text = "a-30b"
for ch in text:
    if not ("0" <= ch <= "9"):
        continue
    if int(ch) == 0:
        print("零")
        break
else:
    print("无零")''','零\n',
        ['循环else缩进到if下会改变含义','continue只跳本轮，不表示搜索已经成功'],
        '搜索有命中提前终止与自然耗尽两条路径，两者都要验证。',
        ('search-path','最后的12为什么不会再被检查？','跳过负数后在第一个命中8处终止',[('负数-4','continue'),('3','不命中继续'),('8','命中break；不访问12')]),
        [case('空候选自然耗尽','',replacements=[('values = [-4, 3, 8, 12]','values = []')],output='未找到\n'),case('无零耗尽','',field='solution',replacements=[('text = "a-30b"','text = "abc123"')],output='无零\n')])
    add(t,'l14','advanced','素数判断：提前停止必须有理由',
        ['用平方根边界减少候选因子','正确处理小于2与完全平方数'],
        '若n有非平凡因子，其中至少有一个不大于平方根；否则两个因子的乘积会大于n。因此检查d*d<=n即可，无需算浮点平方根。本例先拒绝小于2，再用while依次试除，命中因子后break；自然结束的else说明没有因子。边界中的等号不能省，否则49会漏检7。练习扩展为统计区间中的素数，但不要在内层发现因子时误以为break能跳出所有层：它只结束最近的一层循环。',
        ['先处理1、0和负数这些定义外值','因子上界包含平方根本身','用循环else区分找到因子与全部试完'],
        '''n = 49
if n < 2:
    print("非素数")
else:
    divisor = 2
    while divisor * divisor <= n:
        if n % divisor == 0:
            print("非素数", divisor)
            break
        divisor += 1
    else:
        print("素数")''','非素数 7\n',
        '统计2至20（含20）的素数个数，使用试除与break，输出8；每个新候选必须重置它的状态。',
        '''count = 0
limit = 20
for n in range(2, limit + 1):
    prime = True
    divisor = 2
    while divisor * divisor <= n:
        if n % divisor == 0:
            prime = False
            break
        divisor += 1
    if prime:
        count += 1
print(count)''','8\n',
        ['用d*d<n会漏掉完全平方数的平方根因子','内层break只能退出试除循环，不能替代候选状态'],
        '提前停止应来自数学证据，完全平方数是验证上界的重要案例。',
        ('factor-search','49的因子7为何必须被试到？','因子配对使检查范围收缩到平方根',[('候选','2 3 4 5 6'),('边界','7×7=49，必须含等号'),('命中','因子7 → break')]),
        [case('最小素数','',replacements=[('n = 49','n = 2')],output='素数\n'),case('区间不足2','assert count==0',field='solution',replacements=[('limit = 20','limit = 1')],output='0\n')])
    add(t,'l15','intermediate','二维坐标与条件组合',
        ['明确外层行与内层列的对应关系','按坐标条件选取而不手写每个格子'],
        '嵌套循环不是把两个循环随意叠在一起，而是枚举坐标对：外层选定一行，内层遍历该行所有列。本例输出3乘4网格中的边框，判断条件为第一行、最后一行、第一列或最后一列。每个坐标恰好判断一次，角落虽然同时满足两个条件仍只输出一个符号。使用end为空把同一行连起来，内层结束后再换行。练习绘制对角线，要求用行列关系判断而非写死图案，方形大小改变时仍成立。',
        ['外层只负责当前行号','内层逐列判断是否位于边界','内层结束后只换一次行'],
        '''rows = 3
columns = 4
for row in range(rows):
    for col in range(columns):
        if row == 0 or row == rows-1 or col == 0 or col == columns-1:
            print("#", end="")
        else:
            print(".", end="")
    print()''','####\n#..#\n####\n',
        '绘制大小4的双对角线：row==col或row+col==size-1的位置输出X，其余输出点；每行正好4字符。',
        '''size = 4
for row in range(size):
    for col in range(size):
        if row == col or row + col == size - 1:
            print("X", end="")
        else:
            print(".", end="")
    print()''','X..X\n.XX.\n.XX.\nX..X\n',
        ['把换行放在内层会每格独占一行','角落条件用多个独立print会重复画格子'],
        '网格问题先建立坐标关系，再让每个坐标生成恰好一个输出。',
        ('grid','角落同时满足行边界和列边界，为什么只画一个#？','3乘4网格的边界判断与单次输出',[('第一行','####'),('中间行','#..#'),('最后行','####')]),
        [case('单行全为边界','',replacements=[('rows = 3','rows = 1')],output='####\n'),case('单格双对角','',field='solution',replacements=[('size = 4','size = 1')],output='X\n')])
    add(t,'l15','advanced','组合搜索：约束越早检查越省工作',
        ['枚举组合并排除重复排列','把约束放在足够信息已经可知的位置'],
        '从1至5选两个不同数，(1,3)和(3,1)代表同一组合时，就不该两次计数。让第二层从a+1开始，可直接保证a<b，不必先生成再去重。本例进一步要求和为6，得到(1,5)、(2,4)。这种通过循环范围排除无效状态的方法叫约束剪枝：不是运行更快的魔法，而是减少根本不需要检查的候选。练习从三种面额组合出固定总额，并限制硬币总个数；应明确每层代表一种数量，避免把排列误当不同方案。',
        ['内层从a+1起排除相同数和对称重复','只对剩余组合检查和','累计结果个数与打印方案对照'],
        '''limit = 5
target = 6
count = 0
for a in range(1, limit + 1):
    for b in range(a + 1, limit + 1):
        if a + b == target:
            count += 1
            print(a, b)
print("方案", count)''','1 5\n2 4\n方案 2\n',
        '用1元与2元硬币凑6元，硬币总数不超过4。枚举两种硬币数量，输出合法数量对和方案数（2个1元+2个2元；0个1元+3个2元）。',
        '''amount = 6
count = 0
for twos in range(amount // 2 + 1):
    ones = amount - 2 * twos
    if ones + twos <= 4:
        print(ones, twos)
        count += 1
print("方案", count)''','2 2\n0 3\n方案 2\n',
        ['从1开始两层全遍历会把反序组合重复计数','约束过晚才检查会生成大量必然无效候选'],
        '先定义一个方案是什么，再设计范围以避免重复，并尽早消除无效状态。',
        ('constraint-space','为什么不需要再枚举5和1？','上三角候选空间消除对称排列',[('范围','a<b'),('和6','(1,5)、(2,4)'),('排除','(3,3)相同；(5,1)重复')]),
        [case('无解目标','assert count==0',replacements=[('target = 6','target = 20')],output='方案 0\n'),case('零金额唯一空方案','assert count==1',field='solution',replacements=[('amount = 6','amount = 0')],output='0 0\n方案 1\n')])
    add(t,'l16','intermediate','追踪表：定位第一次偏离',
        ['逐轮列出更新前后值','用最终结果之外的证据调试累计错误'],
        '调试不应只盯着最后一个错误数字。把每轮输入、更新前状态、更新后状态打印出来，可以找到第一次偏离预期的地方。本例计算1至4的累计和，before在更新前保存当前total，日志形成三列证据。如果total在循环内被初始化，第一轮可能正确，第二轮就会首次偏离；追踪表比随机修改缩进更可靠。练习跟踪余额变化，验证每一项调整只应用一次，并保留开始余额，最后用“起始加调整总和”独立核对。',
        ['更新前保存before而非事后复制','每轮打印输入、旧值、新值','从最早不一致行反查对应更新'],
        '''total = 0
for number in range(1, 5):
    before = total
    total += number
    print(number, before, total)
print("结果", total)''','1 0 1\n2 1 3\n3 3 6\n4 6 10\n结果 10\n',
        '初始余额100，依次调整20、-15、-5。输出每轮旧余额、调整、新余额，再输出最终余额；不能只把最终100打印出来。',
        '''balance = 100
for change in [20, -15, -5]:
    before = balance
    balance += change
    print(before, change, balance)
print("余额", balance)''','100 20 120\n120 -15 105\n105 -5 100\n余额 100\n',
        ['更新后再保存before会让追踪表两列相同','只测最终值会漏掉中间错误相互抵消的情况'],
        '追踪表记录状态转移，第一次偏离通常最接近真正的错误来源。',
        ('trace-table','第二轮更新前为什么必须是1？','逐轮累计的前值输入后值三列表',[('轮1','0 + 1 → 1'),('轮2','1 + 2 → 3'),('轮3-4','3+3→6；6+4→10')]),
        [case('零轮边界','assert total==0',replacements=[('range(1, 5)','range(1, 1)')],output='结果 0\n'),case('单笔归零','assert balance==0',field='solution',replacements=[('[20, -15, -5]','[-100]')],output='100 -100 0\n余额 0\n')])
    add(t,'l16','advanced','最小反例与独立验算',
        ['从失败数据缩小到最小反例','用不同方法核对循环结果'],
        '一个错误程序在1、2、3上可能恰好正确，因此测试不应只堆更多类似输入。求平均时若每轮把total除以count，结果就不再是总和；用只有两项且值差异明显的数据最容易揭示它。正确程序先完整累计，再只除一次，并对空数据给出明确结果。本例保留循环结果，又用内置sum独立验算；这不是证明所有程序正确，却能检查当前数据的累计有没有偏离。练习检查最大值初值，使用全负数组构成反例，不能用0冒充数据中的最大值。',
        ['累计阶段只做求和和计数','循环后处理空数据再求平均','最大值从首项初始化，避免假造0'],
        '''values = [2, 10]
total = 0
count = 0
for value in values:
    total += value
    count += 1
average = total / count if count else None
print(average)
print("核对", total == sum(values))''','6.0\n核对 True\n',
        '求[-8,-3,-11]最大值，空列表输出None。不得以0初始化，也不得直接用max替代遍历；增加全负数边界解释。',
        '''values = [-8, -3, -11]
largest = None
for value in values:
    if largest is None or value > largest:
        largest = value
print(largest)''','-3\n',
        ['全负数场景把最大值初始化0会返回不存在的值','每轮求平均会改变累计状态含义'],
        '选择能击破错误假设的反例，并用独立计算检查状态是否符合定义。',
        ('counterexample','为什么全负数是最大值算法的重要反例？','错误初值0与来自真实数据的初值对照',[('数据','-8 -3 -11'),('错误0起点','会保留不存在的0'),('正确状态','None → -8 → -3 → -3')]),
        [case('空平均','assert average is None and total==0',replacements=[('values = [2, 10]','values = []')],output='None\n核对 True\n'),case('单个负数','assert largest==-12',field='solution',replacements=[('values = [-8, -3, -11]','values = [-12]')],output='-12\n')])
