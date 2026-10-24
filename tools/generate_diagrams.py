"""Deterministic, locally bundled teaching diagrams. No third-party artwork."""
from pathlib import Path
from html import escape

DEST = Path(__file__).resolve().parents[1] / 'web' / 'course-assets'
DEST.mkdir(parents=True, exist_ok=True)
BG, INK, TEAL, SOFT, AMBER = '#f7f8f4', '#253d32', '#3a745c', '#e2ecdf', '#e6bf83'

def text(x,y,label,size=24,fill=INK,anchor='start',mono=False):
    font='Consolas,monospace' if mono else 'Segoe UI,Microsoft YaHei,sans-serif'
    return f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" fill="{fill}" text-anchor="{anchor}">{escape(label)}</text>'

def box(x,y,w,h,label,fill=SOFT,size=24):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="13" fill="{fill}" stroke="#b6cbb3"/>'+text(x+w/2,y+h/2+8,label,size,anchor='middle')

def arrow(x1,y1,x2,y2,label=None,lx=None,ly=None):
    out=f'<path d="M{x1} {y1} L{x2} {y2}" stroke="{TEAL}" stroke-width="3" fill="none" marker-end="url(#a)"/>'
    return out+(text(lx if lx is not None else (x1+x2)/2,ly if ly is not None else (y1+y2)/2-10,label,21,anchor='middle') if label else '')

def diagram(name,title,subtitle,parts,h=430):
    header=f'<svg xmlns="http://www.w3.org/2000/svg" width="760" height="{h}" viewBox="0 0 760 {h}" role="img"><title>{escape(title)}</title><defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 10 5 0 10" fill="{TEAL}"/></marker></defs><rect width="760" height="{h}" rx="18" fill="{BG}"/>'
    (DEST/name).write_text(header+text(35,48,title,27)+text(35,82,subtitle,18,'#647a6b')+''.join(parts)+'</svg>',encoding='utf-8')

diagram('variables.svg','变量名，指向一个对象','赋值建立名称与对象的关系；重新赋值会改变指向。',[
    text(55,139,'score = 8',24,mono=True),box(50,170,180,65,'score'),box(485,170,200,65,'整数对象 8',AMBER),arrow(245,202,470,202,'引用'),
    text(55,295,'score = 10',24,mono=True),box(50,325,180,65,'score'),box(485,325,200,65,'整数对象 10',AMBER),arrow(245,357,470,357,'新的引用')])

diagram('condition.svg','条件判断：一次只走一个分支','if 条件为真执行左侧；否则执行 else，之后汇合。',[
    '<path d="M380 105 505 170 380 235 255 170z" fill="#e6bf83" stroke="#b6cbb3"/>',text(380,179,'age >= 18 ?',24,anchor='middle',mono=True),
    arrow(255,170,150,170,'True',200,151),arrow(505,170,615,170,'False',565,151),
    box(45,190,210,68,'输出：成年人'),box(510,190,210,68,'输出：未成年'),
    '<path d="M150 258V320H380M615 258V320H380" stroke="#3a745c" stroke-width="3" fill="none"/>',arrow(380,320,380,350),box(270,355,220,55,'继续后面的代码')])

diagram('loop.svg','while 循环：先判断，再执行','循环体必须让条件有机会改变，否则可能无限循环。',[
    box(45,120,180,60,'i = 0'),arrow(230,150,290,150),box(300,120,185,60,'i < 3 ?',AMBER),
    arrow(485,150,555,150,'False',524,131),box(565,120,145,60,'离开循环'),
    arrow(390,180,390,235,'True',432,217),box(295,245,200,75,'print(i)；i += 1'),
    '<path d="M295 280H245V205H330V185" stroke="#3a745c" stroke-width="3" fill="none" marker-end="url(#a)"/>',
    text(380,385,'输出：0 → 1 → 2；之后 i = 3，条件为假。',22,anchor='middle')])

