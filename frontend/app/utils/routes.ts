const publicRoutes = new Set(["login", "signup", "reset-password", "mfa"]);
const neutralRoutes = new Set(["email-verification"]);

export function isPublicRoute(routeName: string | null | undefined): boolean {
  return publicRoutes.has(routeName as string);
}

export function isNeutralRoute(routeName: string | null | undefined): boolean {
  return neutralRoutes.has(routeName as string);
}
