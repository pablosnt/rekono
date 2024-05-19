export default defineNuxtRouteMiddleware((to, _) => {
  const user = userStore();
  const tokens = useTokens();
  const publicRoutes = ["login", "reset-password", "mfa"];
  user.check();
  if (
    (to.name === "mfa" && !tokens.get().mfa) ||
    (!publicRoutes.includes(to.name) && !user.user)
  ) {
    return navigateTo("/login");
  } else if (publicRoutes.includes(to.name) && user.user) {
    return navigateTo("/");
  }
});
