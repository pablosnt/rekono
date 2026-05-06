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

export default function () {
  const api = useApi("/api/");
  const userStore = useUserStore();

  function users(
    optionsRef: Ref<FilterOption[]>,
    queryParams?: Record<string, string> = {},
  ) {
    api
      .list("users/", queryParams, true)
      .then((response) => {
        if (optionsRef.value.length === 0) {
          optionsRef.value = [
            {
              label: "Current user",
              value: parseInt(userStore.user),
            },
          ];
        }
        optionsRef.value = [
          ...optionsRef.value,
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
        optionsRef.value = [];
      });
  }

  function tools(
    optionsRef: Ref<FilterOption[]>,
    queryParams?: Record<string, string> = {},
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
    queryParams?: Record<string, string> = {},
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
    queryParams?: Record<string, string> = {},
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
    queryParams?: Record<string, string> = {},
  ) {
    api.list("targets/", queryParams, true).then((response) => {
      optionsRef.value = (response.items as Target[]).map((target) => ({
        value: target.id,
        label: target.target,
        icon: targetTypes.find((t) => t.value === target.type)?.icon,
      }));
    });
  }

  function tasks(
    optionsRef: Ref<FilterOption[]>,
    queryParams?: Record<string, string> = {},
  ) {
    api.list("tasks/", queryParams, true).then((response) => {
      optionsRef.value = (response.items as Task[]).map((task) => ({
        label: getTaskName(task, true),
        value: task.id,
      }));
    });
  }

  function findings(
    findingType: string,
    parser: (item: Finding) => FilterOption,
    optionsRef: Ref<FilterOption[]>,
    queryParams?: Record<string, string> = {},
  ) {
    api.list(`${findingType}/`, queryParams, true).then((response) => {
      optionsRef.value = (response.items as Finding[]).map((finding) =>
        parser(finding),
      );
    });
  }

  function osint(
    optionsRef: Ref<FilterOption[]>,
    queryParams?: Record<string, string> = {},
  ) {
    findings(
      "osint",
      (osint) => {
        return { label: osint.data, value: osint.id };
      },
      optionsRef,
      queryParams,
    );
  }

  function hosts(
    optionsRef: Ref<FilterOption[]>,
    queryParams?: Record<string, string> = {},
  ) {
    findings(
      "hosts",
      (host) => {
        return { label: host.ip, value: host.id };
      },
      optionsRef,
      queryParams,
    );
  }

  function ports(
    optionsRef: Ref<FilterOption[]>,
    queryParams?: Record<string, string> = {},
  ) {
    findings(
      "ports",
      (port) => {
        return {
          label: port.host
            ? `${port.host?.ip}:${port.port}`
            : port.port.toString(),
          value: port.id,
          icon: getPortIcon(port.port, port.service),
        };
      },
      optionsRef,
      queryParams,
    );
  }

  function technologies(
    optionsRef: Ref<FilterOption[]>,
    queryParams?: Record<string, string> = {},
  ) {
    findings(
      "technologies",
      (technology) => {
        return {
          label: technology.version
            ? `${technology.name} ${technology.version}`
            : technology.name,
          value: technology.id,
        };
      },
      optionsRef,
      queryParams,
    );
  }

  function credentials(
    optionsRef: Ref<FilterOption[]>,
    queryParams?: Record<string, string> = {},
  ) {
    findings(
      "credentials",
      (credential) => {
        return {
          label:
            credential.email ||
            credential.username ||
            `Credential #${credential.id}`,
          value: credential.id,
        };
      },
      optionsRef,
      queryParams,
    );
  }

  function vulnerabilities(
    optionsRef: Ref<FilterOption[]>,
    queryParams?: Record<string, string> = {},
  ) {
    findings(
      "vulnerabilities",
      (vulnerability) => {
        return { label: vulnerability.name, value: vulnerability.id };
      },
      optionsRef,
      queryParams,
    );
  }

  function exploits(
    optionsRef: Ref<FilterOption[]>,
    queryParams?: Record<string, string> = {},
  ) {
    findings(
      "exploits",
      (exploit) => {
        return { label: exploit.title, value: exploit.id };
      },
      optionsRef,
      queryParams,
    );
  }

  return {
    users,
    tools,
    configurations,
    processes,
    targets,
    tasks,
    osint,
    hosts,
    ports,
    technologies,
    credentials,
    vulnerabilities,
    exploits,
  };
}
