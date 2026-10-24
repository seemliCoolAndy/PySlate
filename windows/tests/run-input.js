(async function () {
  // This explicit test fixture uses a fresh workspace-only library.
  await patchState({trusted:true,theme:'light'});
  const {project} = await api('project.create',{name:'真实 input 运行验收',color:'#3c6955',category:'验收'});
  S.projects.push(project);
  await api('file.write',{id:project.id,path:'main.py',content:'name = input("你的名字：")\nprint(f"你好，{name}！这是实际 CPython 的输出。")\n'});
  await openProject(project.id);
  await runCode();
  const timer = setInterval(async function () {
    if (document.querySelector('#stdin-form.waiting')) {
      clearInterval(timer);
      document.querySelector('#stdin').value = '小明';
      await sendInput();
    }
  }, 80);
})();
