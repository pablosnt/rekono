import { jwtDecode } from "jwt-decode";

export const useUserStore = defineStore("user", {
  state: () => ({ user: null, role: null, refreshing: false }),
  actions: {
    login(token: string) {
      const payload = jwtDecode(token);
      this.user = payload.user_id;
      this.role = payload.role;
    },
    logout() {
      this.user = null;
      this.role = null;
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
  },
});
