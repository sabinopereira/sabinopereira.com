import { AppMemory } from "./memories";

export type ProgressPath = {
  label: string;
  completedCount: number;
  missionCount: number;
  planCount: number;
  currentStage: string;
  nextStage: string | null;
  nextTarget: number | null;
  progressRatio: number;
  milestones: Array<{
    label: string;
    unlocked: boolean;
  }>;
};

const stages = [
  { name: "Acordar", target: 1 },
  { name: "Sair", target: 3 },
  { name: "Reparar", target: 7 },
  { name: "Convidar", target: 12 },
  { name: "Pertencer", target: 20 },
  { name: "Anfitriar", target: 35 }
];

export function buildProgressPath(memories: AppMemory[]): ProgressPath {
  const completedCount = memories.length;
  const missionCount = memories.filter(
    (memory) => memory.sourceType === "mission"
  ).length;
  const planCount = memories.filter((memory) => memory.sourceType === "plan")
    .length;
  const savedNoteCount = memories.filter((memory) => memory.note?.trim()).length;
  const currentIndex = Math.max(
    stages.findIndex((stage) => completedCount < stage.target) - 1,
    -1
  );
  const normalizedIndex =
    currentIndex === -1 ? 0 : Math.min(currentIndex, stages.length - 1);
  const nextStage = stages.find((stage) => completedCount < stage.target);
  const previousTarget =
    normalizedIndex === 0 ? 0 : stages[normalizedIndex - 1].target;
  const nextTarget = nextStage?.target ?? null;
  const progressRatio = nextTarget
    ? (completedCount - previousTarget) / (nextTarget - previousTarget)
    : 1;

  return {
    label:
      completedCount === 1
        ? "Saiste do loop 1 vez."
        : `Saiste do loop ${completedCount} vezes.`,
    completedCount,
    missionCount,
    planCount,
    currentStage: stages[normalizedIndex].name,
    nextStage: nextStage?.name ?? null,
    nextTarget,
    progressRatio: Math.max(0, Math.min(progressRatio, 1)),
    milestones: [
      {
        label: "Primeira missao concluida",
        unlocked: missionCount >= 1
      },
      {
        label: "Primeiro plano com pessoas",
        unlocked: planCount >= 1
      },
      {
        label: "Primeira memoria escrita",
        unlocked: savedNoteCount >= 1
      },
      {
        label: "Tres saidas do automatico",
        unlocked: completedCount >= 3
      }
    ]
  };
}
