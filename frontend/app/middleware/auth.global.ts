import { useUserStore } from "~/store/user";

export default defineNuxtRouteMiddleware((to, _) => {
  if (import.meta.server) return;

  const publicRoutes = ["login", "signup", "reset-password"];
  const userStore = useUserStore();

  userStore.check();

  const isAuthenticated = !!userStore.user;
  const isPublicRoute = publicRoutes.includes(to.name as string);

  if (!isPublicRoute && !isAuthenticated) {
    return navigateTo("/login");
  } else if (isPublicRoute && isAuthenticated) {
    return navigateTo("/");
  }
});
