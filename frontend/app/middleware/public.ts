import { useUserStore } from "~/store/user";

export default defineNuxtRouteMiddleware(() => {
  if (import.meta.server) return;

  if (useUserStore().is_authenticated) {
    return navigateTo("/");
  }
});
