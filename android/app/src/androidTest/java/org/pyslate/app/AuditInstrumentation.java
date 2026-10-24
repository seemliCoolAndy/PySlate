package org.pyslate.app;

import android.app.Instrumentation;
import android.content.Context;
import android.content.ContextWrapper;
import android.os.Bundle;
import android.os.SystemClock;
import android.util.Base64;
import org.json.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.*;
import java.util.zip.*;

/** Regression checks against real Android filesystem and service, using an isolated test library. */
public final class AuditInstrumentation extends Instrumentation {
    private ProjectStore store;private RunManager runner;private File testRoot,metadata;private String id;private final JSONArray checks=new JSONArray();
    interface Operation {void run()throws Exception;}
    @Override public void onCreate(Bundle arguments){super.onCreate(arguments);start();}
    @Override public void onStart(){new Thread(()->{
        boolean allPass=false;
        try {
            testRoot=new File(getTargetContext().getFilesDir(),"audit-v030-"+UUID.randomUUID());testRoot.mkdirs();
            Context isolated=new ContextWrapper(getTargetContext()){@Override public File getFilesDir(){return testRoot;}};
            store=new ProjectStore(isolated);metadata=new File(testRoot,"pyslate/library.json");runner=new RunManager(getTargetContext());
            id=call("project.create",new JSONObject().put("name","课程综合项目").put("category","练习集").put("color","#123456").put("practice",true)).getJSONObject("project").getString("id");
            String original=project().toString();
            reject("invalid_update_keeps_memory",()->call("project.update",new JSONObject().put("id",id).put("color","#FFFFFF").put("name","")));
            record("invalid_update_fields_unchanged",project().toString().equals(original),project().toString());
            JSONObject copy=call("project.duplicate",new JSONObject().put("id",id)).getJSONObject("project");
            record("duplicate_preserves_attributes",copy.getString("category").equals("练习集")&&copy.getString("color").equals("#123456")&&copy.getBoolean("practice"),copy.toString());
            record("duplicate_preserves_code",read(copy.getString("id"),"main.py").equals(read(id,"main.py")),"");
            String before=read(id,"main.py");
            reject("create_existing_rejected",()->call("file.create",new JSONObject().put("id",id).put("path","main.py").put("content","LOST")));
            reject("create_case_alias_rejected",()->call("file.create",new JSONObject().put("id",id).put("path","MAIN.py").put("content","LOST")));
            reject("create_dot_alias_rejected",()->call("file.create",new JSONObject().put("id",id).put("path","./main.py").put("content","LOST")));
            record("existing_code_survives_create_attempts",read(id,"main.py").equals(before),"");
            call("file.create",new JSONObject().put("id",id).put("path","package/util.py").put("content","answer = 42\n"));
            record("create_nested_file",read(id,"package/util.py").equals("answer = 42\n"),"");
            reject("windows_reserved_path_rejected",()->call("file.create",new JSONObject().put("id",id).put("path","CON.py")));
            reject("windows_trailing_dot_rejected",()->call("file.create",new JSONObject().put("id",id).put("path","invalid./main.py")));
            reject("case_alias_directory_rejected",()->call("file.create",new JSONObject().put("id",id).put("path","Package/other.py")));
            byte[] normalZip=zip(new String[]{"main.py","data/input.txt"},false);
            JSONObject imported=call("project.import",new JSONObject().put("filename","正常导入.zip").put("base64",encode(normalZip))).getJSONObject("project");
            record("normal_zip_import",read(imported.getString("id"),"data/input.txt").contains("42")&&imported.getString("color").equals("#a1c9b8"),"Imported project keeps a valid CSS cover color");
            byte[] emptyZip=zip(new String[]{"folder/"},true);
            reject("directory_only_zip_rejected",()->call("project.import",new JSONObject().put("filename","空目录.zip").put("base64",encode(emptyZip))));
            byte[] aliasZip=zip(new String[]{"Main.py","main.py"},false);
            reject("case_colliding_zip_rejected",()->call("project.import",new JSONObject().put("filename","别名.zip").put("base64",encode(aliasZip))));
            byte[] pathZip=zip(new String[]{"main.py","../escape.py"},false);
            reject("partial_zip_cleanup",()->call("project.import",new JSONObject().put("filename","越界.zip").put("base64",encode(pathZip))));
            record("rejected_imports_not_published",catalog().getJSONArray("projects").length()==3&&new File(testRoot,"pyslate/projects").list().length==3,"");
            call("state.patch",new JSONObject().put("patch",new JSONObject().put("lessonSources",new JSONObject().put("l29:advanced","solution")).put("practiceIds",new JSONObject().put("l29:advanced:solution",id))));
            JSONObject restoredSource=new ProjectStore(isolated).call(new JSONObject().put("action","bootstrap")).getJSONObject("state");
            record("solution_source_and_practice_key_survive_restart",restoredSource.getJSONObject("lessonSources").getString("l29:advanced").equals("solution")&&restoredSource.getJSONObject("practiceIds").getString("l29:advanced:solution").equals(id),"");
            failedSave("state_patch_rollback",()->call("state.patch",new JSONObject().put("patch",new JSONObject().put("theme","dark"))));
            failedSave("category_create_rollback",()->call("category.create",new JSONObject().put("name","未持久化分类")));
            failedSave("project_update_rollback",()->call("project.update",new JSONObject().put("id",id).put("name","不应保留").put("category","不应新增")));
            failedSave("project_create_rollback",()->call("project.create",new JSONObject().put("name","不应留目录").put("category","不应新增")));
            failedSave("project_duplicate_rollback",()->call("project.duplicate",new JSONObject().put("id",id)));
            failedSave("project_import_rollback",()->call("project.import",new JSONObject().put("filename","不应发布.zip").put("base64",encode(normalZip))));
            failedSave("project_delete_restores_files",()->call("project.delete",new JSONObject().put("id",id)));
            record("failed_delete_code_restored",read(id,"main.py").equals(before),"");
            failedSave("new_file_save_rollback",()->call("file.create",new JSONObject().put("id",id).put("path","not-published.py").put("content","print(1)")));
            record("failed_file_create_removed",!new File(store.directory(id),"not-published.py").exists(),"");
            failedSave("file_write_rollback",()->call("file.write",new JSONObject().put("id",id).put("path","main.py").put("content","not committed")));
            record("failed_file_write_restores_code",read(id,"main.py").equals(before),"");
            failedSave("file_rename_rollback",()->call("file.rename",new JSONObject().put("id",id).put("path","main.py").put("newPath","renamed.py")));
            record("failed_file_rename_restores_path",read(id,"main.py").equals(before)&&!new File(store.directory(id),"renamed.py").exists(),"");
            failedSave("file_delete_rollback",()->call("file.delete",new JSONObject().put("id",id).put("path","main.py")));
            record("failed_file_delete_restores_code",read(id,"main.py").equals(before),"");
            record("failed_operations_leave_no_orphan_projects",new File(testRoot,"pyslate/projects").list().length==3,Arrays.toString(new File(testRoot,"pyslate/projects").list()));
            record("reload_matches_live_catalog",new ProjectStore(isolated).call(new JSONObject().put("action","bootstrap")).toString().equals(catalog().toString()),"");
            for(int n=0;n<105;n++)call("file.write",new JSONObject().put("id",id).put("path","history-check.txt").put("content","revision "+n));
            File[] versions=new File(testRoot,"pyslate/history/"+id).listFiles();
            record("history_is_bounded_without_losing_current_file",versions!=null&&versions.length==100&&read(id,"history-check.txt").equals("revision 104"),"Kept versions="+(versions==null?0:versions.length));
            call("file.write",new JSONObject().put("id",id).put("path","lesson..py").put("content","print('有效文件名')\n"));
            runCheck("two_dots_inside_filename","lesson..py","有效文件名");
            call("file.write",new JSONObject().put("id",id).put("path","main.py").put("content","print('重新运行成功')\n"));
            for(int n=0;n<5;n++){
                String runId=runner.start(store.directory(id),"main.py").getString("runId");SystemClock.sleep(n%2==0?30:370);
                runner.call(new JSONObject().put("action","stop").put("runId",runId));
                runCheck("rapid_stop_restart_"+n,"main.py","重新运行成功");
            }
            allPass=true;for(int i=0;i<checks.length();i++)if(!checks.getJSONObject(i).getBoolean("pass"))allPass=false;
        }catch(Throwable error){try{record("fatal",false,error.toString());}catch(Exception ignored){}}
        finally {
            if(runner!=null)runner.close();JSONObject report=new JSONObject();
            try{report.put("version","0.3.0").put("device",android.os.Build.MODEL).put("api",android.os.Build.VERSION.SDK_INT).put("isolatedData",testRoot==null?"":testRoot.getPath()).put("results",checks).put("allPass",allPass);Files.write(new File(getTargetContext().getFilesDir(),"android-v030-audit.json").toPath(),report.toString(2).getBytes(StandardCharsets.UTF_8));}catch(Exception ignored){}
            Bundle out=new Bundle();out.putString("stream",report.toString());finish(allPass?-1:0,out);
        }
    },"PySlate-Audit").start();}
    private JSONObject call(String action,JSONObject data)throws Exception{return store.call(data.put("action",action));}
    private JSONObject catalog()throws Exception{return call("bootstrap",new JSONObject());}
    private JSONObject project()throws Exception{JSONArray projects=catalog().getJSONArray("projects");for(int i=0;i<projects.length();i++)if(projects.getJSONObject(i).getString("id").equals(id))return projects.getJSONObject(i);throw new IOException("Missing project");}
    private String read(String projectId,String path)throws Exception{return call("file.read",new JSONObject().put("id",projectId).put("path",path)).getString("content");}
    private void record(String name,boolean pass,String details)throws Exception{checks.put(new JSONObject().put("name",name).put("pass",pass).put("details",details));}
    private void reject(String name,Operation operation)throws Exception{boolean rejected=false;String reason="";try{operation.run();}catch(Exception error){rejected=true;reason=error.toString();}record(name,rejected,reason);}
    private void failedSave(String name,Operation operation)throws Exception {
        String before=catalog().toString();byte[] persisted=Files.readAllBytes(metadata.toPath());File original=new File(metadata.getParentFile(),"library-test-backup.json");
        Files.move(metadata.toPath(),original.toPath());metadata.mkdir();Files.write(new File(metadata,"occupied").toPath(),new byte[]{1});
        boolean rejected=false;String reason="";try{operation.run();}catch(Exception error){rejected=true;reason=error.toString();}
        finally{Files.delete(new File(metadata,"occupied").toPath());Files.delete(metadata.toPath());Files.move(original.toPath(),metadata.toPath());}
        record(name,rejected&&catalog().toString().equals(before)&&Arrays.equals(Files.readAllBytes(metadata.toPath()),persisted),reason);
    }
    private static String encode(byte[] bytes){return Base64.encodeToString(bytes,Base64.NO_WRAP);}
    private static byte[] zip(String[] paths,boolean directory)throws Exception{ByteArrayOutputStream bytes=new ByteArrayOutputStream();try(ZipOutputStream zip=new ZipOutputStream(bytes)){for(String path:paths){zip.putNextEntry(new ZipEntry(path));if(!directory)zip.write("print(42)\n".getBytes(StandardCharsets.UTF_8));zip.closeEntry();}}return bytes.toByteArray();}
    private void runCheck(String name,String entry,String expected)throws Exception {
        String runId=runner.start(store.directory(id),entry).getString("runId");long deadline=SystemClock.elapsedRealtime()+10000;StringBuilder text=new StringBuilder();int cursor=0,exit=-999;boolean running=true;
        while(running&&SystemClock.elapsedRealtime()<deadline){JSONObject snapshot=runner.call(new JSONObject().put("action","events").put("runId",runId).put("cursor",cursor));cursor=snapshot.getInt("cursor");JSONArray events=snapshot.getJSONArray("events");for(int i=0;i<events.length();i++){JSONObject event=events.getJSONObject(i);text.append(event.optString("text"));if(event.getString("type").equals("exit"))exit=event.getInt("code");}running=snapshot.getBoolean("running");SystemClock.sleep(30);}
        if(running)runner.call(new JSONObject().put("action","stop").put("runId",runId));record(name,!running&&exit==0&&text.toString().contains(expected),"exit="+exit+"; "+text);SystemClock.sleep(450);
    }
}
