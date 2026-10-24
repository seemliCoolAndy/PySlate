"""Original Chinese course authoring source. Run to regenerate course.json."""
from pathlib import Path
import json
import textwrap

chapters = []

def chapter(id, title, level, description):
    item = dict(id=id, title=title, level=level, description=description, lessons=[])
    chapters.append(item)
    return item

def lesson(ch, id, title, minutes, prerequisites, objectives, explanation, process, code, output,
           exercise, solution, solution_output, mistakes, summary, stdin="", sources=None, cases=None):
    body = "### 理解这个概念\n\n" + explanation.strip() + "\n\n### 跟着程序走一遍\n\n" + "\n".join(f"{i}. {step}" for i, step in enumerate(process, 1))
    entry = dict(id=id, title=title, minutes=minutes, prerequisites=prerequisites.split() if prerequisites else [],
                 objectives=objectives, body=body, code=textwrap.dedent(code).strip()+"\n", stdin=stdin,
                 expectedOutput=output, exercise=exercise, solution=textwrap.dedent(solution).strip()+"\n",
                 solutionExpectedOutput=solution_output, commonMistakes=mistakes, summary=summary)
    if sources: entry["sources"] = sources
    if cases: entry["testCases"] = cases
    ch["lessons"].append(entry)

TUTORIAL = "https://docs.python.org/3.11/tutorial/"
CONTROL = TUTORIAL + "controlflow.html"
DATA = TUTORIAL + "datastructures.html"
IO = TUTORIAL + "inputoutput.html"
ERRORS = TUTORIAL + "errors.html"
CLASSES = TUTORIAL + "classes.html"

c = chapter("start", "01 · 从一行程序开始", "入门", "先学会观察输入、处理与输出，再给数据命名。无需编程基础。")
lesson(c,"l01","让 Python 说第一句话",12,"",["知道代码、解释器与输出各自是什么","运行并修改一条 print 语句"],
"程序是一组按规则书写的指令；Python 解释器负责读懂这些指令并执行。编辑器里写的是源代码，控制台显示的是运行结果。两者不是同一个地方：在控制台看到一句话，并不意味着那句话已经写进文件。\n\n`print()` 是已经准备好的输出工具。圆括号里放要输出的内容；引号表示这里是一段文字，而不是要寻找的名字。第一次运行请保留英文半角圆括号和引号，只改引号内的中文。保存下来的 `.py` 文件就是可以交给 Python 执行的普通文本。",
["解释器读取第一行，识别 print 这个内置工具。","引号里的文字作为参数交给 print，控制台出现一行文字。","第二条指令随后执行，输出显示顺序与代码顺序一致。"],
'''print("你好，Python！")
print("我正在使用 PySlate 学习。")''',"你好，Python！\n我正在使用 PySlate 学习。\n",
"写两行代码，第一行输出你的学习目标，第二行输出‘今天先完成一小步’。可以用自己的文字替换参考答案。",
'''print("目标：独立写一个小工具")
print("今天先完成一小步")''',"目标：独立写一个小工具\n今天先完成一小步\n",
["把中文引号“ ”当成代码引号会触发 SyntaxError；代码结构要用英文半角符号。","直接写 你好 而不加引号，Python 会把它当作名字查找，可能出现 NameError。"],
"源代码是指令，解释器执行指令，控制台呈现结果。先保证一行能运行，再逐步修改。",sources=[TUTORIAL+"introduction.html"])
lesson(c,"l02","输出、注释与可读性",15,"l01",["控制 print 的分隔符与结尾","用注释解释代码的目的"],
"一次 print 可以接收多个参数，参数之间用逗号分隔。默认会在各个值之间加一个空格，并在最后换行。`sep` 控制中间的分隔文字，`end` 控制结尾。它们后面写等号，是在为这个工具的选项指定值。\n\n井号 `#` 到该行末尾是注释，不会被当作指令执行。好的注释解释‘为什么这样做’，例如单位是分钟；重复解释 print 就是在输出，帮助很小。空行可以隔开不同工作步骤，空行本身没有运行结果。",
["第一条 print 用斜杠连接年月日，结尾仍是换行。","第二条 print 把结尾改成一个空格，因此下一条输出留在同一行。","注释和空行被忽略；第三条 print 输出完成状态并换行。"],
'''# 用统一的日期格式标记学习记录
print(2026, 10, 20, sep="/")
print("进度：", end=" ")
print("完成第一课")''',"2026/10/20\n进度： 完成第一课\n",
"用一条 print 输出 A-B-C，再用两条 print 在同一行输出‘学习中...’。",
'''print("A", "B", "C", sep="-")
print("学习", end="")
print("中...")''',"A-B-C\n学习中...\n",
["字符串外的逗号分隔参数；字符串里的逗号只会原样显示。","end='' 不会换行；忘了恢复换行时，后续结果可能挤在一起。"],
"print 可控制分隔和换行；注释服务于读代码的人，不参与运行。",sources=[IO])
lesson(c,"l03","变量：给数据起名字",20,"l02",["使用赋值保存值并更新变量","区分名字、值和赋值时刻"],
"变量像贴在数据上的标签。`pages = 12` 让名字 pages 指向整数 12；等号是‘把右边算出的值交给左边的名字’，不是数学中的恒等式。后面再次赋值，会把这个名字改为指向新值。Python 的值具有类型，名字可以重新绑定；不要把变量想成只能装一种类型的固定容器。\n\n名字区分大小写。课程使用小写英文与下划线组合，例如 pages_read；可读的名字能让你不查注释也知道数据的含义。变量必须先赋值后使用。读取一个变量时，用的是执行到那一刻它指向的值。",
["pages 指向 12；copied 保存当时 pages 的值 12。","pages + 3 先求值为 15，再重新绑定 pages。","输出时 pages 是 15，copied 仍是 12；它不是跟随 pages 变化的公式。"],
'''pages = 12
copied = pages
pages = pages + 3
print("现在读了", pages, "页")
print("更新前是", copied, "页")''',"现在读了 15 页\n更新前是 12 页\n",
"把练习时长 minutes 设为 20，保存到 original，再增加 10。输出更新前后的值。",
'''minutes = 20
original = minutes
minutes = minutes + 10
print(original, minutes)''',"20 30\n",
["Pages 和 pages 是两个不同名字；拼写不一致会造成 NameError。","print('pages') 输出文字 pages；print(pages) 才读取变量的值。"],
"赋值先计算右边再绑定左边。重新赋值只改变这个名字当前指向的值。",sources=[TUTORIAL+"introduction.html"])
lesson(c,"l04","数字与运算顺序",22,"l03",["区分整数与浮点数","使用除法、整除和余数完成数量计算"],
"整数 int 适合记录本数、次数等完整数量，浮点数 float 适合近似表示带小数的测量值。`+ - * /` 分别表示加减乘除；`/` 总是得到浮点结果，`//` 是向负无穷方向取整的商，`%` 是余数，`**` 是幂。对本课的非负整数，整除与余数正好可以回答‘每组几个，可以装多少组，还剩几个’。\n\n乘除比加减先算，括号能明确意图。浮点数采用二进制表示，有些十进制小数不能精确保存，显示时出现很小误差是表示方式造成的。涉及钱时可先使用整数‘分’，后续课程再介绍 Decimal。",
["17 个贴纸每袋放 5 个，整除得到 3 个完整袋。","余数给出未装入完整袋的 2 个。","括号先求 3+2，再乘 4；不加括号时乘法优先。"],
'''stickers = 17
per_bag = 5
print(stickers // per_bag, stickers % per_bag)
print(stickers / per_bag)
print((3 + 2) * 4)
print(3 + 2 * 4)''',"3 2\n3.4\n20\n11\n",
"125 分钟换算成小时和剩余分钟，用 // 与 % 计算。",
'''minutes = 125
hours = minutes // 60
remaining = minutes % 60
print(hours, "小时", remaining, "分钟")''',"2 小时 5 分钟\n",
["除数为 0 会产生 ZeroDivisionError；计算前要确认除数有效。","^ 不是乘方；Python 使用 ** 表示乘方。"],
"选择合适的数值类型，用括号表达优先级，用整除和余数拆分数量。",sources=[TUTORIAL+"introduction.html#numbers"])
lesson(c,"l05","字符串与格式化表达",20,"l04",["连接、重复和计数字符串","用 f 字符串把变量放进文字"],
"字符串 str 表示文本，单引号和双引号都可以，只要前后成对。`+` 连接两个字符串，`*` 让字符串重复指定次数，`len()` 返回字符串中 Unicode 码点的数量。对本课的普通汉字与英文字母，可以把它理解成字符数；复杂表情可能由多个码点组合。\n\nf 字符串在引号前加 f，将大括号内的表达式计算后放入文字。`{price:.2f}` 表示把数值显示为两位小数，显示格式不会改变原值。反斜杠 n 即 `\\n` 表示换行，不是斜杠加字母的两次输出。",
["name 指向文字小禾，stars 是三个星号组成的字符串。","f 字符串读取 name 和 minutes 的值，拼成一句话。","len 统计 Python 的六个字母，最后一条按两位小数显示价格。"],
'''name = "小禾"
minutes = 25
stars = "*" * 3
print(f"{name}学习了{minutes}分钟 {stars}")
print(len("Python"))
price = 3.5
print(f"价格：{price:.2f}")''',"小禾学习了25分钟 ***\n6\n价格：3.50\n",
"用变量保存书名‘Python 笔记’与页数 36，用 f 字符串输出‘Python 笔记：36 页’。",
'''book = "Python 笔记"
pages = 36
print(f"{book}：{pages} 页")''',"Python 笔记：36 页\n",
["没有前缀 f 时，大括号里的名字不会被替换。","字符串与整数不能直接用 + 相加；可用 f 字符串表达混合内容。"],
"字符串负责文本，f 字符串负责把数据清楚地放进文本。",sources=[IO])
lesson(c,"l06","input：让程序听见你",18,"l05",["用 input 接收一行文字","理解输入提示、用户输入与输出的区别"],
"`input('提示')` 会先显示提示，然后等待你提交一行文字，返回时去掉行尾换行符。无论键入的是 18 还是名字，它返回的都是字符串。在 PySlate 中，先运行程序，再在输入框提交数据；等待输入时没有新输出，是正常的暂停。\n\n示例需要两行输入：先姓名，再城市。测试数据只是一组便于重复的输入，你可以自己换内容。提示通过标准输出显示，用户键入的文字是否在控制台回显由运行界面决定；测试期望输出只包含程序实际写出的内容。输入结束却没有足够数据时会产生 EOFError。",
["第一条 input 显示姓名提示并等待，得到‘小禾’。","第二条 input 取得城市；两个变量分别保存两次输入。","print 使用这两个字符串生成问候，不需要把输入内容写死在代码中。"],
'''name = input("姓名：")
city = input("城市：")
print(f"你好，来自{city}的{name}！")''',"姓名：城市：你好，来自杭州的小禾！\n",
"读取相同的两行输入，输出‘小禾的旅行起点是杭州’。提示仍使用‘姓名：’和‘城市：’。",
'''name = input("姓名：")
city = input("城市：")
print(f"{name}的旅行起点是{city}")''',"姓名：城市：小禾的旅行起点是杭州\n",
["输入提示不是变量的值：name 保存你输入的姓名，不保存‘姓名：’。","两次 input 需要两行输入；只提供一行会继续等待或遇到 EOFError。"],
"input 把一行用户输入交给程序，并且总是先交付字符串。",stdin="小禾\n杭州\n",sources=["https://docs.python.org/3.11/library/functions.html#input"])
lesson(c,"l07","类型转换与数值输入",22,"l06",["把输入字符串转换为整数或浮点数","理解转换失败与文本拼接"],
"同样写着 12，字符串 '12' 与整数 12 支持的操作不同：两个字符串相加会连接，两个数字相加才是算术。`int()` 把合适的文本转成整数，`float()` 能解析带小数点的文本，`str()` 能把值转成文本。`type()` 让我们检查值的类型。\n\n转换不是凭空修复任何输入。int('3.5') 会失败，因为文字不是整数格式；int(3.5) 则把已有浮点数向 0 截断。本课先约定输入为合法整数，学到异常处理后再给用户重试机会。把‘读取、转换、计算、显示’分开写，容易找到出错的环节。",
["raw 保存 '12' 这段文字，与自身相加得到 '1212'。","int(raw) 得到数值 12，乘 2 后是 24。","type(raw).__name__ 读取类型名称，帮助确认转换前后的差别。"],
'''raw = input("本数：")
count = int(raw)
print(raw + raw)
print(count * 2)
print(type(raw).__name__, type(count).__name__)''',"本数：1212\n24\nstr int\n",
"仍读取本数，假定每本 15 元，计算总价；不要用字符串重复来计算。",
'''raw = input("本数：")
count = int(raw)
total = count * 15
print(f"总价：{total}元")''',"本数：总价：180元\n",
["int('十二') 不认识中文数词，必须约定输入格式。","input 得到的 '12' 乘 2 会重复成 '1212'，先转成整数才是数值计算。"],
"类型决定运算含义；用户输入参与数学运算前，先明确并完成转换。",stdin="12\n",sources=["https://docs.python.org/3.11/library/functions.html#int"])
lesson(c,"l08","比较与 True、False",20,"l07",["通过比较表达式获得布尔值","区分赋值符号和相等比较"],
"布尔值只有 True 和 False，分别表示条件成立与不成立。`==` 判断相等，`!=` 判断不等，`< <= > >=` 比较大小。它们计算得到一个值，所以也能赋给变量，或者直接打印。\n\n`=` 用于赋值，`==` 用于比较；名称相似但工作不同。比较时要关注类型：字符串 '9' 与 '12' 按字符顺序比较，并不是比较两个数的大小。先把数字文本转成数字，再比较。Python 还支持 0 <= score <= 100 这样的连续比较，可读作分数在闭区间内。",
["score 绑定整数 82，比较 score >= 60 得到 True。","score == 100 为 False；这个比较不会把 score 改成 100。","连续比较同时检查上下界，最终分数依旧为 82。"],
'''score = 82
passed = score >= 60
print(passed)
print(score == 100)
print(0 <= score <= 100)
print(score)''',"True\nFalse\nTrue\n82\n",
"设库存 stock=7、需求 needed=10，输出库存是否足够，以及是否完全用完库存。",
'''stock = 7
needed = 10
print(stock >= needed)
print(stock == needed)''',"False\nFalse\n",
["True 和 False 首字母大写；true 是另一个名字。","用 is 比较普通数字或文字的内容不可靠；内容相等用 ==。"],
"比较表达式产生布尔值；赋值保存值，比较判断值之间的关系。",sources=["https://docs.python.org/3.11/library/stdtypes.html#comparisons"])

