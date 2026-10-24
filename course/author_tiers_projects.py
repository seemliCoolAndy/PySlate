"""Original, executable intermediate/advanced extensions to eight projects."""
from tier_helpers import add, case, clean


GAME = clean(r'''
def play(secret, commands, limit=3, low=1, high=10):
    if type(secret) is not int or not low <= secret <= high or limit < 1:
        raise ValueError("目标与次数配置无效")
    messages, attempts, won = [], 0, False
    for text in commands:
        try:
            guess = int(text)
        except ValueError:
            messages.append("格式错误")
            continue
        if not low <= guess <= high:
            messages.append("越界")
            continue
        attempts += 1
        if guess == secret:
            messages.append("命中")
            won = True
            break
        messages.append("偏小" if guess < secret else "偏大")
        if attempts == limit:
            break
    status = "won" if won else "lost" if attempts == limit else "incomplete"
    return {"status": status, "attempts": attempts, "messages": messages}
''')

BINARY = clean(r'''
def solve(target, low=1, high=100):
    if type(target) is not int or not low <= target <= high:
        raise ValueError("目标不在区间中")
    trace = []
    while low <= high:
        guess = (low + high) // 2
        trace.append(guess)
        if guess == target:
            return trace
        if guess < target:
            low = guess + 1
        else:
            high = guess - 1
    raise AssertionError("有效目标不应丢失")
''')

DECIMAL_CALC = clean(r'''
from decimal import Decimal, DecimalException, localcontext

def calculate(command):
    fields = command.split()
    if len(fields) != 3 or fields[1] not in {"+", "-", "*", "/"}:
        raise ValueError("格式应为 数值 运算符 数值")
    left_text, symbol, right_text = fields
    try:
        left, right = Decimal(left_text), Decimal(right_text)
        if not all(value.is_finite() and abs(value) <= Decimal("1e9") for value in (left, right)):
            raise ValueError("数值必须有限且绝对值不超过十亿")
        with localcontext() as context:
            context.prec = 28
            if symbol == "+": result = left + right
            elif symbol == "-": result = left - right
            elif symbol == "*": result = left * right
            else:
                if right == 0: raise ValueError("除数不能为零")
                result = left / right
        if not result.is_finite(): raise ValueError("结果必须有限")
        return result
    except DecimalException as error:
        raise ValueError("无法计算该数值") from error
''')

EXPRESSION = clean(r'''
import ast
from decimal import Decimal, DecimalException, localcontext

def evaluate(expression):
    if not isinstance(expression, str) or not 0 < len(expression) <= 160:
        raise ValueError("表达式长度须为1至160")
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as error:
        raise ValueError("表达式语法错误") from error
    if sum(1 for _ in ast.walk(tree)) > 64:
        raise ValueError("表达式过于复杂")
    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            value = Decimal(ast.get_source_segment(expression, node).replace("_", ""))
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = visit(node.operand)
            if isinstance(node.op, ast.USub): value = -value
        elif isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Add): value = left + right
            elif isinstance(node.op, ast.Sub): value = left - right
            elif isinstance(node.op, ast.Mult): value = left * right
            else:
                if right == 0: raise ValueError("除数不能为零")
                value = left / right
        else:
            raise ValueError("只支持数字、括号与四则运算")
        if not value.is_finite() or abs(value) > Decimal("1e12"):
            raise ValueError("数值超出计算范围")
        return value
    try:
        with localcontext() as context:
            context.prec = 28
            return visit(tree.body)
    except (DecimalException, RecursionError) as error:
        raise ValueError("无法计算该表达式") from error
''')

ROSTER = clean(r'''
import csv
import io

def import_scores(text):
    reader = csv.DictReader(io.StringIO(text), strict=True)
    if reader.fieldnames != ["name", "score"]:
        raise ValueError("表头须为name,score")
    records, errors, names = [], [], set()
    for row in reader:
        number = reader.line_num
        try:
            if None in row or any(value is None for value in row.values()):
                raise ValueError("列数不一致")
            name = row["name"].strip()
            score = int(row["score"])
            if not name or name in names or not 0 <= score <= 100:
                raise ValueError("姓名为空、重复或分数越界")
        except ValueError:
            errors.append(number)
        else:
            names.add(name)
            records.append({"name": name, "score": score})
    return records, errors

def report(records):
    if not records: return {"count": 0, "average": None}
    return {"count": len(records), "average": sum(row["score"] for row in records) / len(records)}
''')

WEIGHTED = clean(r'''
from decimal import Decimal, DecimalException

def weighted_score(grades, weights):
    if not weights or set(grades) != set(weights):
        raise ValueError("科目必须完整对应")
    try:
        converted = {name: Decimal(str(value)) for name, value in weights.items()}
    except DecimalException as error:
        raise ValueError("权重必须为十进制数") from error
    if any(not value.is_finite() or value <= 0 for value in converted.values()):
        raise ValueError("权重必须为有限正数")
    if sum(converted.values()) != Decimal(1):
        raise ValueError("权重之和必须为1")
    total = Decimal(0)
    for name, weight in converted.items():
        value = grades[name]
        if type(value) is not int or not 0 <= value <= 100:
            raise ValueError("成绩必须是0至100整数")
        total += Decimal(value) * weight
    return total

def rank_students(students, weights):
    rows = [(name, weighted_score(grades, weights)) for name, grades in students.items()]
    rows.sort(key=lambda row: (-row[1], row[0]))
    result, previous, rank = [], None, 0
    for position, (name, score) in enumerate(rows, 1):
        if score != previous: rank = position
        result.append((rank, name, score))
        previous = score
    return result
''')

TASKS = clean(r'''
import json
from pathlib import Path

def new_state():
    return {"next_id": 1, "tasks": []}

def apply(state, command, value):
    result = {"next_id": state["next_id"], "tasks": [dict(task) for task in state["tasks"]]}
    if command == "add":
        title = str(value).strip()
        if not title: raise ValueError("标题不能为空")
        result["tasks"].append({"id": result["next_id"], "title": title, "done": False})
        result["next_id"] += 1
    elif command in {"toggle", "delete"}:
        matches = [task for task in result["tasks"] if task["id"] == value]
        if not matches: raise ValueError("任务ID不存在")
        if command == "toggle": matches[0]["done"] = not matches[0]["done"]
        else: result["tasks"] = [task for task in result["tasks"] if task["id"] != value]
    else: raise ValueError("未知命令")
    return result

def save(path, state):
    path = Path(path)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
    temporary.replace(path)
''')

MIGRATION = clean(r'''
import json
from pathlib import Path

def migrate(document):
    if not isinstance(document, dict): raise ValueError("存档必须为对象")
    version = document.get("version")
    if type(version) is not int or version not in (1, 2): raise ValueError("未知存档版本")
    source = document.get("tasks")
    if not isinstance(source, list): raise ValueError("tasks必须为列表")
    tasks, seen = [], set()
    for position, row in enumerate(source, 1):
        if not isinstance(row, dict) or not isinstance(row.get("title"), str) or not row["title"].strip():
            raise ValueError("任务标题无效")
        if type(row.get("done")) is not bool: raise ValueError("done必须是布尔值")
        task_id = position if version == 1 else row.get("id")
        if type(task_id) is not int or task_id < 1 or task_id in seen: raise ValueError("ID无效或重复")
        seen.add(task_id)
        tasks.append({"id": task_id, "title": row["title"].strip(), "done": row["done"]})
    next_id = max(seen, default=0) + 1 if version == 1 else document.get("next_id")
    if type(next_id) is not int or next_id <= max(seen, default=0): raise ValueError("next_id无效")
    return {"version": 2, "next_id": next_id, "tasks": tasks}

def upgrade_file(path):
    path = Path(path)
    original = path.read_text(encoding="utf-8")
    result = migrate(json.loads(original))
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
    path.with_name(path.name + ".bak").write_text(original, encoding="utf-8")
    temporary.replace(path)
    return result
''')


