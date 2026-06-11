const fs = require('fs');
const { JSDOM, VirtualConsole } = require('jsdom');
const html = fs.readFileSync('INICIAR.html', 'utf8');
const virtualConsole = new VirtualConsole();
virtualConsole.on('jsdomError', (error) => {
  console.error('JSDOM ERROR:', error && error.stack ? error.stack : error);
  process.exit(1);
});
virtualConsole.on('error', (message) => {
  console.error('JSDOM ERROR MESSAGE:', message);
});
virtualConsole.on('log', (message) => {
  console.log('JSDOM LOG:', message);
});
const dom = new JSDOM(html, {
  runScripts: 'dangerously',
  resources: 'usable',
  virtualConsole,
  beforeParse(window) {
    window.scrollTo = () => {};
    window.scrollBy = () => {};
    window.scroll = () => {};
    window.requestAnimationFrame = (cb) => setTimeout(cb, 0);
    window.cancelAnimationFrame = () => {};
  }
});
const w = dom.window;
w.onerror = function(message, source, lineno, colno, error) {
  console.error('ONERROR:', message);
  console.error('SOURCE:', source, 'LINE:', lineno, 'COL:', colno);
  if (error && error.stack) console.error(error.stack);
  process.exit(1);
};
w.addEventListener('error', (e) => {
  console.error('WINDOW ERROR EVENT:', e.message || e.error || e);
  if (e.error && e.error.stack) console.error(e.error.stack);
  process.exit(1);
});
w.addEventListener('unhandledrejection', (e) => {
  console.error('UNHANDLED REJECTION:', e.reason && e.reason.stack ? e.reason.stack : e.reason);
  process.exit(1);
});
setTimeout(() => {
  console.log('JSOK');
  process.exit(0);
}, 5000);
