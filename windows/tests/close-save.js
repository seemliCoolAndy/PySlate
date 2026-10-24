(async function () {
  const created = await api('project.create', {name:'关闭保存验收', color:'#3c6955', category:'验收'});
  S.projects.push(created.project);
  await openProject(created.project.id);
  setTimeout(function () {
    S.editor.dispatch({changes:{from:0,to:S.editor.state.doc.length,insert:'# close-save acceptance\nprint("最后一次编辑已保存")\n'}});
    clearTimeout(S.timer); // Deliberately require the native close flush, not debounce.
  }, 500);
})();
