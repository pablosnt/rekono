export function useValidation() {
  function password(password: string): boolean {
    const regexes = [
      /^[A-Za-z0-9\W]{12,}$/,
      /^.*[a-z]+.*$/,
      /^.*[A-Z]+.*$/,
      /^.*[0-9]+.*$/,
      /^.*[\W]+.*$/,
    ];
    for (let i = 0; i < regexes.length; i++) {
      if (!regexes[i].test(password)) {
        return false;
      }
    }
    return true;
  }

  return {
    email: /^[\w.-]+@[\w-]+\.[\w.-]+$/,
    name: /^[\wÀ-ÿ\s.:\-[\]()@]{0,120}$/,
    text: /^[^;<>]*$/,
    mfa: /^[\d]{6}$/,
    secret: /^[\w\s./\-=+,:<>¿?¡!#&$()@%[\]{}*]{1,500}$/,
    target: /^[\w\d.:\-/]{1,100}$/,
    targetRegex: /^[\w\d.,:\-/*?+()\\]{1,300}$/,
    password,
    cve: /^CVE-\d{4}-\d{1,7}$/,
  };
}
