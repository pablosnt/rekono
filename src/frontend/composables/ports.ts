export function usePorts() {
  const enums = useEnums();
  function getIcon(port: number): string {
    switch (port) {
      case 20:
      case 21:
      case 69:
      case 115:
      case 989:
      case 990:
        return "mdi-folder-network";
      case 22:
      case 23:
        return "mdi-ssh";
      case 25:
      case 109:
      case 110:
      case 143:
      case 465:
      case 587:
      case 993:
      case 995:
        return "mdi-email";
      case 53:
      case 80:
      case 443:
      case 8080:
        return "mdi-web";
      case 123:
        return "mdi-timer-cog";
      case 137:
      case 139:
      case 445:
        return "mdi-nas";
      case 3306:
      case 5432:
      case 2483:
      case 2484:
        return "mdi-database";
      default:
        return enums.findings.Port.icon;
    }
  }

  return { getIcon };
}
