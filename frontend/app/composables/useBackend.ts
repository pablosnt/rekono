import type { FilterOption } from "~/types/crud";
import type {
  User,
  Target,
  Task,
  Tool,
  Configuration,
  Note,
  Process,
} from "~/types/models";
import { useUserStore } from "~/store/user";

// TODO: We have to split this in different composables. It's not sustainable

export default function () {
  const alerts = [
    { item: "OSINT", icon: "i-lucide-rss", field: null },
    { item: "Host", icon: "i-lucide-server", field: "ip" },
    { item: "Open Port", icon: "i-lucide-ethernet-port", field: null },
    { item: "Service", icon: "i-lucide-ethernet-port", field: "service" },
    { item: "Technology", icon: "i-lucide-layers", field: "name" },
    { item: "Credential", icon: "i-lucide-key", field: null },
    { item: "Vulnerability", icon: "i-lucide-bug", field: null },
    { item: "CVE", icon: "i-lucide-bug", field: "cve" },
    { item: "Trending CVE", icon: "i-lucide-bug", field: "trending" },
  ];

  const stages = [
    { label: "OSINT", value: 1, icon: "i-lucide-rss" },
    { label: "Enumeration", value: 2, icon: "i-lucide-network" },
    { label: "Vulnerabilities", value: 3, icon: "i-lucide-bug" },
    { label: "Services", value: 4, icon: "i-lucide-server" },
    { label: "Exploitation", value: 5, icon: "i-lucide-flame" },
  ];

  const intensities = [
    { value: 1, label: "Sneaky", color: "success" },
    { value: 2, label: "Low", color: "info" },
    { value: 3, label: "Normal", color: "neutral" },
    { value: 4, label: "Hard", color: "warning" },
    { value: 5, label: "Insane", color: "error" },
  ];

  const timeUnits = ["Weeks", "Days", "Hours", "Minutes"];

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

  const roles = ["Reader", "Auditor", "Admin"];

  const reportFormats = [
    { label: "JSON", value: "json", icon: "i-lucide-braces" },
    { label: "XML", value: "xml", icon: "i-lucide-code-xml" },
    { label: "PDF", value: "pdf", icon: "i-lucide-file-text" },
  ];

  const reportStatuses = [
    { value: "Ready", color: "success", icon: "i-lucide-check-circle" },
    { value: "Pending", color: "warning", icon: "i-lucide-clock" },
    { value: "Error", color: "error", icon: "i-lucide-x-circle" },
  ];

  const findingTypes = [
    { value: "OSINT", icon: "i-lucide-rss" },
    { value: "Host", icon: "i-lucide-server" },
    { value: "Port", icon: "i-lucide-ethernet-port" },
    { value: "Path", icon: "i-lucide-slash" },
    { value: "Technology", icon: "i-lucide-layers" },
    { value: "Credential", icon: "i-lucide-key" },
    { value: "Vulnerability", icon: "i-lucide-bug" },
    { value: "Exploit", icon: "i-lucide-flame" },
  ];

  const triageStatuses = [
    { value: "Untriaged", color: "neutral", icon: "i-lucide-circle-help" },
    { value: "True Positive", color: "success", icon: "i-lucide-circle-alert" },
    {
      value: "False Positive",
      color: "error",
      icon: "i-lucide-circle-x",
    },
    { value: "Won't Fix", color: "warning", icon: "i-lucide-circle-minus" },
  ];

  const pathTypes = [
    { value: "Endpoint", icon: "i-lucide-globe" },
    { value: "Share", icon: "i-lucide-folder-open" },
  ];

  const osintDataTypes = [
    { value: "IP", icon: "i-lucide-server" },
    { value: "Domain", icon: "i-lucide-globe" },
    { value: "VHOST", icon: "i-lucide-globe" },
    { value: "URL", icon: "i-lucide-link" },
    { value: "Email", icon: "i-lucide-mail" },
    { value: "ASN", icon: "i-lucide-network" },
    { value: "Username", icon: "i-lucide-user" },
    { value: "Password", icon: "i-lucide-key" },
  ];

  const hostOS = [
    { value: "Linux", icon: "simple-icons:linux", color: "warning" },
    { value: "Windows", icon: "lineicons:microsoft", color: "info" },
    { value: "MacOS", icon: "lineicons:apple-brand", color: "neutral" },
    { value: "iOS", icon: "lineicons:apple-brand", color: "neutral" },
    { value: "Android", icon: "lineicons:android-original", color: "success" },
    { value: "Solaris", icon: "simple-icons:oracle", color: "error" },
    { value: "FreeBSD", icon: "simple-icons:freebsd", color: "error" },
    { value: "Other", icon: "i-lucide-server", color: "neutral" },
  ];

  const portStatuses = [
    { value: "Open", color: "success", icon: "i-lucide-square-check" },
    { value: "Open - Filtered", color: "warning", icon: "i-lucide-brick-wall" },
    { value: "Filtered", color: "warning", icon: "i-lucide-brick-wall-shield" },
    { value: "Closed", color: "error", icon: "i-lucide-square-x" },
  ];

  const portProtocols = ["TCP", "UDP"];

  const targetTypes = [
    { value: "Private IP", icon: "i-mdi-security-network" },
    { value: "Public IP", icon: "i-mdi-ip-network" },
    { value: "Network", icon: "i-lucide-network" },
    { value: "IP range", icon: "i-lucide-arrow-left-right" },
    { value: "Domain", icon: "i-lucide-globe" },
  ];

  const authenticationTypes = [
    "None",
    "Basic",
    "Bearer",
    "Cookie",
    "Digest",
    "JWT",
    "NTLM",
    "Token",
  ];

  const executionStatuses = [
    { color: "warning", icon: "i-lucide-loader", value: "Running" },
    { color: "success", icon: "i-lucide-circle-check", value: "Completed" },
    { color: "error", icon: "i-lucide-circle-x", value: "Error" },
    { color: "neutral", icon: "i-lucide-ban", value: "Cancelled" },
    { color: "neutral", icon: "i-lucide-skip-forward", value: "Skipped" },
    { color: "info", icon: "i-lucide-clock", value: "Requested" },
  ];

  function httpStatusColor(status: number): string {
    if (status >= 200 && status < 300) return "success";
    if (status >= 300 && status < 400) return "info";
    if (status >= 400 && status < 500) return "warning";
    if (status >= 500) return "error";
    return "neutral";
  }

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

  function getConfigurationOptions(
    configurationOptionsRef: Ref<FilterOption[]>,
    queryParams?: Record<string, string> = {},
  ) {
    useApi("/api/configurations/")
      .list("", queryParams, true)
      .then((response) => {
        configurationOptionsRef.value = (response.items as Configuration[]).map(
          (configuration) => ({
            label: configuration.name,
            description: configuration.tool.name,
            value: configuration.id,
          }),
        );
      });
  }

  function getProcessOptions(
    processOptionsRef: Ref<FilterOption[]>,
    queryParams?: Record<string, string> = {},
  ) {
    useApi("/api/processes/")
      .list("", queryParams, true)
      .then((response) => {
        processOptionsRef.value = (response.items as Process[]).map(
          (process) => ({
            label: process.name,
            value: process.id,
          }),
        );
      });
  }

  function getTargetOptions(
    targetOptionsRef: Ref<FilterOption[]>,
    queryParams?: Record<string, string> = {},
  ) {
    useApi("/api/targets/")
      .list("", queryParams, true)
      .then((response) => {
        targetOptionsRef.value = (response.items as Target[]).map((target) => ({
          id: target.id,
          target: target.target,
          icon: targetTypes.find((t) => t.value === target.type)?.icon,
        }));
      });
  }

  function getTaskName(task: Task, includeTarget?: boolean) {
    const scanner = task.process
      ? task.process.name
      : `${task.configuration?.tool.name} (${task.configuration?.name})`;
    const target_port = task.target_port
      ? `:${task.target_port.port}${task.target_port.path ? (task.target_port.path[0] === "/" ? task.target_port.path : `/${task.target_port.path}`) : ""}`
      : "";
    const target = `${task.target.target}${target_port}`;
    const text = includeTarget ? `${scanner} - ${target}` : scanner;
    return task.start
      ? `${text} - ${new Date(task.start).toLocaleString()}`
      : text;
  }

  function getTaskOptions(
    taskOptionsRef: Ref<FilterOption[]>,
    queryParams?: Record<string, string> = {},
  ) {
    useApi("/api/tasks/")
      .list("", queryParams, true)
      .then((response) => {
        taskOptionsRef.value = (response.items as Task[]).map((task) => ({
          label: getTaskName(task, true),
          value: task.id,
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
        return "i-lucide-ethernet-port";
    }
  }

  function getUserDisplayName(user: User): string {
    return user.first_name ? user.first_name : user.username || user.email;
  }

  function getNoteRelatedEntity(
    note: Note,
  ): Record<string, string | undefined> | null {
    const route = useRoute();
    const baseTo = `/projects/${route.params.project_id}/`;
    for (const definition of [
      {
        entity: note.exploit,
        to: note.exploit?.vulnerability
          ? `${baseTo}vulnerabilities/${note.exploit?.vulnerability}`
          : note.exploit?.technology?.port?.host?.id
            ? `${baseTo}assets/${note.exploit?.technology?.port?.host?.id}`
            : undefined,
        label: note.exploit?.title,
        icon: "i-lucide-flame",
      },
      {
        entity: note.vulnerability,
        to: `${baseTo}vulnerabilities/${note.vulnerability?.id}`,
        label: note.vulnerability?.name,
        icon: "i-lucide-bug",
      },
      // todo: We might have to include credentials on the technologies page, instead of on a custom view. If so, we can split the views on OSINT, Assets and Vulnerabilities
      {
        entity: note.credential,
        to: `${baseTo}credentials/${note.credential?.id}`,
        icon: "i-lucide-key",
        label:
          note.credential?.username ||
          note.credential?.email ||
          `#${note.credential?.id}`,
      },
      {
        entity: note.technology,
        to: note.technology?.port?.host?.id
          ? `${baseTo}assets/${note.technology?.port?.host?.id}`
          : undefined,
        label: note.technology?.name,
        icon: "i-lucide-code",
      },
      {
        entity: note.path,
        to: note.path?.port?.host?.id
          ? `${baseTo}assets/${note.path?.port?.host?.id}`
          : undefined,
        label: note.path?.path,
        icon: "i-lucide-slash",
      },
      {
        entity: note.port,
        to: `${baseTo}assets/${note.port?.host}`,
        icon: "i-lucide-keethernet-porty",
        label: `${note.port?.host?.ip}:${note.port?.port}`,
      },
      {
        entity: note.host,
        to: `${baseTo}assets/${note.host?.id}`,
        icon: "i-lucide-server",
        label: note.host?.ip,
      },
      {
        entity: note.osint,
        to: `${baseTo}osint/${note.osint?.id}`,
        icon: "i-lucide-rss",
        label: note.osint?.data,
      },
      {
        entity: note.task,
        to: `${baseTo}scans/${note.task?.id}`,
        icon: "i-lucide-play",
        label: note.task?.process
          ? note.task.process.name
          : note.task?.configuration?.tool.name,
      },
      {
        entity: note.target,
        to: `${baseTo}targets/${note.target?.id}`,
        icon: note.target
          ? targetTypes.find((t) => t.value === note.target?.type)?.icon
          : "i-lucide-locate-fixed",
        label: note.target?.target,
      },
    ]) {
      if (definition.entity) {
        return {
          to: definition.to,
          icon: definition.icon,
          label: definition.label || "",
        };
      }
    }
    return null;
  }

  return {
    alerts,
    stages,
    intensities,
    timeUnits,
    wordlistTypes,
    roles,
    reportFormats,
    reportStatuses,
    findingTypes,
    triageStatuses,
    pathTypes,
    osintDataTypes,
    hostOS,
    portStatuses,
    portProtocols,
    targetTypes,
    authenticationTypes,
    executionStatuses,
    httpStatusColor,
    getUserOptions,
    getToolOptions,
    getConfigurationOptions,
    getProcessOptions,
    getTargetOptions,
    getTaskName,
    getTaskOptions,
    getPortIcon,
    getUserDisplayName,
    getNoteRelatedEntity,
  };
}
