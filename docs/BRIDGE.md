# PySlate 0.3 native bridge

Shared assets: `web/index.html`, `app.js`, `app.css`, `design.css`, `vendor.js`, `course-assets/`; course at `course/course.json`. Bundle assets without external requests.

JavaScript `api(action, data)` sends `{action, ...data}`. Android `window.PySlateNative.call(JSON.stringify(request))` returns JSON synchronously (short filesystem calls only). Windows POST relative `api` with JSON to token-scoped endpoint. Native errors: `{error: "human readable message"}`; frontend throws. All successful responses are JSON objects.

Actions:

* `bootstrap` → `{platform:"windows"|"android",version:"0.3.0",python:"3.x",state:{theme:"light",progress:{lessonId:true},drafts:{lessonId:code},lastLesson:"l01",split:0.5,trusted:false},projects:[{id,name,color,category,updated}],categories:["未分类"]}`. Empty library is legitimate; no fake user projects. Frontend separately GET `course/course.json` (Windows maps this URL) or Android assets `../course/course.json`. Native bootstrap MAY include `course` instead; preferred include `course` parsed JSON for both.
* `state.patch`, `{patch:{...topLevelStateFields}}` → `{ok:true}`. Atomic shallow merge top-level, UI sends full progress/drafts objects.
* `category.create`, `{name}` → `{categories:[...]}`.
* `project.create`, `{name,color,category}` → `{project}`. Actual project directory and starter `main.py`.
* `project.update`, `{id,name?,color?,category?}` → `{project}`.
* `project.duplicate`, `{id}` → `{project}`.
* `project.delete`, `{id}` → `{ok:true}`. Soft delete into trash.
* `project.files`, `{id}` → `{files:[{path,size}]}`. Normalized relative `/` paths, recurse files, no private metadata.
* `file.read`, `{id,path}` → `{content}` (UTF-8 text, reject too-large/binary).
* `file.create`, `{id,path,content}` → `{ok:true}`. Exclusive create: existing path or case alias is rejected. UI must use this for a new file; prechecking a displayed file list is insufficient.
* `file.write`, `{id,path,content}` → `{ok:true}`. Atomic write, retain recoverable prior version. Supports resources and subdirectories.
* `file.rename`, `{id,path,newPath}` → `{ok:true}`. No overwrite.
* `file.delete`, `{id,path}` → `{ok:true}`. Recoverable trash.
* `project.export`, `{id}` → `{filename,base64}` (ZIP, standard project files only).
* `project.import`, `{filename,base64}` → `{project}`. ZIP path/symlink/bomb/size checks, fresh project dir; do not overwrite existing.
* `run`, `{id,entry:"main.py"}` → `{runId}`. At most one active process; no UI-thread execution. Real interpreter with cwd=project directory, project import path. Cumulative execution budget 30s, paused during genuine stdin waits; each input wait has a separate 300s deadline. Output limit 256KiB; terminate entire process on limit.
* `events`, `{runId,cursor:0}` → `{events:[{seq:1,type:"stdout"|"stderr"|"input"|"input_end"|"exit",text:"...",code:0}],running:true,cursor:1,waiting:false,inputRequestId:null,stateRevision:1}`. Cursor is last seen seq; return only newer events. `input` includes an increasing integer `requestId`; `input_end` closes that request. The snapshot waiting/inputRequestId is authoritative at its stateRevision. Ignore snapshots older than an accepted input response; never re-enable a consumed request. Streams are real Python output. Exit occurs once, running=false.
* `input`, `{runId,requestId,text}` → `{ok:true,acceptedRequestId,waiting,inputRequestId,stateRevision}`. Empty text submits a valid blank line. Native adds one newline; embedded newlines, stale IDs and repeated IDs are rejected. EOF optional `{eof:true,requestId}`. Only enable the UI input for a current waiting request, disable while submitting, and do not submit during IME composition. Windows retains its older no-ID low-level compatibility path; current UI always sends the ID.
* `stop`, `{runId}` → `{ok:true}`. Kill worker/subprocess, emit exit with code!=0.

Learning execution uses a regular hidden practice project, `project.create` with name `课程练习`, category `练习`, optional `practice:true`. Keep it out of visible library when project.practice true. Write selected lesson draft to `main.py`, execute via same service. Drafts, progress and practiceIds persist per learning unit: beginner keeps the v1 topic key, intermediate/advanced use `topicId:level`. `state.lessonTiers` stores the selected level per topic. Preserve all existing keys on upgrades.

UI limits: max source text 1MiB, max ZIP compressed 20MiB. Native must independently enforce limits and prevent traversal and symlink escapes. Windows is **not a security sandbox**; UI requires affirmative trust acceptance before first execution, persistent state.trusted only after explicit user interaction. Android normal separate process same app UID is not full isolation; no INTERNET/storage permissions, app-private data only; never claim adversarial code is sandboxed.

Android WebView file chooser supports ZIP input, download via `PySlateNative.saveFile(filename,base64)` which opens ACTION_CREATE_DOCUMENT; Windows Blob download via WebView2 download UI. Shared optional `PySlateNative.openExternal(url)` only official HTTPS links after user clicks; external navigation otherwise blocked. No network used at application runtime.

0.3 state writes are applied in the UI only after successful native persistence. Completion actions are ordered. Native storage restores metadata and preserves the previous filesystem state if catalog persistence fails. File create never uses the overwrite endpoint. UI temporarily locks the editor during create/rename/delete submission so autosave cannot recreate an old path. A successful stop makes its run terminal; delayed event snapshots cannot revive it.

Multi-file learning UI uses `files["main.py"]` / `solutionFiles["main.py"]` where present, otherwise `code` / `solution`. `state.lessonSources[unitKey]` records `example` or `solution`, independently of the draft text. Supporting files are prepared from the selected file set. Example practice uses the existing unit key; solution practice uses `unitKey + ":solution"`, preserving previous practice IDs and separating auxiliary modules. Existing legacy wrapper drafts remain executable.
