import type { FilterOption } from "~/types/crud";
import type { User } from "~/types/users";
import { useUserStore } from "~/store/user";

export default function () {
  function firstUpper(value: string) {
    return `${value.charAt(0).toUpperCase()}${value.slice(1)}`;
  }

  const stageOptions = [
    { label: "OSINT", value: 1, icon: "i-lucide-globe" },
    { label: "Enumeration", value: 2, icon: "i-lucide-network" },
    { label: "Vulnerabilities", value: 3, icon: "i-lucide-bug" },
    { label: "Services", value: 4, icon: "i-lucide-server" },
    { label: "Exploitation", value: 5, icon: "i-lucide-flame" },
  ];

  const intensityOptions = [
    { value: 1, label: "Sneaky", color: "success" },
    { value: 2, label: "Low", color: "info" },
    { value: 3, label: "Normal", color: "neutral" },
    { value: 4, label: "Hard", color: "warning" },
    { value: 5, label: "Insane", color: "error" },
  ];

  const timeUnitOptions = ["Weeks", "Days", "Hours", "Minutes"];

  const wordlistTypes = [
    {
      label: "Endpoint",
      value: "Endpoint",
      icon: "i-lucide-globe",
    },
    {
      label: "Subdomain",
      value: "Subdomain",
      icon: "i-lucide-server",
    },
  ];

  function getUserOptions(
    userOptionsRef: Ref<FilterOption[]>,
    queryParams?: Record<string, string> = {},
  ) {
    const userStore = useUserStore();
    useApi("/api/users/")
      .list("", queryParams, true)
      .then((response) => {
        if (userOptionsRef.value.length === 0) {
          userOptionsRef.value = [
            {
              label: "Current user",
              value: userStore.user,
            },
          ];
        }
        userOptionsRef.value = [
          ...userOptionsRef.value,
          ...(response.items as User[])
            .filter((user) => user.id.toString() !== userStore.user)
            .map((user) => ({
              label: user.username,
              value: user.id,
              avatar: {
                text: user.username.charAt(0).toUpperCase(),
                class: "bg-muted text-foreground",
              },
            })),
        ];
      })
      .catch(() => {
        userOptionsRef.value = [];
      });
  }

  function getToolOptions(
    toolOptionsRef: Ref<FilterOption[]>,
    queryParams?: Record<string, string> = {},
  ) {
    useApi("/api/tools/")
      .list("", queryParams, true)
      .then((response) => {
        toolOptionsRef.value = (response.items as Tool[]).map((tool) => ({
          avatar: tool.icon ? { src: tool.icon } : undefined,
          icon: tool.icon ? undefined : "i-lucide-square-terminal",
          label: tool.name,
          value: tool.id,
        }));
      });
  }

  function getPortIcon(port: number, serviceName?: string): string {
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
        return "i-lucide-network";
    }
  }

  return {
    firstUpper,
    stageOptions,
    getUserOptions,
    getToolOptions,
    intensityOptions,
    timeUnitOptions,
    wordlistTypes,
    getPortIcon,
  };
}
