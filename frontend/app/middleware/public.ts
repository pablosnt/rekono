import { useUserStore } from "~/store/user";

export default defineNuxtRouteMiddleware(() => {
  if (import.meta.server) return;

  const userStore = useUserStore();
  if (userStore.user) {
    return navigateTo("/");
  }
});
