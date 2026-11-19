// Project-prefix preview, including ES modules. Does not write or rebuild assets.
const http=require('node:http'),fs=require('node:fs/promises'),path=require('node:path');
const root=path.resolve(__dirname,'../../docs'),prefix='/30DayMapChallenge/';
const types={'.html':'text/html; charset=utf-8','.css':'text/css','.js':'text/javascript','.mjs':'text/javascript','.json':'application/json','.geojson':'application/geo+json','.gif':'image/gif','.png':'image/png','.md':'text/plain; charset=utf-8'};
function createServer(){return http.createServer(async(req,res)=>{try{
 const url=new URL(req.url,'http://localhost');
 if(url.pathname==='/'){res.writeHead(302,{Location:prefix}).end();return;}
 if(!url.pathname.startsWith(prefix)){res.writeHead(404).end();return;}
 let file=path.resolve(root,decodeURIComponent(url.pathname.slice(prefix.length))||'index.html');
 if(file!==root&&!file.startsWith(root+path.sep)){res.writeHead(403).end();return;}
 if((await fs.stat(file)).isDirectory())file=path.join(file,'index.html');
 const body=await fs.readFile(file);
 res.writeHead(200,{'Content-Type':types[path.extname(file)]||'application/octet-stream','Cache-Control':'no-store'}).end(body);
 }catch{res.writeHead(404).end('Not found');}
});}
module.exports={createServer};
if(require.main===module)createServer().listen(8026,'127.0.0.1',()=>console.log('http://127.0.0.1:8026'+prefix));