diagram('slicing.svg','列表索引与切片','items[1:3] 包含起点 1，不包含终点 3。',[
    text(45,135,'items = ["A", "B", "C", "D"]',25,mono=True),
    *[box(65+i*160,190,140,72,c,AMBER if i in(1,2) else SOFT,30)+text(135+i*160,172,str(i),23,anchor='middle',mono=True)+text(135+i*160,293,str(i-4),23,'#647a6b',anchor='middle',mono=True) for i,c in enumerate('ABCD')],
    text(380,347,'索引 1、2 → ["B", "C"]',26,anchor='middle',mono=True),text(380,390,'负索引从右边开始：-1 表示最后一项。',21,anchor='middle')])

diagram('dictionary.svg','字典：通过键，找到对应的值','键必须可哈希；一个字典中，同一个键只保留一个值。',[
    text(85,135,'键（key）',24),text(475,135,'值（value）',24),
    box(65,160,225,65,'"name"'),box(465,160,225,65,'"小林"',AMBER),arrow(305,192,450,192),
    box(65,255,225,65,'"score"'),box(465,255,225,65,'92',AMBER),arrow(305,287,450,287),
    text(380,385,'student["score"]  →  92',25,anchor='middle',mono=True)])

diagram('functions.svg','函数：传入参数，返回结果','调用函数时执行函数体；return 将结果交回调用处。',[
    text(45,136,'def double(n):',25,mono=True),text(45,173,'    return n * 2',25,mono=True),
    box(40,235,160,70,'参数 3'),box(285,220,200,100,'double(n)',SOFT,26),box(570,235,145,70,'结果 6',AMBER),
    arrow(210,270,270,270),arrow(495,270,555,270),text(380,385,'answer = double(3)  →  answer 得到 6',23,anchor='middle',mono=True)])

diagram('scope.svg','作用域：函数有自己的局部名称','读取名称会向外查找；函数内赋值通常创建局部名称。',[
    '<rect x="40" y="115" width="680" height="280" rx="15" fill="#e2ecdf" stroke="#b6cbb3"/>',text(65,154,'模块作用域：x = 10',25),
    '<rect x="80" y="185" width="580" height="145" rx="13" fill="#f7f8f4" stroke="#9bb795"/>',text(105,224,'函数作用域：x = 3',25),text(105,277,'函数里 print(x) → 3',24,mono=True),
    text(65,370,'函数外 print(x) → 10',24,mono=True)])

diagram('exceptions.svg','异常处理：只在发生异常时进入 except','无异常时直接继续；有匹配异常时执行处理代码。',[
    box(250,115,260,60,'try：执行代码',AMBER),arrow(250,145,145,145,'有匹配异常',170,128),arrow(510,145,620,145,'无异常',571,128),
    box(35,200,260,65,'except：处理异常'),'<path d="M145 145V190" stroke="#3a745c" stroke-width="3" marker-end="url(#a)"/>',
    '<path d="M620 145V310H380M165 265V310H380" stroke="#3a745c" stroke-width="3" fill="none"/>',arrow(380,310,380,340),box(245,345,270,60,'继续后面的代码'),
    text(380,435,'未匹配的异常继续向外传播；此图未展开 else / finally。',19,anchor='middle')],h=465)

diagram('classes.svg','类与对象：同一种定义，各自保存状态','实例属性属于各个对象；方法描述对象可以执行的操作。',[
    box(215,120,330,80,'类 Counter：count、add()',AMBER,25),arrow(285,205,200,260,'实例化',220,232),arrow(475,205,560,260,'实例化',535,232),
    box(70,270,260,90,'a：count = 1'),box(430,270,260,90,'b：count = 0'),
    text(380,410,'a.add() 改变 a 的实例状态；不会改变 b.count。',22,anchor='middle')],h=445)

diagram('modules.svg','多文件项目：文件路径与导入路径','运行入口在项目根目录；包中 __init__.py 可以为空。',[
    box(35,115,260,75,'main.py',AMBER,27),box(430,115,295,75,'studytools / stats.py',SOFT,24),arrow(305,152,415,152,'import',360,132),
    text(45,245,'项目目录 /',25),text(75,287,'main.py',24,mono=True),text(75,328,'studytools / __init__.py',24,mono=True),text(75,369,'studytools / stats.py',24,mono=True),
    text(380,425,'from studytools.stats import summarize',23,anchor='middle',mono=True)],h=455)

print(f'Generated {len(list(DEST.glob("*.svg")))} SVG diagrams in {DEST}')

