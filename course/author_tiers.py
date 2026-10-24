"""Compose the three-level original course while keeping v1 lesson IDs compatible."""
from copy import deepcopy
from tier_helpers import LABELS

BEGINNER_VISUALS = {
"l01":("pipeline","屏幕上的一句话在哪一步才真正出现？",[("源码",'print("你好")'),("执行",'解释器读取指令'),("输出",'你好')]),
"l02":("sequence","sep 与 end 各改变了哪一段间隔？",[("三个参数",'2026 | 10 | 20'),("sep分隔",'2026/10/20'),("end空格",'进度： 完成第一课')]),
"l03":("reference","pages 改成15后，copied为什么仍是12？",[("原值",'pages → 12；copied → 12'),("重绑定",'pages → 15'),("不变引用",'copied → 12')]),
"l04":("partition","17个贴纸装成5个一袋，哪里是商与余数？",[("数量",17),("完整袋",'5 + 5 + 5'),("剩余",2)]),
"l05":("pipeline","格式变成3.50，原来的price是否也改变？",[("变量",'小禾；25'),("模板槽位",'{name}；{minutes}'),("显示",'小禾学习了25分钟；3.50')]),
"l06":("sequence","第二次input会覆盖姓名，还是保存另一行？",[("姓名输入",'小禾 → name'),("城市输入",'杭州 → city'),("合成输出",'来自杭州的小禾')]),
"l07":("branch","同样的12，哪一条路径得到1212？",[("文本路径",'"12" + "12" → "1212"'),("转换",'int("12") → 12'),("数值路径",'12 * 2 → 24')]),
"l08":("branch","比较以后，82会不会被100替换？",[("原始分数",82),("比较",'>=60 True；==100 False'),("比较后",'score仍为82')]),
"l09":("branch","人数为0时，为什么没有发生除零？",[("左条件",'count>0为False'),("短路",'跳过total/count'),("结果",False)]),
"l10":("branch","82分会经过哪些判断，在哪个分支停止？",[("有效范围",True),("达到90",False),("达到60",'True → 通过')]),
"l11":("state","banana的哪三轮会改变计数？",[("字符",'b a n a n a'),("累计",'0 1 1 2 2 3'),("结果",3)]),
"l12":("sequence","终点6为什么没有出现在输出里？",[("起点",1),("实际整数",'1 2 3 4 5'),("排除终点",6)]),
"l13":("state","余额达到21后还会再加7吗？",[("初始",0),("三轮更新",'7 → 14 → 21'),("继续条件",'21<20为False')]),
"l14":("branch","14命中后，15是否还会被检查？",[("跳过本轮",'10 11 12 13'),("命中并break",14),("未访问",'15…20')]),
"l15":("matrix","第二行开始时，列编号从哪里重新开始？",[("第一行",'1-1 → 1-2 → 1-3'),("第二行",'2-1 → 2-2 → 2-3'),("总次数",6)]),
"l16":("state","哪一轮第一次与手算预期不一致？",[("期望累计",'1 → 3 → 6'),("错误赋值",'1 → 2 → 3'),("首次偏离",'第2轮')]),
"l17":("pipeline","拆分之前不处理空格，会留下什么？",[("原文",'  Python, JSON, CSV  '),("清洗拆分",'Python | JSON | CSV'),("重新连接",'Python / JSON / CSV')]),
"l18":("matrix","显示编号1和列表索引0指向同一项吗？",[("列表元素",'Python 数学 写作'),("索引",'0 1 2'),("显示编号",'1 2 3')]),
"l19":("state","pop(0)返回了什么，剩下的元素怎样移动？",[("初始",'阅读 练习'),("添加替换",'阅读 写习题 复习'),("删除后",'写习题 复习；返回阅读')]),
"l20":("reference","修改alias和copied时，哪一次会影响原列表？",[("共享",'alias → 原列表'),("浅复制",'copied → 新外层'),("改动",'原首项99；副本第二项88')]),
"l21":("reference","交换x、y时，两个旧值怎样避免丢失？",[("解包",'x=3，y=4'),("先读右侧",'(4,3)'),("重新绑定",'x=4，y=3')]),
"l22":("mapping","更新score后，name的值会变化吗？",[("姓名键",'name → 小禾'),("分数键",'score → 80'),("更新分数",'score → 86')]),
"l23":("venn","愿望清单减去已读，留下哪一本？",[("已读",'Python 数学'),("共同",'Python'),("尚未读愿望",'写作')]),
"l24":("pipeline","先平方再筛选，与先筛选再平方是否等价？",[("输入",'-2 0 2 5'),("筛选正数",'2 5'),("变换",'4 25')]),
"l25":("function","函数返回的12还能参与后续计算吗？",[("参数",'3和4'),("area",'3*4'),("返回",'12 → 调用处')]),
"l26":("binding","没有传greeting时，问候语从哪里来？",[("默认参数",'greeting=你好'),("显式参数",'greeting=早上好'),("分别调用",'独立的返回文本')]),
"l27":("scope","函数内的label为什么没有改掉外面的label？",[("模块",'label=全局'),("局部",'label=局部'),("列表复制",'原阅读；新阅读练习')]),
"l28":("module","import math与from math import ceil绑定哪些名字？",[("模块",'math'),("属性调用",'math.sqrt(81)'),("直接名字",'ceil(2.3)')]),
"l29":("tree","导入名的点号怎样对应包与子模块？",[("包",'urllib'),("子模块",'parse'),("工具",'urlencode / parse_qs')]),
"l30":("branch","格式错误与范围错误最终在哪里汇合处理？",[("85",'转换与范围通过'),("abc",'int触发ValueError'),("120",'主动raise ValueError')]),
"l31":("resource","用w和a分别打开文件后，两行内容怎样留下？",[("w写入",'第一天变量'),("a追加",'第二天循环'),("r读取",'两行完整文本')]),
"l32":("tree","路径描述和真实目录在哪一步开始不同？",[("构造Path",'demo_data/note.txt'),("创建写入",'目录和文件出现'),("枚举",'*.txt匹配note.txt')]),
"l33":("serialization","保存后的文字怎样重新变成可统计的数据？",[("Python结构",'两条待办'),("JSON文件",'UTF-8文字'),("读回",'完成计数1')]),
"l34":("table","名字里有逗号时，为什么不能直接split？",[("CSV字段",'小禾,甲组'),("引用保护",'单个姓名列'),("数字转换",'80+90=170')]),
"l35":("state","固定种子改变了结果的哪种性质？",[("独立随机对象",'Random(2026)'),("骰子",'1到6含两端'),("检查",'每次值都在范围内')]),
"l36":("timeline","跨过闰日和精确小数分别应交给谁？",[("日期",'2024-02-28 + 2天'),("结果日期",'2024-03-01'),("Decimal",'0.10+0.20=0.30')]),
"l37":("queue","先到的A为何先被popleft取走？",[("入队",'A → B'),("取出",'A'),("剩余",'B')]),
"l38":("ordering","两个80分的人为什么保持原来的先后？",[("原序",'小禾80 阿青90 小川80'),("按分数降序",'阿青90 小禾80 小川80'),("同键稳定",'小禾在小川之前')]),
"l39":("interval","每次二分后，哪半边还可能含有目标？",[("有序列表",'1 3 5 7 9 11'),("中点",'索引3值7'),("未命中",'目标8最终区间为空')]),
"l40":("boundary","只测60能检查出上下界错误吗？",[("下界附近",'-1 → 0；0 → 0'),("内部",'60 → 60'),("上界附近",'100 → 100；101 → 100')]),
"l41":("objects","完成第一项后，第二项的done是否变化？",[("共同类",'Task'),("第一实例",'阅读 done=True'),("第二实例",'练习 done=False')]),
"l42":("inheritance","子类怎样复用标题，又扩展时长？",[("父类Task",'title'),("super初始化",'继承公共状态'),("TimedTask",'title+minutes；覆盖summary')]),
"l43":("cursor","取走20后，再次next会回到10吗？",[("列表",'10 20'),("游标",'取10 → 取20 → 耗尽'),("新游标",'重新从10开始')]),
"l44":("state","yield之后的函数在何时继续？",[("创建",'尚未执行循环'),("逐项恢复",'0 → 1 → 4 → 9'),("耗尽后",'再消费为空')]),
"l45":("wrapping","为什么外层仍能拿到原函数的返回值？",[("装饰",'greet → wrapper'),("调用",'开始 → 原函数 → 结束'),("返回",'你好，小禾')]),
"l46":("resource","with块内出错时，关闭会被跳过吗？",[("进入",'打开'),("块内",'模拟ValueError'),("退出",'关闭 → 外层处理')]),
"l47":("optional","没有分数时，None与0分有何不同？",[("非空列表",'80 90 → 85.0'),("空列表",'→ None'),("调用处",'先判断None再格式化')]),
"l48":("test-paths","哪条测试专门证明非法价格被拒绝？",[("普通",'8*3=24'),("边界",'8*0=0'),("异常",'-1触发ValueError')]),
"l49":("environment","包安装进另一个解释器后，当前环境能看见吗？",[("解释器",'Python版本'),("环境",'标准库与第三方包路径'),("虚拟环境",'独立包版本，不是权限沙箱')]),
"l50":("layers","被导入时，哪一部分应该保持安静？",[("转换验证",'parse_quantity'),("纯计算",'inventory_total'),("入口",'main由入口保护启动')]),
"p01":("game-state","非法输入会消耗一次猜测机会吗？",[("无效输入",'不扣次数'),("有效未中",'提示并加次数'),("命中/用完",'break/循环else')]),
"p02":("pipeline","除零应由解析层还是计算层拒绝？",[("文本解析",'12 / 4'),("数值与运算符",'12.0 / 4.0'),("计算显示",'3')]),
"p03":("validation","重复姓名为什么不能悄悄覆盖？",[("逐条校验",'姓名和0至100整数'),("统计",'3人，平均79.3'),("错误",'整批拒绝并提示')]),
"p04":("persistence","写临时文件中途失败时，原待办怎样保住？",[("内存变更",'任务列表'),("写临时",'完整JSON'),("替换",'项目待办文件')]),
"p05":("analysis","把Small转小写后，词频怎样合并？",[("清洗",'小写与首尾标点'),("计数",'8词，6种'),("排序",'small2 tools2 makes1')]),
"p06":("aggregation","坏行被跳过后，报告如何让人知道少了哪项？",[("输入4行",'其中1条坏价格'),("有效3行",'学习38 文具6'),("报告",'坏行5，总额44')]),
"p07":("ledger","撤销支出后，余额应如何重新计算？",[("收入",1000),("支出",33.50),("结余",966.50)]),
"p08":("module-tree","只改入口能不能给纯统计模块增加中位数？",[("入口",'main.py'),("包模块",'studytools/stats.py'),("数据流",'12 18 30 → 60/20/30')]),
}

