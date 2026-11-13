const fs=require('fs'),path=require('path'),http=require('http');
const root=path.resolve(__dirname,'..'),local=process.argv.includes('--local-preview'),prefix='/30DayMapChallenge/';
const types={'.html':'text/html; charset=utf-8','.css':'text/css','.js':'application/javascript','.json':'application/json','.geojson':'application/json','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg','.gif':'image/gif'};
function createServer(localReview=local){const local=localReview;return http.createServer((req,res)=>{let p=decodeURIComponent(new URL(req.url,'http://localhost').pathname),base,file;
 if(p==='/'||p===prefix.slice(0,-1)){res.writeHead(302,{Location:prefix});res.end();return;}
 if(p.startsWith(prefix)){base=path.join(root,'docs');const rest=p.slice(prefix.length);file=local&&(!rest||rest==='index.html')?path.join(root,'.work/gallery-preview/index.html'):path.resolve(base,rest);}
 else if(local&&p.startsWith('/local-day13/')){base=path.join(root,'13');file=path.resolve(base,p.slice('/local-day13/'.length));}
 else{res.writeHead(404);res.end('Not found');return;}
 if(!(local&&file===path.join(root,'.work/gallery-preview/index.html'))&&file!==base&&!file.startsWith(base+path.sep)){res.writeHead(403);res.end();return;}
 if(fs.existsSync(file)&&fs.statSync(file).isDirectory())file=path.join(file,'index.html');
 fs.readFile(file,(err,b)=>{res.writeHead(err?404:200,{'Content-Type':types[path.extname(file)]||'application/octet-stream','Cache-Control':'no-store'});res.end(err?'Not found':b)});
});}
module.exports={createServer};
if(require.main===module)createServer().listen(8026,'127.0.0.1',()=>console.log(`http://127.0.0.1:8026${prefix} (${local?'private local review':'public-safe build'})`));
