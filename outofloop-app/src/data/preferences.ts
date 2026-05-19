import type {
  CostTier,
  MissionIntensity,
  MissionMode
} from "./missions.generated";

export type AppPreferences = {
  primaryMode: MissionMode;
  secondaryMode?: MissionMode;
  preferredIntensity: MissionIntensity;
  preferredCostTier: CostTier;
  privateFirst: boolean;
  hasChildren: boolean;
  maxMinutes: number;
  accessibility: string[];
};

export const defaultPreferences: AppPreferences = {
  primaryMode: "social",
  secondaryMode: "recomeco",
  preferredIntensity: "leve",
  preferredCostTier: "gratis",
  privateFirst: true,
  hasChildren: false,
  maxMinutes: 15,
  accessibility: ["Locais calmos"]
};