c = chapter("flow", "02 · 决策与重复", "入门", "让程序选择一条路径，重复有规律的工作，并能手工追踪每一步。")
lesson(c,"l09","组合条件与短路求值",22,"l08",["用 and、or、not 组合判断","用短路规则避免无效计算"],
"`and` 要求两边都成立，`or` 允许至少一边成立，`not` 反转真假。写入学条件时，‘年龄足够并且有票’对应 and；‘周末或节日’对应 or。组合后先按一句完整中文读一遍，可以发现把‘并且’误写成‘或者’的问题。\n\nPython 从左到右计算条件。and 左侧为假时右侧不再计算；or 左侧为真时右侧不再计算，这叫短路。本例把人数是否大于 0 放在除法前面，人数为 0 时就不会求平均。括号能够让复杂条件的分组更清楚。",
["has_ticket 为 True 且 age>=12 为 True，允许入场。","count 为 0，第一个条件已经为 False，total/count 不会执行。","not 将 False 变成 True；原变量并没有被修改。"],
'''age = 14
has_ticket = True
print(age >= 12 and has_ticket)
count = 0
total = 100
print(count > 0 and total / count >= 60)
print(not False)''',"True\nFalse\nTrue\n",
"设今天不是周末 is_weekend=False，但是假日 is_holiday=True，判断今天是否可以休息；再判断‘不是周末’。",
'''is_weekend = False
is_holiday = True
print(is_weekend or is_holiday)
print(not is_weekend)''',"True\nTrue\n",
["and 与 & 含义不同；本课的逻辑条件使用 and。","先做 total/count 再检查 count 非零，无法防止除零。"],
"组合条件时明确‘都满足’还是‘任一满足’，并利用从左到右的短路规则。",sources=["https://docs.python.org/3.11/library/stdtypes.html#boolean-operations-and-or-not"])
lesson(c,"l10","if：选择一个分支",25,"l09",["编写 if、elif、else 分支","用缩进表示条件控制的范围"],
"if 后面的条件为真时，执行它下方缩进的代码。elif 表示前面没有命中时再检查另一种情况，else 接住剩下的情况。一次 if/elif/else 链只会执行第一个成立的分支；一组独立 if 则可能执行多次。\n\n冒号表示一个代码块即将开始。课程统一每层缩进四个空格，同级语句要对齐。成绩分级从高分往低分判断，否则 95 分会先命中‘大于等于60’，后面的优秀分支就没有机会执行。输入的有效范围也要在分级前检查。",
["score=82 没有超出0至100的有效范围。","它不满足大于等于90，但满足大于等于60，输出‘通过’。","最后的 print 不在任何分支内部，因此总会执行。"],
'''score = 82
if not 0 <= score <= 100:
    print("分数无效")
elif score >= 90:
    print("优秀")
elif score >= 60:
    print("通过")
else:
    print("继续练习")
print("检查结束")''',"通过\n检查结束\n",
"根据 temperature=8 输出衣着建议：低于10为‘穿外套’，10至24为‘长袖’，25及以上为‘短袖’。",
'''temperature = 8
if temperature < 10:
    print("穿外套")
elif temperature < 25:
    print("长袖")
else:
    print("短袖")''',"穿外套\n",
["缺少冒号会导致 SyntaxError；代码块前的冒号与缩进要配套。","混用制表符和空格可能触发 TabError；使用编辑器的四空格缩进。"],
"一条分支链按顺序选择首个成立条件，缩进决定哪些语句属于它。",sources=[CONTROL])
lesson(c,"l11","for：依次处理每个元素",22,"l10",["用 for 遍历字符串","在循环中累计结果"],
"遍历就是依次取出一组数据里的每一项。`for letter in word:` 每次把一个字符交给 letter，再执行缩进的循环体。字符用完后退出循环，继续执行后面的语句；你不需要自己维护一个索引来读字符。\n\n累计变量必须在循环开始前初始化，否则每轮都会重置。本例统计英文单词中的字母 a：每发现一次，就把旧计数加一后重新保存。先能手算每轮的状态，再让程序处理更长的文本，这是检查循环正确性的有效方法。",
["count 初始化为0，letter 依次取得 b、a、n、a、n、a。","只有字符等于 a 的三轮会更新 count。","print 在循环外，最后只输出一次统计值。"],
'''word = "banana"
count = 0
for letter in word:
    if letter == "a":
        count = count + 1
print("a的数量：", count)''',"a的数量： 3\n",
"遍历‘PySlate’，每轮输出一个字符；另用 count 累加字符个数，最后输出总数。",
'''count = 0
for letter in "PySlate":
    print(letter)
    count = count + 1
print("总数：", count)''',"P\ny\nS\nl\na\nt\ne\n总数： 7\n",
["把 count=0 写进循环体，会让每轮从0重新开始。","最终 print 若误缩进到循环内部，会打印多个中间结果。"],
"for 从可遍历的数据中依次取项，循环外初始化，循环内处理，循环后汇总。",sources=[CONTROL])
lesson(c,"l12","range：控制重复次数",22,"l11",["理解 range 的起点、终点与步长","通过边界分析避免少一次或多一次"],
"`range(stop)` 产生从0开始、到 stop 前结束的整数；`range(start, stop, step)` 可以指定起点和步长。终点从不包含在结果内，因此 range(1,6) 正好覆盖1到5。步长为负时倒着走，起点和终点的方向也必须相符。\n\nrange 是按需提供整数的对象，不会为了遍历先生成一份很大的列表。循环变量只是本轮的数值，给它改值不能改变 range 后续会提供哪些数。写数值循环时先写出前两个值与最后一个值，可以及早发现边界错误。",
["range(1,6) 依次提供1、2、3、4、5。","total 从0开始，每轮加上当前 number，最后是15。","range(5,0,-2) 依次输出5、3、1，下一项-1越过终点后停止。"],
'''total = 0
for number in range(1, 6):
    total = total + number
print("合计：", total)
for number in range(5, 0, -2):
    print(number)''',"合计： 15\n5\n3\n1\n",
"输出2、4、6、8、10并累计它们的和。只写一个 for 循环。",
'''total = 0
for number in range(2, 11, 2):
    print(number)
    total = total + number
print("合计：", total)''',"2\n4\n6\n8\n10\n合计： 30\n",
["range(1,5) 不包含5；需要1到5时终点写6。","步长不能为0；起点小于终点而步长为负时通常不会产生任何值。"],
"range 的规则是包含起点、排除终点、按步长前进。",sources=[CONTROL])
lesson(c,"l13","while：条件控制重复",25,"l12",["编写带状态更新的 while 循环","明确循环开始与停止条件"],
"有时不能预先知道要重复几次，例如继续积蓄直到够买书。while 每轮开始前检查条件，条件为真才进入循环体，执行完再回到条件处。与 for 的‘逐项处理’相比，while 适合‘直到某种状态出现’。\n\n写 while 时同时写下三个部分：初始状态、继续条件、状态更新。缺少更新，或者更新方向错误，可能永远无法使条件为假。本例不使用 input，先用确定的零钱增长过程理解循环；交互式菜单同样需要明确的退出命令。",
["money 从0开始，第一次检查0<20成立。","每轮增加7，依次输出7、14、21。","下一次检查21<20为假，退出循环；达到目标可以超过20。"],
'''money = 0
weeks = 0
while money < 20:
    money = money + 7
    weeks = weeks + 1
    print(f"第{weeks}周：{money}元")
print("可以买书了")''',"第1周：7元\n第2周：14元\n第3周：21元\n可以买书了\n",
"从 remaining=3 开始倒数，依次输出3、2、1，循环结束后输出‘出发’。",
'''remaining = 3
while remaining > 0:
    print(remaining)
    remaining = remaining - 1
print("出发")''',"3\n2\n1\n出发\n",
["循环体里没有更新 money，条件会一直为真。","把条件写成 money==20 不能表达‘还不够20就继续’，初始状态就不会进入。"],
"while 在每轮之前检查条件；状态更新必须能让循环最终停止。",sources=[TUTORIAL+"introduction.html#first-steps-towards-programming"])
lesson(c,"l14","break、continue 与搜索",25,"l13",["提前结束当前循环","跳过本轮剩余语句"],
"break 立即离开当前最内层循环，适合找到目标后停止搜索。continue 不离开循环，只跳过本轮后面的语句，转向下一轮。理解它们的区别需要看‘控制接下来去哪里’，而不仅是看输出少了什么。\n\n本例寻找10到20之间第一个能被7整除的数。不能整除时继续下一轮；可以整除时输出并停止。while 中使用 continue 时尤其要小心：如果把状态更新写在 continue 后面，更新可能永远执行不到。先写清晰版本，再考虑用这两个语句简化流程。",
["10、11、12、13 的余数不为0，continue 跳过下面的输出。","number=14 时输出，并由 break 离开整个 for。","循环外的 print 执行一次，说明程序继续运行。"],
'''for number in range(10, 21):
    if number % 7 != 0:
        continue
    print("找到：", number)
    break
print("搜索结束")''',"找到： 14\n搜索结束\n",
"遍历1至6，只输出奇数；遇到5时输出后立刻停止，不处理6。",
'''for number in range(1, 7):
    if number % 2 == 0:
        continue
    print(number)
    if number == 5:
        break''',"1\n3\n5\n",
["continue 只跳过当前轮，下一轮仍会继续；它不能替代退出菜单的 break。","嵌套循环中的 break 只退出它所在的最内层循环。"],
"break 退出当前循环，continue 跳向下一轮；两者都需要明确的使用条件。",sources=[CONTROL])
lesson(c,"l15","嵌套循环与二维任务",25,"l14",["追踪内外循环的执行次数","用嵌套循环生成坐标组合"],
"一层循环遍历行，另一层遍历列，就能处理表格、棋盘与座位。外层每取一个值，内层都会重新从起点完整遍历。两行三列会执行六次内层循环体，而不是五次。\n\n观察缩进可以区分每个位置：最内层的 print 每个座位执行一次，回到外层缩进的 print 每行执行一次，完全退出缩进的 print 最后执行一次。嵌套层数太多会增加理解和运行成本；后续可以把具体工作拆成函数。",
["row=1 时，col 依次取1、2、3，输出第一行三个座位。","外层切到row=2，内层重新从col=1开始。","两层循环结束后，done 的值为6，等于2×3。"],
'''done = 0
for row in range(1, 3):
    for col in range(1, 4):
        print(f"座位{row}-{col}")
        done = done + 1
print("座位数：", done)''',"座位1-1\n座位1-2\n座位1-3\n座位2-1\n座位2-2\n座位2-3\n座位数： 6\n",
"用两层循环打印一个2×2的乘法表，每个组合单独一行，格式为‘1×2=2’。",
'''for left in range(1, 3):
    for right in range(1, 3):
        print(f"{left}×{right}={left * right}")''',"1×1=1\n1×2=2\n2×1=2\n2×2=4\n",
["内外层都命名为 i 会覆盖名字，让人难以分清行与列。","内层范围为3个元素、外层为2个元素时，总轮数为乘积6。"],
"外层固定一项，内层遍历所有项；缩进层次决定语句执行频率。",sources=[CONTROL])
lesson(c,"l16","调试：逐步观察状态",30,"l15",["用最小输入和打印追踪定位逻辑错误","区分语法错误、运行异常与错误结果"],
"程序没有报错，不代表答案正确。语法错误是代码不符合规则，运行异常是执行中遇到不能完成的操作，逻辑错误则是程序跑完但结果不符合目标。调试要先写清期待结果，再找第一次偏离期待的位置。\n\n把问题缩小到能手算的数据：本例要累加1、2、3，先写出预期的累计值1、3、6，再逐轮打印。若曾把 total=number 放进循环，就会看到1、2、3，发现没有保留旧总和。排查结束后可删掉临时输出，或在后续项目中改成可控制的日志。不要同时改许多不相干的地方。",
["第一轮先打印旧total=0和number=1，再更新为1。","第二轮与第三轮依次得到3、6，与手算表一致。","最终值正确后，保留必要结果，移除多余诊断输出即可。"],
'''total = 0
for number in range(1, 4):
    print(f"更新前 total={total}, number={number}")
    total = total + number
    print(f"更新后 total={total}")
print("结果：", total)''',"更新前 total=0, number=1\n更新后 total=1\n更新前 total=1, number=2\n更新后 total=3\n更新前 total=3, number=3\n更新后 total=6\n结果： 6\n",
"求1至4的乘积，初始值应设为几？输出每轮乘积并检查最终为24。",
'''product = 1
for number in range(1, 5):
    product = product * number
    print(number, product)
print("结果：", product)''',"1 1\n2 2\n3 6\n4 24\n结果： 24\n",
["乘积初值设为0会让所有后续结果都为0。","看到最终结果错误就盲目改最后一行，可能掩盖循环内部的真正原因。"],
"先有可验证的预期，再观察状态；定位最早出错的一步比猜测更可靠。",sources=[ERRORS])

