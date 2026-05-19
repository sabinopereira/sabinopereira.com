export type Mission = {
  id: string;
  title: string;
  description: string;
  mode: "coragem" | "social" | "familia" | "saude" | "recomeco";
  intensity: "leve" | "real" | "coragem";
  costTier: "gratis" | "low_cost" | "medio" | "especial";
  durationLabel: "micro" | "leve" | "realista" | "plano" | "maior";
  estimatedMinutes: number;
  accessibilityNote: string;
  reason: string;
};

export const todayMission: Mission = {
  id: "uma-mensagem-simples",
  title: "Uma mensagem simples",
  description:
    "Envia uma mensagem curta a alguem: lembrei-me de ti hoje. Como estas?",
  mode: "social",
  intensity: "leve",
  costTier: "gratis",
  durationLabel: "micro",
  estimatedMinutes: 5,
  accessibilityNote: "Texto, audio ou chamada. O formato e teu.",
  reason:
    "Escolhida porque hoje pede uma acao pequena, social e sem custo."
};

export const upcomingPlans = [
  {
    id: "walk-saturday",
    title: "Volta curta no sabado",
    circle: "Amigos de Lisboa",
    time: "Sabado, 10:00",
    place: "Jardim publico",
    costTier: "gratis",
    durationLabel: "plano",
    participants: "3/6",
    deadline: "fecha hoje as 18:00",
    accessibility: "percurso curto, bancos perto"
  },
  {
    id: "family-table",
    title: "Mesa com pergunta",
    circle: "Familia",
    time: "Domingo, jantar",
    place: "Casa",
    costTier: "gratis",
    durationLabel: "realista",
    participants: "2/5",
    deadline: "fecha amanha as 12:00",
    accessibility: "sentado, baixo ruido"
  }
];

export const circles = [
  {
    id: "family",
    name: "Familia",
    type: "Familia",
    members: 4,
    next: "Mesa com pergunta",
    role: "Membro"
  },
  {
    id: "friends",
    name: "Amigos de Lisboa",
    type: "Amigos",
    members: 7,
    next: "Volta curta no sabado",
    role: "Anfitriao"
  }
];