def populate(t):
    code = GAME + clean('''
result = play(7, ["bad", "0", "3", "7"])
print(" | ".join(result["messages"]))
print(result["status"], result["attempts"])
''')
    solution = GAME + clean('''
def tournament(rounds):
    results = [play(secret, commands) for secret, commands in rounds]
    return sum(result["status"] == "won" for result in results), sum(result["attempts"] for result in results)
wins, attempts = tournament([(7,["3","7"]),(4,["1","2","3"]),(2,["2"])])
print(f"胜场{wins} 尝试{attempts}")
''')
    add(t,'p01','intermediate','猜数字重构：可测试的会话状态',
        ['将交互过程拆成可复用的状态计算','区分无效输入、失败与输入尚未完成'],
        '把读取键盘和游戏规则绑在一起，会让边界测试很难重复。本版play接收目标和一串命令，返回结构化状态；显示层再把消息打印出来。格式错误和越界不消耗次数，有效猜测才增加attempts。命中会立即停止，输入流提前结束则是incomplete，不能误报失败。目标由调用者传入只是为了可重复测试，实际随机选数仍可放在入口。这样的拆分允许以后替换命令来源，而不重写规则。',
        ['逐条识别两种无效输入，次数保持为零','3和7是两次有效猜测，第二次命中','根据结构化结果输出消息，测试直接检查字段'],
        code,'格式错误 | 越界 | 偏小 | 命中\nwon 2\n',
        '增加tournament，接收多轮的(目标,命令序列)，返回胜场与有效尝试总数。不要通过解析打印文字统计；使用play的返回值。',
        solution,'胜场2 尝试6\n',['无效输入也扣次数，会与规则不符','输入用尽但仍有机会时，应标记未完成而非失败'],
        '将状态作为返回值，交互规则才能被不同入口复用和独立测试。',
        ('game-state','bad、0、3、7分别怎样改变次数？','合法性检查与有效尝试计数分离',[('无效','bad、0：次数0'),('有效未中','3：次数1'),('命中','7：次数2，停止')]),
        [case('非法输入不扣次数','assert play(5,["bad","-1","5"],limit=1)["attempts"]==1'),case('多轮空输入保持未完成','assert tournament([(2,[]),(2,["2"])])==(1,1)',field='solution')])

    code = BINARY + clean('''
trace = solve(73)
print("猜测轨迹：" + " ".join(map(str,trace)))
print(f"{len(trace)} 次 / 上限 {(100).bit_length()}")
''')
    solution = clean('''
def follow_hints(low, high, replies):
    trace = []
    for reply in replies:
        if low > high: raise ValueError("提示相互矛盾")
        guess = (low + high) // 2
        trace.append(guess)
        if reply == "hit": return guess, trace
        if reply == "low": low = guess + 1
        elif reply == "high": high = guess - 1
        else: raise ValueError("提示须为low/high/hit")
    if low > high: raise ValueError("提示相互矛盾")
    raise ValueError("尚未确认命中")
target, trace = follow_hints(1,100,["low","high","low","low","low","hit"])
print("确认目标",target)
print(" ".join(map(str,trace)))
''')
    add(t,'p01','advanced','二分策略：让每次猜测缩小可能区间',
        ['用区间不变量设计猜测策略','发现前后提示矛盾并明确失败'],
        '高级目标是从会玩走向能解释策略。维护包含真实目标的闭区间，每次猜中点；偏小时排除中点及左侧，偏大时排除中点及右侧。不能只把low改成guess，否则区间可能不收缩。1至100的最坏猜测上限是7，不代表每个目标都需要7次。示例知道目标以验证策略，练习则只接收外部提示，不可偷看答案；如果提示排空区间，应报告矛盾，而不是继续制造无效猜测。',
        ['从1至100猜50，收到偏小后保留51至100','继续保持目标在新区间中，73在第六次命中','练习改为接收提示，区间为空时拒绝继续'],
        code,'猜测轨迹：50 75 62 68 71 73\n6 次 / 上限 7\n',
        '实现follow_hints，只接收low/high/hit提示。返回确认目标和轨迹；未知提示、缺少命中或互相矛盾均抛ValueError。',
        solution,'确认目标 73\n50 75 62 68 71 73\n',['区间更新忘记越过中点会重复猜测','把最坏上限当作每轮的固定次数，会误判正确策略'],
        '用不变量证明策略，再把不一致的外部反馈变成明确错误。',
        ('interval','每次更新后，真实目标为何仍在保留区间中？','闭区间随偏大偏小提示收缩',[('起点','1..100，猜50'),('缩小','51..100，猜75'),('继续缩小','…72..74，猜73')]),
        [case('端点均可找到','assert solve(1)[-1]==1 and solve(100)[-1]==100 and len(solve(100))<=7'),case('单元素区间','assert solve(8,8,8)==[8]'),case('矛盾提示被拒绝',clean('''
try: follow_hints(1,3,["low","low"])
except ValueError: pass
else: raise AssertionError("矛盾提示被接受")
'''),field='solution')])

    code = DECIMAL_CALC + clean('''
for command in ["0.10 + 0.20", "7 / 2"]:
    print(f"{calculate(command):.2f}")
''')
    solution = DECIMAL_CALC + clean('''
def evaluate_batch(commands):
    results, errors = [], []
    for number, command in enumerate(commands,1):
        try: results.append(calculate(command))
        except ValueError: errors.append(number)
    return results, errors
values, errors = evaluate_batch(["0.10 + 0.20","1 / 0","2 * 3"])
print("结果："+", ".join(f"{value:.2f}" for value in values))
print("错误行：",errors)
''')
    add(t,'p02','intermediate','计算器分层：Decimal与批量错误策略',
        ['将命令解析、数值规则和显示分离','为批量命令定义继续处理的错误策略'],
        '用户输入首先是命令文本，不能直接交给eval。这里约定三个空白分隔字段，明确只支持四则运算；数值从文本构建Decimal，避免先经过浮点近似。除零、非有限数和错误格式统一转成业务ValueError，显示层可以按需要提示而不打印内部堆栈。练习要求批量计算继续处理后续合法行，同时保留失败行号；这与遇到首错立即退出是两种不同产品约定，必须在接口里说清。',
        ['检查三个字段和受支持的运算符','构造并验证两个Decimal，再计算','最终格式化为两位小数，批量层单独记录错误行'],
        code,'0.30\n3.50\n',
        '增加evaluate_batch，返回合法结果列表与错误行号列表。每行失败不能悄悄变成0，也不能阻止后续合法命令执行。',
        solution,'结果：0.30, 6.00\n错误行： [2]\n',['Decimal(float)已经带入浮点近似','错误结果替换为0，会把失败与真实零结果混淆'],
        '计算内核返回精确结果，批量入口决定失败策略，显示层决定格式。',
        ('pipeline','除零那一行应当进入结果还是错误列表？','解析、计算、收集与格式化分层',[('输入文本','0.10 + 0.20'),('数值内核','Decimal → 0.30'),('批量结果','成功列表 + 错误行号')]),
        [case('精确小数与负数','assert calculate("0.1 + 0.2")==Decimal("0.3") and calculate("-2 * 3")==-6'),case('批量保留错误位置','assert evaluate_batch(["1 / 0","NaN + 2","1 - 1"])==([Decimal(0)],[1,2])',field='solution')],sources=['https://docs.python.org/3.13/library/decimal.html'])

    code = EXPRESSION + clean('''
print(evaluate("(2 + 3) * 4"))
print(evaluate("0.1 + 0.2"))
''')
    solution = EXPRESSION + clean('''
def evaluate_lines(lines):
    report = []
    for line in lines:
        try: report.append(("ok",str(evaluate(line))))
        except ValueError as error: report.append(("error",str(error)))
    return report
for status, value in evaluate_lines(["-(3 + 2) / 2","open('data.txt')"]):
    print(status,value)
''')
    add(t,'p02','advanced','解释一棵表达式树：优先级与受限语法',
        ['按语法树结构执行括号和运算优先级','限制表达式规模并拒绝函数调用与名称访问'],
        '手工split不能同时处理括号与优先级。ast.parse负责识别Python表达式结构，我们只解释数字、正负号和四则运算节点；其余节点一律拒绝，既不调用eval，也不访问变量或文件。小数从原始源码片段构建Decimal，而不是从AST里的float再次转换。长度、节点数和数值范围都有上限，避免把“没有eval”误称为无限资源安全。它是这个计算器的输入语言限制，不是应用执行任意Python时的系统沙箱。',
        ['解析成Expression树，括号改变树的父子关系','递归先计算子节点，再计算允许的运算','每步验证结果有限且在范围内，未知节点明确拒绝'],
        code,'20\n0.3\n',
        '增加evaluate_lines，逐行返回(ok,结果文本)或(error,原因)。错误行保留位置，后续行继续，不执行任何名称或调用。',
        solution,"ok -2.5\nerror 只支持数字、括号与四则运算\n",['ast.literal_eval也不是通用算术解释器','允许了Call或Name节点就扩大了输入语言范围，不能悄悄放行'],
        '受限解释器需要同时约定语法、数值规则、规模上限和错误返回。',
        ('expression-tree','为什么(2+3)*4先得到5，而不是先算3*4？','乘法根节点的左孩子是加法子树',[('左子树','2 + 3 → 5'),('右叶子','4'),('根节点','5 * 4 → 20')]),
        [case('一元负号与优先级','assert evaluate("2 + 3 * 4")==14 and evaluate("-(2+3)")==-5'),case('调用与布尔值拒绝',clean('''
for expression in ["__import__('os')", "True+1", "2**1000"]:
    try: evaluate(expression)
    except ValueError: pass
    else: raise AssertionError(expression)
''')),case('逐行错误不伪装成零','assert [status for status,_ in evaluate_lines(["1/0","0+0"]) ]==["error","ok"]',field='solution')],sources=['https://docs.python.org/3.13/library/ast.html'])

    _populate_records(t)
    _populate_analysis(t)
    _populate_modular(t)


