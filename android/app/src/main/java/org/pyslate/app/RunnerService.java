package org.pyslate.app;

import android.app.Service;
import android.content.Intent;
import android.os.*;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;

/** Disposable same-UID process. This is crash/termination isolation, not a hostile-code sandbox. */
public final class RunnerService extends Service {
    public static final int START=1, INPUT=2, STOP=3, EVENT=4, READY=5;
    private Messenger client;
    private final BlockingQueue<String> input=new LinkedBlockingQueue<>(1);
    private final Object inputReadLock=new Object();
    private final AtomicInteger requestCounter=new AtomicInteger(),waitingRequest=new AtomicInteger();
    private final AtomicBoolean inputSubmitted=new AtomicBoolean();
    private final AtomicInteger outputBytes=new AtomicInteger();
    private final AtomicBoolean ended=new AtomicBoolean();
    private final StringBuilder pending=new StringBuilder();
    private String pendingType="stdout";
    private boolean flushScheduled;
    private final Handler main=new Handler(Looper.getMainLooper());
    private final Messenger server=new Messenger(new Handler(Looper.getMainLooper(), message -> {
        switch(message.what) {
            case START:
                client=message.replyTo;
                send(READY,"ready","",android.os.Process.myPid());
                final String folder=message.getData().getString("folder"),entry=message.getData().getString("entry");
                Thread thread=new Thread(() -> {
                    try {
                        if(!Python.isStarted())Python.start(new AndroidPlatform(this));
                        Python.getInstance().getModule("pyslate_runner").callAttr("run",folder,entry,this);
                        finish(0,"");
                    } catch(Throwable error) {emit("stderr",error.toString()+"\n");finish(1,"");}
                },"PySlate-Python");thread.start();break;
            case INPUT: {
                Bundle data=message.getData();int requestId=data.getInt("requestId");
                if(requestId!=waitingRequest.get()||requestId<=0||!inputSubmitted.compareAndSet(false,true))send(EVENT,"input_error","这次输入请求已处理或过期，请按当前提示重试\n",0,requestId);
                else if(!input.offer(data.getBoolean("eof")?"\u0000EOF":data.getString("text","")+"\n")){inputSubmitted.set(false);send(EVENT,"input_error","输入队列忙，请重试\n",0,requestId);}
                break;
            }
            case STOP: finish(130,"程序已停止\n");break;
            default:return false;
        }
        return true;
    }));
    @Override public IBinder onBind(Intent intent) {return server.getBinder();}
    public synchronized void emit(String type,String text) {
        if(ended.get())return;
        if(outputBytes.addAndGet(text.getBytes(StandardCharsets.UTF_8).length)>256*1024) {finish(137,"输出达到256KiB限制，程序已停止\n");return;}
        if(type.equals("input")){flushOutput();send(EVENT,type,text,0);return;}
        if(!type.equals(pendingType))flushOutput();pendingType=type;pending.append(text);
        if(pending.length()>=8192)flushOutput();
        else if(!flushScheduled){flushScheduled=true;main.postDelayed(this::flushOutput,30);}
    }
    private synchronized void flushOutput() {
        flushScheduled=false;
        if(pending.length()==0)return;
        String text=pending.toString();pending.setLength(0);
        // Batch tiny writes so print loops cannot flood the UI Binder queue.
        for(int i=0;i<text.length();i+=8192)send(EVENT,pendingType,text.substring(i,Math.min(text.length(),i+8192)),0);
    }
    public String readLine() throws InterruptedException {
        synchronized(inputReadLock) {
            int requestId=requestCounter.incrementAndGet();inputSubmitted.set(false);waitingRequest.set(requestId);
            synchronized(this){flushOutput();send(EVENT,"input","",0,requestId);}
            try {return input.take();}
            finally {waitingRequest.set(0);send(EVENT,"input_end","",0,requestId);}
        }
    }
    public synchronized void finish(int code,String reason) {
        if(!ended.compareAndSet(false,true))return;
        flushOutput();
        if(!reason.isEmpty())send(EVENT,"stderr",reason,0);
        send(EVENT,"exit","",code);
        // A fresh process per run prevents leaked threads, modules and cwd contaminating later runs.
        main.postDelayed(() -> android.os.Process.killProcess(android.os.Process.myPid()),200);
    }
    private void send(int what,String type,String text,int code) {
        send(what,type,text,code,0);
    }
    private void send(int what,String type,String text,int code,int requestId) {
        if(client==null)return;
        Message event=Message.obtain(null,what);Bundle b=new Bundle();b.putString("type",type);b.putString("text",text);b.putInt("code",code);if(requestId>0)b.putInt("requestId",requestId);event.setData(b);
        try {client.send(event);}catch(RemoteException e){android.os.Process.killProcess(android.os.Process.myPid());}
    }
}
