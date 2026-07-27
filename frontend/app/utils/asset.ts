export function asset(path: string): string {
  const baseUrl = useRuntimeConfig().app?.baseURL || "/";
  return `${baseUrl.endsWith("/") ? baseUrl.slice(0, -1) : baseUrl}${path}`;
}
