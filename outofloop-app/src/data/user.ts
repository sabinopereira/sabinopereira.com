export type AppUser = {
  entryType: "guest" | "account";
  authMethod?: "email" | "apple" | "google";
  name?: string;
  email?: string;
  hasPassword?: boolean;
  photoUri?: string;
  username?: string;
  locality?: string;
  visibility?: {
    showPhoto: boolean;
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
    showPhoto: true,
    showName: true,
    showUsername: true,
    showLocality: true
  }
};
