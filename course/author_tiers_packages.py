"""Actual package trees; bootstrap preserves Android in-process execution."""
from tier_helpers import add,case,clean

def bootstrap(files,directory):
    return clean('''import runpy,sys
from pathlib import Path
''')+f'files={files!r}\nroot=Path({directory!r}).resolve()\n'+clean('''
for name,text in files.items():
    path=root/name
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(text,encoding="utf-8")
saved=list(sys.path)
try:
    sys.path.insert(0,str(root))
    namespace=runpy.run_path(str(root/"main.py"),run_name="__main__")
finally:
    sys.path[:]=saved
globals().update({key:value for key,value in namespace.items() if not key.startswith("__")})
''')

def populate(t):
    files={
        'main.py':'from unitkit import celsius_to_fahrenheit\nprint(celsius_to_fahrenheit(0),celsius_to_fahrenheit(-40))\n',
        'unitkit/__init__.py':'from .temperature import celsius_to_fahrenheit\n',
        'unitkit/temperature.py':'def celsius_to_fahrenheit(value):\n    return value*9/5+32\n',
    }
    answer={
        'main.py':'from lengthkit import centimeters_to_meters\nprint(centimeters_to_meters(250))\n',
        'lengthkit/__init__.py':'from .conversion import centimeters_to_meters\n',
        'lengthkit/conversion.py':'def centimeters_to_meters(value):\n    if value<0:\n        raise ValueError("长度不能为负")\n    return value/100\n',
    }
    add(t,'l29','intermediate','真正的小包：子模块与公共入口', ['创建带__init__.py的实际包目录','使用相对导入导出公共函数'],
        '包把相关模块组织在目录里。本例真正写出main.py、unitkit/__init__.py和unitkit/temperature.py，入口从包名导入公开函数，包的初始化文件再用.from形式的相对导入连接内部模块。相对导入开头的点表示当前包，不能把子模块随意当独立脚本运行；正常启动对象是项目入口main.py。内联自举只是让离线课件一键生成这棵目录，业务代码仍在真实独立文件里；嵌入运行环境显式加入项目目录后用runpy运行，不新建系统进程。',
        ['先观察三个文件的目录结构与各自职责','__init__.py从temperature导出公共函数','main只依赖unitkit公共名字，不复制公式'],
        bootstrap(files,'lesson_package_units'),'32.0 -40.0\n',
        '创建lengthkit包，conversion.py实现非负厘米转米，__init__.py公开centimeters_to_meters；main从包入口调用250厘米，禁止把函数又复制到main。',
        bootstrap(answer,'lesson_package_lengths'),'2.5\n',
        ['直接运行包内子模块可能没有父包上下文而使相对导入失败','把项目目录命名为json.py等标准库名会遮蔽标准模块'], '包的目录结构承载职责边界，公共入口让调用方不依赖内部布局。',
        ('package-tree','main为什么从unitkit导入，而不用知道temperature.py的位置？','真实包初始化文件连接公共接口与子模块',[('项目入口','main.py → from unitkit import ...'),('包入口','unitkit/__init__.py'),('子模块','temperature.py负责公式')]),
        [case('摄氏边界关系','assert celsius_to_fahrenheit(-40)==-40 and celsius_to_fahrenheit(100)==212'),case('答案拒绝负长度',"assert centimeters_to_meters(0)==0\ntry:\n    centimeters_to_meters(-1)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('negative')",field='solution'),case('真实文件集入口','assert celsius_to_fahrenheit(0)==32',fileSet='files')],
        files=files,solutionFiles=answer,sources=['https://docs.python.org/3.11/tutorial/modules.html#packages'])
    files={
        'main.py':'from receiptkit import invoice_total\nprint(invoice_total([("笔",2,3),("本",5,2)]))\n',
        'receiptkit/__init__.py':'from .service import invoice_total\n__all__=["invoice_total"]\n',
        'receiptkit/rules.py':'def validate_rows(rows):\n    result=list(rows)\n    for name,price,count in result:\n        if not isinstance(name,str) or not name.strip() or type(price) is not int or type(count) is not int or price<0 or count<0:\n            raise ValueError("商品记录无效")\n    return result\n',
        'receiptkit/service.py':'from .rules import validate_rows\ndef invoice_total(rows):\n    return sum(price*count for name,price,count in validate_rows(rows))\n',
    }
    answer={
        'main.py':'from gradepkg import grade_summary\nprint(grade_summary([59,60,100]))\n',
        'gradepkg/__init__.py':'from .report import grade_summary\n__all__=["grade_summary"]\n',
        'gradepkg/validation.py':'def checked(values):\n    data=list(values)\n    if any(type(x) is not int or not 0<=x<=100 for x in data):\n        raise ValueError("分数无效")\n    return data\n',
        'gradepkg/report.py':'from .validation import checked\ndef grade_summary(values):\n    data=checked(values)\n    return {"count":len(data),"passed":sum(x>=60 for x in data)}\n',
    }
    add(t,'l29','advanced','包内依赖方向：验证、服务与稳定接口', ['将包拆成单向依赖的内部模块','在不改变公共导入的情况下重构内部文件'],
        '模块一多，互相导入容易形成循环依赖。设计时可以给依赖安排方向：入口只使用包公开服务，service依赖rules，rules只处理纯数据而不反过来导入入口。本例实际创建四文件小包，__init__.py导出invoice_total，使调用方不需要知道内部验证移到了哪个文件。__all__影响星号导入的公开名字，不是安全私有机制，显式导入仍可访问内部模块。高级练习把成绩验证与统计分开，要求生成器输入只材料化一次，非法数据整批拒绝而不是被过滤。',
        ['画出main→公共接口→service→rules的无环方向','校验模块只接收数据并返回已验证列表','用入口不变的测试证明内部重构可替换'],
        bootstrap(files,'lesson_receipt_package'),'16\n',
        '构建gradepkg，validation.py校验0至100整数且排除bool，report.py统计count/passed，__init__只公开grade_summary；main通过公开接口演示59、60、100。',
        bootstrap(answer,'lesson_grade_package'),"{'count': 3, 'passed': 2}\n",
        ['内部模块反向导入main会引入副作用和循环依赖','__all__不是权限隔离，不要当作保护秘密的机制'], '让模块依赖单向流动，用小而稳定的包接口隔离内部重构。',
        ('module-dependencies','校验模块为什么不应该反过来导入main？','四文件包的单向依赖与公共接口',[('调用方','main → receiptkit.invoice_total'),('服务','service → rules.validate_rows'),('底层','rules只处理数据，无反向箭头')]),
        [case('生成器与零项计费','assert invoice_total(iter([("A",0,8),("B",2,0)]))==0 and invoice_total([])==0'),case('答案生成器与bool拒绝',"assert grade_summary(iter([0,60]))=={'count':2,'passed':1}\ntry:\n    grade_summary([True])\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('bool')",field='solution'),case('真实包答案入口','assert grade_summary([])=={"count":0,"passed":0}',field='solution',fileSet='solutionFiles')],
        files=files,solutionFiles=answer,sources=['https://docs.python.org/3.11/tutorial/modules.html#intra-package-references'])
