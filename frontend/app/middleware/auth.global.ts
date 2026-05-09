import { useUserStore } from "~/store/user";

export default defineNuxtRouteMiddleware(async () => {
  if (import.meta.server) return;

  await useUserStore().check();
});
