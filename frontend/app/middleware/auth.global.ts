import { useUserStore } from "~/store/user";
import { useIntegrationsStore } from "~/store/integrations";

export default defineNuxtRouteMiddleware((to, _) => {
  if (import.meta.server) return;

  const publicRoutes = ["login", "signup", "reset-password", "mfa"];

  const userStore = useUserStore();
  userStore.check();
  const isAuthenticated = !!userStore.user;

  if (isAuthenticated) {
    const integrationsStore = useIntegrationsStore();
    if (integrationsStore.isEmpty) {
      integrationsStore.fetch();
    }
  }

  const isPublicRoute = publicRoutes.includes(to.name as string);
  if (!isPublicRoute && !isAuthenticated) {
    return navigateTo("/login");
  } else if (isPublicRoute && isAuthenticated) {
    return navigateTo("/");
  }
});
