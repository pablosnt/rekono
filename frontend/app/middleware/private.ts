import { useUserStore } from "~/store/user";
import { useIntegrationsStore } from "~/store/integrations";

export default defineNuxtRouteMiddleware(() => {
  if (import.meta.server) return;

  const userStore = useUserStore();
  if (userStore.user) {
    const integrationsStore = useIntegrationsStore();
    if (integrationsStore.isEmpty) {
      integrationsStore.fetch();
    }
  } else {
    return navigateTo("/login");
  }
});
