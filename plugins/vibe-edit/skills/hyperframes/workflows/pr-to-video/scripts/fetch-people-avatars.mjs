#!/usr/bin/env node
// Step 1 — contributor avatar fetch (NETWORK; orchestrator-invoked).
//
// The counterpart to ingest.mjs: ingest is a pure offline transform, THIS is the
// one network step on the people front. It reads the people list ingest produced
// and downloads each contributor's GitHub avatar into assets/<login>.png,
// then rewrites people.json with `avatarFetched` flags so downstream (story-design)
// knows which avatars actually exist.
//
// Avatars + a credits/shipped-by scene are the ONE place the faceless default is
// relaxed. They are an OPTIONAL enhancement, so this script is best-effort:
//   - a missing/deleted user, a network blip, an offline run → log + skip
//   - it ALWAYS exits 0 (a failed avatar must never block the build)
//
// Network is constrained on purpose: only https GitHub avatar hosts are fetched
// (SSRF guard), and bytes are only ever written under the project dir (no path
// traversal), so a tampered people.json can't redirect the fetch or the write.
//
// Reads:
//   --people <path>      capture/extracted/people.json (from ingest.mjs)
// Writes:
//   assets/<login>.png    one per contributor whose avatar resolved
//   (rewrites people.json in place with avatarFetched: true/false)
//
// Flags: --project-dir .  --timeout 8000 (ms per request)
//   Avatars are written to <project-dir>/<person.avatarFile>, where avatarFile is
//   the project-root-relative "assets/<login>.png" — the SAME assets/ dir the frame
//   workers reference and assemble-index stages (lib/assets.mjs). Anchor on the
//   project root so the path stays under the project's assets/.
//
// Usage (orchestrator already cd'd into PROJECT_DIR, so --project-dir defaults to "."):
//   node fetch-people-avatars.mjs --people ./capture/extracted/people.json

import { existsSync, mkdirSync, readFileSync, writeFileSync, writeSync, ftruncateSync, lstatSync, realpathSync, openSync, closeSync, fstatSync, unlinkSync } from "node:fs";
import { resolve, join, dirname, basename, relative, sep } from "node:path";

const argv = process.argv.slice(2);
const flag = (name, def) => {
  const i = argv.indexOf(`--${name}`);
  return i >= 0 && i + 1 < argv.length ? argv[i + 1] : def;
};

const peoplePath = resolve(flag("people", "./capture/extracted/people.json"));
const projectDir = resolve(flag("project-dir", "."));
const TIMEOUT = parseInt(flag("timeout", "8000"), 10);

// SSRF guard: avatars only ever come from GitHub's avatar hosts, so refuse any
// other URL rather than fetching whatever string people.json happens to carry.
// `github.com/<login>.png` redirects to avatars.githubusercontent.com. Check
// every hop before fetching it, rather than trusting an automatic redirect.
const AVATAR_HOSTS = new Set(["avatars.githubusercontent.com", "github.com", "www.github.com"]);
function isAllowedAvatarUrl(u) {
  let parsed;
  try {
    parsed = new URL(u);
  } catch {
    return false;
  }
  if (parsed.protocol !== "https:") return false;
  const host = parsed.hostname.toLowerCase();
  return AVATAR_HOSTS.has(host) || host.endsWith(".githubusercontent.com");
}

async function fetchAllowedAvatar(url, signal) {
  for (let redirects = 0; ; redirects++) {
    if (!isAllowedAvatarUrl(url)) throw new Error("avatar redirect is not a GitHub avatar URL");
    const response = await fetch(url, {
      signal,
      redirect: "manual",
      headers: { "User-Agent": "hyperframes-pr-to-video" },
    });
    if (![301, 302, 303, 307, 308].includes(response.status)) return response;
    const location = response.headers.get("location");
    await response.body?.cancel();
    if (!location) throw new Error("avatar redirect has no Location");
    if (redirects >= 5) throw new Error("too many avatar redirects");
    url = new URL(location, url).href;
  }
}

// Path guard: the written file must stay inside the project dir, so a crafted
// avatarFile ("../../etc/…") can't escape via join().
function isUnderProject(p) {
  const r = resolve(p);
  return r === projectDir || r.startsWith(projectDir + sep);
}

