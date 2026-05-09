import { jwtDecode, type JwtPayload } from "jwt-decode";
import type { User } from "~/types/models";

interface UserPayload extends JwtPayload {
  user_id: number;
  role: string;
}

export const useUserStore = defineStore("user", {
  state: () => ({
    user: null as number | null,
    name: null as string | null,
    role: null as string | null,
    refreshing: false,
    is_partial_authenticated: false,
    is_authenticated: false,
    expiration: null as number | null,
    is_admin: false,
    is_auditor: false,
    profile: null as User | null,
  }),
  actions: {
    login(response: Record<string, string>) {
      this.is_partial_authenticated =
        Boolean(response.mfa) && !response.access;
      this.is_authenticated =
        Boolean(response.access) && !response.mfa;
      if (this.is_authenticated) {
        localStorage.setItem("authenticated", true);
        this.fetchProfile();
        const payload = jwtDecode<UserPayload>(response.access);
        this.expiration = payload.exp;
      }
    },
    check() {
      if (
        localStorage.getItem("authenticated") === "true" &&
        !this.is_authenticated
      ) {
        this.is_partial_authenticated = false;
        this.is_authenticated = true;
        this.fetchProfile();
      }
    },
    refresh() {
      this.refreshing = !this.refreshing;
    },
    fetchProfile() {
      useApi()
        .get("profile/")
        .then((response: User) => {
          this.updateProfile(response);
        });
    },
    updateProfile(profile: User) {
      this.profile = profile;
      this.user = profile.id;
      this.name = getUserDisplayName(profile);
      this.role = profile.role;
      this.is_admin = this.isRole("admin");
      this.is_auditor = this.is_admin || this.isRole("auditor");
    },
    isRole(role: string): boolean {
      return (this.role?.toLowerCase() ?? "") === role.toLowerCase();
    },
    isOwner(entity: Record<string, unknown>, field: string = "owner"): boolean {
      return (
        entity[field] !== null &&
        entity[field] !== undefined &&
        ((entity[field] as Record<string, number | unknown>).id as number) ===
          this.user
      );
    },
  },
});