def _populate_records(t):
    code = ROSTER + clean('''
records, errors = import_scores("name,score\\n安安,88\\n小林,101\\n安安,90\\n小周,72\\n")
summary = report(records)
print(f"有效{summary['count']}人，平均{summary['average']:.1f}")
print("错误行：", errors)
''')
    solution = ROSTER + clean('''
def ranked_passes(records, threshold=60):
    if type(threshold) is not int or not 0 <= threshold <= 100:
        raise ValueError("及格线必须为0至100整数")
    return sorted((dict(row) for row in records if row["score"] >= threshold),
                  key=lambda row: (-row["score"], row["name"]))
records, errors = import_scores("name,score\\n安安,88\\n小周,72\\n小林,88\\n")
for row in ranked_passes(records, 80):
    print(row["name"], row["score"])
print("原顺序：" + "、".join(row["name"] for row in records))
''')
    add(t,'p03','intermediate','成绩导入：让坏行可定位、好行可统计',
        ['使用CSV解析真实表格而非手动切逗号','将导入校验、统计和排序分别测试'],
        '真实表格可能包含带逗号的姓名、空字段、重复姓名和越界分数。CSV解析器负责引号与列的规则，业务校验负责姓名唯一以及分数范围；两者职责不同。示例采用逐行继续策略，只有合法记录进入统计，错误记录保留物理行号，方便回到原表修正。空班级的平均分是None，不能伪装成零分。练习再从已校验记录筛选并稳定排序，同时保持原始导入顺序，避免查询操作意外改动数据。',
        ['核对表头并让csv处理引号、换行和列数','逐行校验，合法记录与错误行分别收集','在导入结果上求平均，再独立筛选与排序'],
        code,'有效2人，平均80.0\n错误行： [3, 4]\n',
        '实现ranked_passes：按给定及格线筛选，再按分数降序、姓名升序排列。返回副本，保留原记录顺序；非法及格线抛ValueError。',
        solution,'安安 88\n小林 88\n原顺序：安安、小周、小林\n',
        ['split(",")会拆坏带引号的姓名','空班级的平均分不应返回0，否则无法区分没有数据与全部零分'],
        '导入报告既要能计算，也要能回答哪一行为什么没进入统计。',
        ('csv-validation','为什么第4行没有覆盖第2行安安的成绩？','逐行验证后分流为合法记录与错误行号',[('原始CSV','姓名、分数、行号'),('校验门','范围、列数、重名'),('两个出口','有效2人 / 错误3、4行')]),
        [case('带逗号姓名与空班级',clean('''
rows, issues = import_scores('name,score\\n"陈,小明",90\\n')
assert rows == [{"name":"陈,小明","score":90}] and issues == []
assert report([]) == {"count":0,"average":None}
''')),case('同分排序不修改源记录',clean('''
source=[{"name":"B","score":80},{"name":"A","score":80},{"name":"C","score":59}]
assert [row["name"] for row in ranked_passes(source)]==["A","B"]
assert source[0]["name"]=="B"
'''),field='solution')],sources=['https://docs.python.org/3.13/library/csv.html'])

    code = WEIGHTED + clean('''
students = {"A":{"数学":90,"语文":90}, "B":{"数学":90,"语文":90}, "C":{"数学":80,"语文":80}}
for rank, name, score in rank_students(students, {"数学":"0.6","语文":"0.4"}):
    print(rank, name, f"{score:.1f}")
''')
    solution = WEIGHTED + clean('''
def compare_rankings(students, before, after):
    old = {name:rank for rank,name,_ in rank_students(students,before)}
    new = {name:rank for rank,name,_ in rank_students(students,after)}
    return [(name,old[name],new[name],old[name]-new[name]) for name in sorted(students)]
students={"A":{"数学":90,"语文":70},"B":{"数学":70,"语文":90}}
for name, old, new, change in compare_rankings(students,{"数学":"0.5","语文":"0.5"},{"数学":"0.8","语文":"0.2"}):
    print(f"{name} {old}→{new} {change:+d}")
''')
    add(t,'p03','advanced','加权排名：规则变更与并列名次',
        ['用精确权重计算可解释的综合分','比较两套评分规则对名次的影响'],
        '综合分不仅是加法，还包含一组必须公开的规则。这里要求每个学生的科目恰好对应权重，权重为有限正数且总和为1，缺科不会被偷偷补零。计算使用Decimal，并列采用竞赛名次：两个第一名后是第三名；同分时仅用姓名稳定显示，不把姓名当成成绩。练习比较调整权重前后的名次，变化量定义为旧名次减新名次，正数表示上升。规则改变的影响因此可以被检查，而不是只展示一个新榜单。',
        ['先验证科目集合、权重与每科成绩','按综合分降序排序，再给相同分数相同名次','比较两套完整排名，计算每人的名次变化'],
        code,'1 A 90.0\n1 B 90.0\n3 C 80.0\n',
        '实现compare_rankings，接收学生、旧权重和新权重，按姓名返回(姓名,旧名次,新名次,变化)。保留并列名次，不能把列表下标当名次。',
        solution,'A 1→1 +0\nB 1→2 -1\n',
        ['float权重求和可能偏离1，应从文本构建Decimal','并列第一后的第三名不能错写成第二名'],
        '把评分规则、并列约定与变更影响一起建模，排名才可解释。',
        ('ranking-change','同分的A、B改用数学八成权重后，谁的名次发生变化？','权重调整影响总分，竞赛排名保留并列',[('旧规则','数学0.5 + 语文0.5'),('新规则','数学0.8 + 语文0.2'),('比较','A保持1，B从1到2')]),
        [case('缺科和错误权重明确拒绝',clean('''
for grades, weights in [({"数学":80},{"数学":"0.5","语文":"0.5"}),({"数学":80},{"数学":"NaN"}),({"数学":80},{"数学":"oops"})]:
    try: weighted_score(grades,weights)
    except ValueError: pass
    else: raise AssertionError("非法评分被接受")
''')),case('规则不变时名次变化为零',clean('''
people={"Z":{"x":100},"A":{"x":100},"B":{"x":0}}
assert compare_rankings(people,{"x":"1"},{"x":"1"})==[("A",1,1,0),("B",3,3,0),("Z",1,1,0)]
'''),field='solution')])

    code = TASKS + clean('''
state = apply(new_state(), "add", "复习函数")
state = apply(state, "add", "整理笔记")
state = apply(state, "delete", 1)
state = apply(state, "toggle", 2)
save("tasks.json", state)
loaded = json.loads(Path("tasks.json").read_text(encoding="utf-8"))
print(loaded["tasks"][0]["id"], loaded["tasks"][0]["title"], loaded["tasks"][0]["done"])
print("下一个ID", loaded["next_id"])
''')
    solution = TASKS + clean('''
def apply_batch(state, commands):
    current = state
    for command, value in commands:
        current = apply(current, command, value)
    return current
state = apply(new_state(),"add","第一项")
try:
    state = apply_batch(state,[("add","第二项"),("toggle",99)])
except ValueError:
    print("批次失败，保留原状态")
print(len(state["tasks"]), state["next_id"])
save("tasks.json",state)
''')
    add(t,'p04','intermediate','任务清单：稳定ID与整批提交',
        ['区分任务身份与列表位置','用返回新状态的方式实现批次失败回滚'],
        '删除列表第一项后，第二项的位置会变化，但它的身份不应变化。任务用单调增加的ID定位，删除不会回收编号；next_id与任务一起保存，重启后仍能继续分配。apply先复制状态再修改，错误不会留下半成品。保存采用同目录临时文件写完后replace，降低写入中断造成半个JSON的风险；这仍不是多进程数据库事务。练习把多条命令暂存为候选状态，所有命令成功才交给调用者提交，失败时原状态保持完整。',
        ['依次添加ID1、2，删除ID1后ID2仍然是2','切换任务状态并写入同目录临时文件，再替换主文件','批量命令只更新候选值，成功后再赋给正式状态'],
        code,'2 整理笔记 True\n下一个ID 3\n',
        '实现apply_batch，依次应用命令，全部成功才返回新状态。调用者仅在成功后赋值并保存；任一命令失败时原状态及next_id都不能变化。',
        solution,'批次失败，保留原状态\n1 2\n',
        ['删除后重新按位置编号，会让外部引用指向另一项任务','直接原地修改再抛异常，无法靠不赋值完成回滚'],
        '稳定ID保护身份，候选状态保护批次的一致性。',
        ('transaction','第二条命令失败时，第一条新增任务为何也不应提交？','原状态经过候选状态验证后才整体提交',[('正式状态','1项，next_id=2'),('候选批次','新增 → 错误ID99'),('失败结果','仍1项，next_id=2')]),
        [case('删除不复用ID且文件真实保存',clean('''
base=apply(apply(new_state(),"add","A"),"add","B")
changed=apply(apply(base,"delete",1),"add","C")
assert [row["id"] for row in changed["tasks"]]==[2,3]
assert base["tasks"][0]["id"]==1
assert json.loads(Path("tasks.json").read_text(encoding="utf-8"))["next_id"]==3
''')),case('失败批次不污染原状态',clean('''
original=apply(new_state(),"add","保留")
try: apply_batch(original,[("toggle",1),("delete",999)])
except ValueError: pass
else: raise AssertionError("无效ID被接受")
assert original["tasks"]==[{"id":1,"title":"保留","done":False}]
assert apply_batch(original,[] ) is original
'''),field='solution')],sources=['https://docs.python.org/3.13/library/pathlib.html#pathlib.Path.replace'])

    code = MIGRATION + clean('''
path = Path("legacy_tasks.json")
path.write_text(json.dumps({"version":1,"tasks":[{"title":"复习","done":False},{"title":"记录","done":True}]},ensure_ascii=False),encoding="utf-8")
state = upgrade_file(path)
print("版本",state["version"],"任务ID",[row["id"] for row in state["tasks"]])
print("旧备份版本",json.loads(Path("legacy_tasks.json.bak").read_text(encoding="utf-8"))["version"])
''')
    solution = MIGRATION + clean('''
def load_or_recover(path):
    path = Path(path)
    try:
        return migrate(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, ValueError):
        backup = path.with_name(path.name+".bak")
        recovered = migrate(json.loads(backup.read_text(encoding="utf-8")))
        temporary = path.with_name(path.name+".tmp")
        temporary.write_text(json.dumps(recovered,ensure_ascii=False),encoding="utf-8")
        temporary.replace(path)
        return recovered
path=Path("recover_tasks.json")
path.write_text(json.dumps({"version":1,"tasks":[{"title":"保留","done":True}]}),encoding="utf-8")
upgrade_file(path)
path.write_text("{broken",encoding="utf-8")
state=load_or_recover(path)
print("恢复版本",state["version"],"任务数",len(state["tasks"]))
print("有效备份仍为版本",json.loads(Path("recover_tasks.json.bak").read_text(encoding="utf-8"))["version"])
''')
    add(t,'p04','advanced','存档演进：验证、迁移与可恢复备份',
        ['为旧存档设计明确的版本迁移规则','在恢复失败时保护原文件与有效备份'],
        '项目升级不能要求用户丢掉旧数据。版本1没有ID，迁移按原顺序分配ID；版本2必须验证唯一正整数ID、布尔状态和下一个编号。先在内存中完成解析与校验，再写临时文件，备份原文后替换主文件，避免把未知版本半迁移。练习处理损坏的主文件：只用经过同样校验的备份恢复，绝不把损坏主文件覆盖到备份。这里讨论单进程的恢复策略，磁盘故障与多写者协调还需要更完整的存储设计。',
        ['读取版本1并验证每项字段，再生成版本2候选','保存原始文本为备份，最后替换主存档','恢复时先验证备份，成功才替换主文件且保留备份'],
        code,'版本 2 任务ID [1, 2]\n旧备份版本 1\n',
        '实现load_or_recover：有效主存档直接返回；主存档缺失、损坏或不符合结构时验证.bak并恢复。备份也无效则抛错，不能覆盖任一原文件。',
        solution,'恢复版本 2 任务数 1\n有效备份仍为版本 1\n',
        ['只验证JSON语法，不足以确认ID唯一或done为布尔值','恢复前把损坏主文件复制进备份，会丢失最后一份有效数据'],
        '迁移先验证后发布，恢复只信任已校验的数据，并保护最后的有效副本。',
        ('migration-recovery','主文件已损坏时，哪一份内容可以写入备份？','原版本迁移与损坏恢复采用不同备份策略',[('迁移','有效v1 → 校验 → v2'),('备份','保留有效原文'),('恢复','坏主文件 ← 已验证备份')]),
        [case('未知版本失败不改主文件',clean('''
bad=Path("unknown.json"); bad.write_text('{"version":99,"tasks":[]}',encoding="utf-8")
before=bad.read_bytes()
try: upgrade_file(bad)
except ValueError: pass
else: raise AssertionError("未知版本被迁移")
assert bad.read_bytes()==before and not Path("unknown.json.bak").exists()
''')),case('坏主文件与坏备份均保留',clean('''
bad=Path("both_bad.json"); backup=Path("both_bad.json.bak")
bad.write_text("{broken",encoding="utf-8"); backup.write_text('{"version":2,"next_id":1,"tasks":[{"id":1,"title":"X","done":false}]}',encoding="utf-8")
old_primary,old_backup=bad.read_bytes(),backup.read_bytes()
try: load_or_recover(bad)
except ValueError: pass
else: raise AssertionError("无效备份被发布")
assert bad.read_bytes()==old_primary and backup.read_bytes()==old_backup
'''),field='solution')])


