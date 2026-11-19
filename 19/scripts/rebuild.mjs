// Default: reproduce the saved six-block selection offline. Network is opt-in.
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../../',import.meta.url));
const run=(binary,args)=>{const r=spawnSync(binary,args,{cwd:root,stdio:'inherit',env:{...process.env,PYTHONDONTWRITEBYTECODE:'1'}});if(r.error)throw r.error;if(r.status!==0)throw Error(`${binary} exited ${r.status}`);};
const refresh=process.argv.includes('--refresh');
if(process.argv.slice(2).some(a=>a!=='--refresh'))throw Error('Usage: node 19/scripts/rebuild.mjs [--refresh]');
if(refresh)run(process.execPath,['19/scripts/collect-soho.mjs']);
run(process.env.DAY19_PYTHON||'python3.14',['-B','19/scripts/select-soho.py','--select=D']);
if(refresh)run(process.execPath,['19/scripts/prepare.mjs']);
console.log(refresh?'Refreshed small SoHo samples and runtime geometry.':'Offline selection reproduced; runtime geometry and source snapshots retained.');
