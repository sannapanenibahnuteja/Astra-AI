// Browser startup contracts with simulated Safari storage/network failures.
const vm = require('node:vm');
const assert = require('node:assert/strict');
let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', async () => {
  const html = JSON.parse(input);
  const script = html.match(/<script nonce="NONCE">([\s\S]*?)<\/script>/)[1];
  const fixtureToken = 'a'.repeat(43);
  function browser(options = {}) {
    const nodes = new Map(), timers = new Map(), session = new Map(), local = new Map();
    const node = id => {
      if (!nodes.has(id)) nodes.set(id, {textContent: id === 'status' ? 'Connecting…' : '',
        checked: false, disabled: false, hidden: true, value: '', replaceChildren() {}, appendChild() {},
        click() { if (this.onclick) this.onclick(); }});
      return nodes.get(id);
    };
    let nextTimer = 0, fetches = 0, replaced = false;
    const location = {hash: options.noToken ? '' : '#' + fixtureToken,
      origin: 'https://fixture.example.ts.net', pathname: '/', href: 'https://fixture.example.ts.net/'};
    function storage(map) { return {getItem: key => map.get(key) || null,
      setItem: (key, value) => map.set(key, value), removeItem: key => map.delete(key)}; }
    const context = {console, URL, Uint8Array, Blob, AbortController: options.noAbort ? undefined : AbortController,
      setTimeout(fn, ms) { const id = ++nextTimer; timers.set(id, {fn, ms}); return id; },
      clearTimeout(id) { timers.delete(id); },
      location, history: {replaceState() { if (options.badHistory) throw Error('denied'); replaced = true; location.hash = ''; }},
      document: {hidden: false, getElementById: node, createElement: () => node('li'), addEventListener() {}},
      addEventListener() {}, navigator: {}, performance: {now: () => 0},
      fetch: async () => {
        fetches++;
        if (options.stall) return new Promise(() => {});
        return {ok: !options.unauthorized, status: options.unauthorized ? 401 : 200,
          json: async () => {
            if (options.badJSON) throw Error('not json');
            return options.unauthorized ? {error: 'Pair this phone from Bob Settings again.'} :
              {text: '', done: true, error: '', reminders: []};
          }};
      }};
    for (const [name, map] of [['sessionStorage', session], ['localStorage', local]]) {
      Object.defineProperty(context, name, {enumerable:true,configurable:true,get() { if (options.blockedStorage) throw Error('SecurityError'); return storage(map); }});
    }
    context.window = context;
    vm.createContext(context);
    vm.runInContext(script, context, {timeout: 1000});
    return {node, context, timers, session, location, get fetches() { return fetches; }, get replaced() { return replaced; }};
  }
  async function settle() { for (let i = 0; i < 5; i++) await new Promise(resolve => setImmediate(resolve)); }
  let count = 0;
  try {
    const normal = browser(); await settle();
    assert.match(normal.node('status').textContent, /Connected/);
    assert.equal(normal.fetches, 1); assert.equal(normal.replaced, true); count++;

    const blocked = browser({blockedStorage: true}); await settle();
    assert.match(blocked.node('status').textContent, /Connected/);
    assert.equal(blocked.replaced, false); assert.notEqual(blocked.location.hash, ''); count++;
    blocked.node('rememberPhone').checked = true; blocked.node('rememberPhone').onchange();
    assert.equal(blocked.node('rememberPhone').checked, false); count++;

    const history = browser({badHistory: true}); await settle();
    assert.match(history.node('status').textContent, /Connected/); count++;

    const missing = browser({noToken: true}); await settle();
    assert.match(missing.node('status').textContent, /incomplete or expired/);
    assert.equal(missing.node('pairingPanel').hidden, false); assert.equal(missing.fetches, 0); count++;
    missing.node('pairingLink').value = missing.location.origin + '/#' + fixtureToken;
    missing.node('pair').onclick(); await settle();
    assert.match(missing.node('status').textContent, /Connected/);
    assert.equal(missing.node('pairingLink').value, ''); count++;

    const foreign = browser({noToken: true});
    foreign.node('pairingLink').value = 'https://another.example.ts.net/#' + fixtureToken;
    foreign.node('pair').onclick(); await settle();
    assert.equal(foreign.fetches, 0); assert.match(foreign.node('status').textContent, /this private Bob address/); count++;

    const expired = browser({unauthorized: true}); await settle();
    assert.match(expired.node('status').textContent, /Pair this phone/);
    assert.equal(expired.node('pairingPanel').hidden, false); assert.equal(expired.session.size, 0); count++;

    const stalled = browser({stall: true, noAbort: true}); await settle();
    const deadline = [...stalled.timers.values()].find(timer => timer.ms === 12000);
    assert.ok(deadline); deadline.fn(); await settle();
    assert.match(stalled.node('status').textContent, /timed out/);
    assert.equal(stalled.node('send').disabled, true); count++;

    const wrong = browser({badJSON: true}); await settle();
    assert.match(wrong.node('status').textContent, /did not return the Bob gateway/); count++;

    normal.node('logout').onclick(); await settle();
    assert.equal(normal.session.size, 0); assert.equal(normal.node('mic').disabled, true); count++;
    process.stdout.write(JSON.stringify({passed: true, checks: count, scope: 'Simulated mobile JS; no real Safari, microphone or network.'}));
  } catch (error) { console.error(error); process.exitCode = 1; }
});