c = chapter("data", "03 · 组织一组数据", "基础", "学习字符串处理、常用容器、可变对象与推导式。")
lesson(c,"l17","文本清洗与拆分合并",25,"l16",["调用字符串方法处理文本","解释方法返回的新字符串"],
"字符串方法写在一个文本值后面，通过点号调用。strip() 去掉首尾空白，lower() 转成小写，replace(old,new) 替换指定片段。字符串不可变，方法通常返回新字符串；如果不保存返回结果，原来的变量不会变化。\n\nsplit(',') 把一段文字按逗号拆成一组字符串，结果称为列表，下一课会详细学习。反过来，' / '.join(parts) 用指定分隔符把一组字符串连接起来。真实数据常有多余空格，因此把清洗、拆分、使用分成几步，能看清每一步的结果。",
["strip 去掉首尾空白，lower 得到小写副本。","split 按英文逗号分成三个片段，其中空格还在各片段中。","本例先统一去掉逗号后的空格，再拆分与join，得到整齐的显示文本。"],
'''raw = "  Python, JSON, CSV  "
clean = raw.strip().replace(", ", ",")
parts = clean.split(",")
print(clean.lower())
print(" / ".join(parts))
print(raw == clean)''',"python,json,csv\nPython / JSON / CSV\nFalse\n",
"把‘  Learn-Python-Now  ’清洗成小写，再把连字符改为空格，输出处理结果。",
'''raw = "  Learn-Python-Now  "
clean = raw.strip().lower().replace("-", " ")
print(clean)''',"learn python now\n",
["raw.strip() 不会原地修改 raw，需要把返回结果保存下来。","split(',') 和 split() 不一样，后者按任意连续空白切分。"],
"文本清洗是连续的小变换；保存每个返回值，明确分隔符的含义。",sources=["https://docs.python.org/3.11/library/stdtypes.html#string-methods"])
lesson(c,"l18","列表、索引与遍历",25,"l17",["用列表保存有序数据","用索引和遍历读取元素"],
"列表 list 用方括号包围、逗号分隔多个值，可以保存课程名、成绩或购物项。列表有顺序，索引从0开始：第一个元素是items[0]，最后一个也可写items[-1]。len(items) 是元素个数，最后一个非负索引是 len(items)-1。\n\n需要逐项处理时优先直接 for item in items。需要同时拿到位置时，enumerate(items,start=1) 每轮提供一个编号和一个元素，两个变量按位置接收；这样显示给人的编号能从1开始，同时不改变列表本身的索引规则。",
["subjects 保存三个字符串，索引0读到Python，索引-1读到写作。","enumerate 为列表的元素附上从1开始的显示编号。","每轮 print 展示一项，列表没有被修改。"],
'''subjects = ["Python", "数学", "写作"]
print(subjects[0], subjects[-1])
print("数量：", len(subjects))
for number, subject in enumerate(subjects, start=1):
    print(number, subject)''',"Python 写作\n数量： 3\n1 Python\n2 数学\n3 写作\n",
"建立成绩列表[78,92,85]，输出第2个成绩和最后一个成绩，再用循环求总分。",
'''scores = [78, 92, 85]
print(scores[1], scores[-1])
total = 0
for score in scores:
    total = total + score
print("总分：", total)''',"92 85\n总分： 255\n",
["长度为3的列表不能读取索引3；合法非负索引是0、1、2。","空列表没有最后一个元素，对它使用[-1]会产生 IndexError。"],
"列表保存有序元素，索引从0开始；遍历时可以直接取值或同时取编号。",sources=[DATA])
lesson(c,"l19","修改列表与安全删除",25,"l18",["添加、替换与删除列表元素","避免边遍历边删除导致遗漏"],
"列表是可变对象。append(value) 在末尾添加一个值，items[index]=value 替换指定位置，pop(index) 删除并返回对应元素，不写索引时删除末尾。remove(value) 删除第一个相等的元素，找不到时会出错。修改列表的方法通常返回 None，不要写 items=items.append(...)。\n\n正在遍历的列表若被删除元素，后面的索引会移动，可能跳过某项。筛选任务更适合建立一个新列表。本例从待办项中删除已完成内容，然后通过新列表保留非空文本，避免让遍历与结构修改互相干扰。",
["append 添加‘复习’，索引1被替换成‘写习题’。","pop(0) 返回并删除‘阅读’，剩下两个元素向前移动。","第二段遍历原始列表，把有效项放入另一个列表。"],
'''tasks = ["阅读", "练习"]
tasks.append("复习")
tasks[1] = "写习题"
finished = tasks.pop(0)
print("完成：", finished)
print(tasks)
clean = []
for task in ["阅读", "", "复习"]:
    if task != "":
        clean.append(task)
print(clean)''',"完成： 阅读\n['写习题', '复习']\n['阅读', '复习']\n",
"从[3,0,5,0,8]建立一个只含正数的新列表，保留原有顺序，并打印原列表证明没有修改它。",
'''numbers = [3, 0, 5, 0, 8]
positive = []
for number in numbers:
    if number > 0:
        positive.append(number)
print(positive)
print(numbers)''',"[3, 5, 8]\n[3, 0, 5, 0, 8]\n",
["append 的返回值是 None；把它赋回列表变量会丢掉列表引用。","遍历过程中 remove 同一列表里的多个重复项，可能漏删。"],
"列表修改会改变对象本身；筛选时建立新列表往往更清楚。",sources=[DATA])
lesson(c,"l20","切片、别名与浅复制",30,"l19",["用切片读取一段序列","区分别名和浅复制"],
"切片 items[start:stop:step] 读取一段序列，包含起点、排除终点，和 range 的边界习惯相似。省略起点或终点表示到边缘；[::-1] 以负步长逆序取得副本。字符串也支持同样的切片。切片越过边界通常会自动截到有效范围，单个索引越界则会报错。\n\n`alias=items` 只是让两个名字指向同一个列表。`items[:]` 或 items.copy() 才建立外层副本。本例的元素都是整数，因此修改副本不影响原列表；若元素还是列表，浅复制只复制外层，内层仍被共享。复杂嵌套结构需要重新构造或考虑 copy.deepcopy。",
["items[1:4] 读取索引1、2、3；[::-1] 创建逆序列表。","alias 与 items 共享对象，修改alias[0]也会在items中看到。","copied 是新的外层列表，修改copied[1]不改变items[1]。"],
'''items = [10, 20, 30, 40, 50]
print(items[1:4])
print(items[::-1])
alias = items
copied = items[:]
alias[0] = 99
copied[1] = 88
print(items)
print(copied)''',"[20, 30, 40]\n[50, 40, 30, 20, 10]\n[99, 20, 30, 40, 50]\n[10, 88, 30, 40, 50]\n",
"从[1,2,3,4,5,6]获取前三个数、每隔一个数取一个的结果，以及倒数两个数。",
'''numbers = [1, 2, 3, 4, 5, 6]
print(numbers[:3])
print(numbers[::2])
print(numbers[-2:])''',"[1, 2, 3]\n[1, 3, 5]\n[5, 6]\n",
["stop 指定的位置不包含在切片内。","浅复制不是递归复制；嵌套列表中的内层对象仍可能共享。"],
"切片描述一段序列；赋值共享对象，浅复制建立新外层但不复制所有内部对象。",sources=[DATA])
lesson(c,"l21","元组与解包",25,"l20",["用元组表达固定结构的记录","按位置解包并交换变量"],
"元组 tuple 常用圆括号表示，例如(x,y)，适合表达位置、尺寸等结构固定的一组值。元组自身不可变，不能替换其中某个位置；但如果元组里面放的是可变对象，那个内部对象仍可能变化。因此‘元组不可变’说的是元组保存的引用不能替换。\n\n解包是把一组值按顺序交给多个变量，例如 width,height=size。左右数量必须一致，除非使用星号接住剩余部分。逗号才是创建元组的关键，单元素元组必须写(7,)；单独的(7)仍是整数。交换两个变量也能利用解包，右侧先取得两份旧值。",
["point 记录坐标(3,4)，解包后x和y分别取得3、4。","交换赋值右侧先形成旧y、旧x，再绑定回左侧。","单元素元组的长度为1，结尾逗号不能省略。"],
'''point = (3, 4)
x, y = point
print(x, y)
x, y = y, x
print(x, y)
single = (7,)
print(len(single))''',"3 4\n4 3\n1\n",
"将('小禾', 88)解包成name、score，输出‘小禾得分88’；把a=2、b=9交换后打印。",
'''record = ("小禾", 88)
name, score = record
print(f"{name}得分{score}")
a, b = 2, 9
a, b = b, a
print(a, b)''',"小禾得分88\n9 2\n",
["两个变量接收三项会产生 ValueError，解包数量要匹配。","(7)不是元组，(7,)才是单元素元组。"],
"元组强调固定结构；解包用位置关系把一组数据分配给有意义的名字。",sources=[DATA])
lesson(c,"l22","字典：通过键找到值",28,"l21",["建立和更新键值映射","用 get、items 处理未知键与遍历"],
"字典 dict 用大括号记录‘键:值’。列表回答‘第几个’，字典回答‘哪个名字对应什么值’，适合保存人的资料或类别统计。键必须可哈希，常用字符串或整数；列表不能直接当作键。相同键只保留一项，再次赋值会更新对应的值。\n\n直接读取 data[key] 要求键已存在，否则产生 KeyError。data.get(key,default) 能为未知键提供默认值，但不会自动把它插入字典。items() 每轮提供键与值，可以解包遍历。现代 Python 保留插入顺序，但业务逻辑仍应通过键表达关系，而不是依赖第几个。",
["profile 通过键保存姓名和分数；给score重新赋值更新同一条记录。","city 不存在，get 返回备用文字，没有报错。","items 按插入顺序提供两对键值，输出完整资料。"],
'''profile = {"name": "小禾", "score": 80}
profile["score"] = 86
print(profile["name"], profile["score"])
print(profile.get("city", "未填写"))
for key, value in profile.items():
    print(key, value)''',"小禾 86\n未填写\nname 小禾\nscore 86\n",
"统计列表['书','笔','书','纸','笔','书']中每个物品出现的次数，使用get(...,0)累加。",
'''counts = {}
for item in ["书", "笔", "书", "纸", "笔", "书"]:
    counts[item] = counts.get(item, 0) + 1
for item, count in counts.items():
    print(item, count)''',"书 3\n笔 2\n纸 1\n",
["字典键写错会查到另一项或触发KeyError；字符串键也区分大小写。","{} 是空字典，不能用它表示空集合。"],
"字典通过唯一键组织值；get 处理缺省，items 同时遍历键和值。",sources=[DATA])
lesson(c,"l23","集合、去重与成员判断",25,"l22",["用集合去重和判断成员","求交集、并集与差集"],
"集合 set 只关心某个元素是否存在，不记录重复次数，也没有可依赖的位置顺序。用set(...)可把列表变成集合完成去重，用add增加元素。空集合必须写set()，因为{}已经表示空字典。\n\n`in` 判断成员；a & b 取两边都有的交集，a | b 取并集，a - b 取只属于a的差集。集合输出顺序不能作为正确性的依据；本例用sorted()生成按顺序排列的列表，让每次结果都方便比较。元素必须可哈希，普通字符串与整数适合做集合成员。",
["三次借阅中的Python重复两次，集合只保留一份。","交集找出已经读过又在愿望清单中的书。","差集给出仍未读的愿望书目，并通过sorted稳定显示。"],
'''read = set(["Python", "数学", "Python"])
wanted = {"Python", "写作"}
print("Python" in read)
print(sorted(read & wanted))
print(sorted(wanted - read))
print(sorted(read | wanted))''',"True\n['Python']\n['写作']\n['Python', '写作', '数学']\n",
"把[3,1,3,2,1]去重后升序输出；判断4是否在去重后的集合里。",
'''unique = set([3, 1, 3, 2, 1])
print(sorted(unique))
print(4 in unique)''',"[1, 2, 3]\nFalse\n",
["集合没有第0项，不能写values[0]读取。","直接比较集合打印文本的顺序可能误判，应比较集合本身或排序后再显示。"],
"集合适合存在性、去重与集合运算；需要保序和重复次数时选别的数据结构。",sources=[DATA])
lesson(c,"l24","推导式：清楚地映射和筛选",28,"l23",["把简单循环改写为列表推导式","选择可读的推导式而不是堆叠逻辑"],
"列表推导式把‘从哪里取值、如何筛选、如何变换’写成一个表达式。`[n*n for n in numbers if n>0]` 先从numbers取n，只保留正数，然后计算平方放入新列表。虽然变换部分写在最前面，理解时仍应从for读起。\n\n推导式建立新集合，不会原地修改输入列表。字典推导式用{key:value for ...}，集合推导式用{value for ...}。如果变换需要多条语句、异常处理或复杂副作用，普通循环更易读。不要只为缩短行数把多层条件和嵌套循环全部塞进去。",
["numbers 中只有2、5大于0，它们被变换成4、25。","第二个推导式把每个词映射到长度，生成字典。","两次构造都不修改原始numbers与words。"],
'''numbers = [-2, 0, 2, 5]
squares = [number * number for number in numbers if number > 0]
print(squares)
words = ["cat", "python"]
lengths = {word: len(word) for word in words}
print(lengths)''',"[4, 25]\n{'cat': 3, 'python': 6}\n",
"从range(1,8)筛选偶数，把每个偶数乘10，得到[20,40,60]；用一条列表推导式。",
'''values = [number * 10 for number in range(1, 8) if number % 2 == 0]
print(values)''',"[20, 40, 60]\n",
["过滤条件的if放在for后；想做二选一变换时另有表达式写法，不要混淆。","对每个元素只调用print并收集None，通常没有必要写成列表推导式。"],
"推导式适合清楚的映射和筛选，表达式应比普通循环更容易理解。",sources=[DATA])

c = chapter("functions", "04 · 把程序拆成清楚的部件", "中级", "学习函数、模块、异常与文件路径，让代码可以复用并可靠地处理输入。")
lesson(c,"l25","函数、参数与返回值",30,"l24",["定义并调用完成单一工作的函数","区分return返回值和print显示结果"],
"函数把一段有名字的工作封装起来。def 开始定义，圆括号中列出参数，缩进体里写处理过程；执行定义只创建函数，调用时函数体才真正运行。参数是每次调用收到的数据，本例同一个函数能处理不同的矩形尺寸。\n\nreturn 把结果交还调用处并结束本次函数执行，调用者能继续计算或保存结果。print只把内容显示出来，不替代return。没有显式return的函数默认返回None。优先让计算函数返回数据，让负责界面的代码决定如何显示，后续测试会容易得多。",
["def 建立area函数，这时还没有做乘法。","第一次调用把3交给width、4交给height，返回12保存到first。","第二次调用使用2和5，独立计算并返回10，最后统一输出。"],
'''def area(width, height):
    result = width * height
    return result

first = area(3, 4)
second = area(2, 5)
print(first, second)
print("合计：", first + second)''',"12 10\n合计： 22\n",
"定义to_minutes(hours,minutes)，返回总分钟数，打印2小时15分钟对应的结果。",
'''def to_minutes(hours, minutes):
    return hours * 60 + minutes

print(to_minutes(2, 15))''',"135\n",
["只在函数里print而不return，调用处拿到的通常是None。","return后同一函数体内的普通语句不会继续执行；不要把必要工作写在它后面。"],
"函数接收参数、完成工作、返回结果；调用者负责决定如何使用结果。",sources=[CONTROL])
lesson(c,"l26","默认参数与关键字调用",28,"l25",["选择位置参数或关键字参数传值","使用安全的默认参数"],
"位置参数按顺序对应参数名；关键字参数显式写出名字，例如greet(name='小禾')，适合让多个选项更清楚。定义中的默认值让调用者可以省略某个参数：greeting='你好'表示没有传入时使用该值。没有默认值的参数通常写在有默认值的参数前面。\n\n默认值只在函数定义时求值一次，因此不要把会被修改的列表或字典作为普通累积函数的默认值。本课使用不可变字符串作为默认值；下一课再演示为每次调用新建列表的方法。选择默认值时要考虑调用者最常需要的行为，而不只是为了少写参数。",
["第一轮调用只传name，因此使用默认greeting。","第二轮按名字传入两个参数，顺序不影响对应关系。","返回值都是字符串，外层print才负责显示。"],
'''def greet(name, greeting="你好"):
    return f"{greeting}，{name}！"

print(greet("小禾"))
print(greet(greeting="早上好", name="阿青"))''',"你好，小禾！\n早上好，阿青！\n",
"定义total_price(price,count=1)，返回单价乘数量。分别计算只传单价8以及price=8,count=3的结果。",
'''def total_price(price, count=1):
    return price * count

print(total_price(8))
print(total_price(count=3, price=8))''',"8\n24\n",
["调用中在关键字参数后再写普通位置参数会造成语法错误。","默认列表会在多次调用间共享；若每次应有新列表，使用None作为默认再创建。"],
"默认参数提供常见行为，关键字参数让调用意图更清楚。",sources=[CONTROL])
lesson(c,"l27","作用域、共享对象与纯函数",32,"l26",["区分局部名字与外部名字","控制函数对可变数据的修改"],
"作用域决定一个名字在什么位置可以被找到。函数内赋值产生的名字通常是局部名字，不会自动改写函数外的同名变量。读取名字时，Python先查当前局部，再查外层函数、模块和内置名字。减少依赖全局变量，把需要的数据显式传入，程序会更容易理解和测试。\n\n参数绑定到调用者传入的对象。若对象是列表，在函数中append会修改共享对象；只把参数名重新赋值则是改变局部名字。本例先复制传入列表，返回新列表，原数据保持稳定。None表示没有传入集合，每次调用时再创建，避免默认列表被不同调用共享。",
["label在函数内绑定成‘局部’，不改变外部的‘全局’。","add_note先新建或复制列表，再添加新项。","调用得到两项的新列表，原列表仍只有一项。"],
'''label = "全局"

def add_note(note, notes=None):
    label = "局部"
    if notes is None:
        notes = []
    else:
        notes = notes.copy()
    notes.append(note)
    return notes

original = ["阅读"]
updated = add_note("练习", original)
print(label)
print(original)
print(updated)''',"全局\n['阅读']\n['阅读', '练习']\n",
"写函数with_bonus(scores,bonus)，返回每个分数加bonus后的新列表，并证明原列表[60,80]不变。",
'''def with_bonus(scores, bonus):
    return [score + bonus for score in scores]

original = [60, 80]
print(with_bonus(original, 5))
print(original)''',"[65, 85]\n[60, 80]\n",
["在函数里重新给同名变量赋值，不会自动更新外部变量。","参数收到列表并不意味着自动复制；修改对象可能影响调用者。"],
"分清名字的作用域与对象的共享关系；纯计算尽量返回新结果。",sources=[CLASSES+"#python-scopes-and-namespaces"])
lesson(c,"l28","导入模块与标准库",25,"l27",["用import复用模块里的工具","理解模块命名与搜索中的遮蔽问题"],
"模块通常是一个包含Python定义的.py文件。import math加载标准库math，并让当前代码通过math.sqrt使用它的工具。from math import ceil只把指定名字带入当前作用域。前一种写法更能看出来源，后一种适合少量、明确的名字。\n\n模块中的顶层代码在首次导入时会执行，因此不要把交互菜单放在工具模块顶层。自建模块时，把函数放在utils.py，main.py写import utils；两个文件放在同一项目目录。本课先使用已有模块，综合项目再实际建立多个文件。自己的文件不要命名为math.py、json.py等标准库名字，否则可能遮蔽真正模块。",
["import加载math并绑定模块名，sqrt通过模块名访问。","ceil被直接导入，可以不写math前缀。","两种写法调用的是同一标准库中不同工具，不需要联网下载。"],
'''import math
from math import ceil

print(math.sqrt(81))
print(ceil(2.3))
print(f"圆周率：{math.pi:.3f}")''',"9.0\n3\n圆周率：3.142\n",
"导入math，用math.hypot(3,4)计算直角三角形斜边，再用math.floor(4.9)向下取整。",
'''import math

print(math.hypot(3, 4))
print(math.floor(4.9))''',"5.0\n4\n",
["import后仍要按导入方式使用名字，import math并不会自动创建sqrt这个局部名字。","自己的脚本命名为random.py可能让import random导入错误文件。"],
"模块是代码复用单位；显式导入并保持文件名字清楚，能减少依赖冲突。",sources=[TUTORIAL+"modules.html"])
lesson(c,"l29","包与模块目录",28,"l28",["识别包、子模块和导入路径","理解代码组织与网络访问的区别"],
"包把多个模块组织到同一个命名空间。传统包目录里有__init__.py，例如studytools目录中放stats.py，就能使用from studytools import stats。完整导入名用点号表达层级，文件路径则由目录和文件组成，两者互相对应但不是随意拼接的字符串。\n\n本例使用标准库urllib包里的parse子模块，只负责转换URL中的文字结构，不会发出网络请求。包名中带url并不代表调用它一定联网。自己的小包建议先保留一个清楚的入口main.py，依赖方向从入口指向工具模块，避免两个模块在顶层互相导入。当前解释器搜索不到的包不会因为写了import就自动安装。",
["from urllib.parse直接导入指定子模块中的两个函数。","urlencode把字典转换成查询字符串，空格会编码为加号。","parse_qs把查询文本解析回字典，值用列表保存以支持同名参数重复出现。"],
'''from urllib.parse import urlencode, parse_qs

query = urlencode({"topic": "Python notes", "page": 2})
print(query)
parsed = parse_qs(query)
print(parsed["topic"][0])
print(parsed["page"][0])''',"topic=Python+notes&page=2\nPython notes\n2\n",
"从urllib.parse导入quote和unquote，对‘learn Python’先编码再解码，打印两步结果。",
'''from urllib.parse import quote, unquote

encoded = quote("learn Python")
print(encoded)
print(unquote(encoded))''',"learn%20Python\nlearn Python\n",
["导入路径里用点号，不是写from studytools/stats import...。","ModuleNotFoundError可能来自搜索路径或尚未安装，不能靠重复点击运行修复。"],
"包用层次结构管理模块；清楚的入口与单向依赖让多文件项目更容易维护。",sources=[TUTORIAL+"modules.html#packages"])
lesson(c,"l30","异常处理与输入验证",32,"l29",["捕获预期异常并给出有用提示","用raise表达违反规则的数据"],
"异常表示某一步操作无法按正常方式完成。try中放可能失败的短小操作，except写能处理的具体异常类型。捕获以后程序可继续；没有处理的异常会向调用处传播，最终显示traceback。阅读traceback时先看最后一行的异常类型与消息，再看指向的文件行号。\n\n格式正确不等于业务有效：int('120')能转换，但若代表分数就超出范围。函数可以raise ValueError明确拒绝这种数据。不要用一个大范围except把所有错误静默吞掉，否则拼写错误和程序缺陷也会被伪装成正常情况。本课只捕获与输入有关的ValueError。",
["'85'成功转换并通过范围检查，函数返回85。","'abc'在int阶段触发ValueError，被调用处捕获。","'120'转换成功但违反范围，由函数主动raise，输出相应提示。"],
'''def parse_score(text):
    value = int(text)
    if not 0 <= value <= 100:
        raise ValueError("分数必须在0到100之间")
    return value

for text in ["85", "abc", "120"]:
    try:
        print("有效：", parse_score(text))
    except ValueError:
        print("无效输入：", text)''',"有效： 85\n无效输入： abc\n无效输入： 120\n",
"定义safe_divide(a,b)，b为0时raise ValueError('除数不能为0')。依次尝试(8,2)与(8,0)，捕获ValueError并打印其消息。",
'''def safe_divide(a, b):
    if b == 0:
        raise ValueError("除数不能为0")
    return a / b

for a, b in [(8, 2), (8, 0)]:
    try:
        print(safe_divide(a, b))
    except ValueError as error:
        print(error)''',"4.0\n除数不能为0\n",
["except:会连中断等信号一并捕获，通常应指定能恢复处理的异常类型。","把int转换写在try之外，except就接不到那里发生的异常。"],
"异常处理围绕预期失败建立恢复路径；raise让函数明确拒绝不符合规则的数据。",sources=[ERRORS])
lesson(c,"l31","文件读写与编码",32,"l30",["以UTF-8读写文本文件","理解w覆盖、a追加与自动关闭"],
"内存里的变量在进程退出后消失，文件能把结果留在项目目录中。open(path,mode,encoding)打开文件，'w'写入并清空已有内容，'a'追加，'r'读取。相对路径如'lesson_note.txt'是相对于当前工作目录，不一定是代码文件所在目录；自由编程时请把资源放在同一项目里。\n\nwith是管理资源的语法。进入代码块后获得文件对象，离开块时自动关闭，即使中途发生异常也会做清理。明确encoding='utf-8'让中文在Windows与Android之间更稳定。示例只写自己的lesson_note.txt；学习文件操作前先了解覆盖语义，别把路径换成重要文件。",
["第一段用w新建示例文件，写入一行并在末尾保存换行符。","第二段用a追加另一行，不覆盖第一行。","最后以r读取完整文本；end=''避免给已有换行再添一个换行。"],
'''with open("lesson_note.txt", "w", encoding="utf-8") as file:
    file.write("第一天：变量\n")
with open("lesson_note.txt", "a", encoding="utf-8") as file:
    file.write("第二天：循环\n")
with open("lesson_note.txt", "r", encoding="utf-8") as file:
    text = file.read()
print(text, end="")'''.replace('变量\n"','变量\\n"').replace('循环\n"','循环\\n"'),"第一天：变量\n第二天：循环\n",
"新建practice_note.txt，写入‘阅读’和‘练习’两行。再逐行读取，用strip()去掉行尾换行并加上序号。",
'''with open("practice_note.txt", "w", encoding="utf-8") as file:
    file.write("阅读\\n练习\\n")
with open("practice_note.txt", encoding="utf-8") as file:
    for index, line in enumerate(file, start=1):
        print(index, line.strip())''',"1 阅读\n2 练习\n",
["以w打开现有文件会截断内容；保留原内容应选a或先读出再设计更新流程。","未指定编码可能随平台改变，中文文本应明确使用utf-8。"],
"文件让数据持久化；选择正确模式和编码，用with确保及时关闭资源。",sources=[IO])
lesson(c,"l32","pathlib：可移植的文件路径",30,"l31",["用Path组合目录与文件名","检查路径并列出项目文件"],
"路径既包含文件名也包含目录层级。手写反斜杠容易在字符串里形成转义，而且Windows与Android使用的路径分隔符习惯不同。pathlib.Path表示路径，使用/连接子路径，由平台决定实际分隔符。Path('demo_data')/'note.txt'比手工拼字符串清楚。\n\nmkdir(parents=True,exist_ok=True)创建所需目录并允许它已经存在；exists检查存在性，is_file检查是否是文件，glob按简单模式列出匹配项。read_text、write_text适合小文本。相对路径的根仍是当前工作目录；Path不会自动建立安全沙箱，也不会阻止你指定外部绝对路径。",
["构造demo_data目录对象并创建目录。","通过/取得note.txt路径，写入中文文本后再读取。","glob查找目录中的txt文件，以排序后的文件名稳定输出。"],
'''from pathlib import Path

folder = Path("demo_data")
folder.mkdir(parents=True, exist_ok=True)
note = folder / "note.txt"
note.write_text("路径可以跨平台", encoding="utf-8")
print(note.is_file())
print(note.read_text(encoding="utf-8"))
for file in sorted(folder.glob("*.txt")):
    print(file.name)''',"True\n路径可以跨平台\nnote.txt\n",
"创建practice_data文件夹，把‘完成’写入result.txt，打印文件后缀、文件名和读回的内容。",
'''from pathlib import Path

folder = Path("practice_data")
folder.mkdir(exist_ok=True)
file = folder / "result.txt"
file.write_text("完成", encoding="utf-8")
print(file.suffix)
print(file.name)
print(file.read_text(encoding="utf-8"))''',".txt\nresult.txt\n完成\n",
["Path只是路径描述，构造它不会自动创建目录或文件。","直接拼接Windows反斜杠可能形成\\n、\\t等转义，应使用Path和/。"],
"用Path表达路径关系，明确当前工作目录，再执行读写与目录操作。",sources=["https://docs.python.org/3.11/library/pathlib.html"])

