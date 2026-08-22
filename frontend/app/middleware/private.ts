import { useUserStore } from "~/store/user";
import { useIntegrationsStore } from "~/store/integrations";

export default defineNuxtRouteMiddleware(() => {
  if (import.meta.server) return;

  if (useUserStore().is_authenticated) {
    const integrationsStore = useIntegrationsStore();
    if (integrationsStore.isEmpty) {
      integrationsStore.fetch();
    }
  } else {
    return navigateTo("/login");
  }
});
