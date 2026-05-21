import type {
  CostTier,
  MissionIntensity,
  MissionMode
} from "./missions.generated";

export type AppPreferences = {
  routineFocus: string[];
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
  routineFocus: ["Sair mais de casa", "Conhecer melhor pessoas a minha volta"],
  primaryMode: "social",
  secondaryMode: "recomeco",
  preferredIntensity: "leve",
  preferredCostTier: "gratis",
  privateFirst: true,
  hasChildren: false,
  maxMinutes: 15,
  accessibility: ["Locais calmos"]
};