def _populate_analysis(t):
    tokens = clean(r'''
import re
from collections import Counter
from pathlib import Path

def tokenize(text):
    # 英文字母组成词；中文逐字计数，不冒充中文分词。
    return re.findall(r"[a-z]+(?:'[a-z]+)?|[\u4e00-\u9fff]", text.casefold())

def word_report(text, stopwords=()):
    ignored = {word.casefold() for word in stopwords}
    counts = Counter(word for word in tokenize(text) if word not in ignored)
    return sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
''')
    code = tokens + clean('''
path=Path("analysis_sample.txt")
path.write_text("Python tools, PYTHON! 学习学习。",encoding="utf-8")
for word,count in word_report(path.read_text(encoding="utf-8"),{"tools"}):
    print(word,count)
''')
    solution = tokens + clean(r'''
def bigrams(text):
    # 标点断句，不能把上一句末词和下一句首词拼接。
    counts=Counter()
    for sentence in re.split(r"[.!?。！？\n]+",text):
        words=tokenize(sentence)
        counts.update(zip(words,words[1:]))
    return sorted(counts.items(),key=lambda pair:(-pair[1],pair[0]))
for (left,right),count in bigrams("small tools save time. small tools help!"):
    print(left+" / "+right,count)
''')
    add(t,'p05','intermediate','文本分析：规范化、停用词与相邻词组',
        ['明确英文词与中文字符的统计口径','按句子边界提取相邻词组并稳定排序'],
        '统计结果取决于“词”的定义，而不是Counter本身。这里先用casefold统一大小写，再把英文字母序列视为词，中文按单个汉字计数；这种简化不等于中文分词。停用词在计数之前过滤，同频项按文本排序，让输出可重复。示例真实写入并读取UTF-8样本文件，练习从单词频率扩展到相邻二元组。句号和换行会切断句子，不能把上一句最后一个词与下一句第一个词拼成不存在的搭配。',
        ['从文件读取文本，统一大小写并按约定提取词元','先过滤停用词，再计数和排序','对每句分别滑动取相邻两个词，累计二元组'],
        code,'python 2\n习 2\n学 2\n',
        '实现bigrams：在每句内部统计相邻词元对，按频率降序、词组字典序输出。英文与中文句末标点及换行均为边界；空文本与单词句产生空列表。',
        solution,'small / tools 2\nsave / time 1\ntools / help 1\ntools / save 1\n',
        ['lower和casefold都不是中文分词，必须说明统计单位','先删除所有标点再取相邻对，会把跨句词语错误连接'],
        '先定义文本单位与边界，再统计；可重复的排序让分析结果可比较。',
        ('text-bigram','两句之间的time和small为什么不能组成词组？','文本规范化后在句内形成相邻二元组',[('规范化','Small → small'),('句内窗口','small tools → (small,tools)'),('边界','time. | small，不连接')]),
        [case('同频与中文口径','assert word_report("B a A，学习",{"b"})==[("a",2),("习",1),("学",1)] and word_report("")==[]'),case('二元组不跨句且保留重复','assert bigrams("a b. c d\\na b")==[(("a","b"),2),(("c","d"),1)] and bigrams("solo")==[]',field='solution')])

    retrieval = clean(r'''
import math
import re
from collections import Counter

def words(text):
    return re.findall(r"[a-z]+",text.casefold())

def search(documents, query):
    if not documents: return []
    counts={name:Counter(words(text)) for name,text in documents.items()}
    document_frequency=Counter(word for counter in counts.values() for word in counter)
    idf={word:math.log((len(counts)+1)/(frequency+1))+1
         for word,frequency in document_frequency.items()}
    def vector(counter):
        size=sum(counter.values())
        return {word:count/size*idf[word] for word,count in counter.items() if word in idf} if size else {}
    query_vector=vector(Counter(words(query)))
    query_norm=math.sqrt(sum(value*value for value in query_vector.values()))
    if not query_norm: return []
    result=[]
    for name,counter in counts.items():
        values=vector(counter)
        norm=math.sqrt(sum(value*value for value in values.values()))
        score=sum(value*query_vector.get(word,0) for word,value in values.items())/(norm*query_norm) if norm else 0
        if score>0: result.append((name,score))
    return sorted(result,key=lambda pair:(-pair[1],pair[0]))
''')
    code = retrieval + clean('''
documents={"A":"python tools","B":"python python","C":"garden"}
for name,score in search(documents,"python"):
    print(name,f"{score:.3f}")
''')
    solution = retrieval + clean('''
def search_top(documents,query,limit=2,minimum=0.0):
    if type(limit) is not int or limit<1 or not 0<=minimum<=1:
        raise ValueError("数量与阈值无效")
    return [(name,score) for name,score in search(documents,query) if score>=minimum][:limit]
documents={"A":"python tools","B":"python python","C":"garden"}
for name,score in search_top(documents,"tools garden",minimum=0.6):
    print(name,f"{score:.3f}")
''')
    add(t,'p05','advanced','迷你文档检索：TF-IDF与余弦相似度',
        ['把词频转换成可比较的文档向量','处理空文档、未知词和相似度阈值'],
        '仅按关键词出现次数排名，会偏向长文档。示例先用词频除以文档总词数得到TF，再用log((文档数+1)/(含词文档数+1))+1得到平滑IDF；常见词权重较低，稀有词更有区分力。文档与查询使用同一词表和IDF，通过余弦相似度比较方向，重复同一词不会无限提高分数。空向量不能除以零，未知查询词不凭空创建文档证据。这是教学检索器，尚未实现中文分词、同义词或大规模索引。',
        ['建立每篇文档词频和全库文档频率','用统一IDF生成文档及查询向量','计算余弦相似度，过滤零分并稳定排序'],
        code,'B 1.000\nA 0.605\n',
        '实现search_top，按minimum相似度筛选并最多返回limit项。验证阈值与数量，保留原来的同分姓名顺序；无相关结果应为空列表。',
        solution,'C 0.707\n',
        ['文档频率数的是包含该词的文档数，不是总出现次数','查询完全不在词表时，不能对零长度向量做除法'],
        '检索分数必须和明确的词表、权重公式及边界处理一起解释。',
        ('tfidf','为什么python重复两次的B与单词查询方向完全相同？','文档与查询在统一词表中比较向量方向',[('TF','词次数 / 文档词数'),('IDF','罕见词权重更高'),('余弦','同方向得1，零向量跳过')]),
        [case('未知查询与空文档','assert search({"empty":"","A":"python"},"unknown")==[] and search({},"python")==[]'),case('同分排序与阈值筛选','assert [name for name,_ in search_top({"Z":"one","A":"one"},"one",limit=1,minimum=1)]==["A"] and search_top({"X":"one"},"two")==[]',field='solution')])

    money = clean(r'''
from decimal import Decimal, DecimalException

def money(text, allow_zero=False):
    try:
        amount=Decimal(str(text))
        if not amount.is_finite() or amount<0 or (amount==0 and not allow_zero) or amount>Decimal("1000000000"):
            raise ValueError("金额必须为范围内的有限正数")
        cents=amount.quantize(Decimal("0.01"))
        if amount!=cents: raise ValueError("金额最多精确到分")
        return cents
    except DecimalException as error:
        raise ValueError("金额格式无效") from error
''')
    sales = money + clean(r'''
import csv
import io
from collections import defaultdict

def read_sales(text):
    reader=csv.DictReader(io.StringIO(text),strict=True)
    if reader.fieldnames!=["category","quantity","price"]: raise ValueError("销售表头无效")
    rows,errors=[],[]
    for row in reader:
        try:
            if None in row or any(value is None for value in row.values()): raise ValueError("列数不一致")
            category=row["category"].strip()
            quantity=int(row["quantity"])
            price=money(row["price"],True)
            if not category or not 1<=quantity<=1000000: raise ValueError("类别或数量无效")
            rows.append({"category":category,"quantity":quantity,"price":price})
        except ValueError:
            errors.append(reader.line_num)
    return rows,errors

def category_totals(rows):
    totals=defaultdict(lambda:Decimal("0.00"))
    for row in rows: totals[row["category"]]+=row["quantity"]*row["price"]
    return dict(totals)
''')
    code = sales + clean('''
text="category,quantity,price\\n学习,2,15.00\\n文具,3,2.00\\n学习,1,8.00\\n文具,2,oops\\n"
rows,errors=read_sales(text)
for category,total in sorted(category_totals(rows).items()):
    print(category,f"{total:.2f}")
print("错误行：",errors)
''')
    solution = sales + clean('''
def compare_imports(existing,text,strict=True):
    rows,errors=read_sales(text)
    if strict and errors:
        return list(existing),errors,False
    return list(existing)+rows,errors,True
existing=[{"category":"学习","quantity":1,"price":Decimal("5.00")}]
result,errors,committed=compare_imports(existing,"category,quantity,price\\n文具,2,1.50\\n学习,-1,9.00\\n")
print("提交",committed,"保留",len(result),"行")
print("错误行：",errors)
''')
    add(t,'p06','intermediate','销售CSV：精确金额与导入提交策略',
        ['按类别汇总数量乘单价的精确金额','比较部分接收与整批拒绝的导入规则'],
        '销售表的数量必须是正整数，单价必须有限且精确到分；单价为零可以表示赠品，负数量则不能悄悄当作退货。每行先完整验证，再参与类别汇总，避免把半合法记录计入金额。CSV的列数与引号仍交给解析器处理。练习明确整批拒绝策略：只要存在错误行，新导入的合法行也暂不提交，原记录保留；可选宽松策略则提交合法行并报告错误。两种模式都应让用户知道到底提交了什么。',
        ['解析表头和每行字段，验证金额精度与数量','用Decimal累计各类别金额，最后统一显示两位','把解析结果交给提交层决定整批接受还是拒绝'],
        code,'学习 38.00\n文具 6.00\n错误行： [5]\n',
        '实现compare_imports(existing,text,strict=True)，返回候选记录、错误行号、是否提交。严格模式遇错保持原数据；宽松模式追加合法行，均不修改existing。',
        solution,'提交 False 保留 1 行\n错误行： [3]\n',
        ['金额先转float再Decimal，无法恢复最初的十进制文本','严格导入失败后仍追加部分行，会让“拒绝整批”的提示失真'],
        '解析与提交分开，才能清楚表达导入的原子性约定。',
        ('import-commit','一批中第二行失败时，严格模式该追加第一行吗？','销售行验证完成后由提交策略决定正式状态',[('解析','合法1行 + 错误第3行'),('严格策略','整批拒绝'),('正式数据','原记录保持1行')]),
        [case('赠品合法而超分精度拒绝',clean('''
rows,errors=read_sales('category,quantity,price\\n"书,合辑",2,0.00\\nA,1,0.001\\n')
assert len(rows)==1 and category_totals(rows)=={"书,合辑":Decimal("0.00")} and errors==[3]
''')),case('宽松模式只追加合法行',clean('''
source=[]
rows,errors,done=compare_imports(source,"category,quantity,price\\nA,2,1.10\\nB,0,3.00\\n",strict=False)
assert done and errors==[3] and category_totals(rows)=={"A":Decimal("2.20")} and source==[]
'''),field='solution')])

    orders = money + clean(r'''
def normalize_order(row):
    order_id=row.get("order_id")
    category=row.get("category")
    quantity=row.get("quantity")
    if not isinstance(order_id,str) or not order_id.strip() or len(order_id)>80:
        raise ValueError("订单ID无效")
    if not isinstance(category,str) or not category.strip() or len(category)>40:
        raise ValueError("类别无效")
    if type(quantity) is not int or not 1<=quantity<=1000000:
        raise ValueError("数量无效")
    return order_id.strip(),{"category":category.strip(),"quantity":quantity,"price":f"{money(row.get('price'),True):.2f}"}

def apply_orders(state, rows):
    candidate={order_id:dict(row) for order_id,row in state.items()}
    added=skipped=0
    for row in rows:
        order_id,value=normalize_order(row)
        if order_id in candidate:
            if candidate[order_id]!=value: raise ValueError("订单ID冲突："+order_id)
            skipped+=1
        else:
            candidate[order_id]=value
            added+=1
    return candidate,added,skipped

def sales_total(state):
    return sum((row["quantity"]*Decimal(row["price"]) for row in state.values()),Decimal("0.00"))
''')
    code = orders + clean('''
batch=[{"order_id":"S1","category":"书","quantity":2,"price":"15.00"}]
state,added,skipped=apply_orders({},batch)
state,added,skipped=apply_orders(state,batch)
print("再次导入：新增",added,"跳过",skipped)
print("总额",f"{sales_total(state):.2f}")
''')
    solution = orders + clean(r'''
import json
from pathlib import Path

def save_orders(path,state):
    document={"version":1,"orders":[dict(order_id=key,**state[key]) for key in sorted(state)]}
    path=Path(path); temporary=path.with_name(path.name+".tmp")
    temporary.write_text(json.dumps(document,ensure_ascii=False),encoding="utf-8")
    temporary.replace(path)

def load_orders(path):
    document=json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(document,dict) or type(document.get("version")) is not int or document["version"]!=1 or not isinstance(document.get("orders"),list):
        raise ValueError("订单存档无效")
    state,_,_=apply_orders({},document["orders"])
    return state

batch=[{"order_id":"S1","category":"书","quantity":2,"price":"15.00"}]
state,_,_=apply_orders({},batch)
save_orders("orders.json",state)
state,added,skipped=apply_orders(load_orders("orders.json"),batch)
print("重启再导入：新增",added,"跳过",skipped)
print("总额",f"{sales_total(state):.2f}")
''')
    add(t,'p06','advanced','幂等销售导入：重复提交与订单冲突',
        ['用业务ID防止重复导入重复记账','在持久化后继续保持幂等并拒绝ID冲突'],
        '用户可能多次点导入，也可能在重启后再次选择同一文件。订单ID必须代表同一业务记录：相同ID且内容相同就跳过，相同ID但金额或数量不同则报冲突，不能静默覆盖。每批先写入候选字典，遇到冲突整个批次不提交。金额统一为两位文本，避免15与15.00被误判为不同价格。练习把已接收订单本身保存下来，恢复时重新校验；只保存累计总额无法知道某一订单是否已经入账。',
        ['规范化订单身份、类别、数量和单价','候选表内查ID，相同跳过、冲突拒绝、新ID新增','连同订单ID保存并重新加载，再导入相同批次'],
        code,'再次导入：新增 0 跳过 1\n总额 30.00\n',
        '实现save_orders/load_orders，保存版本号与订单内容，使用临时文件替换；加载时重新验证字段。重启后重复导入不能增加总额。',
        solution,'重启再导入：新增 0 跳过 1\n总额 30.00\n',
        ['只检查ID就跳过，会吞掉同ID不同金额的真实冲突','仅保存总额而不保存已处理ID，重启后无法判断重复订单'],
        '幂等需要稳定身份与内容一致性，持久化必须保留足够的去重证据。',
        ('idempotency','同一个S1再次导入，为什么总额仍是30.00？','订单业务ID区分相同重试与内容冲突',[('首次S1','新增1，总额30.00'),('相同S1','跳过1，总额不变'),('改价S1','冲突，整批不提交')]),
        [case('冲突整批回滚',clean('''
base,_,_=apply_orders({},[{"order_id":"A","category":"x","quantity":1,"price":"1"}])
try: apply_orders(base,[{"order_id":"B","category":"x","quantity":1,"price":"2"},{"order_id":"A","category":"x","quantity":1,"price":"9"}])
except ValueError: pass
else: raise AssertionError("冲突被接受")
assert set(base)=={"A"} and sales_total(base)==Decimal("1.00")
''')),case('磁盘恢复后规范价格仍幂等',clean('''
restored=load_orders("orders.json")
again,added,skipped=apply_orders(restored,[{"order_id":"S1","category":"书","quantity":2,"price":"15.0"}])
assert added==0 and skipped==1 and sales_total(again)==Decimal("30.00")
assert Path("orders.json").exists() and not Path("orders.json.tmp").exists()
'''),field='solution')])

    ledger = money + clean(r'''
from datetime import date

def entry(day,kind,category,amount):
    day=date.fromisoformat(day).isoformat()
    if kind not in {"income","expense"}: raise ValueError("类型须为income或expense")
    if not isinstance(category,str) or not category.strip(): raise ValueError("类别不能为空")
    return {"day":day,"kind":kind,"category":category.strip(),"amount":money(amount)}

def balance(rows):
    return sum((row["amount"] if row["kind"]=="income" else -row["amount"] for row in rows),Decimal("0.00"))

def period(rows,start,end):
    start,end=date.fromisoformat(start).isoformat(),date.fromisoformat(end).isoformat()
    if start>end: raise ValueError("起止日期颠倒")
    return [row for row in rows if start<=row["day"]<=end]
''')
    code = ledger + clean('''
rows=[entry("2026-01-02","income","零用钱","100.00"),entry("2026-01-03","expense","学习","30.20"),entry("2026-02-01","expense","学习","9.80")]
print("一月结余",f"{balance(period(rows,'2026-01-01','2026-01-31')):.2f}")
print("全部结余",f"{balance(rows):.2f}")
''')
    solution = ledger + clean('''
def budget_report(rows,budgets,start,end):
    selected=period(rows,start,end)
    result=[]
    for category,text in sorted(budgets.items()):
        limit=money(text,True)
        spent=sum((row["amount"] for row in selected if row["kind"]=="expense" and row["category"]==category),Decimal("0.00"))
        result.append((category,spent,limit-spent))
    return result
rows=[entry("2026-01-03","expense","学习","30.20"),entry("2026-01-05","income","学习","5.00"),entry("2026-02-01","expense","学习","9.80")]
for category,spent,remaining in budget_report(rows,{"学习":"25.00"},"2026-01-01","2026-01-31"):
    print(category,"支出",f"{spent:.2f}","剩余",f"{remaining:.2f}")
''')
    add(t,'p07','intermediate','记账查询：日期区间与分类预算',
        ['区分收支结余与预算支出的口径','按日期区间汇总并解释预算超额'],
        '记账本的查询必须先说清范围。这里用真实日期验证输入，以规范的年月日文本比较闭区间，起止日期颠倒会报错。结余是收入减支出，而类别预算只扣该类别的支出，不能拿同名收入悄悄抵扣消费。金额统一使用Decimal并精确到分，负数不作为隐含的另一种类型。练习返回已花费与剩余额度，剩余为负表示超额；没有消费的类别也应显示零支出，让未使用的预算可见。',
        ['构造已验证日期、类型、类别和金额的记录','选择闭区间内记录，计算收入减支出','按预算类别只汇总支出，再计算额度减已花费'],
        code,'一月结余 69.80\n全部结余 60.00\n',
        '实现budget_report(rows,budgets,start,end)，按类别排序返回(类别,支出,剩余)。只统计区间内支出，不抵扣收入；预算为零合法，超支保留负剩余。',
        solution,'学习 支出 30.20 剩余 -5.20\n',
        ['把同类别收入扣掉支出，会混淆结余和消费预算','用未经日期校验的任意文本比较，可能接受不存在的日期'],
        '财务统计先定义时间和类型口径，再计算可解释的金额。',
        ('budget','学习类收入5元能否抵扣这个支出预算？','区间筛选后仅将支出扣减预算',[('一月学习支出','30.20'),('预算','25.00'),('剩余','25.00−30.20＝−5.20')]),
        [case('区间端点与无记录',clean('''
rows=[entry("2026-01-01","income","x","1.00"),entry("2026-01-31","expense","x","0.10")]
assert balance(period(rows,"2026-01-01","2026-01-31"))==Decimal("0.90")
assert period(rows,"2026-02-01","2026-02-28")==[]
assert entry("20260101","income","x","1")["day"]=="2026-01-01"
''')),case('零预算与收入不抵扣',clean('''
rows=[entry("2026-01-01","income","x","9"),entry("2026-01-02","expense","x","2")]
assert budget_report(rows,{"x":"0","y":"10"},"2026-01-01","2026-01-31")==[("x",Decimal("2.00"),Decimal("-2.00")),("y",Decimal("0.00"),Decimal("10.00"))]
'''),field='solution')])

    journal = money + clean(r'''
def append_entry(rows,kind,amount,reference=None):
    if kind not in {"income","expense","reversal"}: raise ValueError("流水类型无效")
    value=money(amount)
    if kind=="reversal":
        if type(reference) is not int or reference<1: raise ValueError("引用ID必须为正整数")
        original=next((row for row in rows if row["id"]==reference),None)
        if original is None or original["kind"]=="reversal": raise ValueError("只能冲销原始收支")
        if any(row["kind"]=="reversal" and row["reference"]==reference for row in rows): raise ValueError("不可重复冲销")
        if value!=Decimal(original["amount"]): raise ValueError("冲销金额必须与原记录一致")
        signed=-Decimal(original["signed"])
    else:
        if reference is not None: raise ValueError("原始收支不接受引用")
        signed=value if kind=="income" else -value
    return list(rows)+[{"id":len(rows)+1,"kind":kind,"amount":f"{value:.2f}","signed":f"{signed:.2f}","reference":reference}]

def journal_balance(rows):
    return sum((Decimal(row["signed"]) for row in rows),Decimal("0.00"))
''')
    code = journal + clean('''
rows=append_entry([],"income","100")
rows=append_entry(rows,"expense","30")
rows=append_entry(rows,"reversal","30",reference=2)
print("保留流水",len(rows),"条")
print("结余",f"{journal_balance(rows):.2f}")
''')
    solution = journal + clean(r'''
import json
from pathlib import Path

def replay(document):
    if not isinstance(document,list): raise ValueError("流水必须为列表")
    result=[]
    for saved in document:
        if not isinstance(saved,dict): raise ValueError("流水项无效")
        if type(saved.get("id")) is not int: raise ValueError("流水ID必须为整数")
        result=append_entry(result,saved.get("kind"),saved.get("amount"),saved.get("reference"))
        if result[-1]!=saved: raise ValueError("流水编号或符号与重放结果不符")
    return result

rows=append_entry(append_entry([],"income","100"),"expense","30")
rows=append_entry(rows,"reversal","30",reference=2)
Path("journal.json").write_text(json.dumps(rows,ensure_ascii=False),encoding="utf-8")
restored=replay(json.loads(Path("journal.json").read_text(encoding="utf-8")))
print("重放",len(restored),"条，结余",f"{journal_balance(restored):.2f}")
''')
    add(t,'p07','advanced','追加流水：用冲销纠错并校验重放',
        ['用追加冲销代替删除已发生的记账记录','按业务规则重放存档并检查派生字段一致性'],
        '直接删除错误支出会抹去发生过什么。追加式流水保留原记录，再添加金额相等、符号相反且引用原ID的冲销记录；同一原记录只能冲销一次，冲销本身也不能再次冲销。结余从所有有符号金额求和得到。练习加载存档时依次重放业务操作，重新计算编号与符号，再与保存值比较，发现重复冲销或派生字段不一致。这能检查结构与规则，不能证明文件未被有意篡改，真正审计还需要可信存储与访问控制。',
        ['追加收入与支出，分别生成正负的有符号金额','根据原ID追加反向金额，不改动或删除原记录','加载时重放每条业务操作并核对派生结果'],
        code,'保留流水 3 条\n结余 100.00\n',
        '实现replay(document)，按顺序重建流水并核对保存的ID、符号和引用，拒绝不一致内容。存档恢复后保留三条记录及相同结余。',
        solution,'重放 3 条，结余 100.00\n',
        ['把支出原记录改为零会丢失原始事件','重放校验不是防篡改签名，不能宣称实现了可信财务审计'],
        '追加记录保留纠错过程，重放校验让派生状态可以被重新推导。',
        ('ledger-reversal','冲销后为什么仍有三条流水，而不是只剩一条？','原事件保留，通过反向记录抵消金额',[('收入ID1','+100.00'),('支出ID2','−30.00'),('冲销ID3→2','+30.00，结余100.00')]),
        [case('重复冲销与冲销的冲销均拒绝',clean('''
base=append_entry([],"expense","2")
corrected=append_entry(base,"reversal","2",1)
assert base[0]["signed"]=="-2.00" and len(base)==1
for reference in (1,2):
    try: append_entry(corrected,"reversal","2",reference)
    except ValueError: pass
    else: raise AssertionError("无效冲销被接受")
''')),case('重放拒绝被改动符号',clean('''
saved=[dict(row) for row in restored]
saved[1]["signed"]="30.00"
try: replay(saved)
except ValueError: pass
else: raise AssertionError("错误符号被信任")
assert journal_balance(restored)==Decimal("100.00")
'''),field='solution')])


