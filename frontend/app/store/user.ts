import { jwtDecode, type JwtPayload } from "jwt-decode";
import type { User } from "~/types/users";

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
    is_admin: false,
    is_auditor: false,
    profile: null as User | null,
  }),
  actions: {
    login(token: string) {
      const payload = jwtDecode<UserPayload>(token);
      this.user = payload.user_id;
      this.role = payload.role;
      this.is_admin = this.isRole("admin");
      this.is_auditor = this.is_admin || this.isRole("auditor");
      this.fetchProfile();
    },
    logout() {
      this.user = null;
      this.role = null;
      this.is_admin = false;
      this.is_auditor = false;
    },
    check() {
      const tokens = useTokens();
      const jwt = tokens.get().access;
      if (jwt !== null && this.user === null) {
        this.login(jwt);
      } else if (jwt === null && this.user !== null) {
        this.logout();
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
      this.name = profile.first_name
        ? profile.first_name
        : profile.username
          ? profile.username
          : (profile.email ?? null);
    },
    isRole(role: string): boolean {
      return (this.role?.toLowerCase() ?? "") === role.toLowerCase();
    },
    isOwner(entity: Record<string, unknown>, field: string = "owner"): boolean {
      return entity[field] && (entity[field] as Record<string, unknown>).id === this.user;
    },
  },
});
