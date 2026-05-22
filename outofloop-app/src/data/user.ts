export type AppUser = {
  entryType: "guest" | "account";
  authMethod?: "email" | "apple" | "google";
  name?: string;
  email?: string;
  hasPassword?: boolean;
  username?: string;
  locality?: string;
  visibility?: {
    showName: boolean;
    showUsername: boolean;
    showLocality: boolean;
  };
};

export const defaultUser: AppUser = {
  entryType: "guest",
  username: "@tu",
  locality: "A tua zona",
  visibility: {
    showName: true,
    showUsername: true,
    showLocality: true
  }
};
