(async function () {
  await patchState({trusted:true,theme:'dark'});
  const {project} = await api('project.create',{name:'真实 Python 错误验收',color:'#77718a',category:'验收'});
  S.projects.push(project);
  await api('file.write',{id:project.id,path:'main.py',content:'def greet(name):\n    return "你好，" + name\n\nprint(greet(42))\n'});
  await openProject(project.id);
  await runCode();
})();