c = chapter("processing", "05 · 数据处理与可靠计算", "中级", "读写JSON与CSV，选择标准库，理解排序、复杂度和自动校验。")
lesson(c,"l33","JSON：保存结构化数据",32,"l32",["在Python结构与JSON文本间转换","验证读回的数据结构"],
"JSON是一种通用文本格式，能表达对象、数组、数字、字符串、布尔与空值。Python的dict、list和简单值可以转换为JSON；但集合、自定义对象等不能直接序列化。json.dumps把数据转成字符串，json.loads解析字符串；dump和load则直接操作文件对象。\n\nensure_ascii=False让中文按原文字保存，indent=2增加缩进便于检查；这些显示选项不会改变数据含义。读取文件可能遇到缺失、格式损坏或数据结构不符合预期。JSON能解析成功并不代表包含你要的键，所以仍需业务验证。不要为了加载数据而执行eval，JSON解析已经有专门工具。",
["把含两项待办的字典转成JSON并保存到lesson_tasks.json。","再次从文件读取并解析，得到新的字典和列表。","统计done为True的任务，证明读到的是可计算的结构而非整段文字。"],
'''import json
from pathlib import Path

data = {"tasks": [{"title": "阅读", "done": True}, {"title": "练习", "done": False}]}
file = Path("lesson_tasks.json")
file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
loaded = json.loads(file.read_text(encoding="utf-8"))
done = 0
for task in loaded["tasks"]:
    if task["done"]:
        done += 1
print(loaded["tasks"][0]["title"])
print("已完成：", done)''',"阅读\n已完成： 1\n",
"把字典{'name':'小禾','level':2}存入profile.json再读回，输出name与level+1。",
'''import json
from pathlib import Path

file = Path("profile.json")
file.write_text(json.dumps({"name": "小禾", "level": 2}, ensure_ascii=False), encoding="utf-8")
profile = json.loads(file.read_text(encoding="utf-8"))
print(profile["name"], profile["level"] + 1)''',"小禾 3\n",
["JSON字符串与键使用双引号，单引号形式的Python字典文本不是合法JSON。","json.loads需要文本；给它直接传Path对象不能自动读取文件。"],
"JSON连接文件文本与结构化数据；解析后仍要验证预期字段和业务规则。",sources=["https://docs.python.org/3.11/library/json.html"])
lesson(c,"l34","CSV：表格读写",32,"l33",["使用DictReader按列名读取","正确处理CSV引号、换行与数字类型"],
"CSV把每行记录保存为带分隔符的文本，适合与电子表格交换。字段里本身可能含逗号、引号甚至换行，不能可靠地靠split(',')解析。csv模块会处理这些格式细节；DictReader根据首行列名把每行转换成字典，DictWriter按指定列顺序写入。\n\n以newline=''打开CSV文件，让csv模块管理换行，可避免Windows上出现多余空行。读回的字段默认是字符串，成绩或价格要明确转换。与外部电子表格交换时可按约定使用utf-8-sig兼容BOM；课程自建文件统一utf-8。缺列、非数字或空值需要定义处理策略。",
["writer先写表头，再写两条记录；‘小禾,甲组’中的逗号由模块自动加引号保护。","DictReader按列名提供字典，因此可以用row['score']取值。","score转成整数后累加，最终输出两人的总分。"],
'''import csv

with open("lesson_scores.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["name", "score"])
    writer.writeheader()
    writer.writerows([{"name": "小禾,甲组", "score": 80}, {"name": "阿青", "score": 90}])
with open("lesson_scores.csv", newline="", encoding="utf-8") as file:
    rows = list(csv.DictReader(file))
print(rows[0]["name"])
total = 0
for row in rows:
    total += int(row["score"])
print(total)''',"小禾,甲组\n170\n",
"使用csv.writer写入两行商品数据：['book',2]与['pen',3]。用csv.reader读回，输出商品名与数量加1后的值。",
'''import csv

with open("items.csv", "w", newline="", encoding="utf-8") as file:
    csv.writer(file).writerows([["book", 2], ["pen", 3]])
with open("items.csv", newline="", encoding="utf-8") as file:
    for name, quantity in csv.reader(file):
        print(name, int(quantity) + 1)''',"book 3\npen 4\n",
["CSV读出的'80'仍是字符串，不转换就可能发生拼接或类型错误。","手写split(',')无法处理字段内逗号，应使用csv模块。"],
"用csv模块处理格式，用类型转换处理含义，别把表格文本等同于数值数据。",sources=["https://docs.python.org/3.11/library/csv.html"])
lesson(c,"l35","math、random 与可重复实验",28,"l34",["选择标准库的数值工具","控制随机示例使调试能够复现"],
"标准库提供已经实现并维护的常见功能。math适合平方根、取整、数值常量等；random提供伪随机选择。伪随机序列由内部状态决定，适合游戏与模拟，不适合密码、验证码或安全令牌，安全随机值应看secrets模块。\n\nRandom(seed)创建独立随机对象，不影响其他代码的全局随机状态。固定种子方便复现同一环境中的问题，但不要把复杂跨版本随机序列当作永久文件格式。本课先从只含一个元素的候选表选择，输出必定清楚，再用范围检查验证randint包含两端。练习改变范围，观察多次运行，而不是把随机结果硬编码。",
["sqrt与isclose对数值计算进行检查，避免直接比较近似浮点数。","choice的候选表只有一个词，稳定返回‘继续练习’。","randint(1,6)得到含端点的骰子值，用比较检查范围。"],
'''import math
import random

rng = random.Random(2026)
print(math.sqrt(144))
print(math.isclose(0.1 + 0.2, 0.3))
print(rng.choice(["继续练习"]))
die = rng.randint(1, 6)
print(1 <= die <= 6)''',"12.0\nTrue\n继续练习\nTrue\n",
"创建Random(7)，生成100个1至6之间的整数，输出数量并验证所有数都在合法范围；不要求猜出具体随机序列。",
'''import random

rng = random.Random(7)
values = [rng.randint(1, 6) for _ in range(100)]
print(len(values))
print(all([1 <= value <= 6 for value in values]))''',"100\nTrue\n",
["random不能用于生成密码等安全敏感数据。","用==比较本应相等的浮点近似值可能失败，可按问题容差使用math.isclose。"],
"选用标准库数值工具，随机任务要区分模拟与安全用途，并保留可复现的验证方法。",sources=["https://docs.python.org/3.11/library/math.html","https://docs.python.org/3.11/library/random.html"])
lesson(c,"l36","日期与精确十进制金额",32,"l35",["用date与timedelta做日期计算","从字符串构造Decimal避免先引入浮点误差"],
"日期不是把年月日拼在一起的整数。datetime.date表示一个日历日期，timedelta表示日期或时间的差量，相加时标准库会处理跨月和闰年。isoformat输出年-月-日的固定格式，适合文件存储与交换。本例采用固定日期让结果可重复，实际项目可以按需求读取今天的日期。\n\n金额要求十进制规则时使用decimal.Decimal，构造时优先传文字，如Decimal('0.10')。如果先写成浮点0.1，误差可能已经产生再被带入Decimal。quantize配合ROUND_HALF_UP可以明确四舍五入规则；不同业务可能规定不同舍入方式，应先明确规则再实现。",
["2026-10-20加7天由日期类型计算为2026-10-27。","0.10与0.20都从字符串构建成精确十进制值。","quantize把总额规范到两位小数，输出0.30。"],
'''from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

start = date(2026, 10, 20)
print((start + timedelta(days=7)).isoformat())
amount = Decimal("0.10") + Decimal("0.20")
print(amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))''',"2026-10-27\n0.30\n",
"计算2024-02-28两天后的日期；计算3件单价2.35元商品的总价，以两位小数显示。",
'''from datetime import date, timedelta
from decimal import Decimal

print((date(2024, 2, 28) + timedelta(days=2)).isoformat())
total = Decimal("2.35") * 3
print(f"{total:.2f}")''',"2024-03-01\n7.05\n",
["手工给日数加7不能处理跨月，应使用timedelta。","Decimal(0.1)会接收已经存在的二进制近似值；Decimal('0.1')更符合十进制输入意图。"],
"选择能表达业务规则的类型：日期交给datetime，精确十进制计算交给Decimal。",sources=["https://docs.python.org/3.11/library/datetime.html","https://docs.python.org/3.11/library/decimal.html"])
lesson(c,"l37","Counter、defaultdict 与队列",30,"l36",["按任务选择计数器、分组字典和双端队列","解释FIFO与列表首端操作的差别"],
"collections包含常见容器的专门实现。Counter统计可哈希元素的次数；defaultdict(list)在首次访问某个不存在的键时自动创建空列表，适合分组；deque能高效地在两端添加和移除元素，适合先进先出队列。选择它们可以减少重复编写的边界处理。\n\n队列与栈的规则不同：队列先来先处理，栈后进先出。列表末尾append/pop适合栈；总从列表开头pop(0)会移动后面的元素，大队列可用deque.popleft。本课先认识操作含义，再在算法课里讨论随数据量增长的成本。defaultdict访问未知键会创建记录，检查存在性时可先用in。",
["Counter把词语映射到出现次数，读取‘书’得到2。","defaultdict为每个类别创建列表，append加入姓名。","deque先加入A再加入B，popleft按先来顺序取出A。"],
'''from collections import Counter, defaultdict, deque

counts = Counter(["书", "笔", "书"])
print(counts["书"])
groups = defaultdict(list)
for category, name in [("读书", "小禾"), ("跑步", "阿青"), ("读书", "小川")]:
    groups[category].append(name)
print(groups["读书"])
queue = deque(["A", "B"])
print(queue.popleft())
print(list(queue))''',"2\n['小禾', '小川']\nA\n['B']\n",
"用Counter统计‘banana’，按sorted(counts)的字母顺序输出字符和次数；用deque按顺序取出两个任务。",
'''from collections import Counter, deque

counts = Counter("banana")
for letter in sorted(counts):
    print(letter, counts[letter])
tasks = deque(["阅读", "练习"])
while tasks:
    print(tasks.popleft())''',"a 3\nb 1\nn 2\n阅读\n练习\n",
["defaultdict(list)传的是创建列表的工具list，不是提前创建好的[]。","deque没有普通列表那样的切片操作；需要切片时可先转换为list。"],
"数据结构应该贴合任务：计数用Counter，分组用defaultdict，队列用deque。",sources=["https://docs.python.org/3.11/library/collections.html"])
lesson(c,"l38","排序、key与稳定性",30,"l37",["区分sorted返回新列表与list.sort原地修改","用key函数描述业务排序规则"],
"sorted(iterable)接受可遍历数据并返回新列表，原列表不变；list.sort()直接修改列表并返回None。默认按元素比较，reverse=True可降序。记录往往不能按整个字典直接比较，因此key参数接收一个函数，告诉排序工具‘用哪个值当作比较依据’。\n\n本例将记录按分数从高到低排。key函数只负责提取分数，不负责输出，也不要在里面修改记录。Python排序具有稳定性：当键相等时，保留它们原来的先后顺序。若要多级排序，可以返回元组，例如(-score,name)，先按负分数升序再按姓名升序。",
["score_key从每条记录中读出score。","sorted按该键降序，90分的阿青排在第一。","小禾与小川都是80分，保持输入时的相对顺序；原records顺序没有变化。"],
'''def score_key(record):
    return record["score"]

records = [{"name": "小禾", "score": 80}, {"name": "阿青", "score": 90}, {"name": "小川", "score": 80}]
ranked = sorted(records, key=score_key, reverse=True)
for record in ranked:
    print(record["name"], record["score"])
print("原首项：", records[0]["name"])''',"阿青 90\n小禾 80\n小川 80\n原首项： 小禾\n",
"把['pear','fig','banana','kiwi']按字符串长度升序排序，使用key=len，并打印原列表。",
'''words = ["pear", "fig", "banana", "kiwi"]
print(sorted(words, key=len))
print(words)''',"['fig', 'pear', 'kiwi', 'banana']\n['pear', 'fig', 'banana', 'kiwi']\n",
["key需要函数对象，如key=len；写key=len(words)会提前得到整数，无法用作工具。","items=items.sort()会把items变成None。"],
"排序的核心是明确比较键；留意是否修改原数据以及同键元素的顺序。",sources=["https://docs.python.org/3.11/howto/sorting.html"])
lesson(c,"l39","查找算法与复杂度",35,"l38",["实现线性查找与二分查找","用增长趋势比较算法而不是只看一次计时"],
"算法是解决问题的一组明确步骤。线性查找从头逐项比较，最坏需要检查n项，记作O(n)。二分查找要求数据已按同一规则排序：每次看中间，排除不可能的半边，查找成本随n大致按对数增长，记作O(log n)。预先排序也有成本，不能忽略它来宣称一次查询总是更快。\n\n复杂度描述数据量增长时的趋势，不是精确秒数。本例使用左闭右开的区间[low,high)：low可能命中，high不属于搜索范围。中间值偏小时low移动到mid+1，偏大时high移动到mid。每轮区间必须缩小，否则可能死循环。",
["目标7在有序列表中，初始区间覆盖索引0到5。","mid指向7时直接返回索引；找不到则不断缩小区间。","目标8不在列表中，最终low等于high，返回-1代表未找到。"],
'''def binary_find(values, target):
    low, high = 0, len(values)
    while low < high:
        middle = (low + high) // 2
        if values[middle] == target:
            return middle
        if values[middle] < target:
            low = middle + 1
        else:
            high = middle
    return -1

values = [1, 3, 5, 7, 9, 11]
print(binary_find(values, 7))
print(binary_find(values, 8))
print(binary_find([], 1))''',"3\n-1\n-1\n",
"写线性查找函数linear_find，返回第一次匹配的索引，未找到返回-1。验证空列表、首项、末项和缺失值。",
'''def linear_find(values, target):
    for index, value in enumerate(values):
        if value == target:
            return index
    return -1

for target in [2, 8, 9]:
    print(linear_find([2, 4, 8], target))
print(linear_find([], 2))''',"0\n2\n-1\n-1\n",
["对未排序列表直接二分，可能漏掉确实存在的值。","更新low=middle可能在区间只剩两个位置时卡住，必须证明搜索区间每轮缩小。"],
"选算法先检查前提，再检查边界和区间收缩；复杂度比较的是规模增长趋势。",sources=["https://docs.python.org/3.11/library/bisect.html"])
lesson(c,"l40","assert与边界测试",30,"l39",["把预期结果写成可执行断言","为正常、空值与边界选择测试"],
"测试把‘应该怎样’变成能重复执行的检查。assert condition在条件为假时触发AssertionError，因此能让错误在出现的位置被发现。好的测试不只是把实现再写一遍，而是从要求出发选择有意义的输入和独立预期：正常值、端点、空集合、非法值都值得考虑。\n\n本例把分数夹到0至100之间。测试包括负数、恰好0、中间值、恰好100和超大值，分别覆盖三条路径及端点。assert适合开发检查与测试，不能替代用户输入验证，因为以优化模式启动Python时assert可能被移除。业务验证仍应使用if与raise。",
["clamp先判断下界，再判断上界，合法值原样返回。","每对输入与预期都独立验证，相同函数被调用五次。","任何断言失败都会停止程序；全部通过才显示最后一行。"],
'''def clamp(score):
    if score < 0:
        return 0
    if score > 100:
        return 100
    return score

for value, expected in [(-1, 0), (0, 0), (60, 60), (100, 100), (101, 100)]:
    assert clamp(value) == expected, f"边界失败：{value}"
print("5项边界测试通过")''',"5项边界测试通过\n",
"测试函数is_even(number)，至少覆盖0、正奇数、正偶数和负偶数；全部通过后输出‘4项测试通过’。",
'''def is_even(number):
    return number % 2 == 0

assert is_even(0) is True
assert is_even(3) is False
assert is_even(4) is True
assert is_even(-2) is True
print("4项测试通过")''',"4项测试通过\n",
["只测试一个普通输入，往往发现不了空值和端点问题。","不能用assert作为必须执行的权限或输入校验，优化模式可能移除它。"],
"把明确需求转成独立预期，用少量有代表性的测试覆盖关键路径与边界。",sources=["https://docs.python.org/3.11/reference/simple_stmts.html#the-assert-statement"])

