"""Authoring helpers; content lives in independent, editable chapter modules."""
import textwrap

TIER_IDS = ("beginner", "intermediate", "advanced")
LABELS = {"beginner": "初级", "intermediate": "中级", "advanced": "高级"}

def clean(code):
    return textwrap.dedent(code).strip() + "\n"

def case(name, assertion, field="code", stdin="", output=None, replacements=None, **extra):
    result = dict(name=name, field=field, stdin=stdin, assertions=assertion)
    if output is not None:
        result["expectedOutput"] = output
    if replacements:
        result["replacements"] = [dict(find=old, replace=new) for old,new in replacements]
    result.update(extra)
    return result

def add(target, topic, level, title, goals, explanation, steps, code, output, exercise,
        solution, solution_output, mistakes, summary, visual, tests, stdin="", minutes=None,
        prerequisites=None, **extra):
    if len(tests) < 2:
        raise ValueError(f"{topic}:{level} requires two additional meaningful cases")
    entry = dict(id=level, unitId=f"{topic}:{level}", topicId=topic, label=LABELS[level], title=title,
                 minutes=minutes or (35 if level=="intermediate" else 50),
                 prerequisites=prerequisites or [topic], objectives=goals,
                 body="### 新知识与问题\n\n" + explanation.strip() + "\n\n### 执行与推理\n\n" + "\n".join(f"{i}. {text}" for i,text in enumerate(steps,1)),
                 code=clean(code), stdin=stdin, expectedOutput=output, exercise=exercise,
                 solution=clean(solution), solutionExpectedOutput=solution_output,
                 commonMistakes=mistakes, summary=summary,
                 diagram=f"course-assets/tier-{topic}-{level}.webp",
                 visual=dict(kind=visual[0], caption=visual[1], alt=visual[2],
                             stages=[dict(label=label,value=str(value)) for label,value in visual[3]]))
    entry.update(extra)
    cases=[dict(name="example",field="code",stdin=stdin,expectedOutput=output),
           dict(name="answer",field="solution",stdin=stdin,expectedOutput=solution_output)]
    for item in tests:
        item=dict(item)
        item.setdefault("expectedOutput", output if item["field"]=="code" else solution_output)
        if "stdin" not in item: item["stdin"]=stdin
        cases.append(item)
    entry["testCases"]=cases
    target.setdefault(topic,{})[level]=entry
    return entry
