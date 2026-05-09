import { useUserStore } from "~/store/user";

export default defineNuxtRouteMiddleware(() => {
  if (import.meta.server) return;

  useUserStore().check();
});