c = chapter("advanced", "06 · 独立开发的语言工具", "进阶", "通过对象、迭代、装饰器、上下文管理和测试理解可维护项目；认识环境与依赖的边界。")
lesson(c,"l41","类、对象与实例状态",35,"l40",["定义带属性和方法的类","让每个实例拥有独立状态"],
"当数据和围绕它的操作经常一起出现时，可以用类组织。class定义一种对象的结构与行为，调用类创建实例。__init__在实例创建后初始化状态，self指向本次方法调用的那个实例，self.title等属性保存在该实例上。普通函数关注输入输出，方法多了所属对象的上下文。\n\n本例两个任务各有标题和完成状态。状态应在__init__中通过self赋值，特别是列表、字典等可变状态；若放成类属性，多个实例可能共享同一个对象。类不是所有问题的必选答案，少量纯计算仍适合直接用函数。",
["调用Task两次创建两个实例，分别保存自己的title和done。","first.finish()把first.done改为True，方法收到的self是first。","second.done仍为False，说明它们的实例属性独立。"],
'''class Task:
    def __init__(self, title):
        self.title = title
        self.done = False

    def finish(self):
        self.done = True

first = Task("阅读")
second = Task("练习")
first.finish()
print(first.title, first.done)
print(second.title, second.done)''',"阅读 True\n练习 False\n",
"定义Counter类，初始value=0，add(amount)增加计数。建立两个实例，只给第一个增加3，输出两者value。",
'''class Counter:
    def __init__(self):
        self.value = 0

    def add(self, amount):
        self.value = self.value + amount

first = Counter()
second = Counter()
first.add(3)
print(first.value, second.value)''',"3 0\n",
["实例方法忘记第一个self参数，调用时会出现参数数量错误。","把所有任务的可变列表放在类属性上，可能让不同实例意外共享。"],
"类把状态与操作组织在一起；实例通过self保存各自的属性。",sources=[CLASSES])
lesson(c,"l42","继承、覆盖与组合",35,"l41",["用继承复用真正的共同接口","通过super调用父类行为并认识组合"],
"继承描述一种‘也是’关系。TimedTask继承Task，既有普通任务的标题，又增加分钟数。子类可以覆盖同名方法来提供更具体的行为，super()用于调用按继承顺序找到的父类实现。本课只用简单单继承，不引入多重继承的额外规则。\n\n复用不总要继承。例如学习计划‘拥有’多个任务，更适合用一个列表保存任务对象，这叫组合。若只是想复用几行代码，却不存在合理的‘也是’关系，可以先考虑函数或组合。覆盖方法时尽量保持调用方式与返回含义一致，让调用者能按共同接口使用不同对象。",
["Task.summary返回标题，是基础接口。","TimedTask通过super().__init__完成公共初始化，再保存minutes。","子类覆盖summary，并借助父类返回值组成更详细的文本。"],
'''class Task:
    def __init__(self, title):
        self.title = title

    def summary(self):
        return self.title

class TimedTask(Task):
    def __init__(self, title, minutes):
        super().__init__(title)
        self.minutes = minutes

    def summary(self):
        return f"{super().summary()}（{self.minutes}分钟）"

plan = [Task("阅读"), TimedTask("练习", 20)]
for task in plan:
    print(task.summary())''',"阅读\n练习（20分钟）\n",
"定义Shape类，area返回0；定义Square子类保存side并覆盖area，返回边长平方。打印Shape和边长4的Square面积。",
'''class Shape:
    def area(self):
        return 0

class Square(Shape):
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side * self.side

for shape in [Shape(), Square(4)]:
    print(shape.area())''',"0\n16\n",
["子类重写__init__后，父类初始化不会自动完成；需要时显式调用super().__init__。","为了复用而构造不合理继承树，会让行为约定难以理解；拥有关系更适合组合。"],
"继承复用共同接口，覆盖提供具体行为；拥有关系优先考虑组合。",sources=[CLASSES+"#inheritance"])
lesson(c,"l43","可迭代对象与迭代器",30,"l42",["区分能遍历的数据与记录位置的迭代器","处理迭代耗尽的StopIteration"],
"列表是可迭代对象：iter(values)可以创建负责逐项提供数据的迭代器。next(iterator)每次取得一项并推进位置，耗尽时触发StopIteration。for循环在内部做的就是不断取下一项，遇到耗尽时结束。理解这个协议能帮助你使用文件、生成器和许多标准库工具。\n\n同一个迭代器是一次性的，已经取走的项不会因为再写一个for就重新出现；列表则可再次创建新的迭代器。next(iterator,default)在耗尽时返回默认值而不抛异常。不要把默认值设计成与合法元素无法区分的值，必要时可用独立哨兵对象。",
["iter创建新迭代器，第一次next得到10。","第二次得到20，位置已经来到末尾。","第三次采用默认文字，不再抛异常；对列表重新iter后又能得到10。"],
'''values = [10, 20]
cursor = iter(values)
print(next(cursor))
print(next(cursor))
print(next(cursor, "已经结束"))
print(next(iter(values)))''',"10\n20\n已经结束\n10\n",
"手动遍历iter(['A','B'])，用while True与try/except StopIteration输出两项，耗尽后输出‘完成’。",
'''cursor = iter(["A", "B"])
while True:
    try:
        item = next(cursor)
    except StopIteration:
        break
    print(item)
print("完成")''',"A\nB\n完成\n",
["同一个迭代器耗尽后不会自动回到第一项。","不能对列表直接调用next(values)，应先iter(values)得到迭代器。"],
"可迭代对象能创建迭代器，迭代器保存当前位置并通过next逐项提供数据。",sources=[CLASSES+"#iterators"])
lesson(c,"l44","生成器与流式处理",32,"l43",["用yield按需生成结果","理解惰性执行与一次性消费"],
"函数体中包含yield时，调用得到生成器对象，函数体不会立即完整运行。每次取下一项，代码从上次暂停的位置继续，直到下一个yield，再把一个值交给调用者并暂停。结束时生成器耗尽，同样遵循迭代器协议。\n\n生成器适合逐行处理大文件、按需产生序列，避免先保存所有结果。但它不是‘自动更快’：复杂计算仍要执行，list(generator)仍会把所有结果放入内存。一次性消费后若要重复使用，要重新创建生成器或保存所需结果。资源也需要正确关闭，特别是生成器内部打开文件时。",
["调用squares(4)只创建生成器，尚未输出值。","next触发第一轮，得到0；for继续从1开始取剩余平方。","最后list读取已耗尽的同一个生成器，结果为空列表。"],
'''def squares(count):
    for number in range(count):
        yield number * number

stream = squares(4)
print(next(stream))
for value in stream:
    print(value)
print(list(stream))''',"0\n1\n4\n9\n[]\n",
"写countdown(start)生成器，从start倒数到1；将countdown(3)转换成列表输出，再对新生成器求和。",
'''def countdown(start):
    while start > 0:
        yield start
        start = start - 1

print(list(countdown(3)))
print(sum(countdown(3)))''',"[3, 2, 1]\n6\n",
["在生成器中使用return value不会像yield那样输出下一项。","对同一个生成器先sum再list，后者通常只能得到空列表。"],
"yield让计算暂停并逐项交付结果，适合流式任务；生成器的消费与生命周期仍要设计。",sources=[CLASSES+"#generators"])
lesson(c,"l45","装饰器：包裹函数行为",38,"l44",["把函数当作值传递和返回","通过装饰器加入共同的前后行为"],
"函数也可以像其他对象一样传给函数、赋给变量或作为返回值。装饰器接收一个函数，返回一个带附加行为的函数；@announce放在定义前，相当于定义后执行greet=announce(greet)。本例把开始和结束提示集中在一处，而不让每个业务函数重复写。\n\n内部wrapper通过闭包记住被包装的function。*args收集位置参数，**kwargs收集关键字参数，再原样传给原函数。functools.wraps保留名字和文档等元信息。装饰器不要丢失返回值，也要考虑异常路径：若原函数出错，普通的‘结束’输出不会执行，需要清理时应用try/finally。",
["定义阶段，announce接收greet并返回wrapper，greet名字改为绑定包装函数。","调用时wrapper先输出开始，再把name传给原函数。","结果原样返回，外层print接收它；wraps让名字仍显示greet。"],
'''from functools import wraps

def announce(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        print("开始")
        result = function(*args, **kwargs)
        print("结束")
        return result
    return wrapper

@announce
def greet(name):
    return f"你好，{name}"

print(greet("小禾"))
print(greet.__name__)''',"开始\n结束\n你好，小禾\ngreet\n",
"写double_result装饰器，让被包装的add(a,b)结果乘2后返回。使用wraps，验证add(2,3)==10并输出函数名。",
'''from functools import wraps

def double_result(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        return function(*args, **kwargs) * 2
    return wrapper

@double_result
def add(a, b):
    return a + b

print(add(2, 3))
print(add.__name__)''',"10\nadd\n",
["wrapper忘记return会让所有正常调用结果变成None。","装饰器应返回函数对象，不能在定义时就return wrapper()提前执行。"],
"装饰器通过接收并返回函数集中实现共同行为，同时保留参数、返回值和元信息。",sources=["https://docs.python.org/3.11/glossary.html#term-decorator","https://docs.python.org/3.11/library/functools.html#functools.wraps"])
lesson(c,"l46","上下文管理器与可靠清理",35,"l45",["解释with的进入、使用与退出","用contextmanager和finally保证清理"],
"with把资源的生命周期写成一块清楚的代码：进入时准备资源，块内使用，离开时清理。前面打开文件时已经在使用上下文管理器；它不仅适用于文件，也适合锁、临时设置和事务等成对操作。关键价值是异常发生时仍能退出和清理。\n\ncontextlib.contextmanager允许用生成器形式定义管理器。yield前执行准备，yield交给as变量一个值，yield后放退出工作。清理必须放在try/finally中，这样with块中抛异常时仍会执行。除非确实能处理异常，否则应让异常继续向外传播，别悄悄吞掉故障。",
["进入session时记录‘打开’，yield交出一个字典。","with块使用字典并主动抛出ValueError。","finally仍记录‘关闭’，外层except再处理错误，顺序可从events看出。"],
'''from contextlib import contextmanager

events = []

@contextmanager
def session():
    events.append("打开")
    try:
        yield {"ready": True}
    finally:
        events.append("关闭")

try:
    with session() as resource:
        print(resource["ready"])
        raise ValueError("模拟错误")
except ValueError:
    events.append("已处理")
print(events)''',"True\n['打开', '关闭', '已处理']\n",
"写temporary_list上下文管理器，yield一个初始空列表，退出时清空它。在块内追加A并输出，块外再次输出同一列表证明已清理。",
'''from contextlib import contextmanager

@contextmanager
def temporary_list():
    values = []
    try:
        yield values
    finally:
        values.clear()

with temporary_list() as data:
    data.append("A")
    print(data)
print(data)''',"['A']\n[]\n",
["把清理写在yield后却不放finally，with块的异常可能跳过它。","contextmanager管理器正常路径应恰好yield一次，不能yield多次。"],
"with表达资源作用域，try/finally确保退出清理，异常仍应按责任传播。",sources=["https://docs.python.org/3.11/library/contextlib.html"])
lesson(c,"l47","类型提示与数据契约",32,"l46",["读写函数参数、返回值与容器注解","区分静态提示和运行时校验"],
"类型提示让人和分析工具知道代码期望的值，例如scores:list[int]表示整数列表，->float描述返回值。注解不会自动转换数据，也不会自动拒绝错误类型：Python运行时通常照常执行，静态检查需要额外工具。提示应反映真实约定，不要为了消除工具提示而随意写Any。\n\n空集合如何处理也是接口契约的一部分。本例mean返回float|None：有分数则返回平均值，空列表则返回None。调用者先判断None再做小数格式化，避免把‘没有数据’误当成0分。类型提示不能替代验证外部JSON、CSV或用户输入，外部数据仍需显式检查。",
["函数签名说明接收整数列表，可能返回浮点数或None。","[80,90]得到85.0，调用处确认不是None后显示一位小数。","空列表直接返回None，明确表示没有平均值。"],
'''def mean(scores: list[int]) -> float | None:
    if not scores:
        return None
    return sum(scores) / len(scores)

average = mean([80, 90])
if average is not None:
    print(f"平均：{average:.1f}")
print(mean([]))''',"平均：85.0\nNone\n",
"写find_name(names:list[str],prefix:str)->str|None，返回第一个以prefix开头的姓名，否则返回None，测试有命中与无命中。",
'''def find_name(names: list[str], prefix: str) -> str | None:
    for name in names:
        if name.startswith(prefix):
            return name
    return None

print(find_name(["小禾", "阿青"], "小"))
print(find_name(["小禾", "阿青"], "老"))''',"小禾\nNone\n",
["写了int注解不会把字符串'3'自动转为数字。","可能返回None的函数，调用者必须先处理没有结果的情况。"],
"类型提示记录接口契约；运行时验证与空值处理仍由程序明确完成。",sources=["https://docs.python.org/3.11/library/typing.html"])
lesson(c,"l48","unittest与回归测试",38,"l47",["用标准库组织可重复的单元测试","测试正常值、异常与需求回归"],
"单元测试把一个小功能放在独立环境中验证。unittest.TestCase中的test_方法是测试，assertEqual比较结果，assertRaises检查预期异常。测试应当独立，不依赖某个先前测试已经修改了全局变量；外部文件可使用临时目录。\n\n修复缺陷后，把能复现它的输入加入测试，形成回归保护。本例价格函数拒绝负数；除了普通乘法，还检查零数量与非法价格。真实项目可以把测试放在tests/目录，通过python -m unittest discover运行。在应用编辑器里，本课用显式suite运行，避免把编辑器进程的命令行参数交给unittest.main。",
["定义业务函数后，TestCase类声明三项独立测试。","assertRaises只有在函数确实抛出ValueError时通过。","运行器报告详细结果到标准错误，最后stdout给出稳定的通过数量。"],
'''import unittest

def total_price(price, count):
    if price < 0 or count < 0:
        raise ValueError("不能为负数")
    return price * count

class PriceTests(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(total_price(8, 3), 24)

    def test_zero(self):
        self.assertEqual(total_price(8, 0), 0)

    def test_invalid(self):
        with self.assertRaises(ValueError):
            total_price(-1, 2)

suite = unittest.defaultTestLoader.loadTestsFromTestCase(PriceTests)
result = unittest.TextTestRunner(verbosity=1).run(suite)
if not result.wasSuccessful():
    raise SystemExit(1)
print(f"通过{result.testsRun}项测试")''',"通过3项测试\n",
"为safe_average(values)写3项unittest：普通[2,4]返回3、[0]返回0、空列表抛ValueError。最后输出测试数量。",
'''import unittest

def safe_average(values):
    if not values:
        raise ValueError("没有数据")
    return sum(values) / len(values)

class AverageTests(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(safe_average([2, 4]), 3)

    def test_zero(self):
        self.assertEqual(safe_average([0]), 0)

    def test_empty(self):
        with self.assertRaises(ValueError):
            safe_average([])

suite = unittest.defaultTestLoader.loadTestsFromTestCase(AverageTests)
result = unittest.TextTestRunner().run(suite)
if not result.wasSuccessful():
    raise SystemExit(1)
print(f"通过{result.testsRun}项测试")''',"通过3项测试\n",
["测试方法没有test_前缀，自动发现时可能不会执行。","只打印False而不让测试失败，自动化系统可能误认为成功。"],
"单元测试把需求变成可重复的断言；修复问题时同时加入回归用例。",sources=["https://docs.python.org/3.11/library/unittest.html"])
lesson(c,"l49","解释器、虚拟环境与依赖",35,"l48",["区分Python版本、标准库与第三方包","了解虚拟环境的用途及平台限制"],
"Python解释器运行语言，标准库随解释器一起提供，第三方包需要另外安装并满足版本和平台条件。pip是包安装工具，不是Python语言的一条语句。import报错时，应先确认正在用哪一个解释器、包是否装在它的环境里，以及包名与导入名是否相同。\n\n在完整桌面Python中，python -m venv .venv创建独立环境，随后用该环境的python -m pip安装依赖；用同一个python执行-m pip可以减少装错环境。虚拟环境隔离包版本，不是操作系统安全沙箱。PySlate课程示例只用标准库，Android嵌入环境不承诺支持pip、venv、原生扩展或所有桌面包。依赖第三方包的项目应先检查设备兼容性与许可证，导出到桌面环境后再配置。",
["sys.version_info描述当前解释器版本，检查它是否达到课程目标3.11。","sys.stdlib_module_names列出标准库模块名字，pathlib属于其中。","sys.prefix与sys.base_prefix比较可识别常见venv，但本例不要求它必须处于venv。"],
'''import sys

print("兼容课程：", sys.version_info >= (3, 11))
print("pathlib是标准库：", "pathlib" in sys.stdlib_module_names)
in_venv = sys.prefix != sys.base_prefix
print("环境状态已识别：", isinstance(in_venv, bool))''',"兼容课程： True\npathlib是标准库： True\n环境状态已识别： True\n",
"通过importlib.util.find_spec检查json与csv能否被当前解释器找到。只打印是否找到，不输出设备绝对路径。",
'''from importlib.util import find_spec

for module in ["json", "csv"]:
    print(module, find_spec(module) is not None)''',"json True\ncsv True\n",
["把pip install写进.py文件会造成语法错误，它是终端命令。","桌面可安装的包不一定能在Android嵌入解释器上运行，尤其是含原生二进制扩展时。"],
"先认清当前解释器和平台，再管理依赖；虚拟环境解决包版本隔离问题。",sources=[TUTORIAL+"venv.html"])
lesson(c,"l50","从脚本到可维护项目",40,"l49",["拆分输入、业务逻辑与输出","为项目说明、测试和失败策略建立清楚约定"],
"独立项目需要的不只是能跑的一段代码。先写目标、输入格式、输出规则和错误处理，再把纯计算、文件访问和界面分开。main函数负责协调，工具函数只完成小职责；if __name__=='__main__'让文件直接运行时执行入口，被import时只提供工具而不立刻启动交互。\n\n采用有意义的小写下划线名字、函数文档、统一UTF-8和相对项目路径。README说明运行方法与数据备份，tests记录边界。改动前用版本控制或导出ZIP保留可回退副本。优化应先测量真实瓶颈，文件写入与重复解析往往比几次加法更值得关注。本例以清晰小函数处理库存，后面的多文件项目会真正把职责分到不同文件。",
["parse_quantity只转换和验证数量，不读取文件也不输出。","inventory_total计算各行数量总和，可独立测试。","main组织示例数据与显示；入口保护控制何时启动。"],
'''def parse_quantity(text: str) -> int:
    """解析非负整数数量，拒绝非法输入。"""
    value = int(text)
    if value < 0:
        raise ValueError("数量不能为负")
    return value

def inventory_total(rows: list[str]) -> int:
    return sum(parse_quantity(row) for row in rows)

def main() -> None:
    rows = ["2", "3", "0"]
    print("库存合计：", inventory_total(rows))

if __name__ == "__main__":
    main()''',"库存合计： 5\n",
"把温度转换拆成celsius_to_fahrenheit(value)与main两个函数，加类型提示和入口保护。main输出0与100摄氏度对应的华氏度。",
'''def celsius_to_fahrenheit(value: float) -> float:
    """将摄氏度换算为华氏度。"""
    return value * 9 / 5 + 32

def main() -> None:
    for temperature in [0, 100]:
        print(f"{temperature}C = {celsius_to_fahrenheit(temperature):.1f}F")

if __name__ == "__main__":
    main()''',"0C = 32.0F\n100C = 212.0F\n",
["在模块顶层直接input，会让其他文件import它时意外进入交互。","把读文件、解析、计算、显示塞进一个大函数，难以单独测试失败原因。"],
"用小职责、明确接口、可重复测试与运行说明，把一次性脚本变成可维护项目。",sources=[TUTORIAL+"modules.html#executing-modules-as-scripts","https://peps.python.org/pep-0008/"])