function reserveAvatar(dest) {
  mkdirSync(projectDir, { recursive: true });
  const root = realpathSync(projectDir);
  let parent = root;
  for (const part of relative(projectDir, dirname(dest)).split(sep).filter(Boolean)) {
    const next = join(parent, part);
    try { mkdirSync(next); } catch (error) { if (error.code !== "EEXIST") throw error; }
    parent = realpathSync(next);
    if (parent !== root && !parent.startsWith(root + sep)) throw new Error("avatar parent escapes the project dir");
  }
  const file = join(parent, basename(dest));
  let existing;
  try { existing = lstatSync(file); } catch (error) { if (error.code !== "ENOENT") throw error; }
  if (existing?.isSymbolicLink() || (existing && !existing.isFile())) throw new Error("refusing linked or non-file avatar output");
  if (existing?.size > 0) return { cached: true };
  // Reserve a new file before the asynchronous fetch. Existing empty files are
  // preserved; remove a failed cache explicitly before retrying it.
  const fd = openSync(file, "wx");
  return { file, fd, identity: fstatSync(fd) };
}

function stillOwned(output) {
  try {
    const current = lstatSync(output.file);
    return current.isFile() && current.dev === output.identity.dev && current.ino === output.identity.ino;
  } catch { return false; }
}

let peopleFd;
// Soft-exit helper — avatars are optional, so every early-out is exit 0.
function softExit(msg) {
  if (peopleFd !== undefined) closeSync(peopleFd);
  console.log(`• fetch-avatars: ${msg}`);
  process.exit(0);
}

if (!existsSync(peoplePath)) softExit(`no people.json at ${peoplePath} — skipping (no avatars)`);

let doc;
try {
  // Keep the originally selected file open across network awaits. Replacing
  // its pathname must not redirect the final flag update into another file.
  peopleFd = openSync(peoplePath, "r+");
  doc = JSON.parse(readFileSync(peopleFd, "utf8"));
} catch (e) {
  softExit(`people.json unreadable (${e.message}) — skipping`);
}

const people = Array.isArray(doc.people) ? doc.people : [];
if (!people.length) softExit("no contributors in people.json — skipping");

async function fetchOne(person) {
  const { login, avatarUrl } = person;
  if (!login || !avatarUrl) return "skip";
  if (!isAllowedAvatarUrl(avatarUrl)) {
    person.avatarFetched = false;
    console.log(`  (skip avatar @${login}: not a GitHub avatar URL)`);
    return "fail";
  }
  // avatarFile is project-root-relative ("assets/<login>.png"); anchor on the
  // project root so it stays under the project's assets/ dir.
  const dest = join(projectDir, person.avatarFile || `assets/${login}.png`);
  if (!isUnderProject(dest)) {
    person.avatarFetched = false;
    console.log(`  (skip avatar @${login}: avatar path escapes the project dir)`);
    return "fail";
  }
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), TIMEOUT);
  let output;
  let saved = false;
  try {
    output = reserveAvatar(dest);
    if (output.cached) {
      person.avatarFetched = true;
      return "cached";
    }
    const res = await fetchAllowedAvatar(avatarUrl, ctrl.signal);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const buf = Buffer.from(await res.arrayBuffer());
    if (!buf.length) throw new Error("empty body");
    if (!stillOwned(output)) throw new Error("avatar output changed during download");
    writeFileSync(output.fd, buf);
    saved = true;
    person.avatarFetched = true;
    return "ok";
  } catch (e) {
    person.avatarFetched = false;
    console.log(`  (skip avatar @${login}: ${e.message})`);
    return "fail";
  } finally {
    clearTimeout(timer);
    if (output?.fd !== undefined) {
      closeSync(output.fd);
      if (!saved && stillOwned(output)) unlinkSync(output.file);
    }
  }
}

let ok = 0;
let cached = 0;
let fail = 0;
// Sequential keeps it simple and gentle on github.com; the list is tiny (a PR's
// contributors), so latency is not a concern.
for (const person of people) {
  const r = await fetchOne(person);
  if (r === "ok") ok++;
  else if (r === "cached") cached++;
  else if (r === "fail") fail++;
}

// Persist avatarFetched flags so story-design can reference only real avatars.
try {
  const bytes = Buffer.from(JSON.stringify(doc, null, 2) + "\n");
  let offset = 0;
  while (offset < bytes.length) offset += writeSync(peopleFd, bytes, offset, bytes.length - offset, offset);
  ftruncateSync(peopleFd, bytes.length);
} catch (e) {
  console.log(`  (warn: could not rewrite people.json flags: ${e.message})`);
} finally {
  closeSync(peopleFd);
}

console.log(
  `✓ fetch-avatars: ${ok + cached}/${people.length} avatar(s) in assets/` +
    ` (${ok} new, ${cached} cached, ${fail} failed)`,
);
process.exit(0);
