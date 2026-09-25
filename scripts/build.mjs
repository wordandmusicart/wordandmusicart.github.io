import { copyFile, mkdir, rm } from "node:fs/promises";

const root = new URL("../", import.meta.url);
const dist = new URL("../dist/", import.meta.url);

const publicFiles = [
  "CNAME",
  "index.html",
  "robots.txt",
  "sitemap.xml",
  "styles.css",
  "assets/FixelText-Regular.woff2",
  "assets/TembravaDisplay-Regular.woff2",
  "assets/apple-touch-icon.png",
  "assets/concert-desktop.png",
  "assets/concert-mobile.png",
  "assets/favicon-192.png",
  "assets/favicon-32.png",
  "assets/favicon-512.png",
  "assets/word-and-music-logo-black.svg",
  "assets/word-and-music-logo-white.svg",
  "assets/word-and-music-preview.png",
];

await rm(dist, { recursive: true, force: true });

for (const path of publicFiles) {
  const destination = new URL(path, dist);
  await mkdir(new URL(".", destination), { recursive: true });
  await copyFile(new URL(path, root), destination);
}

console.log(`Built ${publicFiles.length} public files in dist/`);
