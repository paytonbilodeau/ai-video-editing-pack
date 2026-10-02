import assert from "node:assert/strict";
import test from "node:test";

import { planSummary, validatePlan } from "../tools/motion_plan.mjs";


function validPlan() {
  return {
    schema: "ai-mentorship-motion-plan-v1",
    title: "Neutral plan",
    fps: 30,
    width: 1920,
    height: 1080,
    beats: [
      {
        id: "one",
        startFrame: 0,
        endFrame: 45,
        meaning: "Explain one relationship.",
        lane: "designed_explanation",
        caption: "ONE CLEAR IDEA",
        factIds: [],
        asset: { kind: "original_design", source: "none", rights: "original" }
      },
      {
        id: "two",
        startFrame: 45,
        endFrame: 90,
        meaning: "Show approved evidence.",
        lane: "evidence",
        caption: "CHECK THE SOURCE",
        factIds: ["fact-01"],
        asset: {
          kind: "recorded_evidence",
          source: "assets/source-clip.mp4",
          rights: "user_supplied"
        }
      }
    ]
  };
}

test("valid plan passes and produces deterministic summary", () => {
  const plan = validPlan();
  assert.deepEqual(validatePlan(plan), []);
  assert.deepEqual(planSummary(plan), {
    ok: true,
    schema: "ai-mentorship-motion-plan-v1",
    title: "Neutral plan",
    beatCount: 2,
    durationFrames: 90,
    durationSeconds: 3,
    lanes: ["designed_explanation", "evidence"]
  });
});

test("overlap and duplicate beat IDs fail", () => {
  const plan = validPlan();
  plan.beats[1].id = "one";
  plan.beats[1].startFrame = 30;
  const errors = validatePlan(plan);
  assert.ok(errors.some((item) => item.includes("unique")));
  assert.ok(errors.some((item) => item.includes("overlaps")));
});

test("evidence needs an authorized source and evidence asset", () => {
  const plan = validPlan();
  plan.beats[1].asset = {
    kind: "original_design",
    source: "none",
    rights: "original"
  };
  const errors = validatePlan(plan);
  assert.ok(errors.some((item) => item.includes("recorded evidence")));
  assert.ok(errors.some((item) => item.includes("source label")));
});

test("absolute and parent asset paths fail", () => {
  const plan = validPlan();
  plan.beats[1].asset.source = "../private/source.mp4";
  assert.ok(validatePlan(plan).some((item) => item.includes("safe relative")));
  plan.beats[1].asset.source = "D:/Accounts/example/source.mp4";
  assert.ok(validatePlan(plan).some((item) => item.includes("safe relative")));
});
