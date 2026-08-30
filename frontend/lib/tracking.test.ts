import { describe, expect, it } from "vitest";

import { isHalted, outcomeFor, resolveStages, stageIndexFor, STAGES, TERMINAL } from "./tracking";
import type { ApplicationStatus, StatusHistoryRow } from "./types";

let seq = 0;
function row(to: ApplicationStatus, at: string): StatusHistoryRow {
  return {
    id: `h${seq++}`,
    from_status: null,
    to_status: to,
    note: null,
    created_at: at,
  };
}

const index = (key: string) => STAGES.findIndex((s) => s.key === key);
const stateOf = (stages: ReturnType<typeof resolveStages>, key: string) =>
  stages[index(key)].state;

describe("stageIndexFor", () => {
  it("puts a draft before the first stage", () => {
    expect(stageIndexFor("DRAFT")).toBe(-1);
  });

  it("shows the grid check only while it is actually running", () => {
    expect(stageIndexFor("ASSESSING")).toBe(index("screening"));
  });

  it("puts an assessed application with the DISCOM, not at a decision", () => {
    // ASSESSED is the landing state for applications created before the
    // backend started using UNDER_DISCOM_REVIEW. Both mean the same thing to
    // an applicant: it is waiting on the DISCOM.
    expect(stageIndexFor("ASSESSED")).toBe(index("review"));
    expect(stageIndexFor("UNDER_DISCOM_REVIEW")).toBe(index("review"));
    expect(stageIndexFor("UNDER_DISCOM_REVIEW")).toBeLessThan(index("decision"));
  });

  it("never reports an assessed application as decided", () => {
    for (const s of ["ASSESSED", "UNDER_DISCOM_REVIEW"] as ApplicationStatus[]) {
      const stages = resolveStages(s, []);
      expect(stateOf(stages, "decision")).toBe("pending");
    }
  });

  it("stops a cancelled application where the decision would have been", () => {
    expect(stageIndexFor("CANCELLED")).toBe(index("decision"));
  });
});

describe("resolveStages", () => {
  const history = [
    row("SUBMITTED", "2026-01-01T09:00:00Z"),
    row("ASSESSING", "2026-01-01T09:00:20Z"),
    row("UNDER_DISCOM_REVIEW", "2026-01-01T09:00:40Z"),
  ];

  it("reads a legacy ASSESSED row as waiting on the DISCOM", () => {
    const legacy = [
      row("SUBMITTED", "2026-01-01T09:00:00Z"),
      row("ASSESSING", "2026-01-01T09:00:20Z"),
      row("ASSESSED", "2026-01-01T09:00:40Z"),
    ];
    const stages = resolveStages("ASSESSED", legacy);

    expect(stateOf(stages, "screening")).toBe("done");
    expect(stateOf(stages, "review")).toBe("current");
    expect(stages[index("review")].at).toBe("2026-01-01T09:00:40Z");
  });

  it("marks passed stages done, the current one current, the rest pending", () => {
    const stages = resolveStages("UNDER_DISCOM_REVIEW", history);

    expect(stateOf(stages, "submitted")).toBe("done");
    expect(stateOf(stages, "screening")).toBe("done");
    expect(stateOf(stages, "review")).toBe("current");
    expect(stateOf(stages, "decision")).toBe("pending");
    expect(stateOf(stages, "verified")).toBe("pending");
  });

  it("timestamps a stage from the moment it was actually entered", () => {
    const stages = resolveStages("UNDER_DISCOM_REVIEW", history);

    expect(stages[index("submitted")].at).toBe("2026-01-01T09:00:00Z");
    expect(stages[index("screening")].at).toBe("2026-01-01T09:00:20Z");
  });

  it("keeps the first visit's timestamp when a stage is revisited", () => {
    // A re-assessment sends the application back through screening. The tracker
    // should still say when it first got there, not when it last did.
    const revisited = [
      ...history,
      row("ASSESSING", "2026-02-02T11:00:00Z"),
      row("UNDER_DISCOM_REVIEW", "2026-02-02T11:00:30Z"),
    ];

    expect(resolveStages("UNDER_DISCOM_REVIEW", revisited)[index("screening")].at).toBe(
      "2026-01-01T09:00:20Z"
    );
  });

  it("leaves a skipped stage without a timestamp rather than inventing one", () => {
    // Straight from submission to a decision: screening has no row, so it has
    // no time. It is still drawn as passed, but it cannot claim a moment.
    const skipped = [
      row("SUBMITTED", "2026-01-01T09:00:00Z"),
      row("APPROVED", "2026-01-03T10:00:00Z"),
    ];
    const stages = resolveStages("APPROVED", skipped);

    expect(stateOf(stages, "screening")).toBe("done");
    expect(stages[index("screening")].at).toBeNull();
    expect(stages[index("decision")].at).toBe("2026-01-03T10:00:00Z");
  });

  it("never reports a stage as reached without a history row saying so", () => {
    const stages = resolveStages("SUBMITTED", [row("SUBMITTED", "2026-01-01T09:00:00Z")]);
    const timestamped = stages.filter((s) => s.at !== null).map((s) => s.key);

    expect(timestamped).toEqual(["submitted"]);
  });

  it("halts at the decision on rejection, and shows nothing after it as reached", () => {
    const rejected = [
      row("SUBMITTED", "2026-01-01T09:00:00Z"),
      row("UNDER_DISCOM_REVIEW", "2026-01-01T09:01:00Z"),
      row("REJECTED", "2026-01-04T14:00:00Z"),
    ];
    const stages = resolveStages("REJECTED", rejected);

    expect(stateOf(stages, "review")).toBe("done");
    expect(stateOf(stages, "decision")).toBe("stopped");
    expect(stateOf(stages, "installer")).toBe("pending");
    expect(stateOf(stages, "verified")).toBe("pending");
    // Crucially, nothing downstream is "current" — there is no next step.
    expect(stages.filter((s) => s.state === "current")).toHaveLength(0);
  });

  it("treats a cancelled application as halted too", () => {
    expect(isHalted("CANCELLED")).toBe(true);
    expect(stateOf(resolveStages("CANCELLED", []), "decision")).toBe("stopped");
  });

  it("shows every stage complete once verified", () => {
    const stages = resolveStages("VERIFIED", []);

    expect(stateOf(stages, "verified")).toBe("current");
    // The decision reads "passed" rather than "done": it was an approval, and
    // that is the one step whose outcome the applicant came to check.
    expect(stateOf(stages, "decision")).toBe("passed");
    expect(
      stages.slice(0, -1).every((s) => s.state === "done" || s.state === "passed")
    ).toBe(true);
  });

  it("copes with an empty history without claiming anything happened", () => {
    const stages = resolveStages("SUBMITTED", []);

    expect(stages.every((s) => s.at === null)).toBe(true);
    expect(stateOf(stages, "submitted")).toBe("current");
  });
});

