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
  originMission?: string;
  safetyNote: string;
  checklist: string[];
  attendees: CircleMember[];
};

export type CircleMember = {
  id: string;
  displayName: string;
  username: string;
  locality: string;
  avatar: string;
};

export const circleMembers: Record<string, CircleMember[]> = {
  Familia: [
    {
      id: "tiago",
      displayName: "Tiago",
      username: "@tiago",
      locality: "Lisboa",
      avatar: "T"
    },
    {
      id: "ana",
      displayName: "Ana",
      username: "@ana",
      locality: "Odivelas",
      avatar: "A"
    },
    {
      id: "ines",
      displayName: "Ines",
      username: "@ines",
      locality: "Lisboa",
      avatar: "I"
    }
  ],
  "Amigos de Lisboa": [
    {
      id: "marta",
      displayName: "Marta",
      username: "@marta",
      locality: "Campo de Ourique",
      avatar: "M"
    },
    {
      id: "rui",
      displayName: "Rui",
      username: "@rui",
      locality: "Almada",
      avatar: "R"
    },
    {
      id: "joana",
      displayName: "Joana",
      username: "@joana",
      locality: "Lisboa",
      avatar: "J"
    }
  ]
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
    originMission: "Faz uma coisa simples fora de casa com alguem.",
    safetyNote: "Quem criou o plano espera no ponto combinado e confirma presencas.",
    checklist: [
      "Levar agua",
      "Confirmar se o percurso esta confortavel",
      "Sair sem culpa se precisares"
    ],
    attendees: circleMembers["Amigos de Lisboa"]
  },
  {
    id: "family-table",
    title: "Conversa a mesa",
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
    originMission: "Cria um momento de familia sem telemoveis.",
    safetyNote: "Plano privado: so pessoas deste circulo veem a memoria.",
    checklist: [
      "Escolher uma pergunta simples",
      "Sem telemoveis durante 15 minutos",
      "Cada pessoa pode passar a vez"
    ],
    attendees: circleMembers.Familia
  }
];

export const circles = [
  {
    id: "family",
    name: "Familia",
    type: "Familia",
    members: 4,
    next: "Conversa a mesa",
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
