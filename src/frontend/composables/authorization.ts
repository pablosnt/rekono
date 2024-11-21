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

  function isOwner(entity: object, field: string = "owner"): boolean {
    return entity[field] && item[field].id === user.user;
  }

  return { isAdmin, isAuditor, isOwner };
}
