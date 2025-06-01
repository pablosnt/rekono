export default defineNuxtRouteMiddleware((to, _) => {
  const publicRoutes = ["login", "signup", "reset-password", "mfa"];
  const user = userStore();
  const tokens = useTokens();
  if (to.name === "login" && to.query.logout === "true") {
    const refresh = tokens.get().refresh;
    if (refresh) {
      useApi("/api/security/logout/", true).create({ refresh: refresh });
    }
    tokens.remove();
  } else {
    user.check();
    if (
      (to.name === "mfa" && !tokens.get().mfa) ||
      (!publicRoutes.includes(to.name) && !user.user)
    ) {
      return navigateTo("/login");
    } else if (publicRoutes.includes(to.name) && user.user) {
      return navigateTo("/");
    }
  }
});
