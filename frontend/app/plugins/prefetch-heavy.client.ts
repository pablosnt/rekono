import { useUserStore } from "~/store/user";

export default defineNuxtPlugin((nuxtApp) => {
  if (!useUserStore().is_authenticated) return;

  const warm = () => {
    import("~/components/notes/editor.vue").catch(() => {});
    import("~/components/metrics/charts/bar.vue").catch(() => {});
  };

  nuxtApp.hook("app:mounted", () => {
    if (typeof window.requestIdleCallback === "function") {
      window.requestIdleCallback(warm, { timeout: 5000 });
    } else {
      setTimeout(warm, 3000);
    }
  });
});
