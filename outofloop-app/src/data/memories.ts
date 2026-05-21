export type AppMemory = {
  id: string;
  sourceId: string;
  sourceType: "mission" | "plan";
  title: string;
  circle: string;
  time: string;
  place: string;
  privacy: "private" | "participants";
  prompt: string;
  note?: string;
};
