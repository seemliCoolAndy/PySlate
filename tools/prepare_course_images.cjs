/* Deterministic asset encoding. Generated PNG masters are retained separately. */
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),sharp=require('sharp');
const root=path.resolve(__dirname,'..'),assets=path.join(root,'web/course-assets'),artwork=path.join(root,'../artwork'),masters=path.join(artwork,'masters');
const archive=process.argv.includes('--archive');fs.mkdirSync(masters,{recursive:true});
const hash=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const priorPath=path.join(artwork,'image-manifest.json');const priorRows=fs.existsSync(priorPath)?JSON.parse(fs.readFileSync(priorPath,'utf8')).images:[];const priorBy=new Map(priorRows.map(r=>[path.basename(r.master),r]));
(async()=>{const rows=[];for(const name of fs.readdirSync(assets).filter(n=>/^tier-(l\d\d|p0[1-8])-(beginner|intermediate|advanced)\.png$/.test(n)).sort()){
 const input=path.join(assets,name),output=path.join(assets,name.replace(/\.png$/,'.webp')),master=path.join(masters,name);
 const png=fs.readFileSync(input),sourceSha256=hash(png);const info=await sharp(png).metadata();if(info.format!=='png'||info.width<700)throw Error('Invalid generated master: '+name);
 fs.copyFileSync(input,master);
 if(!fs.existsSync(output)||priorBy.get(name)?.sourceSha256!==sourceSha256||priorBy.get(name)?.assetSha256!==hash(fs.readFileSync(output)))await sharp(png).webp({quality:88,effort:6,smartSubsample:true}).toFile(output);
 const encoded=fs.readFileSync(output),meta=await sharp(encoded).metadata();if(meta.format!=='webp'||meta.width!==info.width||meta.height!==info.height)throw Error('Encoding changed dimensions');
 rows.push({master:'masters/'+name,asset:'../'+path.basename(root)+'/web/course-assets/'+path.basename(output),width:meta.width,height:meta.height,masterBytes:png.length,assetBytes:encoded.length,sourceSha256,assetSha256:hash(encoded)});
 if(archive){if(path.dirname(input)!==assets||hash(fs.readFileSync(master))!==sourceSha256)throw Error('Archive verification failed');fs.unlinkSync(input);}
 }
 const manifestPath=path.join(artwork,'image-manifest.json');const previous=fs.existsSync(manifestPath)?JSON.parse(fs.readFileSync(manifestPath,'utf8')).images:[];const merged=new Map(previous.map(r=>[r.master,r]));for(const row of rows)merged.set(row.master,row);const images=[...merged.values()].sort((a,b)=>a.master.localeCompare(b.master));
 const manifest={encoder:'sharp '+(sharp.versions?.sharp||'bundled'),quality:88,format:'WebP',dimensionsPreserved:true,mastersPreserved:true,images};fs.writeFileSync(manifestPath,JSON.stringify(manifest,null,2)+'\n');
 console.log(JSON.stringify({processed:rows.length,total:images.length,masterBytes:images.reduce((n,r)=>n+r.masterBytes,0),assetBytes:images.reduce((n,r)=>n+r.assetBytes,0),archived:archive}));
})().catch(e=>{console.error(e);process.exitCode=1;});
