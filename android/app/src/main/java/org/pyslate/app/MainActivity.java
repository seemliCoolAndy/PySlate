package org.pyslate.app;

import android.app.*;
import android.content.*;
import android.net.Uri;
import android.os.*;
import android.webkit.*;
import android.view.*;
import android.widget.FrameLayout;
import android.util.Base64;
import org.json.*;
import java.io.*;
import java.nio.charset.StandardCharsets;

public final class MainActivity extends Activity {
    private WebView web;
    private FrameLayout frame;
    private ProjectStore store;
    private RunManager runner;
    private ValueCallback<Uri[]> chooser;
    private byte[] exportBytes;
    private boolean backPending;
    private static final int PICK_ZIP=30,SAVE_ZIP=31;

    @Override public void onCreate(Bundle saved) {
        super.onCreate(saved);
        try {store=new ProjectStore(this);runner=new RunManager(this);}catch(Exception e) {fatal(e);return;}
        web=new WebView(this);
        frame=new FrameLayout(this);frame.addView(web,new FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.MATCH_PARENT));setContentView(frame);
        try{applyNativeTheme(store.call(new JSONObject().put("action","bootstrap")).getJSONObject("state").optString("theme","light"));}catch(Exception ignored){}
        if((getApplicationInfo().flags & android.content.pm.ApplicationInfo.FLAG_DEBUGGABLE)!=0)WebView.setWebContentsDebuggingEnabled(true);
        // Android 15 edge-to-edge doesn't resize a fullscreen WebView for the IME.
        // Resize its parent content area instead: WebView padding alone leaves innerHeight unchanged.
        frame.setOnApplyWindowInsetsListener((view,insets)->{
            if(Build.VERSION.SDK_INT>=30){android.graphics.Insets safe=insets.getInsets(WindowInsets.Type.systemBars()|WindowInsets.Type.displayCutout()|WindowInsets.Type.ime());view.setPadding(safe.left,safe.top,safe.right,safe.bottom);return WindowInsets.CONSUMED;}
            view.setPadding(insets.getSystemWindowInsetLeft(),insets.getSystemWindowInsetTop(),insets.getSystemWindowInsetRight(),insets.getSystemWindowInsetBottom());return insets.consumeSystemWindowInsets();
        });
        frame.requestApplyInsets();
        WebSettings settings=web.getSettings();
        settings.setJavaScriptEnabled(true);settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(false);settings.setAllowContentAccess(true);
        settings.setAllowFileAccessFromFileURLs(false);settings.setAllowUniversalAccessFromFileURLs(false);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        settings.setSupportZoom(false);settings.setDefaultTextEncodingName("UTF-8");
        web.addJavascriptInterface(new Bridge(),"PySlateNative");
        web.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(WebView view,WebResourceRequest request) {return !request.getUrl().toString().startsWith("file:///android_asset/web/");}
            @Override public WebResourceResponse shouldInterceptRequest(WebView view,WebResourceRequest request) {
                String url=request.getUrl().toString();
                if(url.startsWith("file:///android_asset/"))return null;
                return new WebResourceResponse("text/plain","UTF-8",new ByteArrayInputStream(new byte[0]));
            }
        });
        web.setWebChromeClient(new WebChromeClient() {
            @Override public boolean onShowFileChooser(WebView view,ValueCallback<Uri[]> callback,FileChooserParams params) {
                if(chooser!=null)chooser.onReceiveValue(null);chooser=callback;
                Intent intent=new Intent(Intent.ACTION_OPEN_DOCUMENT).setType("application/zip").addCategory(Intent.CATEGORY_OPENABLE);
                intent.putExtra(Intent.EXTRA_MIME_TYPES,new String[]{"application/zip","application/x-zip-compressed","application/octet-stream"});
                try {startActivityForResult(intent,PICK_ZIP);}catch(Exception e){chooser.onReceiveValue(null);chooser=null;}return true;
            }
        });
        web.loadUrl("file:///android_asset/web/index.html");
    }
    private void fatal(Exception e) {new AlertDialog.Builder(this).setTitle("PySlate 无法启动").setMessage(e.toString()).setPositiveButton("关闭",(a,b)->finish()).show();}
    private void applyNativeTheme(String theme) {
        boolean dark="dark".equals(theme);int background=android.graphics.Color.parseColor(dark?"#17231e":"#f5f5ef");
        if(frame!=null)frame.setBackgroundColor(background);if(web!=null)web.setBackgroundColor(background);
        getWindow().setStatusBarColor(background);getWindow().setNavigationBarColor(background);
        if(Build.VERSION.SDK_INT>=30){WindowInsetsController controller=getWindow().getInsetsController();if(controller!=null){int light=WindowInsetsController.APPEARANCE_LIGHT_STATUS_BARS|WindowInsetsController.APPEARANCE_LIGHT_NAVIGATION_BARS;controller.setSystemBarsAppearance(dark?0:light,light);}}
        else {View decor=getWindow().getDecorView();int light=View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR|View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR;decor.setSystemUiVisibility(dark?decor.getSystemUiVisibility()&~light:decor.getSystemUiVisibility()|light);}
    }
    public final class Bridge {
        @JavascriptInterface public String call(String json) {
            try {
                if(json.length()>32*1024*1024)throw new IOException("请求超过大小限制");
                JSONObject request=new JSONObject(json);String action=request.getString("action");JSONObject response;
                if(action.equals("run")) {
                    JSONObject bootstrap=store.call(new JSONObject().put("action","bootstrap"));
                    if(!bootstrap.getJSONObject("state").optBoolean("trusted"))throw new IOException("请先阅读并确认本地代码执行提示");
                    response=runner.start(store.directory(request.getString("id")),request.optString("entry","main.py"));
                } else if(action.equals("events")||action.equals("input")||action.equals("stop"))response=runner.call(request);
                else {
                    if((action.equals("file.rename")||action.equals("file.delete")||action.equals("project.delete"))&&runner.isRunning(store.directory(request.getString("id"))))throw new IOException("请先停止程序，再移动或删除正在使用的文件");
                    response=store.call(request);
                    if(action.equals("state.patch")&&request.getJSONObject("patch").has("theme")){String theme=request.getJSONObject("patch").optString("theme","light");runOnUiThread(()->applyNativeTheme(theme));}
                    if(action.equals("bootstrap"))try(InputStream input=getAssets().open("course/course.json")) {response.put("course",new JSONObject(readText(input,8*1024*1024)));}
                }
                return response.toString();
            }catch(Exception e){try{return new JSONObject().put("error",e.getMessage()==null?e.toString():e.getMessage()).toString();}catch(Exception ignored){return "{\"error\":\"操作失败\"}";}}
        }
        @JavascriptInterface public void saveFile(String filename,String base64) {
            try {
                if(base64.length()>ProjectStore.ZIP_LIMIT*4L/3+8)throw new IOException("导出超过20MiB限制");
                byte[] bytes=Base64.decode(base64,Base64.DEFAULT);
                runOnUiThread(()->{exportBytes=bytes;Intent save=new Intent(Intent.ACTION_CREATE_DOCUMENT).addCategory(Intent.CATEGORY_OPENABLE).setType("application/zip").putExtra(Intent.EXTRA_TITLE,filename.replaceAll("[\\\\/:*?\"<>|]","_"));try{startActivityForResult(save,SAVE_ZIP);}catch(Exception e){exportBytes=null;new AlertDialog.Builder(MainActivity.this).setMessage("设备没有可用的文件保存程序").setPositiveButton("确定",null).show();}});
            }catch(Exception e){runOnUiThread(()->new AlertDialog.Builder(MainActivity.this).setMessage(e.getMessage()).setPositiveButton("确定",null).show());}
        }
        @JavascriptInterface public void openExternal(String url) {
            Uri uri=Uri.parse(url);String host=uri.getHost();
            if(!"https".equals(uri.getScheme())||host==null||!(host.equals("docs.python.org")||host.equals("www.python.org")))return;
            runOnUiThread(()->{try{startActivity(new Intent(Intent.ACTION_VIEW,uri));}catch(Exception ignored){}});
        }
        @JavascriptInterface public void finishAfterFlush(String error) {
            runOnUiThread(()->{if(error.isEmpty())finish();else new AlertDialog.Builder(MainActivity.this).setTitle("代码尚未保存").setMessage(error).setPositiveButton("返回编辑器",null).show();});
        }
        @JavascriptInterface public void backResult(boolean handled,String error) {
            runOnUiThread(()->{backPending=false;if(isFinishing()||isDestroyed())return;if(!error.isEmpty())new AlertDialog.Builder(MainActivity.this).setTitle("无法返回").setMessage(error).setPositiveButton("返回编辑器",null).show();else if(!handled)confirmExit();});
        }
    }
    private static String readText(InputStream input,int max) throws IOException {
        ByteArrayOutputStream output=new ByteArrayOutputStream();byte[] buf=new byte[16384];int n;while((n=input.read(buf))!=-1){if(output.size()+n>max)throw new IOException("资源超过限制");output.write(buf,0,n);}return output.toString(StandardCharsets.UTF_8.name());
    }
    @Override protected void onActivityResult(int request,int result,Intent data) {
        super.onActivityResult(request,result,data);
        if(request==PICK_ZIP&&chooser!=null){chooser.onReceiveValue(result==RESULT_OK&&data!=null?new Uri[]{data.getData()}:null);chooser=null;}
        if(request==SAVE_ZIP&&exportBytes!=null){byte[] bytes=exportBytes;exportBytes=null;if(result==RESULT_OK&&data!=null){Uri target=data.getData();new Thread(()->{try(OutputStream out=getContentResolver().openOutputStream(target)){if(out==null)throw new IOException("无法打开目标文件");out.write(bytes);}catch(Exception e){runOnUiThread(()->new AlertDialog.Builder(this).setMessage("导出失败："+e.getMessage()).setPositiveButton("确定",null).show());}},"PySlate-Export").start();}}
    }
    @Override public void onBackPressed() {
        if(web==null){finish();return;}
        if(backPending)return;
        backPending=true;
        web.evaluateJavascript("(async()=>{try{const handled=window.pyslateBack?await window.pyslateBack():false;PySlateNative.backResult(handled===true,'');}catch(e){PySlateNative.backResult(false,String(e));}})()",null);
    }
    private void confirmExit() {
        new AlertDialog.Builder(this).setMessage("退出 PySlate？代码和学习进度会保存到本机。").setNegativeButton("继续学习",null).setPositiveButton("退出",(a,b)->web.evaluateJavascript("(async()=>{try{if(window.pyslateFlush)await window.pyslateFlush();PySlateNative.finishAfterFlush('');}catch(e){PySlateNative.finishAfterFlush(String(e));}})()",null)).show();
    }
    @Override protected void onPause() {if(web!=null)web.evaluateJavascript("window.pyslateFlush ? window.pyslateFlush() : false",null);super.onPause();}
    @Override protected void onDestroy() {if(runner!=null)runner.close();if(chooser!=null)chooser.onReceiveValue(null);if(web!=null){web.removeJavascriptInterface("PySlateNative");web.destroy();}super.onDestroy();}
}
