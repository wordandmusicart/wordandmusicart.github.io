import assert from "node:assert/strict";
import { access, readFile } from "node:fs/promises";

const root = new URL("../", import.meta.url);
const read = (path) => readFile(new URL(path, root), "utf8");
const readBytes = (path) => readFile(new URL(path, root));

const pngDimensions = async (path) => {
  const bytes = await readBytes(path);
  assert.equal(bytes.subarray(1, 4).toString("ascii"), "PNG", `${path} is not PNG`);
  return [bytes.readUInt32BE(16), bytes.readUInt32BE(20)];
};

const [html, css] = await Promise.all([
  read("index.html"),
  read("styles.css"),
]);

for (const path of [
  "assets/word-and-music-logo-black.svg",
  "assets/word-and-music-logo-white.svg",
  "assets/FixelText-Regular.woff2",
  "assets/TembravaDisplay-Regular.woff2",
  "assets/concert-desktop.png",
  "assets/concert-mobile.png",
  "assets/word-and-music-preview.png",
  "assets/favicon-32.png",
  "assets/favicon-192.png",
  "assets/apple-touch-icon.png",
]) {
  await access(new URL(path, root));
}

assert.match(html, /lang="uk"/);
assert.match(html, /Наш найближчий концерт/);
assert.match(html, /https:\/\/eventmate\.app\/events\/share\/koncert-ziti-kohati-mriati/);
assert.match(html, /<picture[\s>]/);
assert.match(html, /media="\(max-width: 700px\)"[^>]+concert-mobile\.png/s);
assert.match(html, /concert-desktop\.png/);
assert.match(html, /word-and-music-logo-black\.svg/);
assert.match(html, /rel="canonical" href="https:\/\/wordandmusic\.art\/"/);
assert.match(html, /property="og:image" content="https:\/\/raw\.githubusercontent\.com\/wordandmusicart\/wordandmusicart\.github\.io\/main\/assets\/word-and-music-preview\.png"/);
assert.match(html, /aria-describedby="concert-details"/);
assert.match(html, /id="concert-details"[^>]*>[^<]*3 жовтня 2026 року о 16:00/);
assert.match(html, /Геннадій Таранок/);
assert.match(html, /rel="icon"[^>]+favicon-32\.png/);
assert.match(html, /rel="apple-touch-icon"[^>]+apple-touch-icon\.png/);
assert.match(css, /@font-face/);
assert.match(css, /FixelText-Regular\.woff2/);
assert.match(css, /100(?:dvh|svh)/);
assert.match(css, /overflow:\s*hidden/);
assert.match(css, /prefers-reduced-motion:\s*reduce/);
assert.match(css, /:focus-visible/);
assert.match(css, /\.sr-only\s*\{/);

assert.deepEqual(await pngDimensions("assets/concert-desktop.png"), [1920, 1080]);
assert.deepEqual(await pngDimensions("assets/concert-mobile.png"), [1080, 1350]);
assert.deepEqual(await pngDimensions("assets/word-and-music-preview.png"), [1200, 630]);
assert.deepEqual(await pngDimensions("assets/favicon-32.png"), [32, 32]);
assert.deepEqual(await pngDimensions("assets/favicon-192.png"), [192, 192]);
assert.deepEqual(await pngDimensions("assets/apple-touch-icon.png"), [180, 180]);

console.log("Static acceptance checks: PASS");
