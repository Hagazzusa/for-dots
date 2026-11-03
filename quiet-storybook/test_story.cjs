/* Dependency-free state tests. This is a small DOM substitute, not browser QA. */
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');
const handlers = {};
function element(text = '') {
  return { hidden: false, disabled: false, textContent: text, attrs: {},
    addEventListener(type, fn) { this[type] = fn; },
    setAttribute(key, value) { this.attrs[key] = value; },
    focus() { document.activeElement = this; },
    closest() { return false; }
  };
}
const scenes = ['아직 따르지 않은 차', '비는 여기까지', '아침은 조용히'].map(title => ({ hidden: false, querySelector: () => element(title) }));
const nodes = Object.fromEntries(['#previous', '#next', '#position', '.turns', '.keyboard'].map(id => [id, element()]));
const document = { activeElement: null, querySelectorAll: () => scenes, querySelector: id => nodes[id], addEventListener: (type, fn) => { handlers[type] = fn; } };
vm.runInNewContext(fs.readFileSync(path.join(__dirname, 'story.js'), 'utf8'), { document, window: { matchMedia: () => ({ matches: false }) } });
function state(page) { assert.equal(scenes.filter(x => !x.hidden).length, 1); assert.equal(scenes[page].hidden, false); assert.ok(nodes['#position'].textContent.startsWith(`${page + 1} / 3`)); }
function key(key, extra = {}) { handlers.keydown({ key, target: element(), preventDefault() {}, ...extra }); }
state(0); assert.equal(nodes['#previous'].disabled, true);
key('ArrowLeft'); state(0);
nodes['#next'].click(); state(1); assert.equal(nodes['#previous'].disabled, false);
key('ArrowRight'); state(2); assert.equal(nodes['#next'].attrs['aria-label'], '첫 장면으로 돌아가기');
key('ArrowRight'); state(2);
nodes['#next'].click(); state(0);
for (let i = 0; i < 30; i++) nodes['#next'].click(); state(0);
key('ArrowRight', { ctrlKey: true }); state(0);
key('ArrowRight', { repeat: true }); state(0);
key('ArrowRight', { target: { closest: () => true } }); state(0);
key('ArrowRight'); state(1); document.activeElement = nodes['#previous']; nodes['#previous'].click(); state(0); assert.equal(document.activeElement, nodes['#next']);
assert.equal(nodes['.turns'].hidden, false);
assert.equal(nodes['.keyboard'].hidden, false);
const html = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');
assert.equal((html.match(/<article /g) || []).length, 3);
assert.equal((html.match(/<img [^>]*alt="[^"]+"/g) || []).length, 3);
assert.ok(!/<article[^>]*hidden/.test(html), 'No-JS story must remain visible');
assert.ok(html.includes('lang="ko"'));
for (const name of ['index.html', 'style.css', 'story.js']) {
  const source = fs.readFileSync(path.join(__dirname, name), 'utf8');
  assert.ok(!/https?:\/\/|fetch\(|XMLHttpRequest|localStorage|sessionStorage|\/workspace\/|\/home\//.test(source));
}
console.log('PASS: bounded keyboard navigation, restart, 30 repeated clicks, modifier/repeat guards, focus recovery, one visible scene, no-JS readability, alt text, local-only sources.');
