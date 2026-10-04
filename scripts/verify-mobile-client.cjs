// Verify reconnection behavior without a phone or any external requests.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const {execFileSync} = require('node:child_process');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const html = execFileSync(path.join(root, 'venv/Scripts/python.exe'), ['-c', 'from desktop.mobile import HTML; print(HTML)'], {cwd:root, env:{...process.env,PYTHONUTF8:'1'},encoding:'utf8'});
const script = html.split('<script nonce="NONCE">')[1].split('</script>')[0].replace(/;poll\(\);\s*$/, ';');
const storage = initial => ({data:{...initial},getItem(k){return this.data[k]||null;},setItem(k,v){this.data[k]=v;},removeItem(k){delete this.data[k];}});
const elements = new Map();
const timers = new Map();let id=0,calls=0;
const ctx = vm.createContext({location:{hash:'#new-token',pathname:'/'},history:{replaceState(){}},sessionStorage:storage(),localStorage:storage({'bob-token':'old-token'}),
  window:{addEventListener(){}},document:{hidden:false,addEventListener(){},getElementById(key){if(!elements.has(key))elements.set(key,{replaceChildren(){},appendChild(){}});return elements.get(key);}},
  AbortController, setTimeout(fn,delay){timers.set(++id,delay);return id;},clearTimeout(n){timers.delete(n);},
  fetch:async()=>{calls++;throw Error('offline');}});
async function main(){
  vm.runInContext(script,ctx);
  assert.equal(ctx.localStorage.getItem('bob-token'),'new-token');
  await vm.runInContext('poll()',ctx);
  assert.equal(vm.runInContext('failures',ctx),1);
  assert.ok([...timers.values()].includes(4000));
  ctx.fetch=async()=>{calls++;return {ok:true,json:async()=>({done:true,text:'',reminders:[]})};};
  await vm.runInContext('poll()',ctx);
  assert.equal(vm.runInContext('failures',ctx),0);
  assert.ok([...timers.values()].includes(5000));
  ctx.document.hidden=true;await vm.runInContext('poll()',ctx);
  assert.ok([...timers.values()].includes(30000));
  let release;ctx.fetch=()=>{calls++;return new Promise(resolve=>{release=resolve;});};
  const pending=vm.runInContext('poll()',ctx);const count=calls;
  await vm.runInContext('poll()',ctx);assert.equal(calls,count);
  release({ok:true,json:async()=>({done:true,text:'',reminders:[]})});await pending;
  ctx.fetch=async()=>({ok:false,status:401,json:async()=>({error:'Pair again'})});
  await vm.runInContext('poll()',ctx);
  assert.equal(vm.runInContext('token',ctx),'');
  assert.equal(ctx.localStorage.getItem('bob-token'),null);
  assert.equal(timers.size,0);
  console.log('Phone reconnection, hidden-page backoff, single poll, token rotation and revocation passed.');
}
main().catch(error=>{console.error(error);process.exitCode=1;});
