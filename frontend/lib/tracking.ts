/**
 * Turning a status column into a progress tracker.
 *
 * This is the whole of the interpretation between what the database records
 * and what a citizen is shown, which is why it lives on its own with no React
 * and no network calls: it is the part worth testing directly.
 *
 * The rule it exists to enforce: a stage is only ever marked done if the
 * application really passed through it. Status history is written by a
 * database trigger on every transition, so "done" means there is a row saying
 * so. Where the application skipped a stage, the tracker leaves it pending
 * rather than back-filling a plausible-looking tick — a progress tracker that
 * invents progress is worse than no tracker at all.
 */

import type { ApplicationStatus, StatusHistoryRow } from "@/lib/types";

export interface TrackerStage {
  key: string;
  label: string;
  detail: string;
  statuses: ApplicationStatus[];
}

export const STAGES: TrackerStage[] = [
  {
    key: "submitted",
    label: "Submitted",
    detail: "Your application has been received.",
    statuses: ["SUBMITTED"],
  },
  {
    key: "screening",
    label: "Grid check",
    detail: "Your requested capacity is simulated against the local network.",
    statuses: ["ASSESSING"],
  },
  {
    // ASSESSED belongs here, not under the grid check. It means the screening
    // finished and nobody has decided anything yet — which is to say the
    // application is with the DISCOM, and the DISCOM's own review queue agrees.
    // Applications created before the backend started landing on
    // UNDER_DISCOM_REVIEW still carry it, and they are in exactly that state.
    key: "review",
    label: "DISCOM review",
    detail: "A reviewer at the distribution company is considering it.",
    statuses: ["ASSESSED", "UNDER_DISCOM_REVIEW", "ENGINEERING_REVIEW"],
  },
  {
    key: "decision",
    label: "Decision",
    detail: "The DISCOM approves or rejects the connection.",
    statuses: ["APPROVED", "REJECTED"],
  },
  {
    key: "installer",
    label: "Installer chosen",
    detail: "You pick a verified installer and book a site visit.",
    statuses: ["VENDOR_SELECTED"],
  },
  {
    key: "installation",
    label: "Installation",
    detail: "Your system is being installed.",
    statuses: ["INSTALLING", "INSTALLED"],
  },
  {
    key: "verified",
    label: "Verified",
    detail: "The DISCOM has verified the completed installation.",
    statuses: ["VERIFIED"],
  },
];

const STAGE_OF: Record<string, number> = Object.fromEntries(
  STAGES.flatMap((s, i) => s.statuses.map((st) => [st, i]))
);

/** Nothing further happens on its own, so there is nothing left to poll for. */
export const TERMINAL: ApplicationStatus[] = ["REJECTED", "CANCELLED", "VERIFIED"];

export type StageState = "done" | "current" | "pending" | "stopped" | "passed";

/**
 * How the DISCOM's decision went, once there is one.
 *
 * The tracker used to name only the bad outcome: a rejection said "Rejected by
 * the DISCOM", while an approval fell through to the stage's own label and read
 * as the word "Decision". An applicant refreshing the page to find out whether
 * they had been approved was shown a heading that did not tell them.
 */
export type Outcome = "approved" | "rejected" | "cancelled" | null;

export function outcomeFor(status: ApplicationStatus): Outcome {
  if (status === "REJECTED") return "rejected";
  if (status === "CANCELLED") return "cancelled";
  // Everything downstream of approval implies the approval happened.
  if (
    status === "APPROVED" ||
    status === "VENDOR_SELECTED" ||
    status === "INSTALLING" ||
    status === "INSTALLED" ||
    status === "VERIFIED"
  ) {
    return "approved";
  }
  return null;
}

export interface ResolvedStage extends TrackerStage {
  state: StageState;
  /** When the application entered this stage, or null if it never did. */
  at: string | null;
}

/**
 * Which stage a status sits in.
 *
 * A cancelled application stops where a decision would have been made: it did
 * reach the DISCOM, and nothing after that will happen.
 */
export function stageIndexFor(status: ApplicationStatus): number {
  if (status === "DRAFT") return -1;
  if (status === "CANCELLED") return STAGE_OF["APPROVED"];
  return STAGE_OF[status] ?? 0;
}

export function isHalted(status: ApplicationStatus): boolean {
  return status === "REJECTED" || status === "CANCELLED";
}

export function resolveStages(
  status: ApplicationStatus,
  history: StatusHistoryRow[]
): ResolvedStage[] {
  const current = stageIndexFor(status);
  const halted = isHalted(status);

  // Earliest moment the application entered each stage. Earliest, not latest,
  // so a re-assessment that revisits a stage does not rewrite when it was
  // first reached.
  const reachedAt = new Map<number, string>();
  for (const row of history) {
    const index = STAGE_OF[row.to_status];
    if (index === undefined) continue;
    const seen = reachedAt.get(index);
    if (seen === undefined || row.created_at < seen) reachedAt.set(index, row.created_at);
  }

  const decision = STAGES.findIndex((s) => s.key === "decision");
  const approved = outcomeFor(status) === "approved";

  return STAGES.map((stage, i) => {
    const at = reachedAt.get(i) ?? null;
    let state: StageState;
    if (halted && i === current) state = "stopped";
    else if (halted && i > current) state = "pending";
    // An approval resolves the decision stage rather than sitting inside it:
    // the DISCOM has finished, and what is outstanding is the applicant's next
    // move. Marking it "current" would say the review is still running.
    else if (approved && i === decision) state = "passed";
    else if (i < current) state = "done";
    else if (i === current) state = "current";
    else state = "pending";
    return { ...stage, state, at };
  });
}
