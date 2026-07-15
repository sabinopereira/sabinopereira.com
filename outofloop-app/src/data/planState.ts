export type PlanStatus = "open" | "accepted" | "checkedIn" | "dismissed";

export type PlanResponse = {
  detailsViews?: number;
  notNowReason?: string;
  safetyConcern?: "reported" | "blocked";
};

export type PlanStatuses = Record<string, PlanStatus>;
export type PlanResponses = Record<string, PlanResponse>;
