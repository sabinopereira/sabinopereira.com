export type AppMemory = {
  id: string;
  planId: string;
  title: string;
  circle: string;
  time: string;
  place: string;
  privacy: "private" | "participants";
  prompt: string;
  note?: string;
};