describe("TERMINAL", () => {
  it("covers every status from which nothing further happens on its own", () => {
    // Polling stops on these. Missing one means a tracker that polls forever.
    expect(TERMINAL).toEqual(
      expect.arrayContaining(["REJECTED", "CANCELLED", "VERIFIED"] as ApplicationStatus[])
    );
  });

  it("does not include a status that is still waiting on someone", () => {
    for (const status of [
      "SUBMITTED",
      "ASSESSING",
      "UNDER_DISCOM_REVIEW",
      "APPROVED",
      "INSTALLING",
    ] as ApplicationStatus[]) {
      expect(TERMINAL).not.toContain(status);
    }
  });
});


describe("naming the decision", () => {
  // The bug: a rejection said "Rejected by the DISCOM" while an approval fell
  // through to the stage label and read as the single word "Decision" — on the
  // one screen opened to find out whether the application was approved.
  it("names an approval", () => {
    expect(outcomeFor("APPROVED")).toBe("approved");
  });

  it("still counts as approved further down the process", () => {
    for (const status of [
      "VENDOR_SELECTED",
      "INSTALLING",
      "INSTALLED",
      "VERIFIED",
    ] as const) {
      expect(outcomeFor(status)).toBe("approved");
    }
  });

  it("names a rejection and a cancellation separately", () => {
    expect(outcomeFor("REJECTED")).toBe("rejected");
    expect(outcomeFor("CANCELLED")).toBe("cancelled");
  });

  it("claims no outcome before the DISCOM has decided", () => {
    for (const status of [
      "DRAFT",
      "SUBMITTED",
      "ASSESSING",
      "ASSESSED",
      "UNDER_DISCOM_REVIEW",
    ] as const) {
      expect(outcomeFor(status)).toBeNull();
    }
  });

  it("marks the decision stage passed on approval, stopped on rejection", () => {
    expect(stateOf(resolveStages("APPROVED", []), "decision")).toBe("passed");
    expect(stateOf(resolveStages("REJECTED", []), "decision")).toBe("stopped");
  });

  it("does not strand an approved application inside the decision stage", () => {
    // "current" on the decision stage says the DISCOM is still deciding.
    const stages = resolveStages("APPROVED", []);
    expect(stateOf(stages, "decision")).not.toBe("current");
  });
});
