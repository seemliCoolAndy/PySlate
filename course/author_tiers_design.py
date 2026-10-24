"""Reliable data processing and program design, all examples executable offline."""
from tier_helpers import add, case

def populate(t):
    add(t,'l33','intermediate','JSON结构校验：能解析不代表能使用', ['校验容器、键和值的类型','拒绝bool冒充整数与重复标识'],
        'json.loads只回答文本是否能解析，并不保证它符合应用需要。本例定义任务列表协议：每项必须是字典，id为正整数且不重复，title为非空字符串，done为真正布尔值。因为Python的bool是int子类，严格id校验用type(value) is int。验证返回新的记录列表，避免把外部未验证结构直接放进程序状态。未知字段在此允许但不带入结果，相当于明确定义可用字段；若要拒绝未知字段，也应写成协议而不是偶然行为。',
        ['解析文本得到普通Python对象','逐项验证类型、范围和id唯一性','只返回通过验证的标准字段'],
        '''import json
def load_tasks(text):
    data=json.loads(text)
    if not isinstance(data,list):
        raise ValueError("任务必须是列表")
    result=[]; seen=set()
    for task in data:
        if not isinstance(task,dict):
            raise ValueError("任务必须是对象")
        key=task.get("id"); title=task.get("title"); done=task.get("done")
        if type(key) is not int or key<=0 or key in seen or not isinstance(title,str) or not title.strip() or type(done) is not bool:
            raise ValueError("任务字段无效")
        seen.add(key)
        result.append({"id":key,"title":title.strip(),"done":done})
    return result
print(load_tasks('[{"id":1,"title":" 阅读 ","done":false}]'))''',"[{'id': 1, 'title': '阅读', 'done': False}]\n",
        '实现load_scores：JSON对象的键为非空姓名，值为0至100整数（排除bool）；返回新字典。',
        '''import json
def load_scores(text):
    data=json.loads(text)
    if not isinstance(data,dict):
        raise ValueError("成绩必须是对象")
    for name,score in data.items():
        if not name.strip() or type(score) is not int or not 0<=score<=100:
            raise ValueError("姓名或成绩无效")
    return data.copy()
print(load_scores('{"小禾":80,"阿青":0}'))''',"{'小禾': 80, '阿青': 0}\n",
        ['JSON解析成功不能替代应用schema校验','isinstance(True,int)会通过，严格整数要排除布尔'], '外部数据经过解析和业务验证两道门，才能进入内部状态。',
        ('validation','id=true为什么不能算作合法编号1？','JSON值映射到Python类型再经过严格协议验证',[('解析','true → bool True'),('id契约','type必须为int'),('结果','拒绝，不混淆编号1')]),
        [case('重复id拒绝',"try:\n    load_tasks('[{\"id\":1,\"title\":\"a\",\"done\":false},{\"id\":1,\"title\":\"b\",\"done\":true}]')\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('duplicate')"),case('布尔成绩拒绝',"assert load_scores('{}')=={}\ntry:\n    load_scores('{\"A\":true}')\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('bool')",field='solution')])
    add(t,'l33','advanced','版本迁移与严格JSON', ['把旧格式迁移成统一新结构','拒绝重复键和非标准浮点常量'],
        '持久文件升级后仍可能遇到旧格式。不要在每个页面里同时支持两套结构，而应在加载边界迁移为统一版本。本例v1只有title列表，v2改为有编号的任务对象，迁移函数返回新结构且不改输入。另一个细节是Python默认JSON解码允许NaN并对重复键保留后值；如果配置要求严格，需用parse_constant和object_pairs_hook拒绝。练习实现严格解码器，让重复配置不再悄悄覆盖，避免解析器的宽松行为成为业务决策。',
        ['通过version选择明确支持的格式','为旧记录产生确定编号并返回v2','拒绝未知版本，严格解码保留冲突证据'],
        '''def migrate(data):
    version=data.get("version")
    if version==1:
        titles=data.get("titles")
        if not isinstance(titles,list) or any(not isinstance(x,str) or not x.strip() for x in titles):
            raise ValueError("旧任务格式无效")
        return {"version":2,"tasks":[{"id":i,"title":title,"done":False} for i,title in enumerate(titles,1)]}
    if version==2:
        return {"version":2,"tasks":[dict(x) for x in data["tasks"]]}
    raise ValueError("不支持的版本")
old={"version":1,"titles":["阅读","练习"]}
print(migrate(old))''',"{'version': 2, 'tasks': [{'id': 1, 'title': '阅读', 'done': False}, {'id': 2, 'title': '练习', 'done': False}]}\n",
        '实现strict_loads，拒绝任意层对象的重复键和NaN/Infinity；正常JSON值保持原结构，不能用eval。',
        '''import json
def unique_pairs(pairs):
    result={}
    for key,value in pairs:
        if key in result:
            raise ValueError("重复键："+key)
        result[key]=value
    return result
def reject_constant(value):
    raise ValueError("非标准数字："+value)
def strict_loads(text):
    return json.loads(text,object_pairs_hook=unique_pairs,parse_constant=reject_constant)
print(strict_loads('{"version":2,"values":[0,1.5]}'))''',"{'version': 2, 'values': [0, 1.5]}\n",
        ['未知版本默认按最新版读会误解释字段','json默认行为并非最严格的配置协议'], '迁移把历史复杂性限制在加载边界，严格解码把格式冲突显式交给调用者。',
        ('schema-migration','旧标题列表怎样变成有稳定字段的新记录？','版本门与单向迁移后的统一结构',[('v1','titles:阅读、练习'),('迁移','编号1和2；done=False'),('v2','统一tasks结构')]),
        [case('迁移不改源','assert old=={"version":1,"titles":["阅读","练习"]}\nassert migrate({"version":1,"titles":[]})=={"version":2,"tasks":[]}'),case('嵌套重复和NaN拒绝',"for text in ('{\"x\":{\"a\":1,\"a\":2}}','[NaN]','[Infinity]'):\n    try:\n        strict_loads(text)\n    except ValueError:\n        pass\n    else:\n        raise AssertionError(text)",field='solution')],sources=['https://docs.python.org/3.11/library/json.html'])
    add(t,'l34','intermediate','CSV坏行定位与严格列协议', ['检查表头与每行列数','保留真实行号并逐行转换数值'],
        'CSV模块处理引号与分隔符，但不会替你判断某一行列数是否符合业务。本例用csv.reader读取逻辑记录，明确要求name,score两列表头，逐行检查长度和分数范围；坏行收集行号，其他有效行继续。这里的行号是逻辑记录序号：若字段中含换行，一条CSV记录可占多物理行，实际文件定位可结合reader.line_num。练习选择整批拒绝的策略，列多列少、空姓名和非整数均不能被默认补值掩盖。',
        ['表头作为协议精确检查','每行先检查列数再解包','数值转换失败记录逻辑记录号'],
        '''import csv,io
def read_scores(text):
    reader=csv.reader(io.StringIO(text,newline=""))
    if next(reader,None)!=["name","score"]:
        raise ValueError("表头错误")
    valid=[]; bad=[]
    for number,row in enumerate(reader,2):
        try:
            if len(row)!=2 or not row[0].strip():
                raise ValueError("列或姓名无效")
            score=int(row[1])
            if not 0<=score<=100:
                raise ValueError("范围")
        except ValueError:
            bad.append(number)
        else:
            valid.append((row[0],score))
    return valid,bad
print(read_scores("name,score\\nA,80\\nB,no\\nC,90,extra\\n"))''',"([('A', 80)], [3, 4])\n",
        '实现strict_items，表头item,count；每行恰两列，名称非空，数量为非负整数。任一坏行抛带逻辑记录号的ValueError。',
        '''import csv,io
def strict_items(text):
    reader=csv.reader(io.StringIO(text,newline=""))
    if next(reader,None)!=["item","count"]:
        raise ValueError("表头错误")
    result=[]
    for number,row in enumerate(reader,2):
        try:
            if len(row)!=2 or not row[0].strip():
                raise ValueError("列无效")
            count=int(row[1])
            if count<0:
                raise ValueError("负数量")
        except ValueError as error:
            raise ValueError(f"记录{number}无效") from error
        result.append((row[0],count))
    return result
print(strict_items('item,count\\n"book,large",2\\n'))''',"[('book,large', 2)]\n",
        ['DictReader多列可能进入None键，不能当作已验证数据','字段含换行时逻辑记录号不等于物理文件行号'], 'CSV工具负责语法，应用负责表头、列数、范围以及坏行策略。',
        ('table-validation','有引号的逗号与多余一列怎样区分？','CSV先还原字段，再校验两列契约',[('合法记录','"book,large",2 → 两列'),('坏记录','C,90,extra → 三列'),('业务校验','拒绝列数不符')]),
        [case('引号逗号合法','assert read_scores(\'name,score\\n"A,B",0\\n\')==([("A,B",0)],[])'),case('缺列不接受',"try:\n    strict_items('item,count\\nx\\n')\nexcept ValueError as e:\n    assert '2' in str(e)\nelse:\n    raise AssertionError('missing')",field='solution')])
    add(t,'l34','advanced','CSV往返与电子表格边界', ['验证引号和多行字段往返不丢失','区分CSV正确转义与表格公式风险'],
        'csv.writer能正确引用含逗号、引号与换行的字段，往返解析应恢复原始字符串。但CSV语法转义不等于电子表格安全：以等号等字符开头的数据，某些表格程序打开时可能当公式执行。要面向电子表格展示可采用显式文本前缀策略，但这会改变导出的值，必须另行注明；原始数据交换则不应偷偷改写。本例先验证纯CSV往返，练习另写展示导出策略，对可疑文本加单引号并承认这是展示约定，非通用安全保证。',
        ['StringIO提供内存文本流并交给csv管理换行','writer引用复杂字段，reader还原','展示导出和原始交换使用不同显式函数'],
        '''import csv,io
def csv_roundtrip(rows):
    stream=io.StringIO(newline="")
    csv.writer(stream,lineterminator="\\n").writerows(rows)
    encoded=stream.getvalue()
    decoded=list(csv.reader(io.StringIO(encoded,newline="")))
    return encoded,decoded
rows=[["name","note"],["A,B",'said "hi"'],["C","line1\\nline2"]]
encoded,decoded=csv_roundtrip(rows)
print(decoded==rows)
print(len(decoded),len(decoded[2]))''','True\n3 2\n',
        '实现spreadsheet_text(value)，若忽略前导空白后首字符是=、+、-、@，则在原值前加单引号；否则原样。只用于展示导出，数字列应另外按数值建模。',
        '''def spreadsheet_text(value):
    stripped=value.lstrip()
    if stripped and stripped[0] in "=+-@":
        return "'"+value
    return value
print(repr(spreadsheet_text(" =1+1")))
print(repr(spreadsheet_text("hello")))''',"\"' =1+1\"\n'hello'\n",
        ['CSV字段加双引号并不会阻止表格程序把它当公式','悄悄改写原始导出会破坏数据往返等价'], '数据格式正确和消费应用如何解释内容是两层问题，导出策略应明确用途。',
        ('roundtrip','被引号保护的换行为什么仍属于同一个字段？','CSV编码与解码保持记录结构',[('原结构','三条记录，每条两字段'),('文本编码','逗号引号换行正确引用'),('读回','仍三条两字段')]),
        [case('空字段与引号往返','x=[["","a,b","x\\ny",\'"\']]\nassert csv_roundtrip(x)[1]==x'),case('前导制表与普通负文本','assert spreadsheet_text("\\t@x")=="\'\\t@x"\nassert spreadsheet_text("")=="" and spreadsheet_text("hello=1")=="hello=1"',field='solution')])
    add(t,'l35','intermediate','随机状态隔离与重放', ['使用独立Random对象避免互相干扰','保存状态重放一段实验'],
        '随机实验想要可调试，不能让不相关代码随意消费同一个全局随机序列。Random(seed)提供独立状态，本例在生成前保存getstate，再setstate恢复，使同一对象在同一运行环境中重放同一段抽样。固定种子并不意味着所有高级随机方法在未来各版本永远生成相同序列，所以测试更适合检查范围、长度和重放关系，不把某段复杂序列硬编码成永久协议。练习设计不放回抽样，明确样本量超出总体大小时应拒绝。',
        ['创建独立随机对象而不调用全局seed','记录抽样前状态','恢复状态后重抽并比较两段结果'],
        '''import random
rng=random.Random(42)
state=rng.getstate()
first=[rng.randint(1,6) for _ in range(8)]
rng.setstate(state)
again=[rng.randint(1,6) for _ in range(8)]
print(first==again)
print(len(first),all(1<=x<=6 for x in first))''','True\n8 True\n',
        '实现draw_without_replacement(items,count,seed)，使用局部Random和sample，样本量0允许，负数或超过总体长度拒绝；不修改输入。',
        '''import random
def draw_without_replacement(items,count,seed):
    if not 0<=count<=len(items):
        raise ValueError("样本量无效")
    return random.Random(seed).sample(items,count)
items=["A","B","C","D"]
draw=draw_without_replacement(items,3,7)
print(len(draw),len(set(draw)),items==["A","B","C","D"])''','3 3 True\n',
        ['全局seed会重置其他代码的随机状态','sample不放回不代表值必定不重复，原总体重复值仍可重复'], '测试随机程序应验证性质与可重放性，并隔离随机状态所有权。',
        ('random-state','恢复状态后，为何下一段骰子序列会完全重现？','随机对象状态快照控制后续抽样',[('快照S','抽样前状态'),('向前','生成8次，状态改变'),('恢复S','再抽8次，与首次一致')]),
        [case('独立对象不干扰','a=random.Random(1); b=random.Random(1)\n[random.Random(9).random() for _ in range(20)]\nassert a.random()==b.random()'),case('零样本和边界','assert draw_without_replacement([1,2],0,1)==[]\nassert set(draw_without_replacement([1,2],2,1))=={1,2}',field='solution')],sources=['https://docs.python.org/3.11/library/random.html'])
    add(t,'l35','advanced','蒙特卡洛不是单次猜测', ['用频数和理论值检查模拟','用确定性枚举验证随机实验的模型'],
        '随机模拟的结果不是证明。两个公平骰子点数和为7的理论概率是6/36，因为36个等可能有序结果中有6个命中。本例先完整枚举给出基准，再做6000次独立抽样，比较观察频率。测试不要求恰好1000次命中，更不应因一次偏差就断言随机库坏了；它检查计数总量、取值范围及理论枚举。练习实现加权离散抽样器，先验证权重非负且总量为正，使用累计区间理解每个结果被选中的机会。',
        ['枚举36个有序结果建立理论基准','随机实验每次重新抽两个骰子','把观察频率看作估计而非精确答案'],
        '''import random
theoretical=sum(a+b==7 for a in range(1,7) for b in range(1,7))
rng=random.Random(5)
trials=6000
hits=sum(rng.randint(1,6)+rng.randint(1,6)==7 for _ in range(trials))
print(theoretical,36)
print(0<=hits<=trials,abs(hits/trials-1/6)<0.05)''','6 36\nTrue True\n',
        '实现choose_weighted(items,weights,rng)，非负整数权重、长度相同且总和正；用randrange(total)与累计区间抽取，零权重项永不选。',
        '''import random
def choose_weighted(items,weights,rng):
    if len(items)!=len(weights) or not weights or any(type(w) is not int or w<0 for w in weights) or sum(weights)==0:
        raise ValueError("权重无效")
    ticket=rng.randrange(sum(weights))
    cumulative=0
    for item,weight in zip(items,weights):
        cumulative+=weight
        if ticket<cumulative:
            return item
rng=random.Random(3)
draws=[choose_weighted(["never","yes"],[0,2],rng) for _ in range(20)]
print(set(draws)=={"yes"})''','True\n',
        ['把有限实验频率当作理论概率会过度推断','累计区间比较写<=会把零权重或边界错误分配'], '先验证概率模型，再使用随机估计；区间边界决定离散抽样是否正确。',
        ('probability','36种结果中，和为7为何恰有6种？','骰子有序结果网格中的反对角线',[('全集','6×6=36'),('命中','(1,6)…(6,1)共6'),('理论','6/36=1/6；模拟近似')]),
        [case('枚举对称与总量','assert theoretical==6 and trials==6000 and abs(hits/trials-1/6)<0.05'),case('确定票号覆盖边界','class Ticket:\n    def __init__(self,n): self.n=n\n    def randrange(self,total): assert self.n<total; return self.n\nassert [choose_weighted(["a","b"],[2,1],Ticket(i)) for i in range(3)]==["a","a","b"]',field='solution')])
    add(t,'l36','intermediate','时间偏移与金额舍入分别建模', ['使用带时区时间表达同一时刻','明确Decimal的输入来源与舍入规则'],
        '日期时间与金额都需要明确表示约定。无时区datetime只是一组墙上时间数字，不能独自说明全球哪个时刻；本例用UTC创建时间，再转换到固定+8偏移。固定偏移不是具备历史夏令时规则的地区时区，不能套给所有地区。金额使用Decimal字符串构造，quantize配合ROUND_HALF_UP明确到分舍入；Decimal(float)会把二进制近似带入。练习只讨论固定偏移预约，不依赖在线时区数据库，也不把日期字符串当时间长度相减。',
        ['建立带UTC时区的datetime','astimezone保持时刻但改变显示偏移','Decimal从文本构造并明确到分规则'],
        '''from datetime import datetime,timezone,timedelta
from decimal import Decimal,ROUND_HALF_UP
instant=datetime(2026,1,1,18,30,tzinfo=timezone.utc)
local=instant.astimezone(timezone(timedelta(hours=8)))
amount=Decimal("2.675").quantize(Decimal("0.01"),rounding=ROUND_HALF_UP)
print(local.isoformat())
print(amount)''','2026-01-02T02:30:00+08:00\n2.68\n',
        '实现meeting_end(start_text,minutes)，输入ISO带时区开始时间，分钟非负，拒绝无时区时间；返回结束时间isoformat。',
        '''from datetime import datetime,timedelta
def meeting_end(start_text,minutes):
    start=datetime.fromisoformat(start_text)
    if start.tzinfo is None or start.utcoffset() is None or minutes<0:
        raise ValueError("需要带时区时间和非负时长")
    return (start+timedelta(minutes=minutes)).isoformat()
print(meeting_end("2026-01-01T23:50:00+08:00",20))''','2026-01-02T00:10:00+08:00\n',
        ['无时区时间不能自动认为就是UTC','Decimal(2.675)和Decimal("2.675")的起点不同'], '时间需明确时区，金额需明确精度和舍入；文本外观不构成完整数值模型。',
        ('timeline','UTC晚上18:30转换到+8后为什么跨日？','同一时刻沿时区偏移改变显示日期',[('UTC','1月1日18:30'),('加8小时','跨越午夜'),('本地显示','1月2日02:30 +08:00')]),
        [case('同一时刻与明确舍入','assert local==instant and amount==Decimal("2.68")'),case('零时长与无时区拒绝',"assert meeting_end('2026-01-01T00:00:00+00:00',0)=='2026-01-01T00:00:00+00:00'\ntry:\n    meeting_end('2026-01-01T00:00:00',1)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('naive')",field='solution')])
    add(t,'l36','advanced','分摊到分：总额必须守恒', ['把Decimal金额转成整数分后分摊','处理余数让所有份额之和精确等于总额'],
        '把10元平分3人，每人显示3.33会只分出9.99。方案必须同时规定舍入和余分分配。本例要求总金额本来就精确到分，转为整数分后做divmod：每人得到商，前remainder人各多1分，因此差额最多1分且总和严格守恒。拒绝负金额、非有限数字以及超过两位小数的输入，不在分摊时悄悄改变总额。练习按百分比计算各行税费，分别比较“每行先舍入”与“总额后舍入”，承认两种政策可能不同而不是把差异当浮点错误。',
        ['验证金额是有限非负且恰好到分','整数分求商与余数','按确定顺序分配剩余1分并核对总和'],
        '''from decimal import Decimal
def split_money(text,people):
    amount=Decimal(text)
    if people<=0 or not amount.is_finite() or amount<0 or amount!=amount.quantize(Decimal("0.01")):
        raise ValueError("金额或人数无效")
    cents=int(amount*100)
    base,extra=divmod(cents,people)
    return [Decimal(base+(i<extra))/100 for i in range(people)]
parts=split_money("10.00",3)
print([f"{x:.2f}" for x in parts])
print(sum(parts)==Decimal("10.00"))''',"['3.34', '3.33', '3.33']\nTrue\n",
        '实现tax_totals(prices,rate)，Decimal文本输入，按ROUND_HALF_UP到分；返回每行舍入税额之和、总价税额后舍入两种结果，演示两项0.05、税率0.1。',
        '''from decimal import Decimal,ROUND_HALF_UP
def tax_totals(prices,rate):
    values=[Decimal(x) for x in prices]
    rate=Decimal(rate)
    if any(not x.is_finite() or x<0 for x in values) or not rate.is_finite() or rate<0:
        raise ValueError("金额或税率无效")
    cent=Decimal("0.01")
    per_line=sum((x*rate).quantize(cent,rounding=ROUND_HALF_UP) for x in values)
    on_total=(sum(values,Decimal(0))*rate).quantize(cent,rounding=ROUND_HALF_UP)
    return per_line,on_total
print(tax_totals(["0.05","0.05"],"0.1"))''',"(Decimal('0.02'), Decimal('0.01'))\n",
        ['逐人四舍五入不能保证份额和等于总额','未声明逐行还是汇总舍入，会使同一数据出现不同合规结果'], '先定义舍入政策，再用整数分与守恒条件验证分配算法。',
        ('allocation','10元除3后，多出的1分应该到哪里？','1000分的商余分配与精确总和',[('整除','1000÷3 商333余1'),('分配','334、333、333分'),('核对','总和1000分')]),
        [case('总额少于人数','p=split_money("0.02",4)\nassert p==[Decimal("0.01"),Decimal("0.01"),Decimal(0),Decimal(0)] and sum(p)==Decimal("0.02")'),case('空税额与零税率','assert tax_totals([],"0.1")== (0,Decimal("0.00"))\nassert tax_totals(["100"],"0")== (Decimal("0.00"),Decimal("0.00"))',field='solution')])
    add(t,'l37','intermediate','Counter、defaultdict与分组报告', ['选择计数与分组所需的容器','检查defaultdict读取可能产生新键'],
        'Counter表达每个值出现多少次，defaultdict(list)表达每组有哪些记录，两者解决不同问题。本例按课程统计人数并保存姓名；defaultdict在用下标读取缺失键时会调用工厂并插入新值，因此只想查询时可用get避免改变结构。Counter缺失计数读为0，但不能据此断言键一定存储在字典里。报告按课程名排序，避免把输入顺序误当排名。练习构建逆向索引：某个单词出现在哪些文档中，同一文档重复出现只记录一次。',
        ['Counter累计类别次数','defaultdict把同类姓名加入列表','查询缺失组用get不制造空组'],
        '''from collections import Counter,defaultdict
records=[("Python","禾"),("CSV","青"),("Python","川")]
counts=Counter(course for course,name in records)
groups=defaultdict(list)
for course,name in records:
    groups[course].append(name)
print(sorted(counts.items()))
print(groups.get("未知",[]),"未知" in groups)''',"[('CSV', 1), ('Python', 2)]\n[] False\n",
        '实现invert_documents(documents)，字典为文档名到词列表，返回单词到排序文档名列表；一文档内重复词只出现一次。',
        '''from collections import defaultdict
def invert_documents(documents):
    index=defaultdict(set)
    for name,words in documents.items():
        for word in words:
            index[word].add(name)
    return {word:sorted(names) for word,names in sorted(index.items())}
print(invert_documents({"b":["py","py"],"a":["py","csv"]}))''',"{'csv': ['a'], 'py': ['a', 'b']}\n",
        ['defaultdict用下标查不存在键会顺便改变字典','词频与文档出现次数不同，不能直接用Counter代替文档集合'], '容器应匹配统计含义，读取是否改变状态也是接口的一部分。',
        ('group-index','同一文档出现两次py，为何索引仍只记一次？','词到文档集合的逆向映射',[('文档b','py py → 集合{b}'),('文档a','py csv'),('py索引','{a,b} → 排序[a,b]')]),
        [case('缺失查询不生键','before=len(groups)\nassert groups.get("none",[])==[] and len(groups)==before'),case('空文档与重复词','assert invert_documents({"x":[],"y":["a","a"]})=={"a":["y"]}',field='solution')])
    add(t,'l37','advanced','deque广度优先搜索与已访问集合', ['用队列按距离层次遍历','在入队时去重避免环与重复队列项'],
        '广度优先搜索使用先进先出队列，先处理离起点1步的点，再处理2步的点，因此无权图中第一次发现某点就得到最短边数。deque.popleft适合队首取出，列表pop(0)会移动后续元素。关键是入队时立刻标记已访问，而不是出队才标记，否则多个邻居会重复加入同一点，环也会反复扩展。本例把距离放进字典兼作已访问集合；练习保存前驱来还原路径，明确起终点相同返回单点路径，不可达返回None。',
        ['起点距离0先入队并标记','逐个出队扩展未见邻居','第一次发现距离等于当前距离加1'],
        '''from collections import deque
def distances(graph,start):
    result={start:0}; queue=deque([start])
    while queue:
        node=queue.popleft()
        for neighbor in graph.get(node,[]):
            if neighbor not in result:
                result[neighbor]=result[node]+1
                queue.append(neighbor)
    return result
graph={"A":["B","C"],"B":["D"],"C":["D"],"D":["A"]}
print(distances(graph,"A"))''',"{'A': 0, 'B': 1, 'C': 1, 'D': 2}\n",
        '实现shortest_path(graph,start,end)，BFS记录前驱并倒序还原路径；不得用全路径枚举，遇环也要终止。',
        '''from collections import deque
def shortest_path(graph,start,end):
    previous={start:None}; queue=deque([start])
    while queue:
        node=queue.popleft()
        if node==end:
            path=[]
            while node is not None:
                path.append(node); node=previous[node]
            return path[::-1]
        for neighbor in graph.get(node,[]):
            if neighbor not in previous:
                previous[neighbor]=node
                queue.append(neighbor)
    return None
print(shortest_path({"A":["B"],"B":["A","C"]},"A","C"))''',"['A', 'B', 'C']\n",
        ['出队才标记会让共同邻居多次入队','BFS最短性适用于无权边，不能直接当加权最短路'], '队列顺序体现层次，入队去重保证环图终止，前驱记录支持还原解释。',
        ('bfs','B和C都指向D，D为何只入队一次？','队列层次与入队时标记的执行过程',[('层0','队列[A]'),('层1','发现B、C，距离1'),('层2','B发现D距离2；C见D已标记')]),
        [case('自环终止','assert distances({"x":["x"]},"x")=={"x":0}'),case('同点与不可达','assert shortest_path({},"A","A")==["A"]\nassert shortest_path({"A":["A"]},"A","B") is None',field='solution')])
    add(t,'l38','intermediate','多键排序与稳定性', ['用元组key表达优先级','处理降序分数与升序姓名的混合规则'],
        '排序key返回元组时，先比较第一项，相同才比较下一项。本例要求分数高在前、同分姓名升序，因此key为(-score,name)，不能简单reverse=True，因为它会让姓名也倒序。稳定排序意味着key相同的记录仍保留输入先后，可用于不额外打乱同名同分记录。sorted返回新列表，原记录顺序不变；list.sort则原地修改并返回None。练习对任务按未完成优先、优先级降序、id升序排序，明确每个维度的方向。',
        ['把每条业务排序规则映射到一个key分量','只对需要降序的数字取负','验证相同key保留原顺序'],
        '''records=[("B",90),("A",90),("C",80)]
ranked=sorted(records,key=lambda item:(-item[1],item[0]))
print(ranked)
print(records)''',"[('A', 90), ('B', 90), ('C', 80)]\n[('B', 90), ('A', 90), ('C', 80)]\n",
        '实现sort_tasks，记录含id、done、priority；未完成在前，同组priority高在前，再按id小在前；返回新列表。',
        '''def sort_tasks(tasks):
    return sorted(tasks,key=lambda x:(x["done"],-x["priority"],x["id"]))
tasks=[{"id":2,"done":False,"priority":1},{"id":1,"done":True,"priority":9},{"id":3,"done":False,"priority":2}]
print([x["id"] for x in sort_tasks(tasks)])''','[3, 2, 1]\n',
        ['全局reverse=True会把所有排序维度一并反转','sorted不复制记录内部可变对象，排序副本不是深复制'], '多维排序逐个指定方向；稳定性与是否原地修改属于不同保证。',
        ('sort-keys','同分A为什么在B前，而低分C仍在最后？','复合key先负分数再姓名',[('B90','key(-90,B)'),('A90','key(-90,A)'),('排序','A90 B90 C80')]),
        [case('同键稳定','items=[("A",1,"first"),("A",1,"second")]\nassert sorted(items,key=lambda x:(x[0],x[1]))==items'),case('任务复合边界','x=[{"id":2,"done":False,"priority":1},{"id":1,"done":False,"priority":1}]\nassert [a["id"] for a in sort_tasks(x)]==[1,2] and x[0]["id"]==2',field='solution')])
    add(t,'l38','advanced','排序后分组：排名规则不是位置编号', ['实现并列竞争排名','用已排序前缀决定下一名次'],
        '排名不是简单enumerate。分数90、90、80采用竞争排名时应为1、1、3；密集排名则是1、1、2，两种都可以但必须声明。本例采用竞争排名：按分数降序，分数改变时名次等于当前一基位置，同分沿用上一名次。稳定排序让同分记录保持原先顺序。练习实现密集排名并用相同数据对照，要求空记录正常返回、同分顺序不改变。把排序与赋名次分成两步，比塞进一个复杂key更清楚。',
        ['稳定按分数降序形成数据次序','只在分数改变时更新rank','竞争排名用位置，密集排名只加1'],
        '''def competition_rank(records):
    ordered=sorted(records,key=lambda x:-x[1])
    result=[]; previous=None; rank=0
    for position,(name,score) in enumerate(ordered,1):
        if position==1 or score!=previous:
            rank=position
        result.append((name,score,rank)); previous=score
    return result
print(competition_rank([("A",90),("B",90),("C",80)]))''',"[('A', 90, 1), ('B', 90, 1), ('C', 80, 3)]\n",
        '实现dense_rank，同分同名次，下一个不同分数名次只加1；使用分数降序稳定排列。',
        '''def dense_rank(records):
    ordered=sorted(records,key=lambda x:-x[1])
    result=[]; previous=None; rank=0
    for position,(name,score) in enumerate(ordered,1):
        if position==1 or score!=previous:
            rank+=1
        result.append((name,score,rank)); previous=score
    return result
print(dense_rank([("A",90),("B",90),("C",80)]))''',"[('A', 90, 1), ('B', 90, 1), ('C', 80, 2)]\n",
        ['给每条记录都用位置作为名次会破坏并列规则','把竞争排名和密集排名混在一起会造成不一致报告'], '先明确并列排名政策，再由已排序前缀维护名次状态。',
        ('ranking','两个第一名之后，是第三还是第二？','竞争与密集排名在同一分数序列上的差异',[('分数','90 90 80'),('竞争排名','1 1 3'),('密集排名','1 1 2')]),
        [case('全并列与空','assert competition_rank([])==[]\nassert [x[2] for x in competition_rank([("B",0),("A",0)])]==[1,1]'),case('乱序与稳定','assert dense_rank([])==[]\nassert dense_rank([("x",0),("a",5),("b",5)])==[("a",5,1),("b",5,1),("x",0,2)]',field='solution')],sources=['https://docs.python.org/3.11/howto/sorting.html'])
    add(t,'l39','intermediate','二分查找重复值的左边界', ['维护左闭右开候选区间','返回第一个不小于目标的位置'],
        '普通二分找到一个相等值就返回，重复数据中不一定是第一项。lower_bound定义为第一个不小于target的位置，不存在则返回len(values)。每轮若中点小于目标，就排除中点及左侧；否则保留中点作为可能答案，把右边界设为mid。区间使用[low,high)，所以初始high为长度，结束low==high。练习实现upper_bound，第一个大于目标的位置，两个边界相减就得到目标重复次数；改变的是等号归属，不是随意加减下标。',
        ['明确结果是插入位置而非可能不存在的元素','小于目标才移动low到mid+1','相等时继续向左收缩寻找更早位置'],
        '''def lower_bound(values,target):
    low,high=0,len(values)
    while low<high:
        mid=(low+high)//2
        if values[mid]<target:
            low=mid+1
        else:
            high=mid
    return low
values=[1,2,2,2,5]
print(lower_bound(values,2),lower_bound(values,6))''','1 5\n',
        '实现upper_bound，第一个严格大于目标的位置；演示[1,2,2,2,5]对2返回4，对0返回0。',
        '''def upper_bound(values,target):
    low,high=0,len(values)
    while low<high:
        mid=(low+high)//2
        if values[mid]<=target:
            low=mid+1
        else:
            high=mid
    return low
print(upper_bound([1,2,2,2,5],2),upper_bound([1,2,2,2,5],0))''','4 0\n',
        ['lower与upper的区别在等号归属，不能结果机械加1','二分前提是已按相同规则有序，不适合乱序列表'], '区间不变量比记忆代码更重要，重复值检验边界定义是否精确。',
        ('binary-interval','命中一个2后，为何还要继续找左侧？','候选区间收缩到第一个2的位置',[('初始','[0,5) mid2 值2'),('向左','[0,2) mid1 值2'),('终点','low=high=1')]),
        [case('空和全相同','assert lower_bound([],1)==0 and lower_bound([2,2],2)==0 and lower_bound([2,2],3)==2'),case('右边界与全相同','assert upper_bound([],1)==0 and upper_bound([2,2],2)==2 and upper_bound([2,2],1)==0',field='solution')])
    add(t,'l39','advanced','复杂度实验：数比较次数而不是盯秒表', ['用操作次数分析算法增长','与线性查找交叉验证结果'],
        '很短的程序计时容易被系统调度和启动开销淹没。为了理解复杂度，本例直接计数二分循环次数，数据长度从16增到1024时，比较数增长近似对数，而逐个扫描最坏与长度成正比。大O描述增长趋势，不保证小数据二分一定更快，也忽略常数及数据准备成本。练习为二分结果写穷举交叉检查：小规模有序列表上与简单线性定义比较，覆盖所有目标位置。这比只检查某个大列表命中一次更有说服力。',
        ['每轮二分累加一次比较计数','在未命中尾部场景观察增长','用易懂的线性定义作为小规模测试参照'],
        '''def search_steps(values,target):
    low,high=0,len(values); steps=0
    while low<high:
        steps+=1
        mid=(low+high)//2
        if values[mid]<target: low=mid+1
        else: high=mid
    return low,steps
for size in [16,64,1024]:
    position,steps=search_steps(list(range(size)),size)
    print(size,position,steps)''','16 16 4\n64 64 6\n1024 1024 10\n',
        '实现count_occurrences，自己写左右二分边界并相减；用小型数据与list.count交叉检查，不在算法内部线性扫描。',
        '''def boundary(values,target,right=False):
    low,high=0,len(values)
    while low<high:
        mid=(low+high)//2
        if values[mid]<target or (right and values[mid]==target): low=mid+1
        else: high=mid
    return low
def count_occurrences(values,target):
    return boundary(values,target,True)-boundary(values,target)
print(count_occurrences([1,2,2,2,5],2))''','3\n',
        ['把Python进程启动时间当算法耗时会误判增长','为了检验有序性每次全扫描会把整体查询退化为线性'], '操作次数揭示增长，简单参照实现和系统边界数据共同检验复杂算法。',
        ('growth','数据量增加64倍，二分比较为何只增加6次？','候选范围每轮减半与比较次数表',[('16项','4次尾部查找'),('64项','6次'),('1024项','10次')]),
        [case('对照所有小目标','for n in range(10):\n    xs=list(range(n))\n    for target in range(-1,n+2):\n        expected=next((i for i,x in enumerate(xs) if x>=target),len(xs))\n        assert search_steps(xs,target)[0]==expected'),case('重复次数穷举对照','for xs in ([],[0],[1,1,1],[-2,-2,0,3,3]):\n    for target in range(-3,5):\n        assert count_occurrences(xs,target)==xs.count(target)',field='solution')])
    add(t,'l40','intermediate','边界测试与等价类', ['按输入类别而非随机例子选择断言','检查正常值、端点和非法值'],
        '测试数量多不等于覆盖好。一个票价函数可能有免费、半价、全价和非法四类，连续测20、21、22岁仍只覆盖全价。本例按年龄区间挑选0、5、6、17、18和负数，端点两侧尤其容易揭示<与<=写错。assert适合开发测试，不适合承担生产输入校验，因为Python优化模式可移除断言。函数必须用显式raise校验非法输入，测试再用assert检查它按契约失败。练习给整数夹取函数写边界集合，防止把测试写成实现的逐行翻译。',
        ['从业务规则列出互异输入类别','每个区间挑内部与相邻端点','异常路径用try断言确实抛错'],
        '''def ticket(age):
    if type(age) is not int or age<0: raise ValueError("年龄无效")
    if age<6: return 0
    if age<18: return 10
    return 20
for age,expected in [(0,0),(5,0),(6,10),(17,10),(18,20)]:
    assert ticket(age)==expected
print("5个边界通过")''','5个边界通过\n',
        '实现clamp(value,low,high)，low>high拒绝，其他将值夹到闭区间；写断言覆盖下界外、恰下界、区间内、恰上界、上界外。',
        '''def clamp(value,low,high):
    if low>high: raise ValueError("区间反向")
    return min(max(value,low),high)
for value,expected in [(-1,0),(0,0),(4,4),(10,10),(11,10)]:
    assert clamp(value,0,10)==expected
print("5个夹取边界通过")''','5个夹取边界通过\n',
        ['assert会被优化移除，不能替代业务输入校验','很多同类正常值不能覆盖一个缺失边界'], '按等价类和边界选择测试，用独立需求决定预期值。',
        ('boundary-tests','为什么5岁和6岁都需要测试？','相邻年龄跨越票价规则边界',[('0至5','免费0'),('6至17','半价10'),('18起','全价20')]),
        [case('非法类型与负数',"for age in (-1,True,1.5):\n    try:\n        ticket(age)\n    except ValueError:\n        pass\n    else:\n        raise AssertionError(age)"),case('退化区间与反向拒绝',"assert clamp(100,3,3)==3\ntry:\n    clamp(1,5,2)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('reversed')",field='solution')])
    add(t,'l40','advanced','变形测试：不靠抄答案验证性质', ['对无易得标准答案的函数验证不变量','用反例说明必要性质不等于充分证明'],
        '排序大数组不想手写全部预期时，可以验证结果单调、元素数量守恒、重复排序不变三种性质。只验证单调不够，错误函数返回空列表也单调；只验证长度也不够，它可能改掉元素。因此性质要互补，Counter用于验证多重集相等。变形测试还会从已有输入构造相关输入，例如整体加常数后最小值也应增加同一常数。本例为自写插入排序验证性质，练习用可逆性测试编码过程，但同时保留明确样例，防止正反函数共享同一个错误约定。',
        ['用已排序前缀实现插入排序','分别验证顺序、多重集和幂等性','为可逆变换保留一个独立已知样例'],
        '''from collections import Counter
def insertion_sort(values):
    result=list(values)
    for i in range(1,len(result)):
        value=result[i]; j=i-1
        while j>=0 and result[j]>value:
            result[j+1]=result[j]; j-=1
        result[j+1]=value
    return result
source=[3,-1,3,0]
result=insertion_sort(source)
assert all(a<=b for a,b in zip(result,result[1:]))
assert Counter(source)==Counter(result)
assert insertion_sort(result)==result
print(result)''','[-1, 0, 3, 3]\n',
        '实现rotate(values,shift)，循环左移（shift可负），空列表返回新空列表。断言移n次等于原序列，先移k再移-k能恢复，并写已知[1,2,3]左移1。',
        '''def rotate(values,shift):
    if not values: return []
    shift%=len(values)
    return list(values[shift:])+list(values[:shift])
assert rotate([1,2,3],1)==[2,3,1]
for shift in range(-5,6):
    assert rotate(rotate([1,2,3],shift),-shift)==[1,2,3]
print(rotate([1,2,3],-1))''','[3, 1, 2]\n',
        ['仅检查有序会让总返回空列表的错误实现通过','可逆性质不能单独确定变换方向，需独立已知样例'], '组合互补性质和明确反例，比机械复制实现更能发现缺陷。',
        ('properties','返回空列表也有序，哪一项性质能揭穿它？','排序验收的三种互补约束',[('单调','相邻前项<=后项'),('守恒','Counter输入=输出'),('幂等','再排序不变')]),
        [case('多重集和来源隔离','for xs in ([],[1],[-3,-1,-2],[2,2]):\n    before=xs[:]; out=insertion_sort(xs)\n    assert out==sorted(xs) and xs==before and Counter(out)==Counter(xs)'),case('周期与空输入','x=[1,2,3,4]\nassert rotate(x,4)==x and rotate(x,0) is not x and rotate([],100)==[]',field='solution')])
    add(t,'l41','intermediate','对象不变量：状态只能通过合法操作变化', ['在构造与方法边界维护业务约束','避免失败操作部分修改对象'],
        '类不只是把几个变量放在一起，更重要的是维护一直成立的约束。本例库存对象的quantity始终非负，sell先验证数量和库存，再一次更新；若失败，库存保持原值。构造函数也要校验初值，不能让对象从非法状态开始。下划线字段表示内部实现约定，不是安全访问控制；Python调用者仍可绕过，因此团队需要遵守接口。练习余额对象把读取与调整分开，并检查两个实例互不共享状态，避免把余额写成类级可变变量。',
        ['构造时建立非负数量不变量','方法先检查候选操作再更新','失败后重新读取证明状态未变'],
        '''class Stock:
    def __init__(self,quantity):
        if type(quantity) is not int or quantity<0: raise ValueError("库存无效")
        self._quantity=quantity
    @property
    def quantity(self): return self._quantity
    def sell(self,count):
        if type(count) is not int or count<0 or count>self._quantity: raise ValueError("出库无效")
        self._quantity-=count
        return self._quantity
stock=Stock(5)
print(stock.sell(2),stock.quantity)''','3 3\n',
        '实现Wallet类，初始余额非负，adjust(delta)余额不足时拒绝且不修改，balance只读property；示例20减7再加2得到15。',
        '''class Wallet:
    def __init__(self,balance=0):
        if balance<0: raise ValueError("初始余额无效")
        self._balance=balance
    @property
    def balance(self): return self._balance
    def adjust(self,delta):
        candidate=self._balance+delta
        if candidate<0: raise ValueError("余额不足")
        self._balance=candidate
        return candidate
wallet=Wallet(20)
wallet.adjust(-7)
print(wallet.adjust(2))''','15\n',
        ['先扣库存后检查会在异常后留下负状态','property只读接口不是防恶意代码的权限边界'], '对象封装的价值是维护不变量；异常路径也必须保持对象可继续使用。',
        ('object-state','卖出数量超过库存时，状态应该停在哪一步？','候选操作校验通过后才提交库存变化',[('当前','库存5'),('合法卖2','校验→库存3'),('非法卖4','拒绝，仍3')]),
        [case('失败不改库存',"s=Stock(1)\ntry:\n    s.sell(2)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('oversell')\nassert s.quantity==1 and s.sell(0)==1"),case('独立实例与失败',"a=Wallet(1); b=Wallet(1)\ntry:\n    a.adjust(-2)\nexcept ValueError:\n    pass\nassert a.balance==b.balance==1\na.adjust(1)\nassert b.balance==1",field='solution')])
    add(t,'l41','advanced','dataclass与不可变值对象', ['用dataclass表达数据角色和自动比较','区分不可变值与有生命周期实体'],
        '有些对象代表值而不是持续变化的实体，例如二维坐标。dataclass能生成初始化、表示和比较方法，frozen=True阻止字段的普通重新赋值，让“移动”返回新坐标而非改旧坐标。它仍是浅层冻结：字段若含列表，列表内部可变，因此本例仅使用整数。实体如任务则有稳定id与完成状态，不宜只因字段相等就断言是同一个任务。练习设计不可变矩形，构造时校验长宽非负，面积为派生property；等值比较与is身份检查要分清。',
        ['字段注解描述坐标数据','移动方法构造新的值对象','把校验放进__post_init__'],
        '''from dataclasses import dataclass
@dataclass(frozen=True)
class Point:
    x:int
    y:int
    def moved(self,dx,dy): return Point(self.x+dx,self.y+dy)
p=Point(2,3); q=p.moved(1,-2)
print(p,q)
print(Point(2,3)==p,Point(2,3) is p)''','Point(x=2, y=3) Point(x=3, y=1)\nTrue False\n',
        '定义frozen Rectangle(width,height)，负值构造拒绝，area返回面积；scaled(factor)返回新矩形且factor非负，不修改旧矩形。',
        '''from dataclasses import dataclass
@dataclass(frozen=True)
class Rectangle:
    width:int
    height:int
    def __post_init__(self):
        if self.width<0 or self.height<0: raise ValueError("尺寸不能为负")
    @property
    def area(self): return self.width*self.height
    def scaled(self,factor):
        if factor<0: raise ValueError("倍数不能为负")
        return Rectangle(self.width*factor,self.height*factor)
r=Rectangle(3,4)
print(r.area,r.scaled(2).area,r.area)''','12 48 12\n',
        ['frozen不递归冻结内部列表','==比较值不等于is比较是否同一对象'], '值对象以等值和不可变行为简化推理，实体对象则需要明确身份与状态生命周期。',
        ('value-object','移动之后，原坐标为什么仍然是(2,3)？','不可变点返回新的独立值',[('原值','Point(2,3)'),('移动参数','dx1 dy-2'),('新值','Point(3,1)，原值保留')]),
        [case('移动逆操作','assert p.moved(2,-1).moved(-2,1)==p and q!=p'),case('零缩放与非法尺寸',"r=Rectangle(0,4)\nassert r.area==0 and Rectangle(2,3).scaled(0)==Rectangle(0,0)\ntry:\n    Rectangle(-1,2)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('negative')",field='solution')])
    add(t,'l42','intermediate','优先组合：把通知方式作为协作对象', ['区分是一种与拥有一种的关系','通过传入协作者替换行为而不改业务对象'],
        '继承适合表达子类能替代父类的“是一种”关系，组合适合表达“拥有并使用一种能力”。任务拥有通知方式，并不意味着任务是一种通知器。本例把notifier对象传给Task，完成任务时调用其send；测试用内存记录器捕获消息，无需真实邮件或网络。替换通知方式不必再建立EmailTask、FileTask等不断增长的子类。练习设计存储协作对象，业务服务只依赖save方法；调用者应明确谁拥有状态，避免同一个默认对象跨服务共享。',
        ['通知器只负责保存发送记录','任务只负责完成状态与调用通知','传入不同协作者改变外部效果'],
        '''class MemoryNotifier:
    def __init__(self): self.messages=[]
    def send(self,text): self.messages.append(text)
class Task:
    def __init__(self,title,notifier):
        self.title=title; self.notifier=notifier; self.done=False
    def complete(self):
        if not self.done:
            self.done=True; self.notifier.send("完成："+self.title)
notifier=MemoryNotifier(); task=Task("阅读",notifier)
task.complete(); task.complete()
print(task.done,notifier.messages)''',"True ['完成：阅读']\n",
        '实现MemoryStore与ProfileService。store.save复制字典保存；service.rename校验非空姓名后存储新资料；不要通过继承把服务变成存储器。',
        '''class MemoryStore:
    def __init__(self): self.records=[]
    def save(self,record): self.records.append(dict(record))
class ProfileService:
    def __init__(self,store): self.store=store
    def rename(self,name):
        name=name.strip()
        if not name: raise ValueError("姓名不能为空")
        self.store.save({"name":name})
store=MemoryStore(); service=ProfileService(store)
service.rename(" 小禾 ")
print(store.records)''',"[{'name': '小禾'}]\n",
        ['为每种外部能力建一个业务子类会导致组合爆炸','存储器保存原字典引用会让后续编辑追改历史记录'], '组合让业务与外部效果分工，协作接口比复杂继承层次更容易替换和测试。',
        ('composition','任务为什么使用通知器，而不是继承通知器？','任务对象连接一个可替换通知协作者',[('Task','title、done'),('协作接口','notifier.send(text)'),('MemoryNotifier','messages记录一次通知')]),
        [case('重复完成不重复通知','assert len(notifier.messages)==1\nx=MemoryNotifier(); y=MemoryNotifier()\nTask("A",x).complete()\nassert y.messages==[]'),case('失败不持久化与快照','s=MemoryStore(); p=ProfileService(s)\ntry:\n    p.rename(" ")\nexcept ValueError:\n    pass\nassert s.records==[]\nx={"name":"A"};s.save(x);x["name"]="B"\nassert s.records==[{"name":"A"}]',field='solution')])
    add(t,'l42','advanced','替代契约：子类不能偷偷加强前提', ['用同一测试契约检查不同实现','通过策略注入避免违反父类承诺'],
        '如果父类承诺任意非负金额都可报价，子类却只接受满100元订单，调用父类接口的代码就会意外失败，这违反可替代性。复用代码不是继承的充分理由。本例用统一shipping(amount)契约构造两种费用策略：固定费用和满额免邮，都接受非负金额、拒绝负值、返回非负费用。统一契约测试对两者执行同样边界；具体费用不同属于允许的策略差异。练习把策略传给Checkout，不依赖具体子类字段，让新策略只需满足接口即可加入。',
        ['先声明所有策略共同的输入输出约定','子类改变算法但不缩小合法输入范围','调用方依赖方法契约而非具体类型'],
        '''class FlatShipping:
    def shipping(self,amount):
        if amount<0: raise ValueError("金额不能为负")
        return 8
class ThresholdShipping:
    def shipping(self,amount):
        if amount<0: raise ValueError("金额不能为负")
        return 0 if amount>=99 else 8
def check_contract(strategy):
    for amount in [0,98,99,200]: assert strategy.shipping(amount)>=0
    try: strategy.shipping(-1)
    except ValueError: return
    raise AssertionError("负数被接受")
for strategy in [FlatShipping(),ThresholdShipping()]: check_contract(strategy)
print("两种策略契约通过")''','两种策略契约通过\n',
        '实现Checkout.total(amount)，把shipping策略通过构造函数传入，金额非负，返回金额加运费；编写零邮费自定义策略证明无需修改Checkout。',
        '''class Checkout:
    def __init__(self,shipping): self.shipping=shipping
    def total(self,amount):
        if amount<0: raise ValueError("金额不能为负")
        fee=self.shipping.shipping(amount)
        if fee<0: raise ValueError("策略返回负运费")
        return amount+fee
class FreeShipping:
    def shipping(self,amount): return 0
print(Checkout(FreeShipping()).total(50))''','50\n',
        ['子类新增调用者不知道的前提会破坏替代契约','业务代码读取具体策略内部字段会使替换失效'], '多态依赖共同契约；策略可以不同，但输入范围和基本保证应一致。',
        ('contract-substitution','满额免邮与固定邮费有哪些共同承诺？','两策略共享合法输入范围和非负输出契约',[('输入契约','所有amount>=0'),('算法差异','固定8 / 满99免邮'),('输出契约','费用>=0，负输入拒绝')]),
        [case('门槛两侧','assert ThresholdShipping().shipping(98)==8 and ThresholdShipping().shipping(99)==0'),case('拒绝坏策略','class Broken:\n    def shipping(self,amount): return -1\ntry:\n    Checkout(Broken()).total(1)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError("negative fee")',field='solution')])
    add(t,'l43','intermediate','可迭代对象与一次性游标', ['区分iterable和iterator的生命周期','为重复遍历创建独立迭代器'],
        '列表可以重复遍历，因为每次iter(list)产生新游标；迭代器本身通常只能向前，耗尽后不会自动重置。本例从同一列表创建两个游标，取走a的首项不会影响b。把迭代器传给sum、list或for会消费它，第二次操作可能得到空结果。练习设计CountDown可迭代对象，让__iter__每次返回新迭代器，而不是对象自己复用一个不断耗尽的游标。接口应说明返回的是可重复数据源还是一次性流，调用者才能安排处理顺序。',
        ['同一来源各自创建游标a、b','分别消费并观察剩余项','可重复对象把新游标建立放在__iter__'],
        '''values=[10,20,30]
a=iter(values); b=iter(values)
print(next(a),next(a))
print(list(b))
print(list(a),list(a))''','10 20\n[10, 20, 30]\n[30] []\n',
        '实现CountDown(start)，start非负，每次iter都重新产生start至1的序列；0为空，连续遍历两次结果相同。',
        '''class CountDown:
    def __init__(self,start):
        if start<0: raise ValueError("起点不能为负")
        self.start=start
    def __iter__(self):
        return iter(range(self.start,0,-1))
data=CountDown(3)
print(list(data),list(data))''','[3, 2, 1] [3, 2, 1]\n',
        ['保存iter(values)后反复list不会重新从头开始','__iter__返回共享游标会让两个消费者互相抢数据'], '数据源可重复与游标一次性不同，明确生命周期能避免悄悄漏数据。',
        ('cursors','a已经取走两项，为何b仍能看到完整列表？','两个独立游标指向同一来源的不同位置',[('来源','10 20 30'),('游标a','位置2，余30'),('游标b','位置0，仍10 20 30')]),
        [case('游标耗尽不复活','assert list(a)==[] and iter(a) is a'),case('独立消费者','x=CountDown(2);a=iter(x);b=iter(x)\nassert next(a)==2 and next(b)==2 and list(a)==[1]\nassert list(CountDown(0))==[]',field='solution')])
    add(t,'l43','advanced','自定义迭代协议与停止边界', ['正确实现__iter__和__next__','让耗尽后的next持续抛StopIteration'],
        '自定义迭代器要让__iter__返回自身，__next__返回下一项或抛StopIteration。耗尽后应持续保持耗尽，不能下一次又从头开始。本例实现半开整数步进迭代器，只允许正步长，current达到stop就停止。调用next(iterator,default)会把StopIteration转换成默认值，但不会吞掉其他异常。练习实现成对读取器，若最后剩一项则以None补齐；这个策略必须显式说明，不能默默丢掉尾项，也不能把来源数据中的None误当耗尽信号。',
        ['构造时校验步长并设置当前状态','每次先检查停止条件再返回并推进','尾项策略使用独立哨兵区分真实None'],
        '''class StepIterator:
    def __init__(self,start,stop,step=1):
        if step<=0: raise ValueError("步长必须为正")
        self.current=start; self.stop=stop; self.step=step
    def __iter__(self): return self
    def __next__(self):
        if self.current>=self.stop: raise StopIteration
        result=self.current; self.current+=self.step
        return result
it=StepIterator(1,7,2)
print(list(it),next(it,"结束"),next(it,"仍结束"))''',"[1, 3, 5] 结束 仍结束\n",
        '实现Pairs(iterator)，每次返回二元组，奇数尾项以None补齐；真实None是普通数据，空来源立即停止。',
        '''class Pairs:
    def __init__(self,values): self.source=iter(values)
    def __iter__(self): return self
    def __next__(self):
        first=next(self.source)
        sentinel=object()
        second=next(self.source,sentinel)
        return first,None if second is sentinel else second
print(list(Pairs([1,None,3])))''','[(1, None), (3, None)]\n',
        ['耗尽后重置current会让for永不真正结束','用None当耗尽标记会与来源中的真实None冲突'], '迭代协议的停止行为也是契约，独立哨兵区分数据与控制状态。',
        ('iterator-state','耗尽之后再次next为什么不能重新返回1？','游标从活动态进入不可逆耗尽态',[('活动','current1→3→5'),('边界','current7>=stop7'),('耗尽','后续均StopIteration')]),
        [case('空区间与跨界步长','assert list(StepIterator(5,5))==[] and list(StepIterator(1,2,9))==[1]'),case('None与奇偶尾项','assert list(Pairs([None]))==[(None,None)]\nassert list(Pairs([]))==[] and list(Pairs([1,2]))==[(1,2)]',field='solution')])
    add(t,'l44','intermediate','惰性流水线与有限消费', ['组合生成器避免保存所有中间数据','观察消费发生时才执行的效果'],
        '生成器创建时不会执行完整循环，只有消费者请求下一项才推进。本例将文本行转换、筛选、平方分成三个生成器，再用islice只取前两项；它不会为整份来源建立中间列表，也不会读取满足需求以后的所有项。惰性不等于没有成本：为了找到两个合格值，仍要扫描前面不合格项。来源只消费一次，若要再次报告应重新打开来源或明确材料化。练习实现take_positive，从任意一次性输入取前n个正数，不得把完整输入先转列表。',
        ['生成器表达式只描述流水线','islice决定实际消费上限','观察来源访问记录确认停止位置'],
        '''from itertools import islice
visited=[]
def source():
    for value in [-2,1,0,3,5]:
        visited.append(value)
        yield value
positive=(x for x in source() if x>0)
squares=(x*x for x in positive)
result=list(islice(squares,2))
print(result,visited)''','[1, 9] [-2, 1, 0, 3]\n',
        '实现take_positive(values,n)，n非负，返回前n个正数；n=0时来源一项也不能被消费。',
        '''from itertools import islice
def take_positive(values,n):
    if n<0: raise ValueError("数量不能为负")
    return list(islice((x for x in values if x>0),n))
print(take_positive(iter([-1,2,0,3,4]),2))''','[2, 3]\n',
        ['生成器表达式不等于已经完成计算','先list(values)会破坏有限消费的内存与终止要求'], '惰性流水线把计算推进交给消费者，但仍要明确一次性来源与停止位置。',
        ('lazy-pipeline','结果只需两个正数，为什么5没有被访问？','来源经筛选与平方直到第二个产出即停',[('扫描','-2→1→0→3'),('产出','1²、3²'),('停止','5尚未访问')]),
        [case('有限消费位置','assert visited==[-2,1,0,3] and result==[1,9]'),case('零消费与无限源','seen=[]\ndef stream():\n    x=0\n    while True:\n        seen.append(x);yield x;x+=1\ns=stream()\nassert take_positive(s,0)==[] and seen==[]\nassert take_positive(s,2)==[1,2] and seen==[0,1,2]',field='solution')])
    add(t,'l44','advanced','生成器清理：提前停止也要关闭资源', ['用finally管理暂停中的生成器资源','在消费方以closing明确结束时机'],
        '生成器可能在yield处暂停很久，for中的break只停止消费者，不保证立刻执行生成器的finally。如果生成器持有文件或其他资源，消费方应明确调用close，或用contextlib.closing包裹。本例以events记录打开、产出和关闭，验证提前只取一项后也清理。close会在暂停点引发GeneratorExit，通常由finally完成清理；不应捕获后继续yield。练习实现分批生成器，验证正常耗尽和提前关闭均有清理记录，强调资源生命周期不是等垃圾回收碰巧发生。',
        ['生成器进入时记录获取资源','yield保留局部状态并暂停','closing退出时调用close触发finally'],
        '''from contextlib import closing
events=[]
def rows():
    events.append("打开")
    try:
        for value in [1,2,3]:
            events.append(f"产出{value}")
            yield value
    finally:
        events.append("关闭")
with closing(rows()) as stream:
    first=next(stream)
print(first,events)''',"1 ['打开', '产出1', '关闭']\n",
        '实现batched(values,size,events)，惰性生成最多size项的列表，末批不足也保留；size正数，finally追加closed，提前close与正常结束都触发。',
        '''def batched(values,size,events):
    if size<=0: raise ValueError("批次大小必须为正")
    try:
        batch=[]
        for value in values:
            batch.append(value)
            if len(batch)==size:
                yield batch; batch=[]
        if batch: yield batch
    finally:
        events.append("closed")
events=[]
print(list(batched(range(5),2,events)),events)''',"[[0, 1], [2, 3], [4]] ['closed']\n",
        ['break不会自动承诺关闭仍被引用的生成器','在GeneratorExit清理时继续yield会破坏关闭协议'], 'yield暂停也延长资源持有期，消费者应明确决定提前结束时的清理责任。',
        ('generator-lifecycle','只读第一项就离开，关闭事件由谁触发？','生成器暂停与closing强制结束的生命周期',[('进入','打开'),('暂停','yield1，资源仍持有'),('退出with','close → finally关闭')]),
        [case('关闭后持续耗尽','assert next(stream,None) is None and events[-1]=="关闭"'),case('提前关闭与末批','e=[];g=batched([1,2,3],2,e)\nassert next(g)==[1,2] and e==[]\ng.close()\nassert e==["closed"]\ne=[]\nassert list(batched([],2,e))==[] and e==["closed"]',field='solution')],sources=['https://docs.python.org/3.11/library/contextlib.html'])
    add(t,'l45','intermediate','带参数装饰器：构造阶段与调用阶段', ['区分装饰器工厂、装饰阶段和调用阶段','保留被装饰函数的元信息'],
        '装饰器要接受选项时，通常多一层工厂：工厂接收配置，返回decorator；decorator接收原函数，返回wrapper；wrapper才在每次调用时运行。本例用prefix配置返回文字的前缀，functools.wraps保留名称与文档等元信息，避免所有函数看起来都叫wrapper。配置只在装饰时确定，函数参数则每次调用不同。练习实现整数结果倍增装饰器，要求原返回值仍作为计算输入，而不是只打印后忘记return。',
        ['先调用工厂绑定固定prefix','装饰阶段保存原函数并建立wrapper','运行阶段转发参数并返回新结果'],
        '''from functools import wraps
def prefixed(prefix):
    def decorate(function):
        @wraps(function)
        def wrapper(*args,**kwargs):
            return prefix+function(*args,**kwargs)
        return wrapper
    return decorate
@prefixed("提示：")
def greet(name): return "你好，"+name
print(greet("小禾"),greet.__name__)''','提示：你好，小禾 greet\n',
        '实现multiplied(factor)装饰器工厂，调用原函数后将返回值乘factor，参数及关键字原样转发，使用wraps。',
        '''from functools import wraps
def multiplied(factor):
    def decorate(function):
        @wraps(function)
        def wrapper(*args,**kwargs): return function(*args,**kwargs)*factor
        return wrapper
    return decorate
@multiplied(3)
def total(a,b=0): return a+b
print(total(2,b=4),total.__name__)''','18 total\n',
        ['把工厂配置与调用参数混在同一层会导致绑定错误','wrapper缺少return会把正确结果变成None'], '装饰器工厂的配置期、装饰期、调用期分别承担不同输入与状态。',
        ('wrapping-stages','prefix什么时候确定，name什么时候才传入？','三阶段嵌套调用与参数归属',[('工厂','prefix=提示：'),('装饰','保存greet函数'),('调用','name小禾 → 拼接返回')]),
        [case('元信息与多次调用','assert greet.__name__=="greet" and greet("A")=="提示：你好，A" and greet("B")=="提示：你好，B"'),case('位置关键字等价','assert total(1,2)==total(a=1,b=2)==9\nassert total(0)==0 and total.__wrapped__(2,4)==6',field='solution')])
    add(t,'l45','advanced','缓存装饰器：命中、异常与状态泄漏', ['定义缓存键与何时提交缓存','用调用计数验证命中和异常不缓存'],
        '缓存不是给函数套个字典就完成了。必须说明哪些参数可作键、失败是否缓存、返回可变对象是否共享。本例只支持单个可哈希参数，成功返回后才写缓存，异常不存；函数应对同样输入有稳定结果，否则缓存会隐藏外部状态变化。返回列表等可变结果会被各次调用共享，本例用整数避免这个陷阱。练习给缓存增加clear方法并记录hits、misses，清空时同时重置统计，用可观察调用次数验证行为而不是只看结果相等。',
        ['查询前确定可哈希key','未命中先执行原函数，成功后再写入','缓存生命周期由显式clear操作控制'],
        '''from functools import wraps
def memo_one(function):
    cache={}
    @wraps(function)
    def wrapper(value):
        if value in cache: return cache[value]
        result=function(value)
        cache[value]=result
        return result
    return wrapper
calls=[]
@memo_one
def square(value):
    calls.append(value)
    if value<0: raise ValueError("非负")
    return value*value
print(square(4),square(4),calls)''','16 16 [4]\n',
        '实现cached(function)，单个可哈希参数，wrapper.stats保存hits/misses；clear清空缓存及统计，异常调用算miss但不缓存。',
        '''from functools import wraps
def cached(function):
    cache={};stats={"hits":0,"misses":0}
    @wraps(function)
    def wrapper(value):
        if value in cache:
            stats["hits"]+=1;return cache[value]
        stats["misses"]+=1
        result=function(value);cache[value]=result
        return result
    def clear():
        cache.clear();stats.update(hits=0,misses=0)
    wrapper.stats=stats;wrapper.clear=clear
    return wrapper
@cached
def doubled(value): return value*2
print(doubled(3),doubled(3),doubled.stats)
doubled.clear()
print(doubled.stats)''',"6 6 {'hits': 1, 'misses': 1}\n{'hits': 0, 'misses': 0}\n",
        ['缓存有副作用或依赖实时外部状态的函数会隐藏变化','在函数成功前写缓存可能把失败状态当正常结果重用'], '缓存需要明确键、结果可变性、失败和清理策略，调用计数才能揭示是否真正命中。',
        ('cache-state','第二次square(4)为何不再执行原函数？','缓存未命中与命中路径分离',[('首次4','miss → 计算16 → 存4:16'),('再次4','hit → 直接16'),('异常输入','执行失败，不写缓存')]),
        [case('失败不会缓存',"for _ in range(2):\n    try:\n        square(-1)\n    except ValueError:\n        pass\nassert calls.count(-1)==2"),case('清空后重算','doubled(2);doubled(2)\nassert doubled.stats=={"hits":1,"misses":1}\ndoubled.clear();doubled(2)\nassert doubled.stats=={"hits":0,"misses":1}',field='solution')])
    add(t,'l46','intermediate','临时状态上下文：异常后恢复原值', ['用contextmanager封装设置与恢复','通过finally保证异常路径恢复状态'],
        'with不仅用于文件，也适合短时间改变配置并在退出后恢复。本例临时改变settings中的mode，进入前保留旧值，finally恢复；即便块内抛异常，也不会把临时模式泄漏到后续任务。若原来根本没有这个键，恢复时应删除而非写入None，否则结构也发生改变。用独立哨兵区分“缺失”与“值为None”，是恢复原状态的关键。练习临时设置字典键，覆盖嵌套with时按后进先出顺序逐层恢复，而不是总恢复到某个全局默认值。',
        ['保存进入当时的值或缺失哨兵','yield把临时状态交给with块','finally准确恢复进入时的结构'],
        '''from contextlib import contextmanager
@contextmanager
def temporary_value(mapping,key,value):
    missing=object();old=mapping.get(key,missing)
    mapping[key]=value
    try: yield mapping
    finally:
        if old is missing: mapping.pop(key,None)
        else: mapping[key]=old
settings={"mode":"normal"}
with temporary_value(settings,"mode","preview"):
    print(settings["mode"])
print(settings["mode"])''','preview\nnormal\n',
        '实现temporary_key同样协议，并用嵌套with设置1、2，退出内层恢复1，退出外层删除原本不存在的键。',
        '''from contextlib import contextmanager
@contextmanager
def temporary_key(mapping,key,value):
    missing=object();old=mapping.get(key,missing)
    mapping[key]=value
    try: yield
    finally:
        if old is missing: mapping.pop(key,None)
        else: mapping[key]=old
data={}
with temporary_key(data,"x",1):
    with temporary_key(data,"x",2): print(data["x"])
    print(data["x"])
print(data)''','2\n1\n{}\n',
        ['恢复为None会制造原来不存在的键','清理代码写在yield后却不放finally，异常时会跳过'], '上下文管理表达可逆临时状态，恢复的是进入时现场而不是假定默认值。',
        ('state-stack','内层退出后为什么恢复1，而不是直接删除x？','嵌套上下文按栈顺序恢复各自旧值',[('外层进入','缺失→1'),('内层进入退出','1→2→1'),('外层退出','1→缺失')]),
        [case('异常与None恢复',"x={'a':None}\ntry:\n    with temporary_value(x,'a',3):\n        raise RuntimeError('test')\nexcept RuntimeError:\n    pass\nassert x=={'a':None}"),case('原缺失异常仍删除',"d={}\ntry:\n    with temporary_key(d,'x',1):\n        raise ValueError('test')\nexcept ValueError:\n    pass\nassert d=={}",field='solution')])
    add(t,'l46','advanced','ExitStack：动态资源按逆序释放', ['管理数量运行时才确定的上下文','在部分获取失败时清理已获得资源'],
        '当需要打开多少资源取决于输入时，写固定层数的with不现实。ExitStack让程序动态登记上下文或清理回调，离开时按后进先出执行，和嵌套with一致。若获取第三个资源失败，已获取的前两个仍会释放。本例用内存事件代替真实设备，清楚显示获取A、B后在错误路径中按B、A关闭。练习实现批量临时键设置，进入过程中某一键验证失败也必须恢复之前设置，强调资源管理与事务校验的关联但不把它说成数据库事务。',
        ['每获取一个资源立即登记清理','后续获取失败由栈释放已有项','逆序释放满足后建资源依赖先建资源的情况'],
        '''from contextlib import contextmanager,ExitStack
events=[]
@contextmanager
def resource(name):
    events.append("open "+name)
    try: yield name
    finally: events.append("close "+name)
try:
    with ExitStack() as stack:
        for name in ["A","B"]: stack.enter_context(resource(name))
        raise ValueError("模拟后续失败")
except ValueError: pass
print(events)''',"['open A', 'open B', 'close B', 'close A']\n",
        '实现temporary_many(mapping,pairs)上下文，用ExitStack和临时单键上下文支持多个设置；键必须为非空字符串，后续无效时也恢复前面项。',
        '''from contextlib import contextmanager,ExitStack
@contextmanager
def one(mapping,key,value):
    if not isinstance(key,str) or not key: raise ValueError("键无效")
    missing=object();old=mapping.get(key,missing);mapping[key]=value
    try: yield
    finally:
        if old is missing: mapping.pop(key,None)
        else: mapping[key]=old
@contextmanager
def temporary_many(mapping,pairs):
    with ExitStack() as stack:
        for key,value in pairs: stack.enter_context(one(mapping,key,value))
        yield mapping
data={"x":0}
with temporary_many(data,[("x",1),("y",2)]): print(data)
print(data)''',"{'x': 1, 'y': 2}\n{'x': 0}\n",
        ['获取全部资源后才登记清理，会在中间失败时泄漏前面资源','回调顺序写成先进先出可能破坏资源依赖'], '动态资源逐项获取逐项登记，逆序退出同时覆盖正常和部分失败路径。',
        ('resource-stack','获取后续资源失败时，已经打开的A和B如何退出？','清理栈后进先出',[('获取A','栈[A]'),('获取B','栈[A,B]'),('失败退出','先close B，再close A')]),
        [case('明确逆序清理','assert events==["open A","open B","close B","close A"]'),case('部分进入失败恢复',"x={'a':0}\ntry:\n    with temporary_many(x,[('a',1),('',2)]):\n        raise AssertionError('should not enter')\nexcept ValueError:\n    pass\nassert x=={'a':0}",field='solution')],sources=['https://docs.python.org/3.11/library/contextlib.html'])
    add(t,'l47','intermediate','类型提示与运行时验证分工', ['用类型提示表达输入输出与可空结果','在外部边界显式验证而不依赖注解'],
        '类型注解描述程序约定，Python不会自动据此阻止错误输入。list[int]不意味着传入字符串时解释器先替你检查。本例在边界显式验证整数列表，再用int|None表达空列表没有最小值。调用处先判断None，才进行后续数值操作；0是合法结果，不能用if result来代替判空。练习定义TypedDict记录结构帮助阅读，同时仍用运行时逻辑检查外部字典。TypedDict不是自动验证器，也不会在运行时转换字段类型。',
        ['注解表明静态契约，显式代码校验外部值','空输入返回None而非伪造0','调用方用is None区分缺失与合法零'],
        '''def minimum(values:list[int])->int|None:
    if any(type(x) is not int for x in values): raise ValueError("需要整数")
    return min(values) if values else None
result=minimum([0,3])
if result is None: print("无数据")
else: print(result+1)
print(minimum([]))''','1\nNone\n',
        '用TypedDict定义User(name:str,age:int)，实现parse_user(data:object)->User，验证字典、非空姓名、0至150整数年龄且排除bool，返回标准新结构。',
        '''from typing import TypedDict
class User(TypedDict):
    name:str
    age:int
def parse_user(data:object)->User:
    if not isinstance(data,dict): raise ValueError("需要对象")
    name=data.get("name");age=data.get("age")
    if not isinstance(name,str) or not name.strip() or type(age) is not int or not 0<=age<=150:
        raise ValueError("用户字段无效")
    return {"name":name.strip(),"age":age}
print(parse_user({"name":" 小禾 ","age":16}))''',"{'name': '小禾', 'age': 16}\n",
        ['if result会把最小值0误当没有数据','TypedDict注解不会自动检查JSON读出的字典'], '静态类型帮助描述契约，外部不可信数据仍需运行时验证。',
        ('type-boundary','注解写了int，为什么仍需要检查True？','外部对象通过验证转成内部类型契约',[('外部','任意object'),('边界','类型、范围、非空校验'),('内部','User{name:str,age:int}')]),
        [case('零与None区分','assert minimum([0])==0 and minimum([]) is None'),case('bool与缺字段拒绝',"for x in ({'name':'A','age':True},{'name':'A'}):\n    try:\n        parse_user(x)\n    except ValueError:\n        pass\n    else:\n        raise AssertionError(x)",field='solution')])
    add(t,'l47','advanced','Protocol：按能力定义接口', ['用结构类型表达所需能力','让函数接受多种实现而不依赖具体父类'],
        '当报告只需要writer.write(text)，不必要求调用者必须继承某个专用父类。typing.Protocol描述所需方法，静态检查器可根据结构判断兼容性；这与组合设计自然配合。运行时Python仍按正常属性查找调用，注解不是自动权限或完整行为验证。runtime_checkable只提供有限属性存在性检查，并不验证签名和返回语义，因此本例不把它当业务校验。练习设计时钟协议并注入固定时钟，让依赖当前日期的报告可重现，不在函数里直接读取真实今天。',
        ['Protocol只声明调用方需要的方法','两个不同实现各自满足write能力','副作用依赖以参数传入以便测试'],
        '''from typing import Protocol
class Writer(Protocol):
    def write(self,text:str)->int: ...
def report(writer:Writer,values:list[int])->None:
    writer.write(f"总计:{sum(values)}\\n")
class MemoryWriter:
    def __init__(self): self.text=""
    def write(self,text:str)->int:
        self.text+=text;return len(text)
writer=MemoryWriter();report(writer,[2,3])
print(writer.text,end="")''','总计:5\n',
        '定义Clock.today()->date协议，实现dated_title(title,clock)返回YYYY-MM-DD:标题，提供FixedClock用于确定性测试；不调用系统日期。',
        '''from typing import Protocol
from datetime import date
class Clock(Protocol):
    def today(self)->date: ...
def dated_title(title:str,clock:Clock)->str:
    return f"{clock.today().isoformat()}:{title}"
class FixedClock:
    def __init__(self,value:date): self.value=value
    def today(self)->date: return self.value
print(dated_title("学习",FixedClock(date(2026,1,2))))''','2026-01-02:学习\n',
        ['Protocol不是要求实现者都继承同一基类','运行时结构检查不证明方法遵守类型和业务语义'], '按能力依赖缩小耦合，时间等环境信息也能通过可测试接口注入。',
        ('structural-interface','为什么MemoryWriter不继承Writer也能交给report？','调用方只依赖write能力而非具体继承树',[('需要能力','write(text)->int'),('实现A','MemoryWriter'),('实现B','兼容文件对象；report不变')]),
        [case('多个输出累计','w=MemoryWriter();report(w,[]);report(w,[1])\nassert w.text=="总计:0\\n总计:1\\n"'),case('闰日固定时钟','assert dated_title("x",FixedClock(date(2024,2,29)))=="2024-02-29:x"',field='solution')])
    add(t,'l48','intermediate','subTest：一条失败不吞掉整张边界表', ['用表格驱动unittest测试','使用assertRaises检查异常消息与类型'],
        '边界数据适合写成输入与预期的表格，但普通for里第一次assert失败就会终止该测试方法，后面的边界看不到结果。unittest的subTest给每组参数独立上下文，失败报告会带参数，其他组还能继续执行。异常测试用assertRaises明确要求失败；若函数悄悄返回默认值，测试会失败。示例用TextTestRunner写到内存流，再由wasSuccessful给课程输出一个确定结果，详细失败仍保留在流里，避免不同运行环境计时文字影响验收。',
        ['把边界与预期集中在数据表','每组进入带参数subTest','异常路径明确断言而非仅运行不崩溃'],
        '''import unittest,io
def shipping(amount):
    if amount<0: raise ValueError("金额不能为负")
    return 0 if amount>=99 else 8
class ShippingTests(unittest.TestCase):
    def test_boundaries(self):
        for amount,expected in [(0,8),(98,8),(99,0),(100,0)]:
            with self.subTest(amount=amount): self.assertEqual(shipping(amount),expected)
    def test_invalid(self):
        with self.assertRaisesRegex(ValueError,"不能为负"): shipping(-1)
result=unittest.TextTestRunner(stream=io.StringIO()).run(unittest.defaultTestLoader.loadTestsFromTestCase(ShippingTests))
assert result.wasSuccessful()
print(result.testsRun,"个方法通过")''','2 个方法通过\n',
        '为parse_level(text)写unittest：整数范围1至3，覆盖1、2、3，拒绝0、4、x。使用subTest与assertRaises，成功输出2个方法通过。',
        '''import unittest,io
def parse_level(text):
    value=int(text)
    if not 1<=value<=3: raise ValueError("范围1至3")
    return value
class LevelTests(unittest.TestCase):
    def test_valid(self):
        for text in ["1","2","3"]:
            with self.subTest(text=text): self.assertEqual(parse_level(text),int(text))
    def test_invalid(self):
        for text in ["0","4","x"]:
            with self.subTest(text=text):
                with self.assertRaises(ValueError): parse_level(text)
result=unittest.TextTestRunner(stream=io.StringIO()).run(unittest.defaultTestLoader.loadTestsFromTestCase(LevelTests))
assert result.wasSuccessful()
print(result.testsRun,"个方法通过")''','2 个方法通过\n',
        ['把testsRun误认为参数表总行数，它统计测试方法数','assertRaises范围包太多语句会不清楚到底哪一步抛错'], '测试表集中需求，subTest保留逐例诊断，异常断言验证失败契约。',
        ('test-table','4条边界数据为什么报告2个方法而不是4个？','方法计数与subTest参数案例的层次',[('方法1','4组金额边界'),('方法2','负金额异常'),('runner计数','2个测试方法')]),
        [case('运行器成功且测试数明确','assert result.wasSuccessful() and result.testsRun==2 and not result.failures and not result.errors'),case('额外空白转换与非法值',"assert parse_level(' 2 ')==2\ntry:\n    parse_level('-1')\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('invalid')",field='solution')])
    add(t,'l48','advanced','故障注入：验证失败时不提交', ['用mock模拟外部写入失败','验证调用顺序与失败后的状态保留'],
        '多数数据丢失缺陷出现在磁盘满、权限变化等正常演示难以触发的路径。unittest.mock可让协作者在指定调用抛OSError，测试业务是否在外部提交成功前就错误更新内存。本例服务先调用store.save(candidate)，成功后才改current；mock失败后current必须保留旧值。测试不应只验证实现内部每个函数都调用一次，而要验证实际契约：提交数据是什么、失败是否保留可恢复状态。练习添加通知步骤，持久化失败时不得发送成功通知。',
        ['把外部存储作为可注入协作者','mock.side_effect制造可复现I/O失败','核对失败后内存与通知均未错误提交'],
        '''from unittest.mock import Mock
class Service:
    def __init__(self,store): self.store=store;self.current="old"
    def update(self,value):
        self.store.save(value)
        self.current=value
store=Mock();store.save.side_effect=OSError("磁盘满")
service=Service(store)
try: service.update("new")
except OSError: pass
assert service.current=="old"
store.save.assert_called_once_with("new")
print("失败保留旧状态")''','失败保留旧状态\n',
        '实现Publisher(store,notifier).publish(text)：先save，成功后send("已发布")；空白文本拒绝且两方不调用。用Mock注入save失败，确认没有成功通知。',
        '''from unittest.mock import Mock
class Publisher:
    def __init__(self,store,notifier): self.store=store;self.notifier=notifier
    def publish(self,text):
        if not text.strip(): raise ValueError("内容为空")
        self.store.save(text)
        self.notifier.send("已发布")
store=Mock();notifier=Mock();store.save.side_effect=OSError("只读")
try: Publisher(store,notifier).publish("正文")
except OSError: pass
notifier.send.assert_not_called()
print("失败不通知")''','失败不通知\n',
        ['先改current再save会在写失败后呈现未落盘的新状态','广泛mock内部细节会让测试只证明调用图，缺少行为价值'], '故障注入把难复现错误变为稳定测试，重点验证提交边界与失败后状态。',
        ('failure-injection','磁盘满时，为什么界面状态仍应显示old？','外部提交成功才允许更新内存与通知',[('候选','new'),('写入','Mock抛OSError'),('后续','不改current，不发成功通知')]),
        [case('成功才更新','s=Mock();x=Service(s);x.update("new")\nassert x.current=="new"\ns.save.assert_called_once_with("new")'),case('空白拒绝与成功通知','s=Mock();n=Mock();p=Publisher(s,n)\ntry:\n    p.publish(" ")\nexcept ValueError:\n    pass\ns.save.assert_not_called();n.send.assert_not_called()\np.publish("ok");s.save.assert_called_once_with("ok");n.send.assert_called_once_with("已发布")',field='solution')])
    add(t,'l49','intermediate','解释器诊断：环境问题先收集证据', ['区分解释器、平台和已安装发行包信息','在离线环境中生成无网络诊断报告'],
        '“已经安装包却导入不了”常因为安装命令与运行程序不是同一个解释器。诊断应记录sys.version_info、sys.executable和平台信息，再检查模块来源或发行包元数据，而不是盲目重复安装。本例构造纯数据报告，但不输出机器路径以保持课程结果稳定；真实工具可以把具体路径显示在本机。虚拟环境隔离的是包版本，不是权限沙箱；移动端嵌入解释器也可能没有可执行的pip入口。练习解析版本需求仅支持明确约定的major.minor格式，不假装实现完整PEP版本排序。',
        ['从正在运行的sys对象读取版本','平台能力与包是否可见分别记录','诊断只读本机信息，不下载或更改环境'],
        '''import sys,platform,importlib.util
diagnostic={"version":tuple(sys.version_info[:2]),"implementation":platform.python_implementation(),"has_json":importlib.util.find_spec("json") is not None}
print(diagnostic["version"]>=(3,11))
print(diagnostic["implementation"],diagnostic["has_json"])''','True\nCPython True\n',
        '实现supports(current,required)，只接受两个非负整数组成的元组，按major/minor比较；不把3.10当十进制3.1。',
        '''def supports(current,required):
    for version in (current,required):
        if not isinstance(version,tuple) or len(version)!=2 or any(type(x) is not int or x<0 for x in version):
            raise ValueError("版本必须为(major,minor)")
    return current>=required
print(supports((3,10),(3,9)),supports((3,9),(3,10)))''','True False\n',
        ['把版本写成float会丢失3.10与3.1的区别','虚拟环境不限制文件或网络权限，不能当安全沙箱'], '先确认运行中的解释器和能力，再排查包来源；版本比较应使用结构化字段。',
        ('environment','为何3.10大于3.9，不能当小数直接比较？','版本字段按元组优先级比较',[('当前','(3,10)'),('要求','(3,9)'),('比较','主版本同3；10>9 → 支持')]),
        [case('标准库可见与版本','assert diagnostic["has_json"] and len(diagnostic["version"])==2'),case('跨主版本与非法bool',"assert supports((4,0),(3,99)) and supports((3,11),(3,11))\ntry:\n    supports((3,True),(3,1))\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('bool')",field='solution')])
    add(t,'l49','advanced','依赖锁定：发现冲突而不是静默升级', ['区分标准库、项目依赖和版本锁','对重复依赖的冲突做确定性检查'],
        '可复现环境不仅是“某个包能安装”，还需要知道使用哪个版本、来自哪里、适用哪个平台。真实锁文件还涉及哈希、平台标签和依赖解析，本课不在离线应用里假装实现完整安装器。我们实现一个范围明确的小协议：每行name==major.minor.patch，忽略空白和注释，同包同版本可重复，不同版本冲突必须拒绝。包名大小写和横线下划线在这里按约定归一，练习进一步比对当前清单与锁定清单，输出缺失和版本不符，不执行安装。',
        ['解析受限协议并拒绝不支持语法','归一包名后检查重复冲突','审计只报告差异，不悄悄改变环境'],
        '''import re
def parse_lock(lines):
    result={}
    for line in lines:
        line=line.strip()
        if not line or line.startswith("#"): continue
        match=re.fullmatch(r"([A-Za-z0-9_-]+)==(\\d+\\.\\d+\\.\\d+)",line)
        if not match: raise ValueError("仅支持精确三段版本")
        name=match[1].lower().replace("_","-");version=match[2]
        if name in result and result[name]!=version: raise ValueError("版本冲突")
        result[name]=version
    return result
print(parse_lock(["Demo_Pkg==1.2.3","demo-pkg==1.2.3"]))''',"{'demo-pkg': '1.2.3'}\n",
        '实现audit_lock(required,installed)，返回排序缺失名与(name,expected,actual)版本差异；不把额外包当冲突，不修改环境。',
        '''def audit_lock(required,installed):
    missing=sorted(set(required)-set(installed))
    mismatched=[(name,required[name],installed[name]) for name in sorted(set(required)&set(installed)) if required[name]!=installed[name]]
    return missing,mismatched
print(audit_lock({"a":"1.0.0","b":"2.0.0"},{"b":"1.0.0","extra":"9.0.0"}))''',"(['a'], [('b', '2.0.0', '1.0.0')])\n",
        ['只保留最后一条依赖会掩盖同包不同版本冲突','课程受限协议不是完整requirements或PEP440解析器'], '锁定与审计先明确支持范围和冲突策略，可复现性依赖诚实而完整的环境记录。',
        ('dependency-conflict','同包两条精确版本不同，为什么不能取最后一条？','名称归一后出现版本冲突的合并点',[('原名','Demo_Pkg / demo-pkg'),('统一名','demo-pkg'),('版本','1.2.3与2.0.0 → 拒绝')]),
        [case('冲突拒绝',"try:\n    parse_lock(['X==1.0.0','x==2.0.0'])\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('conflict')\nassert parse_lock(['# hi',''])=={}"),case('额外包与相同版本','assert audit_lock({"a":"1"},{"a":"1","x":"2"})==([],[])\nassert audit_lock({}, {})==([],[])',field='solution')])
    add(t,'l50','intermediate','命令入口：解析、计算、展示三层', ['将交互与纯业务函数隔离','为命令错误提供稳定返回协议'],
        '项目增长后，应把一次命令拆成解析、业务计算和展示。纯函数接收数据并返回结果，不直接input或print；入口负责把文本转成数据、捕获可解释错误并显示。本例把sum命令设计为命令名加任意数量整数，解析器拒绝未知命令及空参数，业务层只做求和。练习增加avg命令，要求空参数不能除零，输出由外层统一格式化；不要把所有分支重新塞回一个巨型main。函数边界的价值是独立可测试，不是为了让文件数量看起来更多。',
        ['parse_command只理解文本协议','execute只处理已解析命令','main式外层把结果转成用户文字'],
        '''def parse_command(line):
    parts=line.split()
    if not parts or parts[0]!="sum" or len(parts)<2: raise ValueError("用法：sum 整数...")
    return parts[0],[int(x) for x in parts[1:]]
def execute(command,values):
    if command!="sum": raise ValueError("未知命令")
    return sum(values)
command,values=parse_command("sum 2 -1 5")
print("结果",execute(command,values))''','结果 6\n',
        '设计parse与execute支持sum、avg，两种都至少一个数；输出avg 2 4 9的结果5.00。未知命令与非数字应明确失败。',
        '''def parse(line):
    parts=line.split()
    if not parts or parts[0] not in {"sum","avg"} or len(parts)<2: raise ValueError("命令或参数无效")
    return parts[0],[int(x) for x in parts[1:]]
def execute(command,values):
    if not values: raise ValueError("至少一个数")
    if command=="sum": return sum(values)
    if command=="avg": return sum(values)/len(values)
    raise ValueError("未知命令")
command,values=parse("avg 2 4 9")
print(f"{execute(command,values):.2f}")''','5.00\n',
        ['业务函数里读input会使测试不得不模拟整个界面','把未知命令默认为sum会掩盖输入拼写错误'], '清晰分层让协议、业务与展示分别可验证，入口只做协调。',
        ('layers','哪一层应该知道用户输入的是文本sum 2 -1 5？','文本到结构到计算再到展示的单向流',[('解析','sum 2 -1 5 → sum与[2,-1,5]'),('计算','sum→6'),('展示','结果6')]),
        [case('多空白与负数','c,x=parse_command("  sum   -2  0 ")\nassert execute(c,x)==-2'),case('空参数与未知命令拒绝',"assert execute('sum',[0])==0\nfor line in ('avg','unknown 1','sum x'):\n    try:\n        parse(line)\n    except ValueError:\n        pass\n    else:\n        raise AssertionError(line)",field='solution')])
    add(t,'l50','advanced','可恢复流程：显式状态与幂等操作', ['把事件处理设计为返回新状态','通过幂等键避免重试导致重复提交'],
        '真正项目会遇到同一操作被重试两次，例如界面重新提交或导入重复记录。若每次都扣库存，就会重复执行。幂等设计为事件分配稳定id，已处理id再次到来时直接返回原状态；第一次处理先校验，再产生新状态与已处理集合。本例是单进程内存模型，不代表跨进程或断电事务保证，但能明确业务规则。练习增加deposit与withdraw两种事件，并要求失败事件不进入已处理集合，否则修复输入后重试会被错误地当成成功操作。',
        ['事件id定义一次业务操作身份','先查已处理，再验证候选状态','成功后同时返回新余额和新已处理集合'],
        '''def apply_payment(state,event):
    if event["id"] in state["seen"]: return state
    amount=event["amount"]
    if amount<0 or amount>state["balance"]: raise ValueError("支付无效")
    return {"balance":state["balance"]-amount,"seen":state["seen"]|{event["id"]}}
initial={"balance":100,"seen":set()}
event={"id":"pay-1","amount":30}
first=apply_payment(initial,event);again=apply_payment(first,event)
print(first["balance"],again["balance"],initial["balance"])''','70 70 100\n',
        '实现apply_event支持deposit、withdraw及稳定id，金额严格正，余额不可负；返回新状态，重复id不重复执行，失败不修改输入或seen。',
        '''def apply_event(state,event):
    if event["id"] in state["seen"]: return state
    amount=event["amount"];kind=event["kind"]
    if amount<=0 or kind not in {"deposit","withdraw"}: raise ValueError("事件无效")
    balance=state["balance"]+(amount if kind=="deposit" else -amount)
    if balance<0: raise ValueError("余额不足")
    return {"balance":balance,"seen":state["seen"]|{event["id"]}}
state={"balance":10,"seen":set()}
event={"id":"d1","kind":"deposit","amount":5}
state=apply_event(state,event)
state=apply_event(state,event)
print(state["balance"],sorted(state["seen"]))''',"15 ['d1']\n",
        ['重试时重新生成id无法识别同一操作','校验失败也标记seen会把失败操作永久当作已完成'], '幂等性依靠稳定操作身份，校验与提交边界清楚才能安全重试。',
        ('idempotency','同一个pay-1重试，为什么余额不应再减30？','稳定事件id把首次提交和重试分成两条路径',[('初始','balance100 seen空'),('首次pay-1','余额70，记录id'),('再次pay-1','已处理，仍余额70')]),
        [case('重试不重复与原状态保留','assert first is again and initial=={"balance":100,"seen":set()}'),case('失败不标记可修复重试',"s={'balance':1,'seen':set()}\ne={'id':'w1','kind':'withdraw','amount':2}\ntry:\n    apply_event(s,e)\nexcept ValueError:\n    pass\nassert s=={'balance':1,'seen':set()}\ne['amount']=1\nr=apply_event(s,e)\nassert r=={'balance':0,'seen':{'w1'}}",field='solution')])
