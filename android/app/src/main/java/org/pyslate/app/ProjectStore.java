package org.pyslate.app;

import android.content.Context;
import android.util.Base64;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;
import java.util.*;
import java.util.zip.*;

/** Main-process ownership of real files. Metadata never enters exported projects. */
public final class ProjectStore {
    private final File root, projects, metadata, trash, history;
    private final String version;
    private JSONObject state;
    private JSONArray categories;
    private final LinkedHashMap<String, JSONObject> library = new LinkedHashMap<>();
    static final int TEXT_LIMIT = 1024 * 1024;
    static final int ZIP_LIMIT = 20 * 1024 * 1024;

    public ProjectStore(Context context) throws Exception {
        version=context.getPackageManager().getPackageInfo(context.getPackageName(),0).versionName;
        root = new File(context.getFilesDir(), "pyslate");
        projects = new File(root, "projects"); metadata = new File(root, "library.json");
        trash = new File(root, "trash"); history = new File(root, "history");
        projects.mkdirs(); trash.mkdirs(); history.mkdirs();
        state = new JSONObject("{\"theme\":\"light\",\"progress\":{},\"drafts\":{},\"lessonTiers\":{},\"lastLesson\":\"l01\",\"split\":0.5,\"trusted\":false}");
        categories = new JSONArray().put("未分类");
        if (metadata.isFile()) {
            JSONObject saved = new JSONObject(new String(Files.readAllBytes(metadata.toPath()),StandardCharsets.UTF_8));
            state = saved.optJSONObject("state") == null ? state : saved.getJSONObject("state");
            categories = saved.optJSONArray("categories") == null ? categories : saved.getJSONArray("categories");
            JSONArray list = saved.optJSONArray("projects");
            if (list != null) for (int i=0;i<list.length();i++) {
                JSONObject p=list.getJSONObject(i);if("sage".equals(p.optString("color")))p.put("color","#a1c9b8");library.put(p.getString("id"),p);
            }
        }
    }
    static void atomic(File file, byte[] content) throws Exception {
        file.getParentFile().mkdirs();
        File tmp = new File(file.getParentFile(), "." + file.getName() + "." + UUID.randomUUID() + ".tmp");
        try {
            try (FileOutputStream output = new FileOutputStream(tmp)) { output.write(content); output.getFD().sync(); }
            try { Files.move(tmp.toPath(), file.toPath(), StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING); }
            catch (java.nio.file.AtomicMoveNotSupportedException e) { Files.move(tmp.toPath(), file.toPath(), StandardCopyOption.REPLACE_EXISTING); }
        } finally { Files.deleteIfExists(tmp.toPath()); }
    }
    private void persist() throws Exception {
        JSONObject all = new JSONObject().put("state",state).put("categories",categories).put("projects",new JSONArray(library.values()));
        atomic(metadata,all.toString().getBytes(StandardCharsets.UTF_8));
    }
    private JSONObject get(String id) throws Exception {
        JSONObject p=library.get(id); if(p==null) throw new IOException("项目不存在"); return p;
    }
    public synchronized File directory(String id) throws Exception { get(id); return new File(projects,id); }
    private File path(String id,String relative) throws Exception {
        if(relative.isEmpty() || relative.length()>240 || relative.startsWith("/") || relative.contains("\\") || relative.indexOf('\0')>=0 || relative.matches("^[A-Za-z]:.*")) throw new IOException("文件路径无效");
        File current=directory(id);
        for(String part:relative.split("/",-1)) {
            if(part.isEmpty()||part.equals(".")||part.equals("..")||part.endsWith(" ")||part.endsWith(".")||part.matches("(?i)^(CON|PRN|AUX|NUL|COM[1-9¹²³]|LPT[1-9¹²³])(\\..*)?$")||part.matches(".*[\\x00-\\x1f<>:\"|?*].*"))throw new IOException("文件名包含不兼容的路径片段");
            File[] siblings=current.listFiles();if(siblings!=null)for(File sibling:siblings)if(sibling.getName().equalsIgnoreCase(part)&&!sibling.getName().equals(part))throw new IOException("已有仅大小写不同的路径，请使用原有名称");
            current=new File(current,part);if(Files.isSymbolicLink(current.toPath()))throw new IOException("不支持符号链接");
        }
        File base=directory(id).getCanonicalFile(), file=new File(base,relative).getCanonicalFile();
        if(!file.getPath().startsWith(base.getPath()+File.separator)) throw new IOException("路径超出项目");
        return file;
    }
    private void touch(String id) throws Exception { get(id).put("updated",System.currentTimeMillis()); persist(); }
    private JSONObject create(JSONObject request) throws Exception {return create(request,true,true);}
    private JSONObject create(JSONObject request,boolean starter,boolean publish) throws Exception {
        String id=UUID.randomUUID().toString();
        String name=request.optString("name","未命名项目").trim(); if(name.isEmpty()||name.length()>120) throw new IOException("项目名称需为1至120个字符");
        JSONObject p=new JSONObject().put("id",id).put("name",name).put("color",request.optString("color","#dbb572")).put("category",request.optString("category","未分类")).put("updated",System.currentTimeMillis()).put("practice",request.optBoolean("practice",false));
        File folder=new File(projects,id); if(!folder.mkdirs())throw new IOException("无法创建项目目录");
        try {
            if(starter)atomic(new File(folder,"main.py"),"print('你好，PySlate！')\n".getBytes(StandardCharsets.UTF_8));
            library.put(id,p);ensureCategory(p.getString("category"));if(publish)persist();return p;
        }catch(Exception e){library.remove(id);removeTree(folder);throw e;}
    }
    private void ensureCategory(String category)throws Exception {
        if(category.trim().isEmpty()||category.length()>120)throw new IOException("分类名称无效");
        for(int i=0;i<categories.length();i++)if(category.equals(categories.getString(i)))return;
        categories.put(category);
    }
    private static void removeTree(File file)throws IOException {
        if(!Files.isSymbolicLink(file.toPath())&&file.isDirectory()){File[] children=file.listFiles();if(children!=null)for(File child:children)removeTree(child);}
        Files.deleteIfExists(file.toPath());
    }
    private void walk(File base,File dir,JSONArray result) throws Exception {
        File[] children=dir.listFiles(); if(children==null)return;
        Arrays.sort(children,Comparator.comparing(File::getName));
        for(File f:children) {
            if(Files.isSymbolicLink(f.toPath())) continue;
            if(f.isDirectory()) { if(!f.getName().equals("__pycache__"))walk(base,f,result); }
            else result.put(new JSONObject().put("path",base.toPath().relativize(f.toPath()).toString().replace('\\','/')).put("size",f.length()));
        }
    }
    private File backup(String id,File file) throws Exception {
        if(file.isFile()) {
            File previous=new File(history,id+"/"+System.currentTimeMillis()+"-"+UUID.randomUUID()+"-"+file.getName());
            previous.getParentFile().mkdirs(); Files.copy(file.toPath(),previous.toPath());
            File[] versions=previous.getParentFile().listFiles();if(versions!=null&&versions.length>100){Arrays.sort(versions,Comparator.comparing(File::getName).reversed());for(int i=100;i<versions.length;i++)Files.deleteIfExists(versions[i].toPath());}
            return previous;
        }
        return null;
    }
    public synchronized JSONObject call(JSONObject request) throws Exception {
        // Keep failed validation / disk writes from leaking partial changes into later saves.
        String savedState=state.toString(),savedCategories=categories.toString();JSONArray savedProjects=new JSONArray(library.values());
        String savedLibrary=savedProjects.toString();
        try {return dispatch(request);}catch(Exception error){
            state=new JSONObject(savedState);categories=new JSONArray(savedCategories);library.clear();JSONArray old=new JSONArray(savedLibrary);
            for(int i=0;i<old.length();i++){JSONObject p=old.getJSONObject(i);library.put(p.getString("id"),p);}throw error;
        }
    }
    private JSONObject dispatch(JSONObject request) throws Exception {
        String action=request.getString("action"), id=request.optString("id");
        switch(action) {
            case "bootstrap":return new JSONObject().put("platform","android").put("version",version).put("python","3.14").put("state",state).put("projects",new JSONArray(library.values())).put("categories",categories);
            case "state.patch": {
                JSONObject patch=request.getJSONObject("patch");
                for(Iterator<String> it=patch.keys();it.hasNext();) {String key=it.next(); if(Arrays.asList("theme","progress","drafts","lessonTiers","lessonSources","lastLesson","split","trusted","practiceId","practiceIds").contains(key))state.put(key,patch.get(key));}
                persist();return new JSONObject().put("ok",true);
            }
            case "category.create": {
                String name=request.getString("name").trim(); if(name.isEmpty()||name.length()>60)throw new IOException("分类名称无效");
                boolean exists=false;for(int i=0;i<categories.length();i++)if(categories.getString(i).equals(name))exists=true;
                if(!exists)categories.put(name);persist();return new JSONObject().put("categories",categories);
            }
            case "project.create":return new JSONObject().put("project",create(request));
            case "project.update": {
                JSONObject p=new JSONObject(get(id).toString()); for(String key:new String[]{"name","color","category"})if(request.has(key))p.put(key,request.getString(key));
                if(p.getString("name").trim().isEmpty()||p.getString("name").length()>120)throw new IOException("项目名称无效");
                ensureCategory(p.getString("category"));library.put(id,p);touch(id);return new JSONObject().put("project",p);
            }
            case "project.delete": {
                File source=directory(id),destination=new File(trash,id+"-"+System.currentTimeMillis());Files.move(source.toPath(),destination.toPath());library.remove(id);
                try{persist();}catch(Exception error){Files.move(destination.toPath(),source.toPath());throw error;}return new JSONObject().put("ok",true);
            }
            case "project.duplicate": {
                JSONObject original=new JSONObject(get(id).toString());File source=directory(id);JSONArray files=new JSONArray();walk(source,source,files);
                String originalName=original.getString("name");original.put("name",originalName.substring(0,Math.min(117,originalName.length()))+" 副本");JSONObject duplicate=create(original,false,false);String duplicateId=duplicate.getString("id");
                try {long total=0;for(int i=0;i<files.length();i++){String relative=files.getJSONObject(i).getString("path");File from=path(id,relative),to=path(duplicateId,relative);total+=from.length();if(total>100L*1024*1024)throw new IOException("项目超过100MiB复制限制");to.getParentFile().mkdirs();Files.copy(from.toPath(),to.toPath());}persist();return new JSONObject().put("project",duplicate);}
                catch(Exception error){removeTree(new File(projects,duplicateId));library.remove(duplicateId);throw error;}
            }
            case "project.files": {JSONArray files=new JSONArray();File base=directory(id);walk(base,base,files);return new JSONObject().put("files",files);}
            case "file.read": {
                File file=path(id,request.getString("path"));if(file.length()>TEXT_LIMIT)throw new IOException("文本超过1MiB限制");
                byte[] bytes=Files.readAllBytes(file.toPath());for(byte b:bytes)if(b==0)throw new IOException("二进制文件无法作为文本编辑");
                String content=StandardCharsets.UTF_8.newDecoder().decode(java.nio.ByteBuffer.wrap(bytes)).toString();return new JSONObject().put("content",content);
            }
            case "file.create": {
                File file=path(id,request.getString("path"));byte[] bytes=request.optString("content","").getBytes(StandardCharsets.UTF_8);if(bytes.length>TEXT_LIMIT)throw new IOException("文本超过1MiB限制");
                File parent=file.getParentFile();parent.mkdirs();File[] siblings=parent.listFiles();if(siblings!=null)for(File sibling:siblings)if(sibling.getName().equalsIgnoreCase(file.getName()))throw new IOException("目标文件已存在");
                boolean created=false;try{try(OutputStream output=Files.newOutputStream(file.toPath(),java.nio.file.StandardOpenOption.CREATE_NEW,java.nio.file.StandardOpenOption.WRITE)){created=true;output.write(bytes);}touch(id);return new JSONObject().put("ok",true);}catch(Exception error){if(created)Files.deleteIfExists(file.toPath());throw error;}
            }
            case "file.write": {
                File file=path(id,request.getString("path"));byte[] bytes=request.getString("content").getBytes(StandardCharsets.UTF_8);if(bytes.length>TEXT_LIMIT)throw new IOException("文本超过1MiB限制");
                File previous=backup(id,file);boolean written=false;
                try{atomic(file,bytes);written=true;touch(id);}catch(Exception error){if(written){if(previous!=null)Files.copy(previous.toPath(),file.toPath(),StandardCopyOption.REPLACE_EXISTING);else Files.deleteIfExists(file.toPath());}throw error;}return new JSONObject().put("ok",true);
            }
            case "file.rename": {
                File from=path(id,request.getString("path")),to=path(id,request.getString("newPath"));if(to.exists())throw new IOException("目标文件已存在");
                to.getParentFile().mkdirs();Files.move(from.toPath(),to.toPath());try{touch(id);}catch(Exception error){Files.move(to.toPath(),from.toPath());throw error;}return new JSONObject().put("ok",true);
            }
            case "file.delete": {
                File file=path(id,request.getString("path"));if(!file.isFile())throw new IOException("只能删除文件");File previous=backup(id,file);if(!file.delete())throw new IOException("删除失败");try{touch(id);}catch(Exception error){Files.copy(previous.toPath(),file.toPath(),StandardCopyOption.REPLACE_EXISTING);throw error;}return new JSONObject().put("ok",true);
            }
            case "project.export":return export(id);
            case "project.import":return new JSONObject().put("project",importZip(request.optString("filename","导入项目.zip"),request.getString("base64")));
            default:throw new IOException("未知操作："+action);
        }
    }
    private JSONObject export(String id) throws Exception {
        ByteArrayOutputStream data=new ByteArrayOutputStream();File base=directory(id);JSONArray files=new JSONArray();walk(base,base,files);
        long total=0;try(ZipOutputStream zip=new ZipOutputStream(data,StandardCharsets.UTF_8)) {
            for(int i=0;i<files.length();i++) {String name=files.getJSONObject(i).getString("path");File f=path(id,name);total+=f.length();if(total>100L*1024*1024)throw new IOException("项目超过100MiB导出限制");zip.putNextEntry(new ZipEntry(name));Files.copy(f.toPath(),zip);zip.closeEntry();}
        }
        if(data.size()>ZIP_LIMIT)throw new IOException("ZIP超过20MiB限制");
        return new JSONObject().put("filename",get(id).getString("name").replaceAll("[\\\\/:*?\"<>|]","_")+".zip").put("base64",Base64.encodeToString(data.toByteArray(),Base64.NO_WRAP));
    }
    private JSONObject importZip(String filename,String base64) throws Exception {
        if(base64.length()>ZIP_LIMIT*4L/3+8)throw new IOException("ZIP超过20MiB限制");
        byte[] bytes=Base64.decode(base64,Base64.DEFAULT);if(bytes.length>ZIP_LIMIT)throw new IOException("ZIP超过20MiB限制");
        if(bytes.length<4||bytes[0]!='P'||bytes[1]!='K')throw new IOException("不是有效ZIP文件");
        inspectZipDirectory(bytes);
        String name=filename.replaceAll("(?i)\\.zip$","");JSONObject p=create(new JSONObject().put("name",name.isEmpty()?"导入项目":name).put("category","导入项目").put("color","#a1c9b8"),false,false);String id=p.getString("id");
        long total=0;int count=0,fileCount=0;Set<String> entries=new HashSet<>();
        try(ZipInputStream zip=new ZipInputStream(new ByteArrayInputStream(bytes),StandardCharsets.UTF_8)) {
            ZipEntry entry;byte[] buffer=new byte[16384];
            while((entry=zip.getNextEntry())!=null) {
                if(++count>2000)throw new IOException("ZIP文件数超过2000");
                String entryName=entry.getName();if(entry.isDirectory()) {path(id,entryName.replaceAll("/$",""));continue;}
                File file=path(id,entryName);if(!entries.add(entryName.toLowerCase(Locale.ROOT)))throw new IOException("ZIP包含重复路径");fileCount++;file.getParentFile().mkdirs();
                // ZipInputStream does not create symbolic links; every extracted entry is a regular file.
                try(FileOutputStream out=new FileOutputStream(file)) {int n;while((n=zip.read(buffer))!=-1) {total+=n;if(total>100L*1024*1024||total>Math.max(bytes.length*100L,1024*1024L))throw new IOException("ZIP展开体积或压缩率超过限制");out.write(buffer,0,n);}}
            }
            if(fileCount==0)throw new IOException("ZIP内没有文件");
            touch(id);return p;
        } catch(Exception e) {
            removeTree(new File(projects,id));library.remove(id);throw e;
        }
    }
    private static int little16(byte[] data,int at) {return (data[at]&255)|((data[at+1]&255)<<8);}
    private static long little32(byte[] data,int at) {return (little16(data,at)&65535L)|((little16(data,at+2)&65535L)<<16);}
    private static void inspectZipDirectory(byte[] data) throws IOException {
        int end=-1;
        for(int at=data.length-22;at>=Math.max(0,data.length-65557);at--)if(little32(data,at)==0x06054b50L&&at+22+little16(data,at+20)==data.length){end=at;break;}
        if(end<0)throw new IOException("ZIP中央目录损坏");
        if(little16(data,end+4)!=0||little16(data,end+6)!=0)throw new IOException("不支持分卷ZIP");
        int count=little16(data,end+10);long offset=little32(data,end+16),size=little32(data,end+12);
        if(count>2000||offset+size>end||offset>Integer.MAX_VALUE)throw new IOException("ZIP目录体积无效");
        int at=(int)offset;
        for(int i=0;i<count;i++) {
            if(at+46>end||little32(data,at)!=0x02014b50L)throw new IOException("ZIP文件目录无效");
            int unixMode=(int)(little32(data,at+38)>>>16);
            if((unixMode&0xF000)==0xA000)throw new IOException("不允许导入符号链接");
            if((little16(data,at+8)&1)!=0)throw new IOException("不支持加密ZIP");
            int length=46+little16(data,at+28)+little16(data,at+30)+little16(data,at+32);
            if(at+length>end)throw new IOException("ZIP文件目录截断");at+=length;
        }
    }
}