c = chapter("projects", "07 · 八个完整项目", "实战", "从可复现小游戏到持久化数据与真实多文件项目，练习需求、边界、验证与扩展。")

guess_code = '''import random

# 固定种子便于课程复现；正常游玩可改成random.Random()
rng = random.Random(7)
secret = rng.randint(1, 20)
attempts = 0
while attempts < 5:
    text = input("猜1到20：")
    try:
        guess = int(text)
    except ValueError:
        print("请输入整数，不扣次数")
        continue
    if not 1 <= guess <= 20:
        print("超出范围，不扣次数")
        continue
    attempts += 1
    if guess == secret:
        print(f"猜中了，用了{attempts}次")
        break
    if guess < secret:
        print("偏小")
    else:
        print("偏大")
else:
    print(f"机会用完，答案是{secret}")
'''
guess_solution = guess_code.replace('print(f"猜中了，用了{attempts}次")', 'print(f"猜中了，用了{attempts}次")\n        print(f"得分：{(6 - attempts) * 10}")')
lesson(c,"p01","项目一：猜数字游戏",50,"l14 l30 l35",["组合随机数、循环与输入验证","明确无效输入和失败路径的规则"],
"需求：秘密数在1至20之间，玩家最多有5次有效机会。输入不是整数或超出范围时提示但不扣次数；每次有效猜测后提示偏大或偏小，猜中立即结束，否则公布答案。先把规则写清楚，才知道次数应该在哪一行增加。\n\n课程固定随机种子7，所以同一环境可重复测试，秘密数为11。完成后可改为random.Random()让每次游玩变化。while的else块只在条件自然变假、没有break时执行，恰好表示机会用完。验证时至少试猜中、五次失败、无效文字和越界四条路径。本项目只在控制台交互，不需要网络或图形库。",
["初始化随机对象和机会数，循环先读取并验证输入。","只有通过两层验证才累计一次机会，随后决定偏小、偏大或命中。","命中使用break跳过循环else，五次有效失败才进入else公布答案。"],
guess_code,"猜1到20：偏小\n猜1到20：偏大\n猜1到20：猜中了，用了3次\n",
"增加得分：猜中时输出(6-有效次数)×10分，保留原有范围验证和失败逻辑。三次猜中应得30分。",
guess_solution,"猜1到20：偏小\n猜1到20：偏大\n猜1到20：猜中了，用了3次\n得分：30\n",
["在验证之前增加次数，会把文字和越界输入也扣成有效机会。","循环else与if的else不是同一个层级，缩进必须对齐while。"],
"一个小游戏也需要明确状态、有效输入规则、退出条件与可复现测试。",stdin="5\n15\n11\n",sources=[CONTROL,"https://docs.python.org/3.11/library/random.html"],cases=[
    {"name":"invalid-input-does-not-consume-attempt","field":"code","stdin":"abc\n0\n11\n","expectedOutput":"猜1到20：请输入整数，不扣次数\n猜1到20：超出范围，不扣次数\n猜1到20：猜中了，用了1次\n"},
    {"name":"lose-after-five","field":"code","stdin":"1\n2\n3\n4\n5\n","expectedOutput":"猜1到20：偏小\n猜1到20：偏小\n猜1到20：偏小\n猜1到20：偏小\n猜1到20：偏小\n机会用完，答案是11\n"}])

calculator_code = '''import math

def calculate(left, operator, right):
    if operator == "+":
        return left + right
    if operator == "-":
        return left - right
    if operator == "*":
        return left * right
    if operator == "/":
        if right == 0:
            raise ValueError("除数不能为0")
        return left / right
    raise ValueError("不支持的运算符")

def parse_expression(text):
    try:
        left, operator, right = text.split()
        first, second = float(left), float(right)
        if not math.isfinite(first) or not math.isfinite(second):
            raise ValueError("数值必须有限")
        return first, operator, second
    except ValueError:
        raise ValueError("请输入：数字 运算符 数字") from None

try:
    expression = input("表达式：")
    left, operator, right = parse_expression(expression)
    result = calculate(left, operator, right)
    if not math.isfinite(result):
        raise ValueError("结果超出有限数值范围")
    print(f"结果：{result:g}")
except ValueError as error:
    print(f"错误：{error}")
'''
calculator_solution = calculator_code.replace('    raise ValueError("不支持的运算符")', '''    if operator == "**":
        if abs(right) > 10 or abs(left) > 1000:
            raise ValueError("乘方范围过大")
        if left == 0 and right < 0:
            raise ValueError("0不能取负指数")
        if left < 0 and not right.is_integer():
            raise ValueError("负数底数只支持整数指数")
        return left ** right
    raise ValueError("不支持的运算符")''')
