export function useAutz() {
  const user = userStore();

  function isAdmin(): boolean {
    return user.role !== null && user.role.toLowerCase() === "admin";
  }

  function isAuditor(): boolean {
    return (
      isAdmin() || (user.role !== null && user.role.toLowerCase() === "auditor")
    );
  }

  return { isAdmin, isAuditor };
}
