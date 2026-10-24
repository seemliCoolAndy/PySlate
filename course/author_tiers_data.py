"""Text, containers, functions, modules and file lessons: original tier content."""
from tier_helpers import add, case

def populate(t):
    add(t,'l17','intermediate','清洗有顺序：把名单规范化', ['组合strip、split和join','解释连续空白与空字段的差别'],
        '清洗文本不是无脑删除所有空格。人的姓名内部可能需要空格，因此本例只规范首尾及连续空白：不带参数的split会合并连续空白，并忽略两端空白，再用单个空格join。lower只改变大小写，不会改动原字符串；每一步都返回新字符串，所以应接住返回值。带明确分隔符的split(",")则保留空字段，适用于需要诊断缺列的简单记录。真正带引号逗号的CSV不能用本课办法解析，后续会交给csv模块。',
        ['先拆分空白得到有效词段','统一大小写后重新连接','保留清洗前后两份文本作核对'],
        '''raw = "  Ada   LOVELACE  "
parts = raw.split()
normalized = " ".join(parts).lower()
print(normalized)
print(len(parts))''','ada lovelace\n2\n',
        '简单标签串为“ red, ,BLUE,red ”，按逗号拆分，去首尾空白并转小写，忽略空字段但保留重复，最后以竖线连接。',
        '''raw = " red, ,BLUE,red "
tags = []
for part in raw.split(","):
    tag = part.strip().lower()
    if tag:
        tags.append(tag)
print("|".join(tags))''','red|blue|red\n',
        ['忽略方法返回值时原字符串并没有变化','split()和split(" ")遇到连续空格时结果不同'], '规范化步骤有顺序；先约定哪些空白有意义，再决定删除或保留。',
        ('text-pipeline','三个连续空格为什么最终只剩一个？','原始文本经分词再连接的结构变化',[('原文','空格 Ada 三空格 LOVELACE'),('分词','[Ada, LOVELACE]'),('连接','ada lovelace')]),
        [case('纯空白名单','assert parts==[] and normalized==""',replacements=[('"  Ada   LOVELACE  "','"   "')],output='\n0\n'),case('连续空字段','assert tags==["x"]',field='solution',replacements=[('" red, ,BLUE,red "','",,X,,"')],output='x\n')])
    add(t,'l17','advanced','轻量解析器：只拆第一个等号', ['使用partition保留字段内分隔符','把格式错误与合法空值分开'],
        '配置行key=value可能在值中继续包含等号。split("=")不设上限会把一行拆成不确定数量的片段，难以保留原值；partition则始终返回前段、分隔符、后段三部分，且只拆第一次。分隔符为空说明没有等号，与key=表示的合法空值不同。本例忽略空白行和注释，要求键非空，并拒绝重复键，避免后面的配置悄悄覆盖前面。这个小格式没有转义或多行值，限制应明确写下，不能假称能解析任意配置文件。',
        ['strip后跳过空行和注释','partition只消费第一个等号','确认键非空且未出现，再保存原值'],
        '''def parse_config(lines):
    result = {}
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, marker, value = line.partition("=")
        key = key.strip()
        if not marker or not key or key in result:
            raise ValueError("配置格式或键重复")
        result[key] = value.strip()
    return result
config = parse_config(["# demo", "token=a=b", "note="])
print(config)''',"{'token': 'a=b', 'note': ''}\n",
        '把解析器改成支持冒号分隔的头字段，字段名转小写，值内冒号要保留，重复字段应拒绝；用Host: local和Time: 12:30演示。',
        '''def parse_headers(lines):
    result = {}
    for line in lines:
        key, marker, value = line.partition(":")
        key = key.strip().lower()
        if not marker or not key or key in result:
            raise ValueError("头字段无效或重复")
        result[key] = value.strip()
    return result
headers = parse_headers(["Host: local", "Time: 12:30"])
print(headers)''',"{'host': 'local', 'time': '12:30'}\n",
        ['把空值与缺少分隔符混为一谈会拒绝合法note=','重复键直接覆盖会掩盖配置冲突'], '解析先约定语法与冲突策略，再选择只消费必要分隔符的操作。',
        ('parser','token=a=b中的第二个等号属于哪一部分？','第一次分隔后值整体保留',[('原行','token=a=b'),('键与标记','token | ='),('值','a=b，不再拆分')]),
        [case('合法空值与值内等号','assert parse_config(["x=", "y=="])=={"x":"","y":"="}'),case('大小写冲突拒绝',"try:\n    parse_headers(['X: 1','x: 2'])\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('duplicate accepted')",field='solution')])
    add(t,'l18','intermediate','enumerate与zip：成对数据怎样对齐', ['通过enumerate产生展示序号','检查zip截断造成的信息遗漏'],
        '平行列表分别保存姓名与分数时，zip按位置配对；默认会在较短的一侧耗尽时停止，因此不等长可能悄悄漏掉尾部数据。Python3.11可使用zip(...,strict=True)拒绝长度不符，但这里先显式比较长度以给出业务错误。enumerate(...,start=1)只改变展示序号，不改变列表的零起点下标。本例把配对结果再编号，练习要求把商品与数量组合成记录，数据不齐时整体拒绝，不能拿一半报告冒充完整报告。',
        ['先验证两列长度一致','zip建立对应关系而非笛卡尔积','enumerate从1编号展示'],
        '''names = ["小禾", "阿青"]
scores = [80, 95]
if len(names) != len(scores):
    raise ValueError("姓名与分数不齐")
for number, (name, score) in enumerate(zip(names, scores), 1):
    print(number, name, score)''','1 小禾 80\n2 阿青 95\n',
        '实现pair_items(names,counts)，等长则返回(name,count)元组列表，不等长抛ValueError；不要自动补0或静默丢弃。',
        '''def pair_items(names, counts):
    if len(names) != len(counts):
        raise ValueError("商品与数量不齐")
    return list(zip(names, counts))
print(pair_items(["笔", "本"], [2, 3]))''',"[('笔', 2), ('本', 3)]\n",
        ['把enumerate的展示序号拿去当下标会偏移一位','zip默认截断并不代表两列已经对齐'], '配对前检查完整性，展示序号和存储索引各司其职。',
        ('alignment','少一项成绩时，为什么不能直接信任zip的输出？','两列按位置配对而尾项可能被截断',[('姓名列','小禾 阿青'),('成绩列','80 95'),('对齐后','1小禾80；2阿青95')]),
        [case('空列表报告','',replacements=[('names = ["小禾", "阿青"]','names = []'),('scores = [80, 95]','scores = []')],output=''),case('不齐拒绝',"try:\n    pair_items(['笔'], [])\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('truncated')",field='solution')])
    add(t,'l18','advanced','稳定去重：列表既保顺序也能去重复', ['依据首次出现保留顺序','比较成员检查和直接索引的用途'],
        '去重不只关心还剩哪些值，有时还必须保留首次出现顺序。尚未学习集合也可以用列表完成：顺序遍历输入，只在item不在result中时追加。原列表保持不变，输出由新的容器构成。这个方法容易理解，但每次in可能扫描已有结果，最坏比较次数接近平方增长；后面的集合课会优化成员检查。本例区分“重复值”与“相邻重复”，练习要求压缩相邻重复但保留远处再次出现的值，两个需求不能混用同一算法。',
        ['从空结果开始顺序扫描','成员已在结果时不追加','练习只比较上一项，保留非相邻再现'],
        '''def unique_first(values):
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return result
values = ["A", "B", "A", "C", "B"]
print(unique_first(values))''',"['A', 'B', 'C']\n",
        '实现compress_runs，把A,A,B,A,A压缩为A,B,A；空列表返回空列表，不修改输入。',
        '''def compress_runs(values):
    result = []
    for value in values:
        if not result or value != result[-1]:
            result.append(value)
    return result
print(compress_runs(["A", "A", "B", "A", "A"]))''',"['A', 'B', 'A']\n",
        ['set式全局去重不能代替相邻段压缩','删除原列表中的元素可能改变后续遍历位置'], '先定义重复的范围，再选择维护全局已见值还是前一项。',
        ('sequence','末尾的A为什么在压缩后仍保留？','全局去重与相邻段压缩的不同结果',[('输入','A A B A A'),('全局首次','A B'),('相邻压缩','A B A')]),
        [case('空与全重复','assert unique_first([])==[] and unique_first([0,0,0])==[0]'),case('不改输入且保留再现','original=[1,1,2,1]\nassert compress_runs(original)==[1,2,1] and original==[1,1,2,1]',field='solution')])
    add(t,'l19','intermediate','批量删除：构建新列表比边走边删可靠', ['用筛选代替遍历时删除','区分原地更新与创建新结果'],
        '遍历列表时删除当前项，后续元素会左移，循环却继续前进，容易跳过相邻待删项。本例从原记录构建新的保留列表，只收集非负值，最后再决定是否替换原列表。这样遍历依据稳定，筛选逻辑也能逐项解释。若其他变量与原列表共享引用，直接把名字重新绑定到新列表不会修改旧对象；切片赋值items[:]=kept才会保留容器身份。练习明确要求原地清理，因此必须检查别名能否看到变化，而不是只看打印出的一个名字。',
        ['遍历期间不修改来源','新列表只收符合条件的项','原地需求用切片赋值替换内容'],
        '''values = [3, -1, -2, 0, 5]
kept = []
for value in values:
    if value >= 0:
        kept.append(value)
print(kept)
print(values)''','[3, 0, 5]\n[3, -1, -2, 0, 5]\n',
        '实现remove_blank_inplace，删除列表里空字符串或纯空白字符串，保留非空项的原始文本；别名必须观察到相同内容变化。',
        '''def remove_blank_inplace(items):
    kept = []
    for text in items:
        if text.strip():
            kept.append(text)
    items[:] = kept
items = ["a", "", " ", " b "]
alias = items
remove_blank_inplace(items)
print(items)
print(alias is items)''',"['a', ' b ']\nTrue\n",
        ['边遍历边remove会跳过连续待删项','items=kept只重绑局部名字，不能满足原地更新协议'], '先稳定筛选，再按是否需要保留对象身份选择重新绑定或切片赋值。',
        ('filter','连续的-1和-2为什么都不会被漏掉？','稳定来源进入全新保留容器',[('来源','3 -1 -2 0 5'),('逐项判断','保留 丢弃 丢弃 保留 保留'),('结果','3 0 5；来源不变')]),
        [case('连续全为负','assert kept==[] and len(values)==3',replacements=[('[3, -1, -2, 0, 5]','[-1,-2,-3]')],output='[]\n[-1, -2, -3]\n'),case('别名空清理','a=["", " "]\nb=a\nremove_blank_inplace(a)\nassert a==[] and b is a',field='solution')])
    add(t,'l19','advanced','有界历史记录：追加、淘汰与撤销', ['维护最多N项的容器不变量','为撤销设计可检查的历史栈'],
        '编辑器历史不应无限增长。新增一项后若长度超过容量，就从最旧的一侧删除多余部分，始终保持len(history)<=limit。撤销则从末尾pop得到最近操作，与淘汰最旧操作是相反的方向。容量必须为正，空历史的撤销不能盲目pop。这个简单实现采用列表，头部删除需要移动元素，后面的deque课程会讨论频繁队首操作。练习增加连续重复合并：只有相邻同样的快照省略，回到旧值仍是新事件。',
        ['追加后统一从前部删除超量项','从尾部弹出作为最近事件','把容量和空历史边界纳入接口约定'],
        '''def remember(history, item, limit):
    if limit <= 0:
        raise ValueError("容量必须为正")
    history.append(item)
    del history[:-limit]
history = []
for item in ["a", "b", "c", "d"]:
    remember(history, item, 3)
print(history)
print("撤销", history.pop())
print(history)''',"['b', 'c', 'd']\n撤销 d\n['b', 'c']\n",
        '实现push_snapshot，容量为正，忽略与最后一项相同的新快照，其余追加并淘汰最旧；演示A,A,B,A容量2得到B,A。',
        '''def push_snapshot(history, item, limit):
    if limit <= 0:
        raise ValueError("容量必须为正")
    if not history or history[-1] != item:
        history.append(item)
        del history[:-limit]
history = []
for item in ["A", "A", "B", "A"]:
    push_snapshot(history, item, 2)
print(history)''',"['B', 'A']\n",
        ['从头部pop会撤销最旧而非最近操作','忽略所有曾出现值会把真实的返回状态吞掉'], '容器应持续满足容量和顺序不变量，撤销与淘汰的方向必须分清。',
        ('history','容量3时加入d，应该丢a还是c？','队首淘汰与队尾撤销方向相反',[('加入前','a b c'),('加入d','b c d，淘汰a'),('撤销','弹d，留下b c')]),
        [case('容量1','h=[]\nremember(h,1,1)\nremember(h,2,1)\nassert h==[2]'),case('重复不淘汰','h=[1,2]\npush_snapshot(h,2,2)\nassert h==[1,2]',field='solution')])
    add(t,'l20','intermediate','浅复制仍共享里面的行', ['识别嵌套列表的共享引用','根据修改深度复制必要层次'],
        'matrix[:]会创建新的外层列表，但里面每个行列表仍是同一个对象。于是只修改copy[0][0]也会改变原矩阵。若行里只有整数，可用[row[:] for row in matrix]逐行复制，形成独立二维表；若再嵌套更深，仍要继续分析共享层次，不能说切片就是深复制。本例对比浅复制与逐行复制，并用is检查引用关系。练习修复常见的[[0]*columns]*rows陷阱，它重复的是同一行引用，不是多份独立行。',
        ['画出两个外层指向同一行的箭头','逐行切片生成独立行','修改一格后检查来源是否保持原值'],
        '''matrix = [[1, 2], [3, 4]]
shallow = matrix[:]
independent = [row[:] for row in matrix]
shallow[0][0] = 9
independent[1][1] = 8
print(matrix)
print(independent)
print(shallow[0] is matrix[0])''','[[9, 2], [3, 4]]\n[[1, 2], [3, 8]]\nTrue\n',
        '实现make_grid(rows,cols)创建独立的零矩阵。修改第一行一格不应影响第二行，允许零行或零列。',
        '''def make_grid(rows, cols):
    return [[0] * cols for _ in range(rows)]
grid = make_grid(2, 3)
grid[0][1] = 7
print(grid)''','[[0, 7, 0], [0, 0, 0]]\n',
        ['外层复制不能隔离内层可变对象','行列表乘法会重复引用，所有行一起变化'], '复制是否充分取决于修改会深入哪一层，画引用关系比背“复制”更可靠。',
        ('reference-graph','复制外层后，为什么改第一格仍改变原矩阵？','浅复制共享行，逐行复制拥有独立行',[('外层副本','新列表'),('浅层行','仍指向原行[1,2]'),('逐行副本','新行，修改互不影响')]),
        [case('复制层次证据','assert shallow is not matrix and shallow[0] is matrix[0] and independent[0] is not matrix[0]'),case('零维与独立行','assert make_grid(0,3)==[] and make_grid(2,0)==[[],[]]\ng=make_grid(2,1)\ng[0][0]=9\nassert g[1][0]==0',field='solution')])
    add(t,'l20','advanced','切片窗口与不可变快照', ['使用切片构造滑动窗口','明确快照何时不受后续编辑影响'],
        '滑动窗口是连续子序列，不是每隔几项抽样。长度n的数据取宽度k窗口时，起点为0至n-k，共n-k+1个；k大于n时结果为空，k<=0则应拒绝。每个values[start:start+k]会复制外层，使后续向原列表追加或替换数值不改变已有窗口。本课元素是整数，因此这已经足够；元素若为列表则仍有上一层的共享问题。练习要求取所有窗口的平均值，同时保证来源列表不被修改。',
        ['先校验窗口宽度为正','用n-k+1计算有效起点数','切片后再修改来源检查快照独立性'],
        '''def windows(values, width):
    if width <= 0:
        raise ValueError("窗口必须为正")
    return [values[i:i+width] for i in range(len(values)-width+1)]
values = [2, 4, 6, 8]
snapshots = windows(values, 3)
values[0] = 99
print(snapshots)
print(values)''','[[2, 4, 6], [4, 6, 8]]\n[99, 4, 6, 8]\n',
        '实现moving_average，宽度为正，窗口不足时不生成结果。使用连续切片计算，不修改输入，演示[2,4,6,8]宽2得到[3.0,5.0,7.0]。',
        '''def moving_average(values, width):
    if width <= 0:
        raise ValueError("窗口必须为正")
    return [sum(values[i:i+width])/width for i in range(len(values)-width+1)]
print(moving_average([2,4,6,8],2))''','[3.0, 5.0, 7.0]\n',
        ['起点少写+1会漏最后一个窗口','把step设成width会产生分块，不是滑动窗口'], '窗口边界由宽度推导，复制层次由快照隔离要求决定。',
        ('sliding-window','四个数取宽3，为什么只有两个窗口？','窗口每次右移一个位置且不越界',[('起点0','[2 4 6] 8'),('起点1','2 [4 6 8]'),('起点2','不足3，停止')]),
        [case('窗口大于数据','assert windows([1,2],3)==[] and windows([],1)==[]'),case('来源不修改与单元素窗口','x=[-2,4]\nassert moving_average(x,1)==[-2.0,4.0] and x==[-2,4]',field='solution')])
    add(t,'l21','intermediate','星号解包与记录接口', ['处理可变数量的中间字段','在解包前明确最少字段数'],
        '解包让数据结构直接对应变量角色。head,*middle,tail要求至少两项，中间多余项组成列表；只有两项时middle为空列表，而不是None。它适合格式稳定、部分长度可变的记录，例如首项是站名，末项是总计，中间是每日数量。但解包不会自动检查每项业务类型，不能因语法成功就认为数据有效。本例将首尾与中段分开处理，练习则返回首项、剩余列表和总项数，并明确空输入抛异常而不悄悄造默认值。',
        ['首尾字段各占一个固定位置','星号收集中间零项或多项','在函数边界写明最短长度'],
        '''record = ("A站", 3, 5, 8)
station, *daily, total = record
print(station, daily, total)
print(sum(daily) == total)''',"A站 [3, 5] 8\nTrue\n",
        '实现split_first(values)，非空时返回(first,rest,count)，rest是新列表；空输入抛ValueError。',
        '''def split_first(values):
    if not values:
        raise ValueError("至少一项")
    first, *rest = values
    return first, rest, len(values)
print(split_first((10,20,30)))''','(10, [20, 30], 3)\n',
        ['星号收集结果是列表，即便来源是元组','字段数量满足解包规则并不保证总计正确'], '解包建立清晰记录角色，数量和业务约束仍要分别校验。',
        ('unpacking','只有首尾两项时，中间变量是什么？','固定首尾与可变中间段的结构',[('首项','A站'),('星号中段','[3,5]'),('末项','总计8')]),
        [case('零天记录','assert daily==[] and total==0',replacements=[('("A站", 3, 5, 8)','("A站", 0)')],output='A站 [] 0\nTrue\n'),case('单项解包','assert split_first([0])==(0,[],1)',field='solution')])
    add(t,'l21','advanced','元组不可变不代表内容不会变', ['区分容器结构不可变与元素可变','构造不共享可变内容的快照'],
        '元组不能替换某个位置，但其中可以放列表；列表仍能append，所以“元组不可变”指它持有的引用序列不能改，而不是所有后代对象冻结。本例记录由姓名和分数列表组成，对列表追加会改变观察到的记录内容。若需要历史快照，应把内层分数也转成元组；只是tuple(record)不会递归冻结。练习为二维整数表构造元组的元组，使后续编辑源表不影响快照。对于任意对象的递归冻结需另行设计，本课不假装解决所有对象。',
        ['观察元组内部仍指向可变列表','把需要冻结的一层转为元组','修改源数据验证快照未变'],
        '''scores = [80, 90]
record = ("小禾", scores)
snapshot = (record[0], tuple(scores))
scores.append(100)
print(record)
print(snapshot)''',"('小禾', [80, 90, 100])\n('小禾', (80, 90))\n",
        '实现freeze_grid，把整数二维列表转成元组的元组；演示来源修改后快照保持原状，空表返回空元组。',
        '''def freeze_grid(grid):
    return tuple(tuple(row) for row in grid)
grid = [[1,2],[3,4]]
snapshot = freeze_grid(grid)
grid[0][0] = 99
print(snapshot)
print(grid)''','((1, 2), (3, 4))\n[[99, 2], [3, 4]]\n',
        ['把外层转元组不会递归冻结内层列表','试图把含列表的元组作为字典键会遇不可哈希错误'], '不可变性要逐层分析；可靠历史快照必须隔离将被修改的层次。',
        ('object-graph','元组里的分数为什么还能增加？','record共享列表，snapshot拥有不可变分数元组',[('record','姓名 → scores列表'),('追加','80 90 → 80 90 100'),('snapshot','固定(80,90)')]),
        [case('快照不随来源变','assert snapshot[1]==(80,90) and record[1] is scores'),case('空行与空表','assert freeze_grid([])==() and freeze_grid([[]])==((),)',field='solution')])
    add(t,'l22','intermediate','分组统计与缺失值', ['用get建立累计字典','区分不存在的键和计数为0的键'],
        '字典适合按键累计，get(key,0)表达尚未出现时从0开始。不要先判断字典里有没有任意数据，再误以为当前键已经存在。本例对类别逐项累计数量，保留数量为0的类别，因为它表示已知但目前没有库存，不等同于未知。取值时使用in判断键是否存在，比if totals.get(key)更准确：后者会把0当成假。练习把记录按人的名字累计分钟，要求拒绝负时长，并且整个函数不修改传入记录。',
        ['每条记录只更新自己的类别键','0仍作为已知状态保存','查询用成员判断区分未知与零库存'],
        '''records = [("书",2),("笔",0),("书",3)]
totals = {}
for name, quantity in records:
    totals[name] = totals.get(name,0) + quantity
print(totals)
print("笔" in totals, "纸" in totals)''',"{'书': 5, '笔': 0}\nTrue False\n",
        '实现sum_minutes(records)，记录为(name,minutes)，拒绝负数；同名累加，零分钟也要保留姓名。',
        '''def sum_minutes(records):
    result = {}
    for name, minutes in records:
        if minutes < 0:
            raise ValueError("时长不能为负")
        result[name] = result.get(name,0) + minutes
    return result
print(sum_minutes([("小禾",10),("阿青",0),("小禾",20)]))''',"{'小禾': 30, '阿青': 0}\n",
        ['用if get判断存在会误判合法0','忘给默认值0，首次累计会把None参与加法'], '键的存在性和值的真假是不同问题，累计前要决定缺失状态的含义。',
        ('dictionary','笔的0库存与没有纸这个键有什么不同？','按键累积并保留显式零值',[('书','2+3=5'),('笔','已知，0'),('纸','键不存在')]),
        [case('只有零值记录','assert totals=={"笔":0}',replacements=[('[("书",2),("笔",0),("书",3)]','[("笔",0)]')],output="{'笔': 0}\nTrue False\n"),case('拒绝负数',"try:\n    sum_minutes([('x',-1)])\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('negative')",field='solution')])
    add(t,'l22','advanced','合并配置：冲突策略必须显式', ['选择覆盖、保留或拒绝冲突的策略','返回新字典避免修改调用者状态'],
        '字典合并不是只有一种正确行为。用户配置覆盖默认配置适合普通选项，但学生编号冲突时静默覆盖会丢失记录。本例提供拒绝冲突的merge_unique：复制左侧后逐键检查右侧，发现已存在键就抛异常，哪怕两个值相同也拒绝，因为接口约定是键唯一。原始字典不会被改变；先写入左侧再遇错会留下部分修改，因此不应直接修改调用者对象。练习实现只补缺失值的默认合并，合法0、False、空串都必须保留。',
        ['先复制来源形成候选结果','每个右侧键写入前检查冲突','按接口约定决定同键值的处理方式'],
        '''def merge_unique(left,right):
    result = left.copy()
    for key,value in right.items():
        if key in result:
            raise ValueError("重复键："+key)
        result[key] = value
    return result
left = {"A":80}
merged = merge_unique(left,{"B":90})
print(merged)
print(left)''',"{'A': 80, 'B': 90}\n{'A': 80}\n",
        '实现with_defaults(settings,defaults)，只在键不存在时补默认值，不覆盖0或False；返回新字典，不改两份输入。',
        '''def with_defaults(settings, defaults):
    result = settings.copy()
    for key,value in defaults.items():
        if key not in result:
            result[key] = value
    return result
print(with_defaults({"volume":0},{"volume":5,"theme":"light"}))''',"{'volume': 0, 'theme': 'light'}\n",
        ['dict.update会覆盖冲突，不能满足拒绝策略','用value or default会丢失合法假值'], '合并先定义冲突策略与修改权限，再选具体字典操作。',
        ('merge','同一个键出现两次时，哪份数据应该保留？','两种合并协议明确不同的冲突行为',[('唯一合并','A80 + B90 → 两键'),('冲突','A80 + A90 → 拒绝'),('补默认','volume0优先于默认5')]),
        [case('冲突原数据保全',"a={'x':1}\ntry:\n    merge_unique(a,{'y':2,'x':3})\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('conflict')\nassert a=={'x':1}"),case('所有假值保留','a={"x":False,"y":"","z":0}\nr=with_defaults(a,{"x":1,"y":2,"z":3})\nassert r==a and r is not a',field='solution')])
    add(t,'l23','intermediate','集合对账与有序报告', ['用差集查漏项与额外项','对无序集合排序后再展示'],
        '集合表达有哪些不同值，不表达原来的顺序和重复次数。比较应交名单与实交名单，expected-actual是缺交，actual-expected是未登记的额外提交，交集则是双方共有。本例把两种差集都报告，避免只检查缺交却忽略异常记录。集合迭代顺序不能当作稳定展示协议，所以输出前用sorted。若业务关心提交次数，应该另用字典或Counter；去重后的集合无法恢复重复数量。练习将同样方法用于文件名清单核对。',
        ['输入列表转集合只保留不同标识','分别计算两个方向的差集','排序后输出使测试和阅读稳定'],
        '''expected = {"A","B","C"}
actual = {"B","C","D"}
missing = expected - actual
extra = actual - expected
print("缺少", sorted(missing))
print("额外", sorted(extra))''',"缺少 ['A']\n额外 ['D']\n",
        '实现audit(expected,actual)，返回排序后的(缺失,额外)两个列表；重复实际项不影响结果，输入顺序不影响报告。',
        '''def audit(expected, actual):
    expected,actual = set(expected),set(actual)
    return sorted(expected-actual),sorted(actual-expected)
print(audit(["a.py","b.py"],["b.py","c.py","b.py"]))''',"(['a.py'], ['c.py'])\n",
        ['差集方向写反会把缺失与额外互换','直接展示集合会让顺序成为不可靠的接口'], '集合适合成员对账，稳定报告还需要显式排序。',
        ('set-regions','A和D分别落在哪个区域，代表什么？','两集合交叠及各自独有成员',[('应有独占','A → 缺少'),('交集','B C → 正常'),('实际独占','D → 额外')]),
        [case('完全一致','assert missing==extra==set()',replacements=[('actual = {"B","C","D"}','actual = {"A","B","C"}')],output='缺少 []\n额外 []\n'),case('重复与空清单','assert audit([], ["z","z"])==([],["z"])',field='solution')])
    add(t,'l23','advanced','集合加顺序：线性稳定去重', ['用seen集合加速成员判断','限制接口为可哈希元素并解释原因'],
        '列表稳定去重时，反复检查item in result最坏需要平方量比较。把已见成员放进set，同时用list保留首次出现顺序，能避免每次扫描整个结果；常见散列情况下整体接近线性，但不应宣称任何输入都必然常数时间。代价是元素必须可哈希，列表本身不能直接放集合。对字典记录去重，可以选择稳定的标识字段作为键，不能把整个可变字典塞进去。练习按用户id保留第一条记录，并保证不因同名误去重。',
        ['seen只负责已出现判断','result只负责展示顺序','记录去重提取稳定键而非可变整对象'],
        '''def unique_fast(values):
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
print(unique_fast([3,1,3,2,1]))''','[3, 1, 2]\n',
        '实现unique_users(records)，根据id保留第一条字典记录，同名不同id必须保留；不要修改输入记录。',
        '''def unique_users(records):
    seen = set()
    result = []
    for record in records:
        key = record["id"]
        if key not in seen:
            seen.add(key)
            result.append(record.copy())
    return result
print(unique_users([{"id":1,"name":"禾"},{"id":1,"name":"改名"},{"id":2,"name":"禾"}]))''',"[{'id': 1, 'name': '禾'}, {'id': 2, 'name': '禾'}]\n",
        ['返回list(set(values))会丢掉首次顺序','按姓名去重会混淆同名不同人'], '把成员判断与顺序维护分给不同容器，用稳定业务键定义唯一性。',
        ('dual-structure','为何需要seen和result两个容器？','集合判重和列表保序分工',[('读3','seen{3} result[3]'),('读1','seen{1,3} result[3,1]'),('再读3','已见跳过，顺序不变')]),
        [case('合法零与空输入','assert unique_fast([0,0,1])==[0,1] and unique_fast([])==[]'),case('返回记录独立','x=[{"id":1,"name":"A"}]\ny=unique_users(x)\ny[0]["name"]="B"\nassert x[0]["name"]=="A"',field='solution')])
    add(t,'l24','intermediate','推导式：筛选与变换分清顺序', ['区分末尾if筛选和前部条件表达式','保持推导式纯粹且易读'],
        '列表推导式的最后一个if决定某项要不要进入结果，前面的表达式决定留下来的项变成什么。若要保留所有项但把负数改成0，应写条件表达式，而不是末尾筛掉负数。本例并列输出两种结果，说明“删除”和“替换”不是同一需求。推导式适合简短、没有副作用的规则；若需要记录错误、多个步骤或复杂分支，普通循环更清楚。练习清洗数值字符串，但只接收已经约定为整数文本的非空字段，不在一行推导式里偷偷吞异常。',
        ['末尾if先选择正数','表达式把选中正数平方','条件表达式则逐项替换而不改变长度'],
        '''values = [-2,0,3]
positive_squares = [x*x for x in values if x > 0]
clamped = [x if x >= 0 else 0 for x in values]
print(positive_squares)
print(clamped)''','[9]\n[0, 0, 3]\n',
        '输入字段[" 2 ",""," -3 ","  "]，先去空白，忽略空字段，再转换整数并平方；可以分两步推导式提高可读性。',
        '''fields = [" 2 ",""," -3 ","  "]
cleaned = [field.strip() for field in fields]
squares = [int(field)**2 for field in cleaned if field]
print(squares)''','[4, 9]\n',
        ['末尾if删项，不能代替保留长度的条件表达式','为省行数塞进多种副作用会使错误定位困难'], '先确定保留哪些项，再确定每项如何变换；是否改变长度是重要区别。',
        ('mapping','负数在两个结果中为什么一边消失、一边变0？','筛选改变长度，映射保持长度',[('来源','-2 0 3'),('筛选平方','只3 → 9'),('逐项替换','0 0 3')]),
        [case('全非正','assert positive_squares==[] and clamped==[0,0]',replacements=[('values = [-2,0,3]','values = [-2,0]')],output='[]\n[0, 0]\n'),case('空白字段全删除','assert squares==[]',field='solution',replacements=[('fields = [" 2 ",""," -3 ","  "]','fields = ["", " "]')],output='[]\n')])
    add(t,'l24','advanced','矩阵转置与形状校验', ['推导嵌套推导式的索引含义','在变换前拒绝不规则矩阵'],
        '转置将原来的行变为列。对rows行cols列矩阵，结果应有cols行，每行rows项；外层循环选择原列号，内层从每一原行取该列。若直接对不规则行下标取值，可能中途抛异常；更危险的是使用zip默认截断而静默丢数据。本例先验证所有行同宽，再执行转置，约定空矩阵返回空列表。练习把双层推导式改写为普通循环，要求保持行为不变，用两种实现交叉核对；重构的目标是清楚，不是单纯减少行数。',
        ['读取第一行确定列数','验证每一行长度一致','结果外层按列，内层按原行取值'],
        '''def transpose(matrix):
    if not matrix:
        return []
    width = len(matrix[0])
    if any(len(row) != width for row in matrix):
        raise ValueError("行宽不一致")
    return [[row[col] for row in matrix] for col in range(width)]
print(transpose([[1,2,3],[4,5,6]]))''','[[1, 4], [2, 5], [3, 6]]\n',
        '用普通双层循环实现transpose_loop，保留同样的形状校验和空矩阵约定；示例为2乘2矩阵。',
        '''def transpose_loop(matrix):
    if not matrix:
        return []
    width=len(matrix[0])
    if any(len(row)!=width for row in matrix):
        raise ValueError("行宽不一致")
    result=[]
    for col in range(width):
        new_row=[]
        for row in matrix:
            new_row.append(row[col])
        result.append(new_row)
    return result
print(transpose_loop([[1,2],[3,4]]))''','[[1, 3], [2, 4]]\n',
        ['外层仍按原行循环会复制而不是转置','zip截断不能代替形状验证'], '先验证数据形状，再按明确索引变换；用等价实现验证重构没有改变行为。',
        ('matrix-transform','2乘3为何转成3乘2？','原列被收集为结果行',[('输入行','1 2 3 / 4 5 6'),('按列收集','(1,4) (2,5) (3,6)'),('输出形状','3行，每行2项')]),
        [case('不规则拒绝',"try:\n    transpose([[1,2],[3]])\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('ragged')"),case('双重转置与空行','x=[[1,2],[3,4]]\nassert transpose_loop(transpose_loop(x))==x\nassert transpose_loop([[],[]])==[]',field='solution')])
    add(t,'l25','intermediate','返回值与打印：让计算可复用', ['将业务计算从界面输出分离','用多个输入检查同一函数'],
        '函数如果只print而不return，调用者得到的是None，无法继续计算或比较。本例将折后金额作为返回值，外层再负责格式化；同一计算可用于报表、测试或命令行。参数应该表达完整输入，函数内部不要悄悄input或依赖可变全局变量。校验条件也属于接口：价格和数量非负，折扣介于0和1。练习把温度转换做成纯函数，返回数值而不打印，再用外层打印展示。这样测试可以直接比较结果，无需从输出文字反向提取数字。',
        ['计算函数只接收参数并返回结果','非法范围在入口明确拒绝','调用者组合多个返回值再展示'],
        '''def discounted_total(price,quantity,discount):
    if price<0 or quantity<0 or not 0<=discount<=1:
        raise ValueError("价格、数量或折扣无效")
    return price*quantity*(1-discount)
amount=discounted_total(20,3,0.1)
print(f"应付{amount:.2f}")''','应付54.00\n',
        '实现celsius_to_fahrenheit，返回摄氏度乘9/5加32；保持纯计算，外层显示0摄氏对应32.0华氏。',
        '''def celsius_to_fahrenheit(celsius):
    return celsius*9/5+32
converted=celsius_to_fahrenheit(0)
print(f"{converted:.1f}")''','32.0\n',
        ['把print的返回值当金额会得到None','函数内部读取交互输入会让复用和测试困难'], '返回数据让函数可组合，打印应留在需要展示的调用边界。',
        ('function-flow','金额为什么由return交回外层再显示？','输入到纯计算再到格式化的职责分工',[('输入','20、3、折扣0.1'),('返回','54.0数值'),('展示','应付54.00')]),
        [case('全额折扣与零数量','assert discounted_total(20,3,1)==0 and discounted_total(20,0,0)==0'),case('负温与体温','assert celsius_to_fahrenheit(-40)==-40\nassert abs(celsius_to_fahrenheit(37)-98.6)<1e-9',field='solution')])
    add(t,'l25','advanced','契约与组合：验证一次，复用多次', ['用清晰返回结构表达多个结果','拒绝无定义输入而不假造平均数'],
        '一个统计函数既可能需要总数又需要平均值，返回字典比让调用者记住一串位置更清楚。接口契约规定空输入返回count0、total0、averageNone，而不是伪造0分平均。函数先复制可迭代输入，才能多次访问而不耗尽生成器；此处也明确材料化会占用与输入量成正比的内存。练习进一步把校验和计算拆开，成绩范围错误应抛ValueError，不能悄悄过滤以掩盖坏记录。设计先确定含义，再选择返回结构和计算过程。',
        ['复制输入避免迭代器只消费一次的误会','分别定义空集合下各统计量','返回命名字段供调用者明确读取'],
        '''def summarize(values):
    data=list(values)
    total=sum(data)
    return {"count":len(data),"total":total,"average":total/len(data) if data else None}
report=summarize([2,4,9])
print(report)''',"{'count': 3, 'total': 15, 'average': 5.0}\n",
        '实现grade_report，先验证所有分数为0至100整数（bool不算分数），再返回count、passed；空数据允许，不丢弃非法分数。',
        '''def validate_scores(values):
    data=list(values)
    if any(type(x) is not int or not 0<=x<=100 for x in data):
        raise ValueError("成绩应为0至100整数")
    return data
def grade_report(values):
    data=validate_scores(values)
    return {"count":len(data),"passed":sum(x>=60 for x in data)}
print(grade_report([59,60,100]))''',"{'count': 3, 'passed': 2}\n",
        ['空数据平均值写0会混淆没有数据与真实0分','isinstance(True,int)为真，严格整数协议需额外处理bool'], '函数契约应定义空值、坏值和返回字段，组合依赖稳定含义。',
        ('contract','没有成绩与平均0分，为什么不能同样返回0？','空数据和有效零分的返回结构不同',[('空输入','count0 total0 averageNone'),('零分输入','count1 total0 average0.0'),('调用处','先判断average是否None')]),
        [case('一次迭代输入','assert summarize(iter([1,3]))["average"]==2 and summarize([])["average"] is None'),case('布尔与越界拒绝',"for bad in ([True],[101]):\n    try:\n        grade_report(bad)\n    except ValueError:\n        pass\n    else:\n        raise AssertionError('bad score')",field='solution')])
    add(t,'l26','intermediate','只限关键字的选项', ['用星号约束容易混淆的选项参数','保持默认值与显式传参行为清楚'],
        '多个布尔或数字选项放在位置参数里很难读：render(8,False,2)需要记住每个位置。函数定义中的单独星号让后续参数只能按名字传递，调用者写show_unit=False更清楚。本例把核心数值放在前面，精度和单位作为关键字选项，并校验精度范围。默认值在定义时确定，不会因为外部同名变量变化而更新。练习设计一个文本框生成函数，明确左右边界字符与重复次数，要求关键字调用避免把宽度与字符误交换。',
        ['星号之前保留核心值的位置参数','星号之后的选项以参数名调用','给精度设范围而不是允许任意大输出'],
        '''def render(value,*,digits=1,show_unit=True):
    if not 0<=digits<=4:
        raise ValueError("精度应为0至4")
    text=f"{value:.{digits}f}"
    return text+" kg" if show_unit else text
print(render(2.345,digits=2,show_unit=False))''','2.35\n',
        '实现frame(text,*,border="|",padding=1)，padding非负，边界恰为一个字符；返回边界、空格、文本、空格、边界。',
        '''def frame(text,*,border="|",padding=1):
    if len(border)!=1 or padding<0:
        raise ValueError("边界或留白无效")
    space=" "*padding
    return border+space+text+space+border
print(frame("OK",border="#",padding=2))''','#  OK  #\n',
        ['忘记写参数名会触发TypeError，这正是接口保护','不限制精度或填充可能产生无意义的超长输出'], '关键字选项让调用处自带解释，范围约束防止含糊参数产生意外行为。',
        ('call-binding','digits=2为什么比第二个位置写2更清楚？','核心值和命名选项绑定到不同接口位置',[('核心','value=2.345'),('选项','digits2 show_unitFalse'),('结果','文本2.35')]),
        [case('零精度与单位','assert render(2.8,digits=0)=="3 kg"'),case('零留白','assert frame("",padding=0)=="||" and frame("x",padding=0)=="|x|"',field='solution')])
    add(t,'l26','advanced','默认参数的生命周期', ['解释可变默认对象为何跨调用共享','用None哨兵创建每次独立容器'],
        '默认参数表达式只在函数定义时计算一次，不是在每次调用时重新执行。因此def add(x,bucket=[])会让多次省略bucket的调用共享同一个列表。修复不是简单在函数内清空列表，那会破坏显式传入的容器；应以None表示未提供，并在调用时创建新列表。显式传入列表时是否原地修改也要写在契约中。本例选择原地追加并返回同一对象，练习改为纯函数：无论是否传入已有集合，都返回新集合，避免无意改变调用者数据。',
        ['默认值只保存None这个不可变哨兵','省略容器时每次分配新列表','显式容器的修改权限由接口明确说明'],
        '''def append_item(item,bucket=None):
    if bucket is None:
        bucket=[]
    bucket.append(item)
    return bucket
a=append_item("A")
b=append_item("B")
print(a,b,a is b)''',"['A'] ['B'] False\n",
        '实现with_tag(tag,existing=None)，返回包含新标签的新集合；即便显式传入集合也不修改原集合。',
        '''def with_tag(tag,existing=None):
    result=set() if existing is None else set(existing)
    result.add(tag)
    return result
base={"python"}
print(sorted(with_tag("offline",base)))
print(sorted(base))''',"['offline', 'python']\n['python']\n",
        ['bucket=[]会让省略参数的多次调用串联状态','用if not bucket会把显式空容器误当未提供'], '默认值的定义时生命周期与每次调用的状态生命周期必须分清。',
        ('lifecycle','两次未传bucket的调用，为什么必须得到两个列表？','定义时None与调用时新容器的生命周期',[('定义','默认None'),('调用A','新列表[A]'),('调用B','另一个新列表[B]')]),
        [case('显式容器保持身份','x=[]\ny=append_item(0,x)\nassert y is x and x==[0]'),case('空集合不被修改','x=set()\ny=with_tag("x",x)\nassert x==set() and y=={"x"} and y is not x',field='solution')])
    add(t,'l27','intermediate','参数传递：修改对象还是重绑名字', ['追踪函数局部名字与调用者对象','设计返回新结果的非破坏接口'],
        '函数参数接收的是对象引用。给参数重新赋值，只改变函数内部名字；对参数指向的列表append，则会改变共享对象。本例分别演示rebind和mutate，不用“传值或传址”的含糊口号代替具体对象关系。若函数应该只计算结果，应先复制并返回，不让调用者意外观察到变化。浅复制对一层数字列表足够，对嵌套结构仍需回顾复制课程。练习实现排序后的新列表，明确原数据保留和返回对象独立两个要求。',
        ['rebind只让局部名指向另一列表','append通过共享引用改原对象','返回新结果时验证原列表与身份'],
        '''def rebind(items):
    items=[99]
def mutate(items):
    items.append(3)
values=[1,2]
rebind(values)
print(values)
mutate(values)
print(values)''','[1, 2]\n[1, 2, 3]\n',
        '实现sorted_copy(values,*,descending=False)，返回排序副本而不修改来源；不要用返回None的list.sort作为返回值。',
        '''def sorted_copy(values,*,descending=False):
    result=list(values)
    result.sort(reverse=descending)
    return result
source=[3,1,2]
print(sorted_copy(source))
print(source)''','[1, 2, 3]\n[3, 1, 2]\n',
        ['把局部参数重新绑定误认为会替换调用者变量','list.sort原地修改并返回None，不能当排序结果返回'], '逐步画名字到对象的箭头，可以准确判断一次操作是否影响调用者。',
        ('references','items=[99]为什么没有替换values？','局部重绑与共享对象修改对照',[('调用时','items与values指向[1,2]'),('局部重绑','items→[99]，values不动'),('原地追加','共享列表变[1,2,3]')]),
        [case('独立列表只改目标','x=[]\ny=[]\nmutate(x)\nassert x==[3] and y==[]'),case('空与降序副本','x=[1,3,2]\ny=sorted_copy(x,descending=True)\nassert y==[3,2,1] and x==[1,3,2]\nassert sorted_copy([])==[]',field='solution')])
    add(t,'l27','advanced','闭包状态与nonlocal', ['区分封闭作用域和全局作用域','为每个调用者创建独立状态'],
        '内层函数可以读取外层函数的局部变量，但若要重新绑定它，必须声明nonlocal；否则赋值会把它当作内层局部变量。闭包让状态与访问它的函数一起保留，不需要散落在模块全局。本例工厂创建两个独立计数器，它们各自拥有value；同一个计数器连续调用会累计，不同计数器互不干扰。闭包并不会自动线程安全，本课只讨论单线程顺序调用。练习创建有下限的余额调整器，失败调整不能改变已保存状态。',
        ['每次工厂调用创建一份封闭状态','内层用nonlocal明确需要重新绑定','失败前先校验候选值再提交状态'],
        '''def make_counter(start=0):
    value=start
    def next_value(step=1):
        nonlocal value
        value+=step
        return value
    return next_value
a=make_counter()
b=make_counter(10)
print(a(),a(),b(),a())''','1 2 11 3\n',
        '实现make_wallet(initial)，返回adjust(delta)。余额不可为负，非法调整抛ValueError且不改变余额，合法调整返回新余额。',
        '''def make_wallet(initial):
    if initial<0:
        raise ValueError("初始余额无效")
    balance=initial
    def adjust(delta):
        nonlocal balance
        candidate=balance+delta
        if candidate<0:
            raise ValueError("余额不足")
        balance=candidate
        return balance
    return adjust
wallet=make_wallet(20)
print(wallet(-5),wallet(3))''','15 18\n',
        ['用global会把状态放到模块层并让实例相互干扰','先修改余额再检查会在异常后留下负状态'], '闭包封装各自的状态，nonlocal表达重新绑定；校验成功后才提交变化。',
        ('closure','为什么b从10开始，却不改变a的计数？','两个工厂调用各有独立封闭变量',[('工厂A','value0 →1→2→3'),('工厂B','value10 →11'),('访问函数','各自绑定自己的value')]),
        [case('独立与负步长','x=make_counter(5)\ny=make_counter(5)\nassert x(-2)==3 and y()==6 and x()==4'),case('失败保持余额',"w=make_wallet(2)\ntry:\n    w(-3)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('overdraft')\nassert w(0)==2",field='solution')])
    add(t,'l28','intermediate','导入命名：模块名比星号更清楚', ['使用限定名称避免名称冲突','区分模块对象与导入的单个对象'],
        'import math把模块对象绑定给math，之后使用math.sqrt清楚表明来源；from math import sqrt只绑定函数名，若本地又给sqrt赋值就会遮蔽函数。通配导入会让来源更加难追踪，不适合本课程项目。本例使用math.hypot计算二维距离，它比手工拼平方和开根号更直接地表达意图；同时用ceil估计非负长度需要多少固定长度材料。模块导入不会自动联网，使用标准库也不需要安装第三方包。练习要求对单位和零长度建立明确前提。',
        ['保留math限定名避免本地变量遮蔽','hypot把两个方向分量转成距离','ceil只用于业务要求向上数量的地方'],
        '''import math
dx,dy=3,4
distance=math.hypot(dx,dy)
pieces=math.ceil(distance/2)
print(distance,pieces)''','5.0 3\n',
        '实现rope_pieces(dx,dy,piece_length)，piece_length必须为正；总距离0时返回0，其他情况返回向上取整的材料件数。',
        '''import math
def rope_pieces(dx,dy,piece_length):
    if piece_length<=0:
        raise ValueError("单段长度必须为正")
    return math.ceil(math.hypot(dx,dy)/piece_length)
print(rope_pieces(6,8,3))''','4\n',
        ['通配导入后同名变量可能遮蔽函数且来源不清','ceil不是四舍五入，所需材料数量通常不能向下取'], '限定模块名表达来源，选择语义吻合的标准库函数比手工拼公式更可靠。',
        ('module-call','3和4怎样经过math.hypot得到5？','输入分量到标准库距离再到件数',[('分量','dx3 dy4'),('模块调用','math.hypot →5.0'),('件数','ceil(5/2)=3')]),
        [case('零距离','assert distance==0 and pieces==0',replacements=[('dx,dy=3,4','dx,dy=0,0')],output='0.0 0\n'),case('恰好整段与负方向','assert rope_pieces(-6,8,5)==2 and rope_pieces(0,0,1)==0',field='solution')])
    add(t,'l28','advanced','模块缓存与副作用边界', ['解释重复导入一般不会重跑模块主体','将计算入口与导入时行为分离'],
        '模块第一次导入后通常缓存在sys.modules，同一名字再次导入会得到同一个模块对象，而不是重新执行初始化代码。因此不应靠“再次import”重置业务状态。更好的设计是模块只定义常量、函数和类，需要的状态通过工厂或调用参数创建。这个知识也解释为什么测试要隔离进程，或者明确管理模块缓存。本例使用importlib.import_module查看同一math对象，并把可变数据放在显式函数返回值中。练习设计一个无全局可变库存的模块式接口，使两次建立的库存互不共享。',
        ['通过标准导入与importlib拿到同名模块','用is核对缓存对象身份','把业务状态建立移到函数调用时'],
        '''import importlib
import math
again=importlib.import_module("math")
def new_settings():
    return {"scale":1,"tags":[]}
first=new_settings()
second=new_settings()
first["tags"].append("demo")
print(again is math)
print(first,second)''',"True\n{'scale': 1, 'tags': ['demo']} {'scale': 1, 'tags': []}\n",
        '实现new_inventory(items)，每次返回包含独立counts字典的状态；输入items是(name,count)记录，可重复则累加，不保存全局库存。',
        '''def new_inventory(items):
    counts={}
    for name,count in items:
        if count<0:
            raise ValueError("库存不能为负")
        counts[name]=counts.get(name,0)+count
    return {"counts":counts}
a=new_inventory([("笔",2)])
b=new_inventory([("笔",2)])
a["counts"]["笔"]-=1
print(a,b)''',"{'counts': {'笔': 1}} {'counts': {'笔': 2}}\n",
        ['重复import不会按预期清空已缓存状态','工厂返回共享模板内的嵌套字典仍会共享数据'], '模块导入负责提供能力，业务状态应显式创建，才能控制生命周期。',
        ('module-cache','再次导入math为什么得到同一个对象？','模块缓存与业务工厂的不同生命周期',[('第一次导入','sys.modules[math]'),('再次导入','取同一个模块'),('工厂调用','每次新建独立业务字典')]),
        [case('工厂层次独立','assert first is not second and first["tags"] is not second["tags"]'),case('重复项与独立状态','x=new_inventory([("a",1),("a",2)])\ny=new_inventory([])\nassert x["counts"]=={"a":3} and y["counts"]=={}',field='solution')])
    add(t,'l30','intermediate','异常边界：只捕获可以解释的失败', ['缩小try范围避免误吞程序错误','将输入错误转换为清楚消息'],
        'try范围越大，越容易把真正的编程错误误报成输入问题。本例只把int转换和范围验证放进try，捕获预期的ValueError；结果展示放在else，保证只对成功转换的数据执行。不要写except Exception后继续输出默认成绩，那会掩盖拼写错误或文件权限故障。异常消息应说明可行动的规则，而不是只写“失败”。练习实现可复用的整数解析器，由外层决定是否打印；错误应通过raise传递，不要在库函数里终止整个应用进程。',
        ['转换与范围校验构成明确失败边界','except只处理ValueError','else执行依赖成功数据的展示'],
        '''raw=" 60 "
try:
    score=int(raw)
    if not 0<=score<=100:
        raise ValueError("分数范围0至100")
except ValueError as error:
    print("输入错误：",error)
else:
    print("通过",score>=60)''','通过 True\n',
        '实现parse_positive(text)，返回正整数；文本格式错误或值不为正都抛ValueError，消息统一为“需要正整数”，保留异常因果链。',
        '''def parse_positive(text):
    try:
        value=int(text)
    except ValueError as error:
        raise ValueError("需要正整数") from error
    if value<=0:
        raise ValueError("需要正整数")
    return value
print(parse_positive(" 12 "))''','12\n',
        ['except Exception会把意外程序错误伪装成用户输入错误','捕获后继续使用未赋值变量会产生第二个异常'], '在能解释并恢复的边界捕获特定异常，成功路径和失败路径应清楚分离。',
        ('exception-path','格式错误与成功转换后分别会走哪条路？','try分出except与else两条互斥路径',[('转换','int(raw)'),('错误','ValueError → except'),('成功','范围校验通过 → else')]),
        [case('范围错误有提示','',replacements=[('raw=" 60 "','raw="101"')],output='输入错误： 分数范围0至100\n'),case('格式错误保留原因',"try:\n    parse_positive('x')\nexcept ValueError as e:\n    assert str(e)=='需要正整数' and isinstance(e.__cause__,ValueError)\nelse:\n    raise AssertionError('invalid')",field='solution')])
    add(t,'l30','advanced','批量校验：收集错误还是立即失败', ['为批量导入选择明确错误策略','返回成功记录及带行号错误而不吞异常'],
        '交互单次输入通常适合立即报错，批量导入则可能需要一次看到多行错误。本例选择逐行独立验证，返回有效值和(行号,原因)列表；只捕获预期的ValueError，其余错误仍向上传播。行号从1开始并计入空行，保证用户能定位原文件。导入部分成功不是自动正确的业务选择：若要求整批事务，应先验证全部再提交。本练习明确采用“全有或全无”，任何错误就抛异常，不返回部分总和，避免调用者误把不完整数据用于结算。',
        ['enumerate保留真实输入位置','每行独立try并收集明确错误','整批策略先验证完才给出总和'],
        '''def import_numbers(lines):
    valid=[]
    errors=[]
    for number,text in enumerate(lines,1):
        try:
            value=int(text)
            if value<0:
                raise ValueError("不能为负")
        except ValueError:
            errors.append((number,"需要非负整数"))
        else:
            valid.append(value)
    return valid,errors
print(import_numbers(["2","x","-1","0"]))''',"([2, 0], [(2, '需要非负整数'), (3, '需要非负整数')])\n",
        '实现strict_total(lines)：每行必须是非负整数；失败抛带行号的ValueError，不返回部分总和；空输入返回0。',
        '''def strict_total(lines):
    values=[]
    for number,text in enumerate(lines,1):
        try:
            value=int(text)
            if value<0:
                raise ValueError("负数")
        except ValueError as error:
            raise ValueError(f"第{number}行无效") from error
        values.append(value)
    return sum(values)
print(strict_total(["2","3","0"]))''','5\n',
        ['删除空行后重新编号会导致报告行号偏移','返回部分总和却不标明错误会让数据看似完整'], '批量错误策略必须写进接口：部分接受附错误，或全部验证后一次提交。',
        ('batch-validation','第二行错误后，第四行的0应被保留吗？','部分接受与整批拒绝两种策略对照',[('输入','2、x、-1、0'),('收集模式','有效[2,0]；错2和3行'),('严格模式','遇错抛异常，不给部分总和')]),
        [case('错误保留真实行号','assert import_numbers(["","4"]）==([4],[(1,"需要非负整数")])'.replace('）',')')),case('整批拒绝含行号',"assert strict_total([])==0\ntry:\n    strict_total(['8','bad','3'])\nexcept ValueError as e:\n    assert '第2行' in str(e)\nelse:\n    raise AssertionError('partial import')",field='solution')])
    add(t,'l31','intermediate','追加日志与读回验证', ['区分w覆盖和a追加的文件语义','用with确保每次写入及时关闭'],
        'w模式打开文件时会截断旧内容，适合完整重建结果；a模式把新增内容写到末尾，适合日志。本例第一次明确新建演示文件，之后两次以a追加，再完整读回验证三行顺序。每次with退出会关闭文件并完成Python缓冲区写出，但这不等于断电后绝对持久；涉及更强保证需要操作系统层机制。文本编码明确使用UTF-8，不能依赖当前机器默认编码。练习把日志函数独立出来，要求调用两次都追加且每条恰好一行。',
        ['演示初始化只使用一次w','新增记录始终使用a并附换行','关闭后重新读取检查实际落盘文本'],
        '''with open("lesson_log.txt","w",encoding="utf-8") as stream:
    stream.write("开始\\n")
for event in ["处理","结束"]:
    with open("lesson_log.txt","a",encoding="utf-8") as stream:
        stream.write(event+"\\n")
with open("lesson_log.txt",encoding="utf-8") as stream:
    lines=stream.read().splitlines()
print(lines)''',"['开始', '处理', '结束']\n",
        '实现append_event(path,event)，拒绝含回车换行的事件避免一条伪装多条；每次追加UTF-8一行，用两次调用展示读回。',
        '''def append_event(path,event):
    if "\\n" in event or "\\r" in event:
        raise ValueError("事件不能包含换行")
    with open(path,"a",encoding="utf-8") as stream:
        stream.write(event+"\\n")
append_event("events.txt","创建")
append_event("events.txt","完成")
with open("events.txt",encoding="utf-8") as stream:
    print(stream.read().splitlines())''',"['创建', '完成']\n",
        ['每次使用w会只剩最后一条记录','事件里自带换行会破坏一事件一行的协议'], '文件模式是数据保留策略；写完后读回能验证真实内容而非只验证内存变量。',
        ('file-growth','两次追加后，第一条开始记录为什么仍在？','文件从首行逐步增长而不被截断',[('新建w','开始'),('追加a','开始 / 处理'),('再追加','开始 / 处理 / 结束')]),
        [case('完整日志内容','',expectedFiles={'lesson_log.txt':'开始\n处理\n结束\n'}),case('拒绝伪造多行',"try:\n    append_event('events.txt','x\\ny')\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('multiline')",field='solution',expectedFiles={'events.txt':'创建\n完成\n'})])
    add(t,'l31','advanced','安全更新：先写临时文件再替换', ['防止计算失败前截断原文件','解释原子替换的范围与局限'],
        '直接用w覆盖重要文件时，程序在写到一半失败可能留下残缺数据。常用模式是先在同目录写临时文件，完整关闭后再用Path.replace替换目标；替换前若失败，旧文件仍在。它解决单次更新的可见完整性，不自动提供多进程锁、断电绝对持久或回滚历史。本例把所有文本先准备好，再写同目录临时文件，并在finally清理残留。练习在写入前校验行记录，任何包含换行的条目都拒绝，确保旧文件不因业务校验失败而被覆盖。',
        ['先准备完整内容而不是边验证边覆盖','临时文件与目标在同目录','成功替换后或异常时均清理临时残留'],
        '''from pathlib import Path
def replace_text(path,text):
    path=Path(path)
    temporary=path.with_name(path.name+".tmp")
    try:
        temporary.write_text(text,encoding="utf-8")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
replace_text("state.txt","完整状态\\n")
print(Path("state.txt").read_text(encoding="utf-8").strip())''','完整状态\n',
        '实现save_lines(path,lines)，先把输入材料化并拒绝含回车换行的行，再按同目录临时替换写入；空列表应产生空文件。',
        '''from pathlib import Path
def save_lines(path,lines):
    data=list(lines)
    if any("\\n" in line or "\\r" in line for line in data):
        raise ValueError("每项必须是单行")
    path=Path(path)
    temp=path.with_name(path.name+".tmp")
    try:
        temp.write_text("".join(line+"\\n" for line in data),encoding="utf-8")
        temp.replace(path)
    finally:
        temp.unlink(missing_ok=True)
save_lines("records.txt",["甲","乙"])
print(Path("records.txt").read_text(encoding="utf-8").splitlines())''',"['甲', '乙']\n",
        ['临时文件放另一磁盘会破坏同文件系统替换前提','固定.tmp名不适合并发写，本例明确单写者'], '先校验、后完整写临时、再提交替换；此模式不等于万能数据库事务。',
        ('commit','替换之前失败，旧文件为什么还能保住？','候选临时文件与旧文件在提交点之前分离',[('旧文件','完整旧状态'),('准备','同目录临时文件写完整'),('提交点','replace后目标指向新内容')]),
        [case('连续替换读回','replace_text("x.txt","old")\nreplace_text("x.txt","")\nassert Path("x.txt").read_text()=="" and not Path("x.txt.tmp").exists()'),case('非法行不覆盖',"p=Path('keep.txt')\np.write_text('old',encoding='utf-8')\ntry:\n    save_lines(p,['a\\nb'])\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('bad line')\nassert p.read_text()=='old'",field='solution')])
    add(t,'l32','intermediate','路径扫描：稳定排序与文件类型', ['用Path区分文件与目录','让扫描结果可重现且不误读子目录'],
        '目录扫描得到的是路径对象，不保证天然按名称排序。若生成报告，需要显式sorted并按名字显示，以免不同文件系统顺序造成差异。本例在独立演示目录里建立两个txt文件和一个同样以.txt结尾的目录；只检查suffix会把目录误当文本文件，必须同时is_file。iterdir只看一层，rglob才递归；选哪种应由任务范围决定，不能为了方便无意扫描整个用户目录。练习统计直接子文件的行数，不进入子目录，也不读取非txt文件。',
        ['只在指定演示目录建立小型夹具','同时检查类型与后缀','排序后展示相对名字而非机器绝对路径'],
        '''from pathlib import Path
root=Path("lesson_scan")
root.mkdir(exist_ok=True)
(root/"b.txt").write_text("B",encoding="utf-8")
(root/"a.txt").write_text("A",encoding="utf-8")
(root/"fake.txt").mkdir(exist_ok=True)
names=sorted(p.name for p in root.iterdir() if p.is_file() and p.suffix==".txt")
print(names)''',"['a.txt', 'b.txt']\n",
        '实现count_text_lines(root)，统计直接子txt文件的splitlines长度并返回按名排序的(name,count)列表；子目录不进入。',
        '''from pathlib import Path
def count_text_lines(root):
    result=[]
    for path in sorted(Path(root).iterdir()):
        if path.is_file() and path.suffix==".txt":
            result.append((path.name,len(path.read_text(encoding="utf-8").splitlines())))
    return result
root=Path("texts")
root.mkdir(exist_ok=True)
(root/"a.txt").write_text("甲\\n乙\\n",encoding="utf-8")
print(count_text_lines(root))''',"[('a.txt', 2)]\n",
        ['后缀像txt的路径也可能是目录','扫描结果不排序会使展示与测试随环境变化'], '路径任务明确根目录、递归范围、类型筛选和排序，才能得到可靠清单。',
        ('filesystem','fake.txt为什么不能进入文本文件报告？','同后缀文件和目录按类型筛选',[('a.txt','文件 ✓'),('b.txt','文件 ✓'),('fake.txt','目录 ×')]),
        [case('目录名不误计','assert "fake.txt" not in names and len(names)==2'),case('忽略子目录和空文件','(root/"sub").mkdir()\n(root/"sub"/"x.txt").write_text("x")\n(root/"empty.txt").write_text("")\nassert count_text_lines(root)==[("a.txt",2),("empty.txt",0)]',field='solution')])
    add(t,'l32','advanced','相对路径约束与符号链接边界', ['用resolve和relative_to检查路径归属','说明路径检查不构成操作系统沙箱'],
        '接收用户给出的相对路径时，简单检查字符串是否含两个点并不足够：不同分隔符、绝对路径、符号链接都会影响最终位置。本例把候选路径相对根目录解析，用resolve得到规范位置，再用relative_to确认它仍在根内；绝对路径输入直接拒绝。它适合本地单用户项目工具的常规防误操作，但检查与打开之间若目录被另一个进程替换，仍有竞态，不能宣称安全沙箱。练习只允许单层文件名，采用更窄的输入协议，减少需要处理的路径状态。',
        ['根目录与候选都先规范化','拒绝绝对输入并验证归属','明确单用户无并发篡改的使用前提'],
        '''from pathlib import Path
def inside(root,name):
    root=Path(root).resolve()
    relative=Path(name)
    if relative.is_absolute():
        raise ValueError("只接受相对路径")
    target=(root/relative).resolve()
    try:
        target.relative_to(root)
    except ValueError as error:
        raise ValueError("路径越界") from error
    return target
root=Path("workspace")
print(inside(root,"notes/a.txt").relative_to(root.resolve()).as_posix())''','notes/a.txt\n',
        '实现simple_filename(name)，只允许非空单层文件名，拒绝点、双点、斜线、反斜线、冒号及控制字符；返回原名字。该协议不是完整Windows保留名检测器。',
        '''def simple_filename(name):
    if not name or name in {".",".."} or any(ch in name for ch in "/\\\\:") or any(ord(ch)<32 for ch in name):
        raise ValueError("只允许单层文件名")
    return name
print(simple_filename("日记.txt"))''','日记.txt\n',
        ['仅字符串前缀检查会把root-other误当root子目录','resolve检查不能替代权限隔离或解决所有并发竞态'], '先收窄路径协议，再检查规范位置；文件边界检查与安全沙箱是不同保证。',
        ('path-boundary','../outside.txt为何必须在打开前拒绝？','规范化候选位置与根边界对比',[('允许','root/notes/a.txt'),('归一化','root/../outside.txt → root外'),('检查','relative_to失败 → 拒绝')]),
        [case('上级越界拒绝',"try:\n    inside(root,'../outside.txt')\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('escaped')"),case('各种分隔符拒绝',"for x in ('','..','a/b','a\\\\b','C:x'):\n    try:\n        simple_filename(x)\n    except ValueError:\n        pass\n    else:\n        raise AssertionError(x)\nassert simple_filename('a..txt')=='a..txt'",field='solution')])
