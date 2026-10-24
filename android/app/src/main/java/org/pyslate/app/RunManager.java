package org.pyslate.app;

import android.content.*;
import android.os.*;
import org.json.*;
import java.io.*;
import java.util.*;

public final class RunManager {
    private final Context context;
    private final Handler main=new Handler(Looper.getMainLooper());
    private final LinkedHashMap<String,Run> runs=new LinkedHashMap<>();
    private final long executionTimeoutMs,inputTimeoutMs;
    private Run active;
    private static final class Run {
        String id,folder,entry; boolean running=true,bound=false; int pid=0,seq=0; Messenger worker;
        boolean waiting,inputSubmitted;int inputRequestId;long activeSince,activeElapsed,waitingSince,stateRevision;
        final ArrayList<JSONObject> events=new ArrayList<>(); ServiceConnection connection;
    }
    public RunManager(Context context) {this(context,30000,300000);}
    /** Package-private budgets make timeout tests fast; the app always uses 30s/5min. */
    RunManager(Context context,long executionTimeoutMs,long inputTimeoutMs) {
        if(executionTimeoutMs<=0||inputTimeoutMs<=0)throw new IllegalArgumentException("超时必须为正数");
        this.context=context;this.executionTimeoutMs=executionTimeoutMs;this.inputTimeoutMs=inputTimeoutMs;
    }
    private synchronized void event(Run r,String type,String text,int code) {
        event(r,type,text,code,0);
    }
    private synchronized void event(Run r,String type,String text,int code,int requestId) {
        if(!r.running)return;
        r.stateRevision++;
        if(r.events.size()>=4096&&!type.equals("exit")) {
            try {
                r.events.add(new JSONObject().put("seq",++r.seq).put("type","stderr").put("text","运行事件达到4096项限制，程序已停止\n").put("code",0));
                r.events.add(new JSONObject().put("seq",++r.seq).put("type","exit").put("text","").put("code",137));
            }catch(JSONException ignored){}
            r.running=false;if(r.pid>0)android.os.Process.killProcess(r.pid);main.post(()->unbind(r));return;
        }
        long now=SystemClock.elapsedRealtime();
        if(type.equals("input")&&requestId>0) {
            if(!r.waiting)r.activeElapsed+=now-r.activeSince;
            r.waiting=true;r.inputSubmitted=false;r.inputRequestId=requestId;r.waitingSince=now;
        }else if(type.equals("input_end")&&r.waiting&&requestId==r.inputRequestId) {
            r.waiting=false;r.inputSubmitted=false;r.activeSince=now;
        }else if(type.equals("input_error")&&r.waiting&&requestId==r.inputRequestId)r.inputSubmitted=false;
        try {JSONObject item=new JSONObject().put("seq",++r.seq).put("type",type).put("text",text).put("code",code);if(requestId>0)item.put("requestId",requestId);r.events.add(item);}catch(JSONException ignored){}
        if(type.equals("exit")) {r.running=false;r.waiting=false;main.post(()->unbind(r));}
    }
    private void unbind(Run r) {if(r.bound) {try{context.unbindService(r.connection);}catch(Exception ignored){}r.bound=false;}}
    private synchronized void terminate(Run r,int code,String reason) {
        if(!r.running)return;
        if(!reason.isEmpty())event(r,"stderr",reason,0);
        if(r.pid>0)android.os.Process.killProcess(r.pid);
        else if(r.worker!=null)try{r.worker.send(Message.obtain(null,RunnerService.STOP));}catch(Exception ignored){}
        event(r,"exit","",code);
    }
    public synchronized JSONObject start(File directory,String entry) throws Exception {
        if(active!=null&&active.running)throw new IOException("已有程序正在运行");
        if(entry.isEmpty()||entry.startsWith("/")||entry.contains("\\"))throw new IOException("入口路径无效");
        for(String part:entry.split("/",-1))if(part.isEmpty()||part.equals(".")||part.equals(".."))throw new IOException("入口路径无效");
        File file=new File(directory,entry).getCanonicalFile();if(!file.getPath().startsWith(directory.getCanonicalPath()+File.separator)||!file.isFile())throw new IOException("入口文件不存在");
        Run r=new Run();r.id=UUID.randomUUID().toString();r.folder=directory.getCanonicalPath();r.entry=entry;r.activeSince=SystemClock.elapsedRealtime();runs.put(r.id,r);active=r;
        while(runs.size()>8)runs.remove(runs.keySet().iterator().next());
        final Messenger receiver=new Messenger(new Handler(Looper.getMainLooper(),message->{
            Bundle b=message.getData();
            if(message.what==RunnerService.READY) {r.pid=b.getInt("code");if(!r.running)android.os.Process.killProcess(r.pid);}
            else if(message.what==RunnerService.EVENT)event(r,b.getString("type","stderr"),b.getString("text",""),b.getInt("code"),b.getInt("requestId"));
            return true;
        }));
        r.connection=new ServiceConnection() {
            @Override public void onServiceConnected(ComponentName name,IBinder binder) {
                r.worker=new Messenger(binder);Message start=Message.obtain(null,RunnerService.START);start.replyTo=receiver;Bundle b=new Bundle();b.putString("folder",r.folder);b.putString("entry",r.entry);start.setData(b);
                try {r.worker.send(start);}catch(Exception e){terminate(r,1,"Python进程启动失败\n");}
            }
            @Override public void onServiceDisconnected(ComponentName name) {event(r,"exit","Python进程已退出",1);}
            @Override public void onBindingDied(ComponentName name) {event(r,"exit","Python进程连接中断",1);}
        };
        main.postDelayed(()->{if(!r.running)return;r.bound=context.bindService(new Intent(context,RunnerService.class),r.connection,Context.BIND_AUTO_CREATE);if(!r.bound)terminate(r,1,"无法启动运行服务\n");},350);
        main.postDelayed(()->watchdog(r),100);
        return new JSONObject().put("runId",r.id);
    }
    private synchronized void watchdog(Run r) {
        if(!r.running)return;
        long now=SystemClock.elapsedRealtime();
        if(r.waiting&&now-r.waitingSince>=inputTimeoutMs)terminate(r,124,inputTimeoutMs==300000?"等待输入超过5分钟，程序已停止；请重新运行\n":"等待输入超时，程序已停止；请重新运行\n");
        else if(!r.waiting&&r.activeElapsed+now-r.activeSince>=executionTimeoutMs)terminate(r,124,executionTimeoutMs==30000?"累计执行超过30秒（等待输入不计时），程序已停止\n":"累计执行超时（等待输入不计时），程序已停止\n");
        if(r.running)main.postDelayed(()->watchdog(r),100);
    }
    private Run get(String id) throws IOException {Run r=runs.get(id);if(r==null)throw new IOException("运行记录不存在");return r;}
    public synchronized JSONObject call(JSONObject req) throws Exception {
        Run r=get(req.getString("runId"));switch(req.getString("action")) {
            case "events": {JSONArray events=new JSONArray();int cursor=req.optInt("cursor");for(JSONObject e:r.events)if(e.getInt("seq")>cursor)events.put(e);boolean waiting=r.running&&r.waiting&&!r.inputSubmitted;return new JSONObject().put("events",events).put("running",r.running).put("cursor",r.seq).put("waiting",waiting).put("inputRequestId",waiting?r.inputRequestId:JSONObject.NULL).put("stateRevision",r.stateRevision);}
            case "stop":terminate(r,130,"程序已停止\n");return new JSONObject().put("ok",true);
            case "input": {
                if(!r.running)throw new IOException("程序已经结束");
                if(!r.waiting||r.inputSubmitted)throw new IOException("程序目前没有待提交的输入请求");
                if(req.optInt("requestId",-1)!=r.inputRequestId)throw new IOException("输入请求已更新，请按当前提示重新输入");
                String text=req.optString("text");
                if(text.getBytes(java.nio.charset.StandardCharsets.UTF_8).length>65536)throw new IOException("单行输入超过64KiB限制");
                if(text.indexOf('\n')>=0||text.indexOf('\r')>=0)throw new IOException("请一次提交一行输入");
                Message input=Message.obtain(null,RunnerService.INPUT);Bundle data=new Bundle();data.putString("text",text);data.putBoolean("eof",req.optBoolean("eof"));data.putInt("requestId",r.inputRequestId);input.setData(data);
                r.worker.send(input);r.inputSubmitted=true;r.stateRevision++;return new JSONObject().put("ok",true).put("requestId",r.inputRequestId).put("stateRevision",r.stateRevision);
            }
            default:throw new IOException("未知运行操作");
        }
    }
    public synchronized void close() {if(active!=null)terminate(active,130,"");}
    public synchronized boolean isRunning(File directory) throws IOException {return active!=null&&active.running&&active.folder.equals(directory.getCanonicalPath());}
}