lesson(c,"p02","项目二：安全的四则计算器",50,"l25 l30",["拆分表达式解析和计算职责","处理除零与格式错误而不使用eval"],
"需求：接收‘数字 运算符 数字’，支持加减乘除，显示结果，错误时给出具体提示。空格是明确的输入协议，因此‘12 / 4’有效，‘12/4’会被提示重新按格式输入。这个范围虽小，却比直接eval任意文字更清楚，也避免把输入当Python程序执行。\n\nparse_expression只处理文本格式和数值转换，calculate只根据已转换参数计算，最后一层负责显示。分层后能单独测试四种运算、未知运算符、除零与少字段。浮点适合普通近似计算；涉及财务时改用Decimal并补充舍入规则。此版本计算一次后结束，菜单循环可作为另一个扩展。",
["读取一行并split成三段，左右数值转换成float。","calculate选择匹配运算符，除法先验证除数。","外层把结果格式化；ValueError沿调用栈传播到统一提示位置。"],
calculator_code,"表达式：结果：3\n",
"增加**乘方运算。为避免意外的大计算，要求底数绝对值不超过1000、指数绝对值不超过10，超出时报ValueError。",
calculator_solution,"表达式：结果：3\n",
["eval会把用户文本当代码运行，这个计算器只应解析约定的数字与运算符。","把左右数字留成字符串，+会连接文字而不是做加法。"],
"小而明确的输入协议配合纯计算函数，让交互程序容易验证和扩展。",stdin="12 / 4\n",cases=[
    {"name":"division-by-zero","field":"code","stdin":"8 / 0\n","expectedOutput":"表达式：错误：除数不能为0\n"},
    {"name":"malformed-expression","field":"code","stdin":"abc + 2\n","expectedOutput":"表达式：错误：请输入：数字 运算符 数字\n"},
    {"name":"power-extension","field":"solution","stdin":"2 ** 5\n","expectedOutput":"表达式：结果：32\n"}])

grades_code = '''def parse_records(text):
    records = {}
    if not text.strip():
        raise ValueError("至少输入一条记录")
    for item in text.split(","):
        try:
            name, raw_score = item.split(":")
            score = int(raw_score)
        except ValueError:
            raise ValueError("每项格式必须是姓名:整数分数") from None
        name = name.strip()
        if not name or name in records:
            raise ValueError("姓名不能为空或重复")
        if not 0 <= score <= 100:
            raise ValueError("分数必须在0到100之间")
        records[name] = score
    return records

try:
    records = parse_records(input("成绩："))
    values = list(records.values())
    print("人数：", len(values))
    print(f"平均分：{sum(values) / len(values):.1f}")
    print("最高分：", max(values))
    print("及格人数：", sum(score >= 60 for score in values))
except ValueError as error:
    print(f"错误：{error}")
'''
grades_solution = grades_code.replace('    print("及格人数：", sum(score >= 60 for score in values))', '''    print("及格人数：", sum(score >= 60 for score in values))
    def ranking_key(item):
        return -item[1], item[0]
    for position, (name, score) in enumerate(sorted(records.items(), key=ranking_key), start=1):
        print(f"{position}. {name} {score}")''')
lesson(c,"p03","项目三：成绩统计器",60,"l22 l30 l38",["把多条文本记录解析成字典","验证空输入、重复姓名和分数范围"],
"需求：一行输入多个‘姓名:分数’，以英文逗号分隔；输出人数、平均、最高分与及格人数。姓名不能为空，也不能重复，本版本明确拒绝重复项，防止字典悄悄覆盖前一位同学。分数是0至100的整数，60分及格。\n\n解析函数在返回前完成全部校验，因此统计代码可以确信数据非空且合法。这里不把坏数据当0分，也不悄悄删掉它，因为那会改变成绩的含义。遇到错误时整批拒绝，修正后重跑；在后续CSV项目中再学习带错误行报告的‘跳过坏行’策略。平均分只在显示时保留一位小数。",
["按逗号拆项、按冒号拆字段，逐一验证姓名和分数。","完整字典返回后才读取分数列表并统计，不会对空列表求平均。","生成器表达式把及格判断转为True/False，sum累计通过人数。"],
grades_code,"成绩：人数： 3\n平均分：79.3\n最高分： 95\n及格人数： 2\n",
"在统计后增加排名：按分数降序，同分时按姓名升序。显示位置编号、姓名和分数，保留原统计。",
grades_solution,"成绩：人数： 3\n平均分：79.3\n最高分： 95\n及格人数： 2\n1. 阿青 95\n2. 小禾 88\n3. 小川 55\n",
["字典重复键会覆盖旧值，因此要在赋值前决定重复姓名的处理策略。","对空分数列表求max或平均会出错，应在解析阶段拒绝空输入。"],
"先清晰地定义并验证记录，再计算统计；不要让错误输入悄悄影响结果。",stdin="小禾:88,阿青:95,小川:55\n",cases=[
    {"name":"duplicate-name","field":"code","stdin":"小禾:80,小禾:90\n","expectedOutput":"成绩：错误：姓名不能为空或重复\n"},
    {"name":"empty-input","field":"code","stdin":"\n","expectedOutput":"成绩：错误：至少输入一条记录\n"},
    {"name":"score-out-of-range","field":"code","stdin":"小禾:120\n","expectedOutput":"成绩：错误：分数必须在0到100之间\n"}])

todo_code = '''import json
import time
from pathlib import Path

FILE = Path("project_todos.json")

def load_tasks():
    if not FILE.exists():
        return []
    data = json.loads(FILE.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("任务文件应为列表")
    ids = set()
    for task in data:
        if not isinstance(task, dict) or set(task) != {"id", "title", "done"}:
            raise ValueError("任务字段不完整")
        if type(task["id"]) is not int or task["id"] <= 0 or task["id"] in ids:
            raise ValueError("任务编号无效")
        if not isinstance(task["title"], str) or not task["title"].strip() or type(task["done"]) is not bool:
            raise ValueError("任务类型无效")
        ids.add(task["id"])
    return data

def save_tasks(tasks):
    temporary = FILE.with_suffix(".tmp")
    temporary.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")
    # Windows扫描程序偶尔会短暂占用目标文件；有限重试，不掩盖永久错误。
    for attempt in range(5):
        try:
            temporary.replace(FILE)
            break
        except PermissionError:
            if attempt == 4:
                raise
            time.sleep(0.05 * (attempt + 1))

def main():
    try:
        tasks = load_tasks()
    except (OSError, ValueError) as error:
        print(f"读取失败，未覆盖原文件：{error}")
        return
    next_id = max((task["id"] for task in tasks), default=0) + 1
    while True:
        try:
            command = input("> ").strip()
        except EOFError:
            break
        if command == "quit":
            print("已退出")
            break
        if command.startswith("add "):
            title = command[4:].strip()
            if not title:
                print("标题不能为空")
                continue
            tasks.append({"id": next_id, "title": title, "done": False})
            next_id += 1
            save_tasks(tasks)
            print("已添加")
        elif command.startswith("done "):
            try:
                task_id = int(command[5:])
                task = next(task for task in tasks if task["id"] == task_id)
            except (ValueError, StopIteration):
                print("编号无效")
                continue
            task["done"] = True
            save_tasks(tasks)
            print("已完成")
        elif command == "list":
            if not tasks:
                print("暂无任务")
            for task in tasks:
                mark = "x" if task["done"] else " "
                print(f"{task['id']} [{mark}] {task['title']}")
        # DELETE_EXTENSION
        else:
            print("命令：add 标题 / done 编号 / list / quit")

if __name__ == "__main__":
    main()
'''
todo_delete = '''elif command.startswith("delete "):
            try:
                task_id = int(command[7:])
            except ValueError:
                print("编号无效")
                continue
            remaining = [task for task in tasks if task["id"] != task_id]
            if len(remaining) == len(tasks):
                print("编号无效")
                continue
            tasks = remaining
            save_tasks(tasks)
            print("已删除")'''
todo_solution = todo_code.replace('# DELETE_EXTENSION',todo_delete).replace('/ list / quit','/ delete 编号 / list / quit')
todo_code = todo_code.replace('        # DELETE_EXTENSION\n','')
todo_output = "> 已添加\n> 已添加\n> 已完成\n> 1 [x] 阅读\n2 [ ] 练习\n> 已退出\n"
lesson(c,"p04","项目四：持久化待办清单",90,"l30 l32 l33 l43",["设计稳定编号而不是把显示位置当身份","读写JSON并避免损坏文件被静默覆盖"],
"需求：add 标题添加任务，done 编号完成任务，list显示，quit退出。任务写入项目目录的project_todos.json，下次运行继续读取。本课提供的演示输入假定首次运行、文件不存在；再次运行会保留旧任务，这正是持久化的目的。删除测试数据前先确认是课程文件。\n\n现有任务使用稳定编号，不因列表位置变化而改号。本版重启以当前最大编号续接，因此删除最高编号后重启可能复用该编号；需要永久身份时应单独持久化next_id或使用UUID。加载阶段校验字段、编号与类型，损坏文件会提示并停止。保存先写同目录临时文件，再replace更新，降低写到一半丢失原文件的风险；重要应用还应有备份与并发写入协调。每次变更后保存，退出无需依赖最后一次保存。",
["load_tasks读取已有JSON或返回新列表，next_id来自现有最大编号。","菜单解析命令，变更后立即save_tasks；未知编号不会创建新任务。","用两次独立运行测试持久化：先add并quit，再次运行只list，应看到旧任务。"],
todo_code,todo_output,
"增加delete 编号命令：验证编号存在后删除对应记录并保存，其他任务保留原编号。空列表list输出‘暂无任务’。",
todo_solution,todo_output,
["用列表索引作为永久编号，删除首项后会让后面任务的身份变化。","捕获JSON损坏后直接返回[]并保存，会覆盖用户原始数据。"],
"持久化项目需要稳定身份、结构验证、变更保存与失败时保护原文件。",stdin="add 阅读\nadd 练习\ndone 1\nlist\nquit\n",sources=["https://docs.python.org/3.11/library/json.html","https://docs.python.org/3.11/library/pathlib.html"],cases=[
    {"name":"unknown-task","field":"code","stdin":"done 99\nlist\nquit\n","expectedOutput":"> 编号无效\n> 暂无任务\n> 已退出\n"},
    {"name":"delete-extension","field":"solution","stdin":"add 阅读\nadd 练习\ndelete 1\nlist\nquit\n","expectedOutput":"> 已添加\n> 已添加\n> 已删除\n> 2 [ ] 练习\n> 已退出\n"}])

text_code = '''from collections import Counter
from pathlib import Path

# 课程自带的可重建样本，不处理用户现有文件
source = Path("lesson_sample_text.txt")
source.write_text("Python makes small tools.\\nSmall tools save time.\\n\\n", encoding="utf-8")
text = source.read_text(encoding="utf-8")
lines = text.splitlines()
words = []
for token in text.lower().split():
    word = token.strip(".,!?;:\\"'()")
    if word:
        words.append(word)
counts = Counter(words)

def frequency_key(item):
    return -item[1], item[0]

ranked = sorted(counts.items(), key=frequency_key)
print("总行数：", len(lines))
print("非空行：", sum(bool(line.strip()) for line in lines))
print("单词数：", len(words))
print("不同单词：", len(counts))
for word, count in ranked[:3]:
    print(word, count)
'''
text_solution = text_code + '''
import json
report = {"lines": len(lines), "nonempty_lines": sum(bool(line.strip()) for line in lines), "word_count": len(words), "top_words": ranked[:3]}
target = Path("lesson_text_report.json")
target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
loaded = json.loads(target.read_text(encoding="utf-8"))
print("报告已保存：", loaded["word_count"])
'''
text_output = "总行数： 3\n非空行： 2\n单词数： 8\n不同单词： 6\nsmall 2\ntools 2\nmakes 1\n"
lesson(c,"p05","项目五：文本文件分析器",65,"l17 l32 l37 l38",["明确文本统计口径并执行清洗","用稳定排序生成词频报告"],
"需求：读取UTF-8英文文本，统计总行数、非空行数、词数、不同词数和前三个高频词。示例会新建自己的lesson_sample_text.txt作为可重建样本；迁移到实际工具时把样本生成移出分析函数，再由用户选择输入文件。处理前先定义‘词’：本版按空白分词并清除首尾有限标点，全部转小写。\n\n这不是完整的自然语言分词器，中文句子、连字符词和复杂标点不在本版口径内，应在说明中诚实写明。splitlines保留中间空行作为行记录，末尾一个换行不额外产生一行。词频相同按字母序排序，让报告稳定，不能把偶然出现顺序当成业务规则。",
["生成固定样本并读取文本，拆出各行与清洗后的单词。","Counter统计词频，按负次数与单词元组排序。","输出统计与前三名；手工核对样本有8词、6种单词，避免仅相信代码。"],
text_code,text_output,
"保留控制台报告，再把行数、非空行数、词数和前三名写入lesson_text_report.json。重新读回并输出报告词数。",
text_solution,text_output+"报告已保存： 8\n",
["没有定义分词口径就比较不同工具的‘词数’，结果可能并不等价。","不处理大小写会把Small与small统计为不同词。"],
"数据分析先定义统计口径，再清洗、统计、排序，并用小样本独立核对。",sources=["https://docs.python.org/3.11/library/collections.html#collections.Counter"])

sales_code = '''import csv
from collections import defaultdict
from decimal import Decimal, InvalidOperation

rows = [
    {"item": "书,合集", "category": "学习", "quantity": "2", "price": "15.00"},
    {"item": "笔", "category": "文具", "quantity": "3", "price": "2.00"},
    {"item": "练习册", "category": "学习", "quantity": "1", "price": "8.00"},
    {"item": "橡皮", "category": "文具", "quantity": "2", "price": "oops"},
]
with open("lesson_sales.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["item", "category", "quantity", "price"])
    writer.writeheader()
    writer.writerows(rows)

totals = defaultdict(lambda: Decimal("0.00"))
bad_lines = []
valid = 0
with open("lesson_sales.csv", newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    if reader.fieldnames != ["item", "category", "quantity", "price"]:
        raise ValueError("CSV列不符合约定")
    for line_number, row in enumerate(reader, start=2):
        try:
            if None in row:
                raise ValueError("多余字段")
            quantity = int(row["quantity"])
            price = Decimal(row["price"])
            if quantity < 0 or not price.is_finite() or price < 0 or not row["category"].strip():
                raise ValueError("数值或类别无效")
        except (ValueError, InvalidOperation, TypeError):
            bad_lines.append(line_number)
            continue
        totals[row["category"]] += quantity * price
        valid += 1
print("有效记录：", valid)
print("跳过行：", bad_lines)
for category in sorted(totals):
    print(f"{category}：{totals[category]:.2f}")
print(f"合计：{sum(totals.values()):.2f}")
'''
sales_solution = sales_code + '''
with open("lesson_sales_summary.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["category", "amount"])
    for category in sorted(totals):
        writer.writerow([category, f"{totals[category]:.2f}"])
with open("lesson_sales_summary.csv", newline="", encoding="utf-8") as file:
    exported = list(csv.DictReader(file))
print(f"已导出{len(exported)}类")
'''
sales_output = "有效记录： 3\n跳过行： [5]\n学习：38.00\n文具：6.00\n合计：44.00\n"
lesson(c,"p06","项目六：CSV销售分析",80,"l34 l36 l37",["按列名解析并验证表格数据","生成带坏行说明的分类汇总"],
"需求：按类别汇总数量×单价，输出有效记录数、坏行号码和总额。样本由程序生成在lesson_sales.csv，其中最后一条单价故意写成oops，用来验证错误路径；不要把跳过坏行假装成‘全量数据均有效’。对真正输入文件，应另保留原文件并把错误行报告交给使用者修正。\n\nCSV解析交给csv模块处理，金额使用Decimal。先检查列结构，再逐行验证数量非负、价格为有限非负数、类别非空。Decimal还可表示NaN和Infinity，因此仅检查price<0不够，必须先检查is_finite。按类别累加后排序输出。此版允许超过两位的小数并在显示时保留两位；财务系统应在导入时明确精度与舍入策略。",
["写入包含逗号字段与一条坏价格的样本，csv负责正确引用字段。","逐行转换数量与金额，坏行记录为第5行，不参与合计。","三条有效销售合计44.00元，学习38.00、文具6.00，与手算结果核对。"],
sales_code,sales_output,
"把分类汇总写成lesson_sales_summary.csv，列为category、amount，按类别顺序写入；读回后输出导出的类别数量。",
sales_solution,sales_output+"已导出2类\n",
["跳过坏行却不报告行号，会让缺失数据难以追查。","Decimal('NaN')不是有效金额，除了负数还应拒绝非有限值。"],
"表格分析需要格式解析、业务验证、错误报告与独立核对，汇总数字本身只是最后一步。",sources=["https://docs.python.org/3.11/library/csv.html","https://docs.python.org/3.11/library/decimal.html"])

