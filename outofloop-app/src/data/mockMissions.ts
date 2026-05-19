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
