package org.pyslate.app;

import android.app.Instrumentation;
import android.os.Bundle;
import android.os.SystemClock;
import org.json.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.*;

/** Executes packaged course examples and answers on actual Android CPython. */
public class CourseInstrumentation extends Instrumentation {
    private ProjectStore store;private RunManager manager;private final JSONArray results=new JSONArray();private String filter="",courseSha256="";private int schemaVersion=1,unitsTested=0,topicsTested=0;
    @Override public void onCreate(Bundle args){filter=args==null?"":args.getString("lesson","");android.util.Log.i("PySlateCourse","onCreate");super.onCreate(args);start();}
    @Override public void onStart(){new Thread(()->{int failed=0;try{
        android.util.Log.i("PySlateCourse","starting");store=new ProjectStore(getTargetContext());manager=new RunManager(getTargetContext());
        String text;try(InputStream stream=getTargetContext().getAssets().open("course/course.json")){ByteArrayOutputStream bytes=new ByteArrayOutputStream();byte[] buf=new byte[16384];int n;while((n=stream.read(buf))>=0)bytes.write(buf,0,n);text=bytes.toString("UTF-8");}
        byte[] digest=java.security.MessageDigest.getInstance("SHA-256").digest(text.getBytes(StandardCharsets.UTF_8));StringBuilder hash=new StringBuilder();for(byte b:digest)hash.append(String.format("%02x",b&255));courseSha256=hash.toString();
        JSONObject course=new JSONObject(text);schemaVersion=course.optInt("version",1);android.util.Log.i("PySlateCourse","course loaded "+text.length());JSONArray chapters=course.getJSONArray("chapters");
        for(int c=0;c<chapters.length();c++){JSONArray lessons=chapters.getJSONObject(c).getJSONArray("lessons");for(int l=0;l<lessons.length();l++){
            JSONObject lesson=lessons.getJSONObject(l);
            String topicId=lesson.getString("id");if(!filter.isEmpty()&&!filter.equals(topicId)&&!filter.startsWith(topicId+":"))continue;topicsTested++;
            JSONArray tiers=lesson.optJSONArray("tiers");
            if(schemaVersion>=2&&tiers!=null){
                for(int tierAt=0;tierAt<tiers.length();tierAt++){
                    JSONObject tier=tiers.getJSONObject(tierAt);String unitId=tier.optString("unitId",topicId+":"+tier.getString("id"));if(filter.contains(":" )&&!filter.equals(unitId))continue;
                    JSONObject unit=new JSONObject(lesson.toString());unit.remove("tiers");for(Iterator<String> keys=tier.keys();keys.hasNext();){String key=keys.next();unit.put(key,tier.get(key));}unit.put("id",unitId).put("topicId",topicId).put("tierId",tier.getString("id"));unitsTested++;
                    JSONArray cases=unit.getJSONArray("testCases");if(cases.length()<2)throw new IOException("每个难度单元必须包含完整example/answer用例");for(int i=0;i<cases.length();i++){JSONObject test=cases.getJSONObject(i);execute(unit,test.optString("field","code"),test.optString("stdin",unit.optString("stdin")),test.getString("expectedOutput"),test.getString("name"),test);}
                }
            }else{
                unitsTested++;execute(lesson,"code",lesson.optString("stdin"),lesson.getString("expectedOutput"),"example");
                execute(lesson,"solution",lesson.optString("stdin"),lesson.getString("solutionExpectedOutput"),"answer");
                JSONArray cases=lesson.optJSONArray("testCases");if(cases!=null)for(int i=0;i<cases.length();i++){JSONObject test=cases.getJSONObject(i);execute(lesson,test.optString("field","code"),test.optString("stdin"),test.getString("expectedOutput"),test.getString("name"),test);}
            }
        }}
        for(int i=0;i<results.length();i++)if(!results.getJSONObject(i).getBoolean("pass"))failed++;
    }catch(Throwable error){failed++;try{results.put(new JSONObject().put("id","fatal").put("pass",false).put("error",error.toString()));}catch(Exception ignored){}}
    finally{if(manager!=null)manager.close();JSONObject report=new JSONObject();try{int executions=results.length();for(int i=0;i<results.length();i++)if(results.getJSONObject(i).has("followup"))executions++;report.put("complete",true).put("schemaVersion",schemaVersion).put("sourceCourseSha256",courseSha256).put("topicsTested",topicsTested).put("unitsTested",unitsTested).put("lessonFilter",filter).put("executedPrograms",executions).put("platform","android").put("api",android.os.Build.VERSION.SDK_INT).put("device",android.os.Build.MODEL).put("tests",results.length()).put("failed",failed).put("results",results);Files.write(new File(getTargetContext().getFilesDir(),"android-course.json").toPath(),report.toString(2).getBytes(StandardCharsets.UTF_8));}catch(Exception ignored){}Bundle output=new Bundle();output.putString("stream","Android course cases="+results.length()+", failed="+failed);finish(failed==0?-1:0,output);}},"PySlate-Course-Validation").start();}
    private JSONObject call(String action,JSONObject data)throws Exception{data.put("action",action);return store.call(data);}
    private void write(String id,String path,String content)throws Exception{call("file.write",new JSONObject().put("id",id).put("path",path).put("content",content));}
    private void execute(JSONObject lesson,String field,String stdin,String expected,String name)throws Exception{
        execute(lesson,field,stdin,expected,name,new JSONObject());
    }
    private void execute(JSONObject lesson,String field,String stdin,String expected,String name,JSONObject test)throws Exception{
        String id=call("project.create",new JSONObject().put("name","课程验收 "+lesson.getString("id")).put("practice",true)).getJSONObject("project").getString("id");
        JSONObject result;boolean pass=false;
        try{
        JSONObject files=lesson.optJSONObject(test.optString("fileSet",field.equals("solution")?"solutionFiles":"files"));
        if(files!=null)for(Iterator<String> iterator=files.keys();iterator.hasNext();){String path=iterator.next();write(id,path,files.getString(path));}
        JSONObject initial=test.optJSONObject("initialFiles");if(initial!=null)for(Iterator<String> iterator=initial.keys();iterator.hasNext();){String path=iterator.next();write(id,path,initial.getString(path));}
        String code=test.has("fileSet")?files.getString("main.py"):lesson.getString(field);JSONArray replacements=test.optJSONArray("replacements");if(replacements!=null)for(int i=0;i<replacements.length();i++){JSONObject replacement=replacements.getJSONObject(i);String find=replacement.getString("find");if(find.isEmpty()||!code.contains(find))throw new IOException("测试replacements找不到原文："+find);code=code.replace(find,replacement.getString("replace"));}if(test.has("assertions"))code+="\n"+test.getString("assertions")+"\n";
        write(id,"main.py",code);
        result=runOne(id,stdin);pass=result.getInt("exit")==0&&normalize(result.getString("stdout")).equals(normalize(expected));
        JSONObject expectedFiles=test.optJSONObject("expectedFiles");if(expectedFiles!=null)for(Iterator<String> iterator=expectedFiles.keys();iterator.hasNext();){String path=iterator.next();String content=call("file.read",new JSONObject().put("id",id).put("path",path)).getString("content");if(!content.equals(expectedFiles.getString(path)))pass=false;}
        if(test.has("followupStdin")){SystemClock.sleep(220);JSONObject followup=runOne(id,test.getString("followupStdin"));result.put("followup",followup);if(followup.getInt("exit")!=0||!normalize(followup.getString("stdout")).equals(normalize(test.getString("followupExpectedOutput"))))pass=false;}
        }catch(Exception error){result=new JSONObject().put("exit",-999).put("error",error.toString());}
        result.put("id",lesson.getString("id")).put("case",name).put("field",field).put("pass",pass);
        if(lesson.has("topicId"))result.put("topicId",lesson.getString("topicId")).put("tierId",lesson.getString("tierId"));
        if(!pass)result.put("expected",expected);else {result.remove("stdout");result.remove("stderr");}results.put(result);
        Bundle progress=new Bundle();progress.putString("stream",lesson.getString("id")+" "+name+" "+(pass?"PASS":"FAIL")+"\n");sendStatus(0,progress);
        JSONObject partial=new JSONObject().put("complete",false).put("tests",results.length()).put("results",results);Files.write(new File(getTargetContext().getFilesDir(),"android-course.json").toPath(),partial.toString(2).getBytes(StandardCharsets.UTF_8));
        call("project.delete",new JSONObject().put("id",id));SystemClock.sleep(220);
    }
    private static String normalize(String value){return value.replace("\r\n","\n");}
    private JSONObject runOne(String id,String stdin)throws Exception{
        String runId=manager.start(store.directory(id),"main.py").getString("runId");
        ArrayList<String> inputs=new ArrayList<>(Arrays.asList(stdin.split("\n",-1)));if(stdin.endsWith("\n")||stdin.isEmpty())inputs.remove(inputs.size()-1);
        int inputAt=0,cursor=0,exit=-999;boolean running=true;long started=SystemClock.elapsedRealtime();StringBuilder out=new StringBuilder(),err=new StringBuilder();
        while(running&&SystemClock.elapsedRealtime()-started<35000){JSONObject data=manager.call(new JSONObject().put("action","events").put("runId",runId).put("cursor",cursor));cursor=data.getInt("cursor");JSONArray events=data.getJSONArray("events");
            for(int i=0;i<events.length();i++){JSONObject event=events.getJSONObject(i);switch(event.getString("type")){
                case "stdout":out.append(event.optString("text"));break;
                case "stderr":err.append(event.optString("text"));break;
                case "input":JSONObject input=new JSONObject().put("action","input").put("runId",runId).put("requestId",event.getInt("requestId"));if(inputAt<inputs.size())input.put("text",inputs.get(inputAt++));else input.put("eof",true);manager.call(input);break;
                case "exit":exit=event.getInt("code");break;
            }}running=data.getBoolean("running");SystemClock.sleep(15);
        }
        return new JSONObject().put("exit",exit).put("elapsedMs",SystemClock.elapsedRealtime()-started).put("stdout",out.toString()).put("stderr",err.toString());
    }
}
