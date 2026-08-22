import { useUserStore } from "~/store/user";
import type { FilterOption } from "~/types/crud";
import type {
  User,
  Tool,
  Configuration,
  Target,
  Process,
  Task,
  Finding,
} from "~/types/models";
import { targetTypes } from "~/constants";
import { getTaskName } from "~/utils/tasks";

function parseTarget(target: Target): FilterOption {
  return {
    value: target.id,
    label: target.target,
    icon: targetTypes.find((t) => t.value === target.type)?.icon,
  };
}

export default function () {
  const api = useApi("/api/");
  const userStore = useUserStore();

  function users(
    optionsRef: Ref<FilterOption[]>,
    queryParams: Record<string, string> = {},
  ) {
    api.list("users/", queryParams, true).then((response) => {
      if (optionsRef.value.length === 0) {
        optionsRef.value = [
          {
            label: "Current user",
            value: userStore.user,
          },
        ];
      }
      optionsRef.value = [
        ...optionsRef.value,
        ...(response.items as User[])
          .filter((user) => user.id !== userStore.user)
          .map((user) => ({
            label: user.username,
            value: user.id,
            avatar: {
              text: user.username.charAt(0).toUpperCase(),
              class: "bg-muted text-foreground",
            },
          })),
      ];
    });
  }

  function tools(
    optionsRef: Ref<FilterOption[]>,
    queryParams: Record<string, string> = {},
  ) {
    api.list("tools/", queryParams, true).then((response) => {
      optionsRef.value = (response.items as Tool[]).map((tool) => ({
        avatar: tool.icon ? { src: tool.icon } : undefined,
        icon: tool.icon ? undefined : "i-lucide-square-terminal",
        label: tool.name,
        value: tool.id,
      }));
    });
  }

  function configurations(
    optionsRef: Ref<FilterOption[]>,
    queryParams: Record<string, string> = {},
  ) {
    api.list("configurations/", queryParams, true).then((response) => {
      optionsRef.value = (response.items as Configuration[]).map(
        (configuration) => ({
          label: configuration.name,
          description: configuration.tool.name,
          value: configuration.id,
        }),
      );
    });
  }

  function processes(
    optionsRef: Ref<FilterOption[]>,
    queryParams: Record<string, string> = {},
  ) {
    api.list("processes/", queryParams, true).then((response) => {
      optionsRef.value = (response.items as Process[]).map((process) => ({
        label: process.name,
        value: process.id,
      }));
    });
  }

  function targets(
    optionsRef: Ref<FilterOption[]>,
    queryParams: Record<string, string> = {},
  ) {
    api.list("targets/", queryParams, true).then((response) => {
      optionsRef.value = (response.items as Target[]).map(parseTarget);
    });
  }

  function option<T>(
    endpoint: string,
    value: string | number,
    parser: (item: T) => FilterOption,
  ): Promise<FilterOption> {
    return api.get(`${endpoint}${value}/`).then((item) => parser(item as T));
  }

  function target(value: string | number): Promise<FilterOption> {
    return option("targets/", value, parseTarget);
  }

  function task(value: string | number): Promise<FilterOption> {
    return option<Task>("tasks/", value, (task) => ({
      label: getTaskName(task, true),
      value: task.id,
    }));
  }

  function host(value: string | number): Promise<FilterOption> {
    return option<Finding>("hosts/", value, (host) => ({
      label: host.ip,
      value: host.id,
    }));
  }

  function port(value: string | number): Promise<FilterOption> {
    return option<Finding>("ports/", value, (port) => ({
      label: port.host ? `${port.host?.ip}:${port.port}` : port.port.toString(),
      value: port.id,
      icon: getPortIcon(port.port, port.service),
    }));
  }

  function technology(value: string | number): Promise<FilterOption> {
    return option<Finding>("technologies/", value, (technology) => ({
      label: technology.version
        ? `${technology.name} ${technology.version}`
        : technology.name,
      value: technology.id,
    }));
  }

  function credential(value: string | number): Promise<FilterOption> {
    return option<Finding>("credentials/", value, (credential) => ({
      label:
        credential.email ||
        credential.username ||
        `Credential #${credential.id}`,
      value: credential.id,
    }));
  }

  function vulnerability(value: string | number): Promise<FilterOption> {
    return option<Finding>("vulnerabilities/", value, (vulnerability) => ({
      label: vulnerability.name,
      value: vulnerability.id,
    }));
  }

  function exploit(value: string | number): Promise<FilterOption> {
    return option<Finding>("exploits/", value, (exploit) => ({
      label: exploit.title,
      value: exploit.id,
    }));
  }

  return {
    users,
    tools,
    configurations,
    processes,
    targets,
    target,
    task,
    host,
    port,
    technology,
    credential,
    vulnerability,
    exploit,
  };
}
