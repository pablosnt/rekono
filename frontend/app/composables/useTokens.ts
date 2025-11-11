import { useUserStore } from "~/store/user";

export default function () {
  const mfaToken = "mfa-token";
  const accessToken = "access-token";
  const refreshToken = "refresh-token";
  const user = useUserStore();

  function get(): object {
    return {
      access: localStorage.getItem(accessToken),
      refresh: localStorage.getItem(refreshToken),
      mfa: sessionStorage.getItem(mfaToken),
    };
  }

  function remove(): void {
    localStorage.removeItem(accessToken);
    localStorage.removeItem(refreshToken);
    sessionStorage.removeItem(mfaToken);
  }

  function login(data: object): boolean {
    if (data) {
      if (data.access) {
        remove();
        localStorage.setItem(accessToken, data.access);
        localStorage.setItem(refreshToken, data.refresh);
        user.login(data.access);
        return true;
      } else if (data.mfa) {
        remove();
        sessionStorage.setItem(mfaToken, data.mfa);
        return false;
      }
    }
    return false;
  }

  return { get, remove, login };
}
