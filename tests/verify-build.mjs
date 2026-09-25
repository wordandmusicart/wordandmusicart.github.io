import assert from "node:assert/strict";
import { readdir } from "node:fs/promises";

const dist = new URL("../dist/", import.meta.url);
const files = [];

async function collect(directory, prefix = "") {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const name = `${prefix}${entry.name}`;
    if (entry.isDirectory()) {
      await collect(new URL(`${entry.name}/`, directory), `${name}/`);
    } else {
      files.push(name);
    }
  }
}

await collect(dist);

assert.deepEqual(files.sort(), [
  "CNAME",
  "assets/FixelText-Regular.woff2",
  "assets/TembravaDisplay-Regular.woff2",
  "assets/apple-touch-icon.png",
  "assets/concert-desktop.png",
  "assets/concert-desktop-640.png",
  "assets/concert-desktop-960.png",
  "assets/concert-desktop-1280.png",
  "assets/concert-mobile.png",
  "assets/concert-mobile-480.png",
  "assets/concert-mobile-720.png",
  "assets/favicon-192.png",
  "assets/favicon-32.png",
  "assets/favicon-512.png",
  "assets/word-and-music-logo-black.svg",
  "assets/word-and-music-logo-white.svg",
  "assets/word-and-music-preview.png",
  "index.html",
  "robots.txt",
  "sitemap.xml",
  "styles.css",
].sort());

console.log("Public file allowlist: PASS");
