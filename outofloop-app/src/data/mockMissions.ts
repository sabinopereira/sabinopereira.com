export type UpcomingPlan = {
  id: string;
  title: string;
  circle: string;
  time: string;
  place: string;
  costTier: string;
  durationLabel: string;
  acceptedCount: number;
  capacity: number;
  deadline: string;
  accessibility: string;
  host: string;
  safetyNote: string;
  checklist: string[];
};

export const upcomingPlans: UpcomingPlan[] = [
  {
    id: "walk-saturday",
    title: "Volta curta no sabado",
    circle: "Amigos de Lisboa",
    time: "Sabado, 10:00",
    place: "Jardim publico",
    costTier: "gratis",
    durationLabel: "plano",
    acceptedCount: 3,
    capacity: 6,
    deadline: "fecha hoje as 18:00",
    accessibility: "percurso curto, bancos perto",
    host: "Marta",
    safetyNote: "O anfitriao espera no ponto combinado e confirma presencas.",
    checklist: [
      "Levar agua",
      "Confirmar se o percurso esta confortavel",
      "Sair sem culpa se precisares"
    ]
  },
  {
    id: "family-table",
    title: "Mesa com pergunta",
    circle: "Familia",
    time: "Domingo, jantar",
    place: "Casa",
    costTier: "gratis",
    durationLabel: "realista",
    acceptedCount: 2,
    capacity: 5,
    deadline: "fecha amanha as 12:00",
    accessibility: "sentado, baixo ruido",
    host: "Tiago",
    safetyNote: "Plano privado: so pessoas deste circulo veem a memoria.",
    checklist: [
      "Escolher uma pergunta simples",
      "Sem telemoveis durante 15 minutos",
      "Cada pessoa pode passar a vez"
    ]
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
