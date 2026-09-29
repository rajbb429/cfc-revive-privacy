// Copies the web app in breathe/ into www/, the folder Capacitor packs into the Android
// app, and adds native.js: the Capacitor runtime and the plugins the page calls
// (billing, keep-awake, back button), which the plain web version doesn't load.
import { cpSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const SKIP = ['tools', 'store-listing.md', 'sw.js'];

rmSync('www', { recursive: true, force: true });
cpSync('breathe', 'www', {
  recursive: true,
  filter: (src) => !SKIP.some((s) => src === `breathe/${s}` || src.startsWith(`breathe/${s}/`)),
});

const bundles = [
  '@capacitor/core/dist/capacitor.js',
  '@capgo/native-purchases/dist/plugin.js',
  '@capacitor/app/dist/plugin.js',
  '@capacitor-community/keep-awake/dist/plugin.js',
];
const native = bundles
  .map((b) => readFileSync(require.resolve(b), 'utf8').replace(/\/\/# sourceMappingURL=.*$/m, ''))
  .join('\n;\n');
writeFileSync('www/native.js', native);

const page = readFileSync('www/index.html', 'utf8');
const marker = '<script>\n(() => {';
if (page.split(marker).length !== 2) throw new Error('index.html: app script not found');
writeFileSync('www/index.html', page.replace(marker, `<script src="native.js"></script>\n${marker}`));
console.log('Built www/ for the Android app');
