export function getPortIcon(port: number, serviceName?: string): string {
  if (serviceName) {
    const service = serviceName.toLowerCase();
    if (
      service.includes("http") ||
      service.includes("web") ||
      service.includes("apache") ||
      service.includes("nginx")
    ) {
      return "i-mdi-web";
    }
    if (service.includes("ssh") || service.includes("terminal")) {
      return "i-mdi-ssh";
    }
    if (service.includes("ftp") || service.includes("sftp")) {
      return "i-mdi-folder-network";
    }
    if (
      service.includes("mail") ||
      service.includes("smtp") ||
      service.includes("imap") ||
      service.includes("pop")
    ) {
      return "i-mdi-email";
    }
    if (
      service.includes("database") ||
      service.includes("mysql") ||
      service.includes("postgres") ||
      service.includes("mongo")
    ) {
      return "i-mdi-database";
    }
    if (service.includes("dns")) {
      return "i-lucide-route";
    }
    if (service.includes("ntp") || service.includes("time")) {
      return "i-mdi-timer-cog";
    }
    if (
      service.includes("share") ||
      service.includes("smb") ||
      service.includes("cifs")
    ) {
      return "i-mdi-nas";
    }
  }
  switch (port) {
    case 20:
    case 21:
    case 69:
    case 115:
    case 989:
    case 990:
      return "i-mdi-folder-network";
    case 22:
    case 23:
      return "i-mdi-ssh";
    case 25:
    case 109:
    case 110:
    case 143:
    case 465:
    case 587:
    case 993:
    case 995:
      return "i-mdi-email";
    case 53:
      return "i-lucide-route";
    case 80:
    case 443:
    case 8080:
    case 8443:
      return "i-mdi-web";
    case 123:
      return "i-mdi-timer-cog";
    case 137:
    case 139:
    case 445:
      return "i-mdi-nas";
    case 3306:
    case 5432:
    case 2483:
    case 2484:
      return "i-mdi-database";
    default:
      return "i-lucide-ethernet-port";
  }
}
