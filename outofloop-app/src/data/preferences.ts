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
  hasPets: boolean;
  likedActivities: string[];
  maxMinutes: number;
  accessibility: string[];
  availability: string[];
  usualEnergy: "baixa" | "media" | "alta";
  socialComfort: "sozinho" | "uma_pessoa" | "grupo_pequeno" | "grupo";
  activityCompanyPreference:
    | "sozinho"
    | "uma_pessoa"
    | "grupo_pequeno"
    | "grupo_aberto"
    | "depende";
  soloIdeasPreference: "sim" | "as_vezes" | "com_pessoas";
  smartHelp: {
    suggestMissions: boolean;
    improveCreatedPlans: boolean;
    summarizeCircleFeedback: boolean;
    useHistoryForRecommendations: boolean;
    flagDiscomfortSignals: boolean;
  };
};

export const defaultPreferences: AppPreferences = {
  routineFocus: ["Sair mais de casa", "Conhecer melhor pessoas a minha volta"],
  primaryMode: "social",
  secondaryMode: "recomeco",
  preferredIntensity: "leve",
  preferredCostTier: "gratis",
  privateFirst: true,
  hasChildren: false,
  hasPets: false,
  likedActivities: ["Caminhar", "Cafe", "Corrida"],
  maxMinutes: 15,
  accessibility: ["Locais calmos"],
  availability: ["Fim de tarde", "Fim de semana"],
  usualEnergy: "media",
  socialComfort: "uma_pessoa",
  activityCompanyPreference: "depende",
  soloIdeasPreference: "sim",
  smartHelp: {
    suggestMissions: true,
    improveCreatedPlans: true,
    summarizeCircleFeedback: true,
    useHistoryForRecommendations: true,
    flagDiscomfortSignals: true
  }
};
