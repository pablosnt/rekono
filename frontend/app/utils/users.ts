export function getUserDisplayName(user: User): string {
  return user.first_name || user.username || user.email || "";
}