def _populate_modular(t):
    stats = clean('''
def parse_minutes(text):
    if not text.strip(): raise ValueError("至少输入一段时长")
    try: values=[int(part.strip()) for part in text.split(",")]
    except ValueError as error: raise ValueError("时长必须为逗号分隔整数") from error
    if any(value<0 or value>1440 for value in values): raise ValueError("每段时长应为0至1440分钟")
    return values

def summarize(minutes):
    if not minutes or any(type(value) is not int or not 0<=value<=1440 for value in minutes):
        raise ValueError("需要至少一个0至1440分钟的整数")
    return {"count":len(minutes),"total":sum(minutes),"average":sum(minutes)/len(minutes),"longest":max(minutes)}
''')
    main = clean('''
from studyblocks.stats import parse_minutes, summarize

def main():
    try:
        result=summarize(parse_minutes(input("时长（逗号分隔）：")))
    except ValueError as error:
        print("输入错误："+str(error))
        return
    print(f"{result['count']}段 / 总{result['total']}分钟 / 均{result['average']:.1f}分钟")

if __name__=="__main__":
    main()
''')
    files={"main.py":main,"studyblocks/__init__.py":'"""学习时长的纯计算工具包。"""\n',"studyblocks/stats.py":stats}
    solution_stats=stats+clean('''
def long_count(minutes,threshold=30):
    summarize(minutes)
    if type(threshold) is not int or not 0<=threshold<=1440: raise ValueError("长时段阈值无效")
    return sum(value>=threshold for value in minutes)
''')
    solution_main=main.replace('from studyblocks.stats import parse_minutes, summarize','from studyblocks.stats import parse_minutes, summarize, long_count').replace('result=summarize(parse_minutes(input("时长（逗号分隔）：")))','minutes=parse_minutes(input("时长（逗号分隔）："))\n        result=summarize(minutes)').replace('    print(f"{result[\'count\']}段 / 总{result[\'total\']}分钟 / 均{result[\'average\']:.1f}分钟")','    print(f"{result[\'count\']}段 / 总{result[\'total\']}分钟 / 均{result[\'average\']:.1f}分钟")\n    print(f"长时段{long_count(minutes)}段")')
    solution_files={**files,"main.py":solution_main,"studyblocks/stats.py":solution_stats}
    add(t,'p08','intermediate','多文件CLI：让输入入口依赖纯计算模块',
        ['通过真实包结构分离输入输出与计算规则','在不运行交互入口的情况下测试模块边界'],
        '多文件项目的价值不是把长代码随意切开。入口main.py负责读取与显示，工具包stats.py负责解析和统计，导入工具包不会突然要求用户输入。每段时长允许零分钟但不允许负数或超过一天，空列表没有平均值，必须明确拒绝。示例在课程专属目录生成三份真实文件，通过runpy在同一Python进程执行入口，不依赖子进程。切换文件能看到对应职责，练习只扩展计算模块与入口显示，原有统计接口保持不变。',
        ['建立studyblocks包，把规则放进stats.py','main.py只调用函数，格式化结果并处理业务错误','纯函数断言检查边界，再用真实入口检查组合行为'],
        _bootstrap(files,'lesson_blocks_intermediate','studyblocks',('parse_minutes','summarize')),
        '时长（逗号分隔）：3段 / 总65分钟 / 均21.7分钟\n',
        '增加long_count(minutes,threshold=30)，统计达到阈值的时段数，并由入口显示。边界等于阈值应计入；验证分钟与阈值，不修改原summarize的返回结构。',
        _bootstrap(solution_files,'lesson_blocks_solution','studyblocks',('parse_minutes','summarize','long_count')),
        '时长（逗号分隔）：3段 / 总65分钟 / 均21.7分钟\n长时段1段\n',
        ['在模块顶层调用input，会使导入和测试都阻塞','复制两套统计规则到入口与模块，后续修改容易不一致'],
        '职责分层的模块应可独立导入，而真实入口还需要组合执行验证。',
        ('module-boundary','导入stats时，为什么不应出现输入提示？','交互入口依赖纯函数，工具包不依赖入口',[('main.py','input → 调用 → print'),('stats.py','解析、校验、统计'),('测试','直接调用纯函数 + 真实入口')]),
        [case('纯模块零分钟与负数边界',clean('''
assert summarize([0,30])["average"]==15 and parse_minutes(" 0, 30 ")==[0,30]
try: summarize([-1])
except ValueError: pass
else: raise AssertionError("负时长被接受")
'''),stdin='25,0,40\n'),case('真实三文件入口', 'assert summarize([10,20])["total"]==30',stdin='10,20\n',fileSet='files',output='时长（逗号分隔）：2段 / 总30分钟 / 均15.0分钟\n'),case('答案阈值等号及文件集', 'assert long_count([0,29,30,31])==2 and long_count([0],0)==1',field='solution',stdin='30,30\n',fileSet='solutionFiles',output='时长（逗号分隔）：2段 / 总60分钟 / 均30.0分钟\n长时段2段\n')],
        stdin='25,0,40\n',files=files,solutionFiles=solution_files,
        sources=['https://docs.python.org/3.13/library/runpy.html#runpy.run_path'])

    parsing = clean('''
def parse_records(text):
    records=[]
    for number,line in enumerate(text.splitlines(),1):
        if not line.strip(): continue
        fields=line.split(",")
        if len(fields)!=2 or not fields[0].strip(): raise ValueError(f"第{number}行应为姓名,分钟")
        try: minutes=int(fields[1])
        except ValueError as error: raise ValueError(f"第{number}行分钟无效") from error
        if not 0<=minutes<=1440: raise ValueError(f"第{number}行分钟越界")
        records.append({"name":fields[0].strip(),"minutes":minutes})
    return records
''')
    reporting = clean('''
def build_report(records,minimum=0):
    if type(minimum) is not int or not 0<=minimum<=1440: raise ValueError("筛选阈值无效")
    groups={}
    for row in records:
        if row["minutes"]>=minimum:
            groups.setdefault(row["name"],[]).append(row["minutes"])
    return [{"name":name,"count":len(values),"total":sum(values),"longest":max(values)}
            for name,values in sorted(groups.items())]
''')
    cli = clean('''
from pathlib import Path
from sessionreport.parsing import parse_records
from sessionreport.reporting import build_report

def main():
    source=Path(input("记录文件：").strip())
    try:
        records=parse_records(source.read_text(encoding="utf-8"))
        rows=build_report(records,minimum=20)
    except (OSError,UnicodeError,ValueError) as error:
        print("读取失败："+str(error))
        return
    for row in rows:
        print(f"{row['name']}：{row['count']}段，总{row['total']}分钟，最长{row['longest']}分钟")
    if not rows: print("没有符合条件的记录")

if __name__=="__main__":
    main()
''')
    sample='安安,25\n小林,10\n安安,40\n小林,20\n'
    files={"main.py":cli,"sessionreport/__init__.py":'"""分层学习时间报表。"""\n',"sessionreport/parsing.py":parsing,"sessionreport/reporting.py":reporting,"records.txt":sample}
    solution_reporting=reporting+clean('''
def summary_document(records,minimum=0):
    rows=build_report(records,minimum)
    return {"version":1,"minimum":minimum,"people":rows,"total":sum(row["total"] for row in rows)}
''')
    solution_cli = clean('''
import json
from pathlib import Path
from sessionreport.parsing import parse_records
from sessionreport.reporting import build_report, summary_document

def main():
    source=Path(input("记录文件：").strip())
    try:
        document=summary_document(parse_records(source.read_text(encoding="utf-8")),minimum=20)
    except (OSError,UnicodeError,ValueError) as error:
        print("读取失败："+str(error))
        return
    destination=Path("report.json")
    temporary=destination.with_name(destination.name+".tmp")
    temporary.write_text(json.dumps(document,ensure_ascii=False,sort_keys=True),encoding="utf-8")
    temporary.replace(destination)
    print(f"已写report.json：{len(document['people'])}人，总{document['total']}分钟")

if __name__=="__main__":
    main()
''')
    solution_files={**files,"main.py":solution_cli,"sessionreport/reporting.py":solution_reporting}
    # 引导代码还原入口工作目录，使相对数据路径与原生文件集运行一致。
    add(t,'p08','advanced','多文件报表：解析、筛选与可迁移输出',
        ['以明确模块边界组织可维护的数据处理CLI','用真实文件集回归确认入口、模块和输出保持一致'],
        '高级版从一行时长扩展到多人记录。parsing只把文件文本解析为结构化记录，reporting按阈值筛选并分组，入口负责文件路径、错误显示和最终输出。零分钟在解析层合法，是否纳入报表由筛选规则决定；不应把两种规则混在一起。练习输出带版本与阈值的JSON，方便别的程序继续使用。示例与答案都提供真实文件集，并在同一进程用runpy运行；测试既检查函数边界，也直接执行文件集，避免引导示例正确而导出的项目无法运行。',
        ['将姓名与分钟解析为记录，保留错误行号','按至少20分钟筛选，再按姓名分组汇总','入口显示报表，答案将同一结果原子写入JSON文件'],
        _bootstrap(files,'lesson_report_advanced','sessionreport',('parse_records','build_report'),cwd=True),
        '记录文件：安安：2段，总65分钟，最长40分钟\n小林：1段，总20分钟，最长20分钟\n',
        '增加summary_document，并将入口改为写report.json，包含version、minimum、people与total。JSON要保留中文，使用临时文件替换；同一筛选规则必须用于显示与导出。',
        _bootstrap(solution_files,'lesson_report_solution','sessionreport',('parse_records','build_report','summary_document'),cwd=True),
        '记录文件：已写report.json：2人，总85分钟\n',
        ['入口重新实现一次筛选，会让屏幕结果与JSON产生差异','仅执行生成文件的引导脚本，没有验证真实main.py及包导入'],
        '模块接口、真实入口与文件产物三层都通过，项目才算可迁移。',
        ('report-modules','筛选阈值应在哪一层实施，才能让屏幕与JSON一致？','解析模块与报表模块由入口组合成可迁移项目',[('parsing.py','文本 → 姓名、分钟'),('reporting.py','筛选 → 分组 → 结构化报表'),('main.py','文件输入 → 显示或JSON')]),
        [case('真实文件集过滤边界与零分钟', 'assert build_report(parse_records("A,0\\nA,20\\nB,19\\n"),20)==[{"name":"A","count":1,"total":20,"longest":20}]',stdin='records.txt\n',fileSet='files'),case('答案真实文件集写出完整JSON',clean('''
document=json.loads(Path("report.json").read_text(encoding="utf-8"))
assert document=={"version":1,"minimum":20,"people":[{"name":"安安","count":2,"total":65,"longest":40},{"name":"小林","count":1,"total":20,"longest":20}],"total":85}
assert not Path("report.json.tmp").exists()
'''),field='solution',stdin='records.txt\n',fileSet='solutionFiles'),case('空数据与错误行定位',clean('''
assert summary_document([],20)=={"version":1,"minimum":20,"people":[],"total":0}
try: parse_records("A,20\\nB,-1\\n")
except ValueError as error: assert "第2行" in str(error)
else: raise AssertionError("错误行被接收")
'''),field='solution',stdin='records.txt\n')],
        stdin='records.txt\n',files=files,solutionFiles=solution_files,
        sources=['https://docs.python.org/3.13/library/runpy.html#runpy.run_path','https://docs.python.org/3.13/library/json.html'])


