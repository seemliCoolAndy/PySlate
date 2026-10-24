package org.pyslate.app;

import android.app.Instrumentation;
import android.os.Bundle;
import android.os.SystemClock;
import org.json.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.*;
import java.util.zip.*;
import android.util.Base64;

/** Device-side checks using the actual bound service and embedded interpreter, no mock output. */
public final class SmokeInstrumentation extends Instrumentation {
    private ProjectStore store;private RunManager manager;private String id;private JSONArray results=new JSONArray();
    @Override public void onCreate(Bundle args){super.onCreate(args);start();}
    @Override public void onStart(){new Thread(()->{int status=0;try{
        store=new ProjectStore(getTargetContext());manager=new RunManager(getTargetContext());
        id=call("project.create",new JSONObject().put("name","设备验收测试").put("practice",true)).getJSONObject("project").getString("id");
        write("helper.py","def twice(n):\n    return n * 2\n");
        check("print_input_import_files", "from helper import twice\nfrom pathlib import Path\nname = input('名字：')\nPath('result.txt').write_text(name, encoding='utf-8')\nprint('你好', name, twice(21))\n",true,"你好 测试同学 42",0,false);
        String file=new String(Files.readAllBytes(new File(store.directory(id),"result.txt").toPath()),StandardCharsets.UTF_8);
        record("file_persistence",file.equals("测试同学"),file);
        check("syntax_traceback","if True print('bad')\n",false,"SyntaxError",1,false);
        check("loop_function","def total(n):\n    return sum(i for i in range(n))\nprint(total(10))\n",false,"45",0,false);
        check("user_stop","while True:\n    pass\n",false,"程序已停止",130,true);
        check("output_limit","while True:\n    print('x' * 16384)\n",false,"256KiB",137,false);
        check("event_limit","import sys\nfor i in range(10000):\n    sys.stdin.bridge.emit('input', '')\n",false,"4096",137,false);
        check("timeout","while True:\n    pass\n",false,"30秒",124,false);
        JSONObject exported=call("project.export",new JSONObject().put("id",id));
        JSONObject imported=call("project.import",new JSONObject().put("filename","交换测试.zip").put("base64",exported.getString("base64"))).getJSONObject("project");
        String content=call("file.read",new JSONObject().put("id",imported.getString("id")).put("path","helper.py")).getString("content");
        record("zip_roundtrip",content.contains("twice"),content);
        call("project.delete",new JSONObject().put("id",imported.getString("id")));
        boolean traversal=false;try{call("file.read",new JSONObject().put("id",id).put("path","../library.json"));}catch(Exception e){traversal=true;}
        record("path_traversal_rejected",traversal,"");
        rejectedZip("zip_path_traversal_rejected",zip("../escape.py"));
        byte[] symlink=zip("shortcut.py");
        for(int at=0;at+46<symlink.length;at++)if(symlink[at]=='P'&&symlink[at+1]=='K'&&symlink[at+2]==1&&symlink[at+3]==2){symlink[at+40]=(byte)0xFF;symlink[at+41]=(byte)0xA1;break;}
        rejectedZip("zip_symlink_rejected",symlink);
        JSONObject patch=new JSONObject().put("progress",new JSONObject().put("android_smoke",true)).put("drafts",new JSONObject().put("android_smoke","print(42)"));
        call("state.patch",new JSONObject().put("patch",patch));
        JSONObject restored=new ProjectStore(getTargetContext()).call(new JSONObject().put("action","bootstrap"));
        record("state_reload",restored.getJSONObject("state").getJSONObject("progress").getBoolean("android_smoke"),"");
        call("project.delete",new JSONObject().put("id",id));
        for(int i=0;i<results.length();i++)if(!results.getJSONObject(i).getBoolean("pass"))status=1;
    }catch(Throwable error){try{record("fatal",false,error.toString());}catch(Exception ignored){}status=1;}finally{
        if(manager!=null)manager.close();
        JSONObject report=new JSONObject();try{report.put("device",android.os.Build.MODEL).put("api",android.os.Build.VERSION.SDK_INT).put("python","3.14").put("results",results);Files.write(new File(getTargetContext().getFilesDir(),"android-smoke.json").toPath(),report.toString(2).getBytes(StandardCharsets.UTF_8));}catch(Exception ignored){}
        Bundle result=new Bundle();result.putString("stream",report.toString());finish(status==0?-1:0,result);
    }},"PySlate-Smoke").start();}
    private JSONObject call(String action,JSONObject data)throws Exception{data.put("action",action);return store.call(data);}
    private void write(String path,String content)throws Exception{call("file.write",new JSONObject().put("id",id).put("path",path).put("content",content));}
    private void record(String name,boolean pass,String details)throws Exception{results.put(new JSONObject().put("name",name).put("pass",pass).put("details",details));}
    private byte[] zip(String name)throws Exception{ByteArrayOutputStream out=new ByteArrayOutputStream();try(ZipOutputStream zip=new ZipOutputStream(out)){zip.putNextEntry(new ZipEntry(name));zip.write("print(42)\n".getBytes(StandardCharsets.UTF_8));zip.closeEntry();}return out.toByteArray();}
    private void rejectedZip(String name,byte[] bytes)throws Exception{boolean rejected=false;String reason="";try{call("project.import",new JSONObject().put("filename","rejected.zip").put("base64",Base64.encodeToString(bytes,Base64.NO_WRAP)));}catch(Exception e){rejected=true;reason=e.getMessage();}record(name,rejected,reason);}
    private void check(String name,String code,boolean sendInput,String expected,int exitCode,boolean stop)throws Exception{
        write("main.py",code);String runId=manager.start(store.directory(id),"main.py").getString("runId");long start=SystemClock.elapsedRealtime();int cursor=0,exit=-999;StringBuilder output=new StringBuilder();boolean sent=false,stopped=false;boolean running=true;
        while(running&&SystemClock.elapsedRealtime()-start<38000){JSONObject data=manager.call(new JSONObject().put("action","events").put("runId",runId).put("cursor",cursor));cursor=data.getInt("cursor");JSONArray events=data.getJSONArray("events");
            for(int i=0;i<events.length();i++){JSONObject event=events.getJSONObject(i);String type=event.getString("type");if(type.equals("input")&&sendInput&&!sent){manager.call(new JSONObject().put("action","input").put("runId",runId).put("requestId",event.getInt("requestId")).put("text","测试同学"));sent=true;}if(type.equals("exit"))exit=event.getInt("code");else if(!type.equals("input"))output.append(event.optString("text"));}
            if(stop&&!stopped&&SystemClock.elapsedRealtime()-start>1500){manager.call(new JSONObject().put("action","stop").put("runId",runId));stopped=true;}
            running=data.getBoolean("running");SystemClock.sleep(40);
        }
        String text=output.toString();record(name,!running&&exit==exitCode&&text.contains(expected),"exit="+exit+"; tail="+text.substring(Math.max(0,text.length()-700)));SystemClock.sleep(450);
    }
}
