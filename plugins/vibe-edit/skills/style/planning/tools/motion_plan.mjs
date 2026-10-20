#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

export const PLAN_SCHEMA = "ai-mentorship-motion-plan-v1";
export const LANES = new Set([
  "designed_explanation",
  "evidence",
  "physical_metaphor",
  "restrained_hybrid"
]);
const RIGHTS = new Set(["original", "user_supplied", "licensed", "official"]);
const ASSET_KINDS = new Set([
  "original_design",
  "recorded_evidence",
  "official_asset",
  "authorized_image",
  "authorized_video"
]);

function isSafeAssetSource(value) {
  if (value === "none") return true;
  if (typeof value !== "string" || !value.trim()) return false;
  const normalized = value.replaceAll("\\", "/");
  return !(
    path.posix.isAbsolute(normalized) ||
    normalized === ".." ||
    normalized.startsWith("../") ||
    /^[A-Za-z]:\//.test(normalized) ||
    normalized.startsWith("~/") ||
    normalized.startsWith("file://")
  );
}

export function validatePlan(plan) {
  const errors = [];
  if (!plan || typeof plan !== "object" || Array.isArray(plan)) {
    return ["Plan must be one JSON object."];
  }
  if (plan.schema !== PLAN_SCHEMA) errors.push(`schema must be ${PLAN_SCHEMA}`);
  if (typeof plan.title !== "string" || !plan.title.trim()) errors.push("title is required");
  for (const [field, minimum] of [["fps", 1], ["width", 320], ["height", 320]]) {
    if (!Number.isInteger(plan[field]) || plan[field] < minimum) {
      errors.push(`${field} must be an integer of at least ${minimum}`);
    }
  }
  if (!Array.isArray(plan.beats) || plan.beats.length === 0) {
    errors.push("beats must contain at least one beat");
    return errors;
  }

  const ids = new Set();
  let priorEnd = 0;
  plan.beats.forEach((beat, index) => {
    const label = `beats[${index}]`;
    if (!beat || typeof beat !== "object" || Array.isArray(beat)) {
      errors.push(`${label} must be an object`);
      return;
    }
    if (typeof beat.id !== "string" || !beat.id.trim()) {
      errors.push(`${label}.id is required`);
    } else if (ids.has(beat.id)) {
      errors.push(`${label}.id must be unique`);
    } else {
      ids.add(beat.id);
    }
    if (!Number.isInteger(beat.startFrame) || !Number.isInteger(beat.endFrame)) {
      errors.push(`${label} frames must be integers`);
    } else {
      if (beat.startFrame < priorEnd) errors.push(`${label} overlaps the prior beat`);
      if (beat.endFrame <= beat.startFrame) errors.push(`${label} must have positive duration`);
      priorEnd = Math.max(priorEnd, beat.endFrame);
    }
    if (typeof beat.meaning !== "string" || !beat.meaning.trim()) {
      errors.push(`${label}.meaning is required`);
    }
    if (!LANES.has(beat.lane)) errors.push(`${label}.lane is invalid`);
    if (typeof beat.caption !== "string" || beat.caption.length > 90) {
      errors.push(`${label}.caption must be a string of at most 90 characters`);
    }
    if (!Array.isArray(beat.factIds) || beat.factIds.some((item) => typeof item !== "string")) {
      errors.push(`${label}.factIds must be an array of strings`);
    }
    const asset = beat.asset;
    if (!asset || typeof asset !== "object" || Array.isArray(asset)) {
      errors.push(`${label}.asset is required`);
    } else {
      if (!ASSET_KINDS.has(asset.kind)) errors.push(`${label}.asset.kind is invalid`);
      if (!RIGHTS.has(asset.rights)) errors.push(`${label}.asset.rights is invalid`);
      if (!isSafeAssetSource(asset.source)) errors.push(`${label}.asset.source must be a safe relative label`);
      if (beat.lane === "evidence" && !["recorded_evidence", "official_asset"].includes(asset.kind)) {
        errors.push(`${label} evidence lane needs recorded evidence or an official asset`);
      }
      if (beat.lane === "evidence" && asset.source === "none") {
        errors.push(`${label} evidence lane needs a source label`);
      }
    }
  });
  return errors;
}

export function planSummary(plan) {
  return {
    ok: true,
    schema: plan.schema,
    title: plan.title,
    beatCount: plan.beats.length,
    durationFrames: Math.max(...plan.beats.map((beat) => beat.endFrame)),
    durationSeconds: Number(
      (Math.max(...plan.beats.map((beat) => beat.endFrame)) / plan.fps).toFixed(3)
    ),
    lanes: [...new Set(plan.beats.map((beat) => beat.lane))].sort()
  };
}

function main(argv) {
  if (argv.length !== 1) {
    console.error("Usage: node tools/motion_plan.mjs PLAN.json");
    return 2;
  }
  try {
    const plan = JSON.parse(fs.readFileSync(argv[0], "utf8"));
    const errors = validatePlan(plan);
    if (errors.length) {
      console.error(JSON.stringify({ ok: false, errors }, null, 2));
      return 1;
    }
    console.log(JSON.stringify(planSummary(plan), null, 2));
    return 0;
  } catch (error) {
    console.error(JSON.stringify({ ok: false, errors: [String(error.message || error)] }, null, 2));
    return 1;
  }
}

if (path.resolve(process.argv[1] || "") === fileURLToPath(import.meta.url)) {
  process.exitCode = main(process.argv.slice(2));
}
