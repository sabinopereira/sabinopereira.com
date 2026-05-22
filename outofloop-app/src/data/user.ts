export type AppUser = {
  entryType: "guest" | "account";
  name?: string;
  email?: string;
};

export const defaultUser: AppUser = {
  entryType: "guest"
};
