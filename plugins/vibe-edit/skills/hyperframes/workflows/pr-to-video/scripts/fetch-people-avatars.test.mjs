import assert from "node:assert/strict";
import { test } from "node:test";
import { spawnSync } from "node:child_process";
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, existsSync, rmSync, symlinkSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const SCRIPT = fileURLToPath(new URL("./fetch-people-avatars.mjs", import.meta.url));
function run(avatarUrl, responses, initialState) {
  const dir = mkdtempSync(join(tmpdir(), "avatar-redirect-test-"));
  try {
    const people = join(dir, "people.json");
    const originalPeople = join(dir, "original-people.json");
    const calls = join(dir, "calls.json");
    const preload = join(dir, "mock.mjs");
    const project = join(dir, "project");
    const external = join(dir, "outside");
    const externalFile = join(external, "example.png");
    const output = join(project, "assets/example.png");
    mkdirSync(project);
    mkdirSync(external);
    writeFileSync(externalFile, "");
    if (initialState === "linked-parent") symlinkSync(external, join(project, "assets"));
    if (["linked-leaf", "cached", "empty"].includes(initialState)) mkdirSync(join(project, "assets"));
    if (initialState === "linked-leaf") symlinkSync(externalFile, output);
    if (initialState === "cached") writeFileSync(output, "existing-avatar");
    if (initialState === "empty") writeFileSync(output, "");
    writeFileSync(people, JSON.stringify({ people: [{ login: "example", avatarUrl }] }));
    writeFileSync(preload, `import {writeFileSync,unlinkSync,symlinkSync,renameSync} from 'node:fs';
const responses=${JSON.stringify(responses)}; const calls=[];
globalThis.fetch=async (url, options)=>{
  calls.push({url:String(url),redirect:options.redirect});
  writeFileSync(${JSON.stringify(calls)},JSON.stringify(calls));
  const step=responses[calls.length-1];
  if(!step || step.url!==String(url)) throw Error('Unexpected mocked request');
  if(step.replaceOutput){unlinkSync(${JSON.stringify(output)});symlinkSync(${JSON.stringify(externalFile)},${JSON.stringify(output)});}
  if(step.replacePeople){renameSync(${JSON.stringify(people)},${JSON.stringify(originalPeople)});symlinkSync(${JSON.stringify(externalFile)},${JSON.stringify(people)});}
  return new Response(step.body || null,{status:step.status,headers:step.location?{location:step.location}:{}});
};`);
    const result = spawnSync(process.execPath, ["--import", preload, SCRIPT, "--people", people, "--project-dir", project], { encoding: "utf8" });
    assert.equal(result.status, 0, result.stderr);
    return {
      calls: existsSync(calls) ? JSON.parse(readFileSync(calls, "utf8")) : [],
      bytes: existsSync(output) ? readFileSync(output, "utf8") : null,
      person: JSON.parse(readFileSync(existsSync(originalPeople) ? originalPeople : people, "utf8")).people[0],
      externalBytes: readFileSync(externalFile, "utf8"),
    };
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
}
const github = "https://github.com/example.png";
const avatar = "https://avatars.githubusercontent.com/u/1";

test("follows a GitHub avatar redirect only after checking the next host", () => {
  const result = run(github, [{url:github,status:302,location:avatar},{url:avatar,status:200,body:"fixture-png"}]);
  assert.deepEqual(result.calls, [{url:github,redirect:"manual"},{url:avatar,redirect:"manual"}]);
  assert.equal(result.bytes,"fixture-png");
  assert.equal(result.person.avatarFetched,true);
});
test("rejects an off-host redirect before sending the next request", () => {
  const result = run(github, [{url:github,status:302,location:"http://127.0.0.1/private"}]);
  assert.deepEqual(result.calls,[{url:github,redirect:"manual"}]);
  assert.equal(result.bytes,null);
  assert.equal(result.person.avatarFetched,false);
});
test("resolves a relative redirect on the approved host", () => {
  const next="https://github.com/avatar.png";
  const result=run(github,[{url:github,status:307,location:"/avatar.png"},{url:next,status:200,body:"fixture"}]);
  assert.equal(result.calls.length,2);
  assert.equal(result.calls[1].url,next);
  assert.equal(result.bytes,"fixture");
});
test("refuses a non-GitHub starting URL without network access", () => {
  const result=run("https://example.invalid/avatar.png",[]);
  assert.deepEqual(result.calls,[]);
  assert.equal(result.bytes,null);
});
test("redirect without Location is not saved as an avatar", () => {
  const result=run(github,[{url:github,status:302}]);
  assert.equal(result.bytes,null);
  assert.equal(result.person.avatarFetched,false);
});
test("redirect loops stop after five hops", () => {
  const result=run(github,Array.from({length:8},()=>({url:github,status:302,location:github})));
  assert.equal(result.calls.length,6);
  assert.equal(result.bytes,null);
  assert.equal(result.person.avatarFetched,false);
});
for (const initialState of ["linked-parent", "linked-leaf"]) {
  test(`refuses ${initialState} output without touching the outside file`, () => {
    const result=run(github,[],initialState);
    assert.deepEqual(result.calls,[]);
    assert.equal(result.externalBytes,"");
    assert.equal(result.person.avatarFetched,false);
  });
}
test("an output replaced during fetch cannot redirect the descriptor write", () => {
  const result=run(github,[{url:github,status:200,body:"downloaded-avatar",replaceOutput:true}]);
  assert.equal(result.externalBytes,"");
  assert.equal(result.person.avatarFetched,false);
});
test("reuses an existing nonempty regular avatar without a network call", () => {
  const result=run(github,[],"cached");
  assert.deepEqual(result.calls,[]);
  assert.equal(result.bytes,"existing-avatar");
  assert.equal(result.person.avatarFetched,true);
});
test("preserves an existing empty regular file rather than overwriting it", () => {
  const result=run(github,[],"empty");
  assert.deepEqual(result.calls,[]);
  assert.equal(result.bytes,"");
  assert.equal(result.person.avatarFetched,false);
});
test("people pathname replacement cannot redirect the final metadata write", () => {
  const result=run(github,[{url:github,status:200,body:"downloaded-avatar",replacePeople:true}]);
  assert.equal(result.externalBytes,"");
  assert.equal(result.person.avatarFetched,true);
});
