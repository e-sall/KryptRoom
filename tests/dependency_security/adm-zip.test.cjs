const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { createRequire } = require('node:module');
const { spawnSync } = require('node:child_process');
const test = require('node:test');

// Test only the ZIP dependency and installer boundary. No PSI/protocol execution.
const protocPackage = require.resolve('protoc-gen-js/package.json');
const protocRequire = createRequire(protocPackage);
const admPath = protocRequire.resolve('adm-zip');
const AdmZip = protocRequire('adm-zip');

function scratch(t) {
  const parent = path.resolve(os.tmpdir());
  const dir = fs.mkdtempSync(path.join(parent, 'kryptroom-admzip-'));
  t.after(() => {
    assert.equal(path.dirname(path.resolve(dir)), parent);
    assert.ok(path.basename(dir).startsWith('kryptroom-admzip-'));
    fs.rmSync(dir, { recursive: true, force: true });
  });
  return dir;
}

test('protoc resolves the fixed scoped ZIP dependency without changing PSI/protoc versions', () => {
  assert.equal(protocRequire('adm-zip/package.json').version, '0.6.1');
  assert.equal(require(protocPackage).version, '3.21.4');
  assert.equal(require('@openmined/psi.js/package.json').version, '2.0.6');
});

for (const binary of ['protoc-gen-js', 'protoc-gen-js.exe']) {
  test(`installer six-argument extraction remains compatible for ${binary}`, t => {
    const dir = scratch(t);
    const zip = new AdmZip();
    zip.addFile(`bin/${binary}`, Buffer.from('bounded synthetic binary bytes'));
    zip.addFile('README.txt', Buffer.from('do not extract'));
    const archive = new AdmZip(zip.toBuffer());
    assert.equal(archive.extractEntryTo(`bin/${binary}`, dir, false, true, false, binary), true);
    assert.equal(fs.readFileSync(path.join(dir, binary), 'utf8'), 'bounded synthetic binary bytes');
    assert.equal(fs.existsSync(path.join(dir, 'README.txt')), false);
  });
}

test('unchanged original post-install script accepts the fixed API with bounded network fixture', t => {
  const dir = scratch(t);
  for (const name of ['package.json', 'index.js', 'post-install.js']) {
    fs.copyFileSync(path.join(path.dirname(protocPackage), name), path.join(dir, name));
  }
  const binary = `protoc-gen-js${process.platform === 'win32' ? '.exe' : ''}`;
  const zip = new AdmZip();
  zip.addFile(`bin/${binary}`, Buffer.from('synthetic installer fixture; never executed'));
  fs.writeFileSync(path.join(dir, 'fixture.zip'), zip.toBuffer());
  // Intercept only this child's HTTPS transport; run the original installer bytes.
  fs.writeFileSync(path.join(dir, 'fixture-preload.cjs'), `
    const fs = require('node:fs');
    const path = require('node:path');
    const events = require('node:events');
    const https = require('node:https');
    const Module = require('node:module');
    const load = Module._load;
    Module._load = function(name, ...rest) {
      if (name === 'adm-zip') return load.call(this, ${JSON.stringify(admPath)}, ...rest);
      return load.call(this, name, ...rest);
    };
    https.get = (url, callback) => {
      if (!url.startsWith('https://github.com/protocolbuffers/protobuf-javascript/releases/download/v3.21.4/')) throw Error('unexpected installer URL');
      const request = new events.EventEmitter();
      queueMicrotask(() => {
        const response = new events.EventEmitter(); response.statusCode = 200;
        callback(response);
        response.emit('data', fs.readFileSync(path.join(__dirname, 'fixture.zip')));
        response.emit('end');
      });
      return request;
    };
  `);
  const child = spawnSync(process.execPath, ['--require', path.join(dir, 'fixture-preload.cjs'), path.join(dir, 'post-install.js')], {
    cwd: dir, encoding: 'utf8', timeout: 10000, windowsHide: true,
  });
  assert.equal(child.status, 0, child.stderr);
  assert.equal(fs.readFileSync(path.join(dir, 'bin', binary), 'utf8'), 'synthetic installer fixture; never executed');
});

test('extraction refuses an existing directory symlink/junction without touching its target', t => {
  const dir = scratch(t);
  const root = path.join(dir, 'root');
  const outside = path.join(dir, 'sentinel');
  fs.mkdirSync(root); fs.mkdirSync(outside);
  fs.writeFileSync(path.join(outside, 'binary'), 'preserve');
  fs.symlinkSync(outside, path.join(root, 'bin'), process.platform === 'win32' ? 'junction' : 'dir');
  const zip = new AdmZip(); zip.addFile('bin/binary', Buffer.from('replacement'));
  assert.throws(() => new AdmZip(zip.toBuffer()).extractEntryTo('bin/binary', root, true, true));
  assert.equal(fs.readFileSync(path.join(outside, 'binary'), 'utf8'), 'preserve');
});

test('duplicate names in a tiny archive are rejected before extraction', () => {
  const zip = new AdmZip();
  zip.addFile('a.txt', Buffer.from('a'));
  zip.addFile('b.txt', Buffer.from('b'));
  const data = zip.toBuffer();
  const from = Buffer.from('b.txt'); const to = Buffer.from('a.txt');
  for (let at = data.indexOf(from); at >= 0; at = data.indexOf(from, at + from.length)) to.copy(data, at);
  assert.throws(() => new AdmZip(data).getEntries());
});