def _bootstrap(files,directory,package,exports,cwd=False):
    """Generate actual files, run in-process, restore only owned module names."""
    return clean('''
import os
import runpy
import sys
from pathlib import Path
''') + f'files={files!r}\n' + f'root=Path({directory!r}).resolve()\n' + clean('''
for relative,source in files.items():
    path=root/relative
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(source,encoding="utf-8")
old_path,old_argv,old_cwd=list(sys.path),list(sys.argv),Path.cwd()
''') + f'prefix={package!r}\n' + clean('''
owned=lambda name:name==prefix or name.startswith(prefix+".")
cached={name:value for name,value in sys.modules.items() if owned(name)}
for name in list(cached): del sys.modules[name]
try:
    sys.path.insert(0,str(root))
    sys.argv=[str(root/"main.py")]
''') + ('    os.chdir(root)\n' if cwd else '') + clean('''
    namespace=runpy.run_path(str(root/"main.py"),run_name="__main__")
finally:
    sys.path[:]=old_path
    sys.argv[:]=old_argv
    os.chdir(old_cwd)
    for name in list(sys.modules):
        if owned(name): del sys.modules[name]
    sys.modules.update(cached)
''').replace('namespace=runpy.run_path','    namespace=runpy.run_path',1) + f'globals().update({{name:namespace[name] for name in {exports!r}}})\n'