def build_tiers(chapters, authored):
    seen=[]
    for chapter in chapters:
        for lesson in chapter["lessons"]:
            topic=lesson["id"]
            beginner=deepcopy({key:value for key,value in lesson.items() if key!="tiers"})
            beginner.update(id="beginner",unitId=f"{topic}:beginner",topicId=topic,label=LABELS["beginner"],diagram=f"course-assets/tier-{topic}-beginner.webp")
            kind,caption,stages=BEGINNER_VISUALS[topic]
            beginner["visual"]=dict(kind=kind,caption=caption,alt=caption,stages=[dict(label=label,value=str(value)) for label,value in stages])
            old_cases=beginner.get("testCases",[])
            beginner["testCases"]=[dict(name="example",field="code",stdin=beginner["stdin"],expectedOutput=beginner["expectedOutput"]),dict(name="answer",field="solution",stdin=beginner["stdin"],expectedOutput=beginner["solutionExpectedOutput"]),*old_cases]
            missing={"intermediate","advanced"}-set(authored.get(topic,{}))
            if missing: raise ValueError(f"Missing authored tiers for {topic}: {sorted(missing)}")
            lesson["tiers"]=[beginner,authored[topic]["intermediate"],authored[topic]["advanced"]]
            for unit in lesson["tiers"]:
                unit.setdefault("sources",deepcopy(lesson.get("sources",[])))
            lesson["diagram"]=beginner["diagram"]
            lesson["visual"]=beginner["visual"]
            seen.append(topic)
    if len(seen)!=58: raise ValueError("The v2 curriculum must retain all 58 topic IDs")
    try:
        from visual_overrides import VISUAL_OVERRIDES
    except ModuleNotFoundError as error:
        if error.name!="visual_overrides": raise
        VISUAL_OVERRIDES={}
    for chapter in chapters:
        for lesson in chapter["lessons"]:
            for unit in lesson["tiers"]:
                for key,value in VISUAL_OVERRIDES.get(unit["unitId"],{}).items():
                    if key not in {"caption","alt"}: raise ValueError("Visual review may only override caption/alt")
                    unit["visual"][key]=value
            lesson["visual"]=deepcopy(lesson["tiers"][0]["visual"])

def author_all():
    target={}
    from author_tiers_foundation import populate as foundation
    from author_tiers_data import populate as data
    from author_tiers_packages import populate as packages
    from author_tiers_design import populate as design
    from author_tiers_projects import populate as projects
    for populate in (foundation,data,packages,design,projects): populate(target)
    return target
