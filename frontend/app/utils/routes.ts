const publicRoutes = new Set(["login", "signup", "reset-password", "mfa"]);

export function isPublicRoute(routeName: string | null | undefined): boolean {
  return publicRoutes.has(routeName as string);
}
