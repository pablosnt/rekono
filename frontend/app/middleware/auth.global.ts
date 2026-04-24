import { useUserStore } from "~/store/user";
import { useIntegrationsStore } from "~/store/integrations";

export default defineNuxtRouteMiddleware((to, _) => {
  if (import.meta.server) return;

  const userStore = useUserStore();
  userStore.check();
  const isAuthenticated = !!userStore.user;

  if (isAuthenticated) {
    const integrationsStore = useIntegrationsStore();
    if (integrationsStore.isEmpty) {
      integrationsStore.fetch();
    }
  }

  const isPublic = isPublicRoute(to.name as string);
  if (!isPublic && !isAuthenticated) {
    return navigateTo("/login");
  } else if (isPublic && isAuthenticated) {
    return navigateTo("/");
  }
});
