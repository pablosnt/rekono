import { jwtDecode } from "jwt-decode";
import type { User } from "~/types/models";
import { useIntegrationsStore } from "./integrations";

export const useUserStore = defineStore("user", {
  state: () => ({
    user: null as number | null,
    name: null as string | null,
    role: null as string | null,
    refreshing: false,
    refreshTimeout: null as NodeJS.Timeout | null,
    is_partial_authenticated: false,
    is_authenticated: false,
    is_admin: false,
    is_auditor: false,
    profile: null as User | null,
  }),
  actions: {
    login(response: Record<string, string>) {
      this.is_partial_authenticated = Boolean(response.mfa) && !response.access;
      this.is_authenticated = Boolean(response.access) && !response.mfa;
      if (this.is_authenticated) {
        localStorage.setItem("authenticated", true);
        this.fetchProfile();
        this.scheduleSilentRefreshing(response.access);
      }
    },
    scheduleSilentRefreshing(access: string) {
      this.refreshTimeout = setTimeout(
        this.refresh,
        new Date(jwtDecode(access).exp * 1000).getTime() -
          Date.now() -
          60 * 1000,
      );
    },
    refresh() {
      useApi("")
        .refresh()
        .then((response) => this.scheduleSilentRefreshing(response.access));
    },
    logout() {
      if (this.refreshTimeout) clearTimeout(this.refreshTimeout);
      localStorage.removeItem("authenticated");
      this.$reset();
      useIntegrationsStore().$reset();
      navigateTo("/login");
    },
    check() {
      if (
        localStorage.getItem("authenticated") === "true" &&
        !this.is_authenticated
      ) {
        return this.fetchProfile();
      }
    },
    switchRefreshing() {
      this.refreshing = !this.refreshing;
    },
    fetchProfile() {
      return useApi()
        .get("profile/")
        .then((response: User) => {
          this.is_partial_authenticated = false;
          this.is_authenticated = true;
          this.updateProfile(response);
        })
        .catch(() => this.logout());
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
