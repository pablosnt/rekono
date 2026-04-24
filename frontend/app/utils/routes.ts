const publicRoutes = ["login", "signup", "reset-password", "mfa"];

export function isPublicRoute(routeName: string | null | undefined): boolean {
  return publicRoutes.includes(routeName as string);
}