ledger_code = '''import csv
import time
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

FILE = Path("project_ledger.csv")
FIELDS = ["kind", "category", "amount"]

def parse_amount(text):
    try:
        amount = Decimal(text)
    except InvalidOperation:
        raise ValueError("金额格式无效") from None
    if not amount.is_finite() or amount <= 0 or amount > Decimal("1000000000"):
        raise ValueError("金额必须为有限正数且不超过十亿")
    if amount.as_tuple().exponent < -2:
        raise ValueError("金额最多两位小数")
    return amount

def load_entries():
    if not FILE.exists():
        return []
    with FILE.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != FIELDS:
            raise ValueError("账本列格式错误")
        entries = []
        for row in reader:
            if None in row or any(not isinstance(row.get(field), str) for field in FIELDS):
                raise ValueError("账本字段缺失或多余")
            if row["kind"] not in {"income", "expense"} or not row["category"]:
                raise ValueError("账本记录格式错误")
            parse_amount(row["amount"])
            entries.append(row)
        return entries

def save_entries(entries):
    temporary = FILE.with_suffix(".tmp")
    with temporary.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(entries)
    # 处理Windows上的瞬时占用，超过有限次数仍将错误交给调用者。
    for attempt in range(5):
        try:
            temporary.replace(FILE)
            break
        except PermissionError:
            if attempt == 4:
                raise
            time.sleep(0.05 * (attempt + 1))

def summary(entries):
    income = Decimal("0.00")
    expense = Decimal("0.00")
    categories = defaultdict(lambda: Decimal("0.00"))
    for entry in entries:
        amount = parse_amount(entry["amount"])
        if entry["kind"] == "income":
            income += amount
        else:
            expense += amount
            categories[entry["category"]] += amount
    print(f"收入：{income:.2f} 支出：{expense:.2f} 结余：{income - expense:.2f}")
    for category in sorted(categories):
        print(f"{category}：{categories[category]:.2f}")

def main():
    try:
        entries = load_entries()
    except (OSError, ValueError) as error:
        print(f"读取失败，未覆盖原账本：{error}")
        return
    while True:
        try:
            command = input("账本> ").strip()
        except EOFError:
            break
        if command == "quit":
            print("已退出")
            break
        if command == "summary":
            summary(entries)
            continue
        # UNDO_EXTENSION
        try:
            kind, category, text = command.split()
            if kind not in {"income", "expense"}:
                raise ValueError("只支持income或expense")
            amount = parse_amount(text)
        except ValueError as error:
            print(f"输入无效：{error}")
            continue
        entries.append({"kind": kind, "category": category, "amount": f"{amount:.2f}"})
        save_entries(entries)
        print("已记账")

if __name__ == "__main__":
    main()
'''
ledger_undo = '''if command == "undo":
            if not entries:
                print("没有可撤销记录")
                continue
            entries.pop()
            save_entries(entries)
            print("已撤销")
            continue'''
ledger_solution = ledger_code.replace('# UNDO_EXTENSION',ledger_undo)
ledger_code = ledger_code.replace('        # UNDO_EXTENSION\n','')
ledger_output = "账本> 已记账\n账本> 已记账\n账本> 已记账\n账本> 收入：1000.00 支出：33.50 结余：966.50\n交通：8.00\n午餐：25.50\n账本> 已退出\n"
lesson(c,"p07","项目七：本地记账本",100,"p04 p06",["为金额定义可验证的精度与范围规则","实现持久化收入、支出和分类汇总"],
"需求：income 类别 金额记录收入，expense 类别 金额记录支出，summary汇总，quit退出。账本保存在project_ledger.csv；课程演示从空项目开始，再次运行会累加已有记录。金额必须为有限正数、不超过十亿，输入最多两位小数；类别不含空格。这里用严格拒绝而不是隐式舍入，确保用户知道实际记入的金额。\n\n先验证再把记录加入内存并保存，同目录临时文件写完后替换账本。汇总把收入与支出分开累计，结余是两者之差，并按支出类别排序显示。读取时也验证数据，不盲目信任磁盘文件。此项目是单人离线练习账本，不具备银行对账、审计追踪或多进程写入协调；迁移到真实使用前应增加备份和更完整的导入校验。",
["启动时加载并验证CSV，损坏则提示退出而不覆盖原账本。","解析命令与金额，保存标准两位小数字符串，Decimal参与汇总。","示例收入1000，支出25.50和8，结余966.50；退出后重开summary仍应一致。"],
ledger_code,ledger_output,
"增加undo命令撤销最后一笔并立刻保存；没有记录时显示‘没有可撤销记录’。这只是撤销最近一笔，不是完整历史系统。",
ledger_solution,ledger_output,
["用float累计金额可能引入二进制小数误差；从输入字符串构造Decimal。","以为文件存在就必然合法，可能把错误类型或NaN带入统计。"],
"持久化金额数据需要明确精度、范围、失败策略与复核方法，不能只关注总和。",stdin="income 工资 1000\nexpense 午餐 25.50\nexpense 交通 8\nsummary\nquit\n",sources=["https://docs.python.org/3.11/library/decimal.html"],cases=[
    {"name":"reject-nan","field":"code","stdin":"expense 午餐 NaN\nsummary\nquit\n","expectedOutput":"账本> 输入无效：金额必须为有限正数且不超过十亿\n账本> 收入：0.00 支出：0.00 结余：0.00\n账本> 已退出\n"},
    {"name":"reject-excess-precision","field":"code","stdin":"expense 午餐 1.234\nquit\n","expectedOutput":"账本> 输入无效：金额最多两位小数\n账本> 已退出\n"},
    {"name":"undo-extension","field":"solution","stdin":"income 工资 100\nexpense 午餐 25\nundo\nsummary\nquit\n","expectedOutput":"账本> 已记账\n账本> 已记账\n账本> 已撤销\n账本> 收入：100.00 支出：0.00 结余：100.00\n账本> 已退出\n"}])

cli_files = {
    "studytools/__init__.py": '"""学习时间统计工具包。"""\n',
    "studytools/stats.py": '''"""纯计算模块：不读取输入，不在导入时运行界面。"""

def summarize(minutes: list[int]) -> dict:
    if not minutes:
        raise ValueError("至少输入一段时长")
    if any(value < 0 for value in minutes):
        raise ValueError("时长不能为负")
    return {"count": len(minutes), "total": sum(minutes), "average": sum(minutes) / len(minutes), "longest": max(minutes)}
''',
    "main.py": '''"""入口：可接收命令行参数，也可从标准输入读取。"""
import argparse
from studytools.stats import summarize

def main() -> None:
    parser = argparse.ArgumentParser(description="统计学习时长，单位分钟")
    parser.add_argument("minutes", nargs="*", type=int)
    arguments = parser.parse_args()
    try:
        values = arguments.minutes
        if not values:
            values = [int(value) for value in input("分钟（空格分隔）：").split()]
        report = summarize(values)
    except ValueError as error:
        print(f"错误：{error}")
        return
    print(f"次数：{report['count']}")
    print(f"总计：{report['total']}分钟")
    print(f"平均：{report['average']:.1f}分钟")
    print(f"最长：{report['longest']}分钟")

if __name__ == "__main__":
    main()
'''
}
cli_solution_files = cli_files.copy()
cli_solution_files["studytools/stats.py"] = cli_files["studytools/stats.py"].replace('def summarize(', 'from statistics import median\n\ndef summarize(').replace('"longest": max(minutes)', '"longest": max(minutes), "median": median(minutes)')
cli_solution_files["main.py"] = cli_files["main.py"].replace('    print(f"最长：{report[\'longest\']}分钟")', '    print(f"最长：{report[\'longest\']}分钟")\n    print(f"中位数：{report[\'median\']:.1f}分钟")')

def bootstrap(files):
    return '''import runpy
import sys
from pathlib import Path

# 在独立的课程子目录中生成可迁移的真实Python项目。
files = ''' + repr(files) + '''
root = Path("lesson_study_cli")
for name, content in files.items():
    target = root / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
# runpy在当前解释器执行真实入口，Windows与Android都无需启动额外进程。
entry = (root / "main.py").resolve()
old_path, old_argv = sys.path[:], sys.argv[:]
old_modules = {name: module for name, module in sys.modules.items()
               if name == "studytools" or name.startswith("studytools.")}
for name in old_modules:
    del sys.modules[name]
try:
    sys.path.insert(0, str(root.resolve()))
    sys.argv = [str(entry)]
    runpy.run_path(str(entry), run_name="__main__")
finally:
    sys.path[:], sys.argv = old_path, old_argv
    for name in list(sys.modules):
        if name == "studytools" or name.startswith("studytools."):
            del sys.modules[name]
    sys.modules.update(old_modules)
'''

lesson(c,"p08","项目八：多文件学习时间CLI",100,"l29 l47 l48 l50",["真正建立包、入口与工具模块并执行import","为命令行、标准输入和纯计算划分职责"],
"需求：输入多段非负整数分钟数，输出次数、总时长、平均与最长。项目使用真实文件：main.py负责参数、输入与输出，studytools/__init__.py标识工具包，studytools/stats.py只负责统计。桌面终端可运行python main.py 12 18 30；没有参数时从标准输入读取，因此应用编辑器也能使用。\n\n本课单文件示例先在lesson_study_cli子目录生成上述文件，再通过标准库runpy在当前解释器执行main.py，实际发生跨文件import，不需要额外进程。代码在执行前暂时设置项目搜索路径，结束后恢复路径、参数与该工具包的模块缓存，因此重复运行示例和答案也不会拿到旧版模块。应用如支持载入多文件示例，可直接使用files中的项目文件。修改答案时保持文件名和导入名一致。进一步可添加tests/test_stats.py与README，导出ZIP后在标准Python环境运行。",
["把三个项目文件写入课程子目录，保留标准包结构。","入口通过argparse收集参数，业务函数summarize校验并返回字典。","输出来自真正执行的main.py；12、18、30合计60、平均20、最长30。"],
bootstrap(cli_files),"分钟（空格分隔）：次数：3\n总计：60分钟\n平均：20.0分钟\n最长：30分钟\n",
"在stats模块返回统计学中位数median，在入口增加一行显示。必须修改两个文件并保持入口不重复计算中位数；演示数据的中位数为18。",
bootstrap(cli_solution_files),"分钟（空格分隔）：次数：3\n总计：60分钟\n平均：20.0分钟\n最长：30分钟\n中位数：18.0分钟\n",
["文件不在同一项目结构内、包名拼错或入口工作方式不对，会导致ModuleNotFoundError。","在stats模块顶层写input，会让import它的测试或其他模块意外等待输入。"],
"可迁移项目依靠真实文件与标准import；入口负责交互，模块负责可测试的业务。",stdin="12 18 30\n",sources=[TUTORIAL+"modules.html","https://docs.python.org/3.11/library/argparse.html"],cases=[
    {"name":"negative-duration","field":"code","stdin":"12 -1 30\n","expectedOutput":"分钟（空格分隔）：错误：时长不能为负\n"},
    {"name":"even-count-median","field":"solution","stdin":"10 20 30 40\n","expectedOutput":"分钟（空格分隔）：次数：4\n总计：100分钟\n平均：25.0分钟\n最长：40分钟\n中位数：25.0分钟\n"}])
c["lessons"][-1]["files"] = cli_files
c["lessons"][-1]["solutionFiles"] = cli_solution_files

by_id = {entry["id"]: entry for item in chapters for entry in item["lessons"]}
by_id["l30"]["body"] += "\n\n参考答案中的 except ValueError as error 会把捕获到的异常对象绑定给 error，print(error)显示它的消息；这与直接忽略异常不同。"
by_id["l33"]["body"] += "\n\n代码中的 done += 1 是 done = done + 1 的简写，对本课整数计数含义相同；可变对象的增量赋值还可能修改原对象，不能一概理解为复制。"
by_id["l35"]["body"] += "\n\n练习里的 all(...) 接收一组真假值，全部为真才返回True。列表推导式先为每个骰子值产生范围检查结果；下划线 _ 是普通变量名，这里约定表示不使用的循环计数。"
by_id["l37"]["body"] += "\n\n容器作为条件时，空容器是假、非空容器是真。因此练习中的 while tasks 会持续取出任务，直到队列变空。"
by_id["p08"]["body"] += "\n\n嵌入解释器可能不自动搜索任意项目目录，因此自举示例显式把生成目录加入sys.path。runpy保留当前解释器的真实input与输出，在Android上同样能等待输入。这是运行环境适配，不需要修改stats业务模块；它也不提供安全沙箱。"
by_id["p02"]["testCases"].extend([
    {"name": "reject-nonfinite-number", "field": "code", "stdin": "NaN + 2\n", "expectedOutput": "表达式：错误：请输入：数字 运算符 数字\n"},
    {"name": "reject-overflow-result", "field": "code", "stdin": "1e308 * 1e308\n", "expectedOutput": "表达式：错误：结果超出有限数值范围\n"},
    {"name": "reject-zero-negative-power", "field": "solution", "stdin": "0 ** -1\n", "expectedOutput": "表达式：错误：0不能取负指数\n"},
    {"name": "reject-complex-power", "field": "solution", "stdin": "-4 ** 0.5\n", "expectedOutput": "表达式：错误：负数底数只支持整数指数\n"},
])
by_id["p04"]["testCases"].extend([
    {"name": "reload-persisted-tasks", "field": "code", "stdin": "add 阅读\ndone 1\nquit\n", "expectedOutput": "> 已添加\n> 已完成\n> 已退出\n", "followupStdin": "list\nquit\n", "followupExpectedOutput": "> 1 [x] 阅读\n> 已退出\n"},
    {"name": "protect-malformed-task-file", "field": "code", "stdin": "add 新任务\nquit\n", "initialFiles": {"project_todos.json": "{}"}, "expectedOutput": "读取失败，未覆盖原文件：任务文件应为列表\n", "expectedFiles": {"project_todos.json": "{}"}},
])
by_id["p07"]["testCases"].extend([
    {"name": "reload-persisted-ledger", "field": "code", "stdin": "income 工资 100\nexpense 午餐 25.50\nquit\n", "expectedOutput": "账本> 已记账\n账本> 已记账\n账本> 已退出\n", "followupStdin": "summary\nquit\n", "followupExpectedOutput": "账本> 收入：100.00 支出：25.50 结余：74.50\n午餐：25.50\n账本> 已退出\n"},
    {"name": "protect-malformed-ledger-file", "field": "code", "stdin": "income 工资 100\nquit\n", "initialFiles": {"project_ledger.csv": "wrong\n"}, "expectedOutput": "读取失败，未覆盖原账本：账本列格式错误\n", "expectedFiles": {"project_ledger.csv": "wrong\n"}},
])
by_id["p08"]["testCases"].extend([
    {"name": "empty-duration-list", "field": "code", "stdin": "\n", "expectedOutput": "分钟（空格分隔）：错误：至少输入一段时长\n"},
    {"name": "direct-multifile-entry", "field": "code", "fileSet": "files", "stdin": "12 18 30\n", "expectedOutput": "分钟（空格分隔）：次数：3\n总计：60分钟\n平均：20.0分钟\n最长：30分钟\n"},
    {"name": "direct-multifile-answer", "field": "solution", "fileSet": "solutionFiles", "stdin": "10 20 30 40\n", "expectedOutput": "分钟（空格分隔）：次数：4\n总计：100分钟\n平均：25.0分钟\n最长：40分钟\n中位数：25.0分钟\n"},
])

def write_course():
    from author_tiers import author_all,build_tiers
    build_tiers(chapters,author_all())
    from deepen_v3 import apply as apply_reviewed_difficulty
    apply_reviewed_difficulty(chapters)
    data = {"version": 2, "title": "PySlate 离线 Python 课程", "language": "zh-CN", "pythonTarget": "3.11+", "tierOrder":["beginner","intermediate","advanced"],"testCaseSemantics":"canonical cases; ordered replacements followed by appended assertions; exact stdout/file/followup checks", "authorship": "PySlate 原创中文教材；官方文档用于事实核查与延伸阅读，未批量复制教程文本。", "chapters": chapters}
    target = Path(__file__).with_name("course.json")
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {sum(len(item['lessons']) for item in chapters)} topics / 174 learning units to {target}")


if __name__ == "__main__":
    write_course()
